from qdrant_client import QdrantClient
import time
from qdrant_client.models import Distance, VectorParams, PointStruct, FilterSelector

class QdrantWrapper:
    def __init__(self, collection_name="threadmon-reports-ioc"):
        self.host = "localhost"
        self.port = 6333
        self.collection_name = collection_name
        self.client = QdrantClient(self.host, port=self.port)
        self.collection_name = collection_name
        self._establish_connection()
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def _establish_connection(self, max_retries: int = 3, retry_delay: int = 3 ) -> None:

        for attempt in range(max_retries):
            try:
                self.client = QdrantClient(self.host, port=self.port)
                if self._test_connection():
                    print(f"Successfully connected to Qdrant at {self.host}:{self.port}")
                    return
                else:
                    raise ConnectionError("Connection test failed")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(
                        f"Failed to connect to Qdrant after {max_retries} attempts: {str(e)}"
                    )
                


    def clear_collection(self):
        """
        Deletes all vectors/points from the collection while keeping the collection structure.
        """
        try:
            # Delete all points in the collection
            self.client.delete(
                collection_name=self.collection_name,
                points_selector= FilterSelector(filter=None)  # No filter means delete all points
            )
            print(f"Successfully cleared all vectors from collection: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {e}")

    def ingest_embeddings(self, docs):

        points = [
            PointStruct(
                id=i,
                vector=doc["embeddings"],
                payload={"text": doc["text"], "document": doc["document"]}
            )
            for i, doc in enumerate(docs)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, limit=5):
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [
            {"document": hit.payload["document"], "content": hit.payload["text"]}
            for hit in search_result
        ]



# docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:v0.10.1
