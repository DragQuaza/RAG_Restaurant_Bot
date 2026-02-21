import os
import datetime
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
import database

from dotenv import load_dotenv
load_dotenv()

# Initialize Database
database.init_db()

# Load Vector Store         
def init_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    index_path = "faiss_index"
    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        loader = TextLoader("data/knowledge_base.txt")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        vectorstore = FAISS.from_documents(splits, embeddings)
        vectorstore.save_local(index_path)
    return vectorstore

try:
    vectorstore = init_vectorstore()
    retriever = vectorstore.as_retriever()
except Exception as e:
    retriever = None
    print(f"Warning: Could not initialize vectorstore: {e}")

@tool
def search_restaurant_knowledge(query: str) -> str:
    """Useful to search for restaurant policies, opening hours, menu, rules, etc."""
    if retriever:
        docs = retriever.invoke(query)
        return "\n\n".join([d.page_content for d in docs])
    return "Knowledge base unavailable."

class BookingInput(BaseModel):
    customer_name: str = Field(description="Name of the customer")
    phone_number: str = Field(description="Phone number of the customer")
    number_of_guests: int = Field(description="Number of guests")
    date: str = Field(description="Date of the booking (YYYY-MM-DD)")
    time: str = Field(description="Time of the booking (HH:MM AM/PM)")
    special_requests: str = Field(description="Any special requests or dietary restrictions", default="")

@tool(args_schema=BookingInput)
def book_table(customer_name: str, phone_number: str, number_of_guests: int, date: str, time: str, special_requests: str = "") -> str:
    """Books a table at the restaurant limit is 8 guests online."""
    if number_of_guests > 8:
        return "Sorry, the maximum table size for online booking is 8 guests. For larger parties, please contact us directly."
    booking_id = database.add_booking(customer_name, phone_number, number_of_guests, date, time, special_requests)
    return f"Success! Table booked. Your Booking ID is {booking_id}. IMPORTANT: Tell the user their booking ID."

@tool
def cancel_booking(booking_id: int) -> str:
    """Cancels a restaurant booking by booking ID."""
    success = database.cancel_booking(booking_id)
    if success:
        return f"Booking {booking_id} has been successfully cancelled."
    return f"Failed to find or cancel booking {booking_id}."

@tool
def check_booking(booking_id: int) -> str:
    """Retrieves booking details by booking ID."""
    booking = database.get_booking(booking_id)
    if booking:
        return f"Booking Details: ID: {booking[0]}, Name: {booking[1]}, Guests: {booking[3]}, Date: {booking[4]}, Time: {booking[5]}, Status: {booking[7]}"
    return "Booking not found."

@tool
def modify_booking(booking_id: int, new_date: str = None, new_time: str = None, new_guests: int = None) -> str:
    """Modifies an existing booking. Provide only the fields that need changing."""
    kwargs = {}
    if new_date: kwargs['date'] = new_date
    if new_time: kwargs['time'] = new_time
    if new_guests: kwargs['number_of_guests'] = new_guests
    
    if not kwargs:
        return "No modification parameters provided."
        
    success = database.modify_booking(booking_id, **kwargs)
    if success:
        return f"Booking {booking_id} has been successfully modified."
    return f"Failed to modify booking {booking_id}."

def get_agent_executor():
    llm = ChatOpenAI(
        model="z-ai/glm-4.5-air:free", 
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        temperature=0
    )
    tools = [search_restaurant_knowledge, book_table, cancel_booking, check_booking, modify_booking]
    
    memory = MemorySaver()
    agent = create_react_agent(llm, tools, checkpointer=memory)
    return agent

def chat_with_bot(user_input: str, session_id: str) -> str:
    agent_executor = get_agent_executor()
    
    # Retrieve history
    history_records = database.get_conversation_history(session_id)
    
    system_message = SystemMessage(
        content="You are a helpful restaurant assistant for 'The Gourmet Haven'. "
                "You can answer questions about the restaurant, menu, and policies using the search_restaurant_knowledge tool. "
                "You can also book, modify, cancel, or check bookings. "
                "Always be polite and confirm details before booking a table. "
                "When booking, you must collect: Name, Phone, Number of Guests, Date, and Time. If any is missing, ask for it. "
                f"Current date/time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    chat_history = [system_message]
    for role, content in history_records:
        if role == "user":
            chat_history.append(HumanMessage(content=content))
        else:
            chat_history.append(AIMessage(content=content))
            
    database.log_message(session_id, "user", user_input)
    chat_history.append(HumanMessage(content=user_input))
            
    try:
        result = agent_executor.invoke(
            {"messages": chat_history},
            config={"configurable": {"thread_id": session_id}}
        )
        
        # Extract response content
        response = result["messages"][-1].content
        
        # Handle case where response might be a list of parts (common in Gemini integrations)
        if isinstance(response, list):
            # Try to extract text strings from the list items
            texts = []
            for item in response:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
            
            response = "".join(texts) if texts else str(response)

    except Exception as e:
        response = f"I'm sorry, I encountered an error answering your request. Please ensure the API Key is valid and try again. Error details: {str(e)}"
        
    database.log_message(session_id, "assistant", response)
    
    return response
