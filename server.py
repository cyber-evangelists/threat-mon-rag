# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
import json

from typing import Dict, Any, List, Optional

from src.config.config import Config


from src.qdrant.qdrant_utils import QdrantWrapper
from src.embedder.embedder import EmbeddingWrapper
from src.parser.threatmon_parser import FileProcessor

from src.utils.connections_manager import ConnectionManager
from src.chatbot.rag_chat_bot import RAGChatBot
from src.reranker.re_ranking import RerankDocuments

app = FastAPI()

collection_name = Config.COLLECTION_NAME

# Initialize all clients/wrappers
embedding_client = EmbeddingWrapper()
qdrant_client = QdrantWrapper()
file_processor = FileProcessor()

chatbot = RAGChatBot()

reranker = RerankDocuments()


# Dictionary to hold WebSocket connections
connections: Dict[WebSocket, Dict[str, Any]] = {}

manager = ConnectionManager()


try:

    logger.info("Starting Data Ingestion")
    qdrant_client.delete_collection(collection_name=Config.COLLECTION_NAME)
    logger.info("collection deleted...")
    qdrant_client._create_collection_if_not_exists()
    logger.info("Collection created....")
    processed_chunks = file_processor.process_all_files(Config.DATA_DIRECTORY)
    qdrant_client.ingest_embeddings(processed_chunks)

    logger.info("Successfully ingested Data")

except Exception as e:
    logger.error(f"Error in data ingestion: {str(e)}")


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

        # filename = find_file_names(query, database_files)

        query_embeddings = embedding_client.generate_embeddings(query)


        logger.info("Searching for top 5 results....")
        top_5_results = qdrant_client.search(query_embeddings, 5)
        logger.info("Retrieved top 5 results")

        if not top_5_results:
            logger.warning("No results found in database")
            await websocket.send_json({
                "result": "The database is empty. Please ingest some data first before searching."
            })
            return
        

        reranked_docs = reranker.rerank_docs(query, top_5_results)
        reranked_top_5_list = [item['content'] for item in reranked_docs]

        context = reranked_top_5_list[:2]

        # only top 2 documents are passing as a context
        response, conversation_id  = chatbot.chat(query, context)

        logger.info("Generating response from Groq")

        await websocket.send_json({
            "result": response
        })

    except Exception as e:
        logger.error(f"Error in search handling: {str(e)}")
        await websocket.send_json({
            "error": f"Search failed: {str(e)}"
        })


async def add_feedback(websocket: WebSocket, action:str,  comment: str) -> None:

    try:
        logger.info(f"in the add feedback function...")

        logger.info(action)
        logger.info(comment)

        chatbot.add_feedback(action, comment)

        await websocket.send_json({
            "result": "Feedback added successfully"
        })

    except Exception as e:
        logger.error(f"Error in search handling: {str(e)}")
        await websocket.send_json({
            "error": f"Feedback Addition failed: {str(e)}"
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
                elif action == "positive":
                    await add_feedback(websocket, action , payload["comment"])
                elif action == "negative":
                    await add_feedback(websocket, action , payload["comment"])
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
                
                
               