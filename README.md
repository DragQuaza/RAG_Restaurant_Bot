# 🍽️ Gourmet Haven Assistant

Gourmet Haven Assistant is a professional, AI-powered reservation and information bot designed for the "Gourmet Haven" restaurant. It utilizes **Retrieval-Augmented Generation (RAG)** and **Agentic Workflows** to provide a seamless conversational experience for guests.

The assistant can handle menu inquiries, explain restaurant policies, and manage the entire booking lifecycle—including creating, checking, modifying, and cancelling reservations—directly within the chat interface.

## 🚀 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/) (ReAct Agent pattern)
- **LLM**: GLM-4.5 (via [OpenRouter](https://openrouter.ai/))
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss)
- **Database**: SQLite (Persistent storage for bookings and conversation logs)
- **Models/Validation**: Pydantic

## 📂 Project Structure

- `app.py`: The main entry point for the Streamlit web application.
- `rag_engine.py`: Core logic for the AI Agent, including tool definitions (booking, searching), vector store initialization, and LangGraph integration.
- `database.py`: SQLite database abstraction layer for handling reservations and session history.
- `data/knowledge_base.txt`: Source text file containing restaurant information (menu, hours, rules) used to populate the vector store.
- `faiss_index/`: Directory containing the locally persisted FAISS vector index.
- `restaurant.db`: The SQLite database file generated at runtime.
- `requirements.txt`: Python dependencies.

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- An [OpenRouter API Key](https://openrouter.ai/keys)

### Step-by-Step Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rag
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your `OPENROUTER_API_KEY`.

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## 🔧 Environment Variables

The application requires the following environment variables to be set in a `.env` file:

| Variable | Description |
| :--- | :--- |
| `OPENROUTER_API_KEY` | Your OpenRouter API key for accessing LLMs (e.g., GLM-4.5). |

## 🛠️ Features

- **Smart Retrieval**: Uses RAG to answer specific questions about the restaurant's menu and policies.
- **Automated Bookings**: Collects guest details conversationally and persists them to the database.
- **Booking Management**: Guests can check their booking status, modify dates/times, or cancel reservations using their Booking ID.
- **Conversation History**: Remembers the context of the current session for a natural dialogue flow.
- **Safety Limits**: Prevents online bookings for parties larger than 8 guests, directing them to contact the restaurant.
