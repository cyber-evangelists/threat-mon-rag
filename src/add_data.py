from threatmon_parser import FileProcessor
from qdrant_utils import QdrantWrapper
from config import Config

def main():



    qdrant_client = QdrantWrapper(Config.COLLECTION_NAME)
    qdrant_client._create_collection_if_not_exists()


    data_directory = "../data/ThreatMon-Reports-IOC-main"

    try:

        processor = FileProcessor()
        processed_chunks = processor.process_all_files(data_directory)

        qdrant_client.ingest_embeddings(processed_chunks)
        print("Data Ingested Successfully.")
    
    except Exception as e:        
        print(f"Error ingesting data: {str(e)}")


if __name__ == "__main__":
    main()