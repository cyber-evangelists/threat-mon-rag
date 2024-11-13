# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from loguru import logger
from typing import Dict, Any, List, Optional

from src.config.config import Config
from src.embedder.embedder import EmbeddingWrapper
from src.qdrant.qdrant_utils import QdrantWrapper
from src.parser.threatmon_parser import FileProcessor
from src.utils.utils import  rerank_docs
from src.utils.connections_manager import ConnectionManager
from src.chatbot.rag_chat_bot import RAGChatBot


app = FastAPI()

# Initialize all clients/wrappers
embedding_client = EmbeddingWrapper()
qdrant_client = QdrantWrapper()
file_processor = FileProcessor()

chatbot = RAGChatBot()


# Dictionary to hold WebSocket connections
connections: Dict[WebSocket, Dict[str, Any]] = {}

manager = ConnectionManager()



async def handle_ingest(websocket: WebSocket, data: Any) -> None:
    """
    Handle data ingestion action with proper error handling.

    Args:
        websocket (WebSocket): The WebSocket connection to send responses.
        data (Any): The data to be ingested.

    Returns:
        None: Responses are sent through the WebSocket connection.

    Raises:
        Exception: Any unexpected errors during the ingestion process.
    """
    try:
        logger.info("Ingesting Data")

        data_directory = Config.DATA_DIRECTORY
        processed_chunks = file_processor.process_all_files(data_directory)

        qdrant_client.ingest_embeddings(processed_chunks)

        logger.info("Successfully ingested Data")

        await websocket.send_json({
            "result": "Data ingested successfully"
        })

    except Exception as e:
        logger.error(f"Error in data ingestion: {str(e)}")
        await websocket.send_json({
            "error": f"Ingestion failed: {str(e)}"
        })





async def handle_search(websocket: WebSocket, query: str) -> None:
    """
    Handle search action with proper error handling.

    Args:
        websocket (WebSocket): The WebSocket connection to send responses.
        query (str): The search query string.

    Returns:
        None: Responses are sent through the WebSocket connection.

    Raises:
        Exception: Any unexpected errors during the search process.
    """
    try:
        logger.info(f"Processing search query")

        # Generate embeddings
        logger.info("Generating embeddings")
        query_embeddings = embedding_client.generate_embeddings(query)

        # Search in Qdrant
        logger.info("Searching for top 5 results")
        top_5_results = qdrant_client.search(query_embeddings, 5)
        logger.info("Retrieved top 5 results")

        # Check if results are empty
        if not top_5_results:
            logger.warning("No results found in database")
            await websocket.send_json({
                "result": "The database is empty. Please ingest some data first before searching."
            })
            return

        # Rerank documents
        logger.info("Reranking documents")
        reranked_docs = rerank_docs(query, top_5_results)
        reranked_top_5_list = [item['content'][:1000] for item in reranked_docs]
        logger.info("Documents reranked")

        # Use top 2 documents as context
        context = reranked_top_5_list[:2]

        logger.info("Generating response from Groq")
        response = chatbot.chat(query, context)

        await websocket.send_json({
            "result": response
        })

    except Exception as e:
        logger.error(f"Error in search handling: {str(e)}")
        await websocket.send_json({
            "error": f"Search failed: {str(e)}"
        })



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages
            data = await websocket.receive_json()
            
            try:
                # Parse the received data
                logger.info("Accepting Responses")

                action = data.get("action")
                payload = data.get("payload")

                if action == "pong":
                    continue  # Handle heartbeat response

                if not action:
                    await websocket.send_json({"error": "No action specified"})
                    continue


                if action == "search":
                    await handle_search(websocket, payload["query"])
                elif action == "ingest_data":
                    await handle_ingest(websocket, payload)
                else:
                    await websocket.send_json({"error": f"Unknown action: {action}"})
           
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except KeyError as ke:
                await websocket.send_json({"error": f"Missing required field: {ke}"})
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({"error": "Internal server error"})

        
    except WebSocketDisconnect as ws_error:
        logger.info(f"Client disconnected. Code: {ws_error.code}, Reason: {ws_error.reason}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        await manager.disconnect(websocket)
                
                
               
