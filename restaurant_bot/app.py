import streamlit as st
import uuid
import os
from rag_engine import chat_with_bot
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Gourmet Haven Assistant", page_icon="🍽️")

st.title("🍽️ Gourmet Haven Reservation Assistant")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to The Gourmet Haven! How can I help you today? You can ask about our menu, policies, or book a table."}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about the menu or book a table..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Make sure API key is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        st.error("Please set OPENROUTER_API_KEY in the .env file.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_bot(prompt, st.session_state.session_id)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
