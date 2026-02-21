import os
from rag_engine import chat_with_bot

print("Testing bot...")
response = chat_with_bot("Hello, I want to book a table for 4 on Monday at 8pm", "test-session-1")
print("Bot response:", response)
