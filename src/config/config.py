
from dotenv import load_dotenv
import os

load_dotenv()

class Config:

    MODEL_NAME = "llama3-8b-8192"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.1-8b-instant"
    MAX_CHAT_HISTORY = 20
    GRADIO_SERVER_NAME = "0.0.0.0" 
    GRADIO_SERVER_PORT = int(7860)
    WEBSOCKET_URI = "ws://rag-server:8000/ws"
    DATA_DIRECTORY = "data/"
    WEBSOCKET_TIMEOUT = 300  # 5 minutes
    HEARTBEAT_INTERVAL = 30  # 30 seconds
    MAX_CONNECTIONS = 100

