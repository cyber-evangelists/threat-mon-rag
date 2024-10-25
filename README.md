# RAG System Using LLaMA 3.2 with knowledge base of Threatmon-feeds-IOC

## Introduction

This project implements a Retrieval-Augmented Generation (RAG) based system where users ask question related to the ThreatMon-Reports-IOC and it will response to the query

## Setting Up

Follow these steps to set up and run the project:

1. Clone the repository:
   ```
   git clone https://github.com/cyber-evangelists/threat-mon-rag
   ```

2. Navigate to the project directory:
   ```
   cd threat-mon-rag
   ```

3. Download data from [this site](https://github.com/ThreatMon/ThreatMon-Reports-IOC) and add that folder into the same repository
   

4. Create a virtual environment:
   ```
   python -m venv venv
   ```

5. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

6. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

7. Set up Qdrant:
   a. Pull the Qdrant Docker image:
      ```
      docker pull qdrant/qdrant
      ```
   b. Run the Qdrant server:
      ```
      docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:v0.10.1
      ```

8. Add the data to the qdrant vector database
   ```
   python src/add_data.py
   ```

9. Run the graio app:
   ```
   python app.py
   ```

10. Enter Query and click on Search button, and the response will be shown below



