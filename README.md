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
   

4. Make sure that the docker is installed on your system:
   ```
   docker --version
   ```
   If docker is not installed, run the following command:
   ```
   sudo apt install docker
   ```

5. Set up Qdrant:
   Pull the Qdrant Docker image:
   ```
   docker pull qdrant/qdrant
   ```

6. Build the docker environment::
   ```
   docker compose up
   ```

7. Add the data to the qdrant vector database
   ```
   python src/add_data.py
   ```

8. Access the graio app by pasting this URL:
   ```
   http://localhost:7860/
   ```

9. Enter Query and click on Search button, and the response will be shown below

### Demo Video Link

 [Video Link ](https://www.loom.com/share/3c80678750e148a78e0d8016b281ac19?sid=480ca59b-bf06-4c26-848e-b8552fe43a54)




