from src.ollamawrapper import OllamaWrapper
import gradio as gr
from src.embedder import EmbeddingWrapper
from src.qdrant_utils import QdrantWrapper
from src.utils import prepare_prompt
from src.utils import rerank_docs
from src.config import Config

ollama = OllamaWrapper()
embedder = EmbeddingWrapper()
qdrant_client = QdrantWrapper(Config.COLLECTION_NAME)


def handle_search(query, history):
    # Get response from Ollama

    query_embeddings = embedder.generate_embeddings(query)

    top_5_results = qdrant_client.search(query_embeddings, 5)

    reranked_docs = rerank_docs(query, top_5_results)

    reranked_top_5_list = [item['content'] for i, item in enumerate(reranked_docs)]

    context = " ".join(reranked_top_5_list[:3])

    prompt =  prepare_prompt(query, context)
    ollama_response = ollama.generate_text(prompt)
    
    # Update chat history
    history = history or []
    history.append((query, ollama_response))
    return "", history

def clear_chat():
    return None

# Create the Gradio interface
with gr.Blocks() as demo:
    # Add a title
    gr.Markdown("# ASM Chatbot")
    
    # Create a textbox for input (now at the top)
    with gr.Row():
        msg = gr.Textbox(label="Type your message here...", placeholder="Enter your query")
    
    # Add buttons in a row
    with gr.Row():
        search_btn = gr.Button("Search")
        clear = gr.Button("Clear")
    
    # Create a chatbot component below
    chatbot = gr.Chatbot(height=400, show_label=False)
    
    # Set up event handlers
    search_btn.click(
        fn=handle_search,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )
    
    clear.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)