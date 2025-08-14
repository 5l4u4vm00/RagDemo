# RagDemo - Full-Stack RAG Chat Application

This project is a full-stack Retrieval-Augmented Generation (RAG) application. It combines a Vue.js frontend with a Python FastAPI backend to create a smart chat assistant that answers questions based on a provided document collection.

The application uses vector and graph-based retrieval to deliver accurate, context-aware responses. It supports multiple document formats and can be configured to use either local (Ollama) or remote (OpenAI) Large Language Models.

## Tech Stack

- **Frontend:** Vue.js, Vite, Pinia, Tailwind CSS
- **Backend:** Python, FastAPI, Ollama, OpenAI
- **Vector Store:** FAISS for efficient similarity search
- **Data Processing:** NetworkX for graph-based retrieval
- **Containerization:** Docker, Docker Compose

## Features

- **Intuitive Chat Interface:** A clean, web-based UI for user interaction.
- **Multi-Format Support:** Processes both PDF (`.pdf`) and Microsoft Word (`.docx`) files.
- **Advanced Retrieval:**
  - **Vector Search:** Uses `multilingual-e5-large` for fast, semantic retrieval.
  - **Graph Search:** Builds a knowledge graph to find contextually related information.
- **Flexible LLM Configuration:** Supports both local models via Ollama and the OpenAI API.
- **Containerized:** The entire application is managed via Docker for easy setup and deployment.

## Getting Started

Please run the application with Docker.
Please run the ollama service.

### Prerequisites

- [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/install/)
- An Azure OpenAI API key and endpoint (if using the OpenAI model).

### Configuration

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd RagDemo
   ```

2. **Set Up Environment Variables:**
   Create a `.env` file in the `RagDemo_Server` directory and add your Azure OpenAI credentials. If you would not use OpenAI model, you can ignore this.

   ```env
   # RagDemo_Server/.env
   AZURE_OPENAI_KEY="your-azure-openai-key"
   AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
   ```

### Running the Application

1. **Launch with Docker Compose:**
   From the project root, run:

   ```bash
   docker-compose up --build
   ```

2. **Access the Application:**
   - **Frontend Chat:** `http://localhost:5173`
   - **Backend API Docs:** `http://localhost:8888/docs`

## How It Works

1. **Ingestion:** The backend service reads and splits text from documents into smaller chunks.
2. **Embedding:** Each chunk is converted into a vector embedding using an multilingual-e5-large model.
3. **Storage:** Create an data folder. Embeddings are stored in a FAISS vector index (`<your data name>.faiss`), and the raw text is saved in `your data name.json`, finally put these in the data folder.
4. **Graph Creation:** A knowledge graph (`<your data name>.graphml`) is built to map relationships between text chunks based on semantic similarity.
5. **Retrieval & Generation:**
   - A user's question is converted into a vector.
   - The FAISS index finds the most relevant text chunks (Vector Search).
   - The knowledge graph is used to find related chunks for additional context (Graph Search).
   - The retrieved context and the original question are sent to the configured LLM (Ollama or OpenAI).
   - The LLM generates a response, which is streamed back to the user.
