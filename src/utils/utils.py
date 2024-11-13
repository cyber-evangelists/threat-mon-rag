from typing import List, Dict, Any

from sentence_transformers import CrossEncoder

def rerank_docs(
    query: str,
    top_5_results: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Rerank documents based on their relevance to the query using a cross-encoder.

    Args:
        query (str): The search query.
        top_5_results (List[Dict[str, str]]): Initial top 5 search results to rerank.

    Returns:
        List[Dict[str, str]]: Reranked list of documents.
    """
    # Re-ranking using cross-encoder
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

    # Prepare pairs for reranking
    pairs = [[query, doc["content"]] for doc in top_5_results]

    # Get relevance scores
    scores = reranker.predict(pairs)

    # Sort by new scores
    reranked_results = [
        doc for _, doc in sorted(
            zip(scores, top_5_results),
            reverse=True
        )
    ]

    return reranked_results