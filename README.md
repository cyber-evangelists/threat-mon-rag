# RAG System Using LLaMA 3.2 with knowledge base of Threatmon-feeds-IOC

## Introduction

This project implements a Retrieval-Augmented Generation (RAG) based system where users ask question related to the ThreatMon-Reports-IOC and it will response to the query. This project is completed using Web Sockets Fast API.

## Setting Up

Follow these steps to set up and run the project:

1. Clone the repository:

   ```
   git clone https://github.com/cyber-evangelists/threat-mon-rag
   ```

2. Navigate to the project root directory:

   ```
   threat-mon-rag
   ```

3. Make sure that the docker is installed on your system:

   ```
   docker --version
   ```

   If docker is not installed, run the following command:

   ```
   sudo apt install docker
   ```

4. In the same directory, create a file name `.env` and add following API key

   ```
   GROQ_API_KEY=your_api_key
   LANGCHAIN_API_KEY=your_langchain_api_key
   LANGCHAIN_PROJECT=project_name
   LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   LANGCHAIN_TRACING_V2=true
   ```

5. Build the docker environment::

   ```
   docker compose up --build
   ```

6. Access the graio app by pasting this URL:

   ```
   http://localhost:7860/
   ```

7. There is button `Ingest data`, click on this button to first ingest data into qdrant vector database. Then Enter Query and click on Search button, and the response will be shown below.
