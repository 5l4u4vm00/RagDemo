# RagDemo - Full-Stack RAG Chat Application

This project is a full-stack Retrieval-Augmented Generation (RAG) application that functions as a smart assistant. It features a Vue.js frontend and a FastAPI backend, allowing users to ask questions and receive answers based on a collection of provided documents.

The application leverages advanced techniques like vector and graph-based retrieval to provide accurate, context-aware responses. It supports multiple document formats and can be configured to use either local (Ollama) or remote (OpenAI) Large Language Models.

## Architecture

The application consists of two main services orchestrated by Docker Compose:

-   **`RagDemo_Client` (Frontend):** A web-based chat interface built with Vue.js. It communicates with the backend API to send questions and display responses.
-   **`RagDeom_Server` (Backend):** An API built with Python and FastAPI. It handles document processing, embedding generation, and interaction with the LLM to generate answers.

## Features

-   **Web Interface:** An intuitive chat interface for interacting with the assistant.
-   **Document-based Q&A:** Answers questions based on the content of documents stored in the `RagDeom_Server/documents` directory.
-   **Multi-format Document Support:** Can process both PDF (`.pdf`) and Microsoft Word (`.docx`) files.
-   **Vector-based Retrieval:** Utilizes OpenAI's `text-embedding-3-small` model for efficient similarity search.
-   **Graph-based Retrieval:** Creates a knowledge graph of related text chunks to provide more contextually relevant information.
-   **FAISS Vector Store:** Stores vector embeddings in a FAISS index for fast retrieval.
-   **Dual LLM Support:** Flexible configuration to use either a local LLaMA model (via Ollama) or the OpenAI API.
-   **Containerized:** Easily run the entire application using Docker and Docker Compose.

## Getting Started

The recommended way to run the application is with Docker.

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)
-   An Azure OpenAI API key and endpoint (if using the OpenAI model).

### Configuration

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd RagDemo
    ```

2.  **Add Documents:**
    Place the PDF and DOCX files you want to use as the knowledge base into the `RagDeom_Server/documents/` directory.

3.  **Set Up Environment Variables:**
    Create a file named `.env` inside the `RagDeom_Server` directory and add your Azure OpenAI credentials. This step is required even if you plan to use a local model.

    ```
    # RagDeom_Server/.env
    AZURE_OPENAI_KEY="your-azure-openai-key"
    AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
    ```

### Running the Application

1.  **Launch with Docker Compose:**
    Open a terminal in the project's root directory and run:
    ```bash
    docker-compose up --build
    ```
    On the first launch, the backend service will automatically read the documents, create vector embeddings, and build the knowledge graph. This may take some time depending on the number and size of your documents.

2.  **Access the Application:**
    -   **Frontend Chat:** Open your web browser and navigate to `http://localhost:5173`.
    -   **Backend API Docs:** The backend API documentation is available at `http://localhost:8888/docs`.

## Manual Setup (for Development)

For development, you can run the frontend and backend services separately. Refer to the README files in the `RagDemo_Client` and `RagDeom_Server` directories for detailed instructions.

## How It Works

1.  **Document Processing:** The backend reads text from PDF and DOCX files in the `documents` directory and splits it into smaller chunks.
2.  **Vector Embedding:** Each text chunk is converted into a vector embedding using the OpenAI `text-embedding-3-small` model.
3.  **Vector Storage:** The embeddings are stored in a FAISS index (`vectorDB.faiss`), and the corresponding text chunks are saved in `textList.json`.
4.  **Graph Creation:** A knowledge graph (`graphDB.graphml`) is built where nodes are text chunks, and edges connect chunks with high cosine similarity, capturing relationships between them.
5.  **Question Answering:**
    -   When a user asks a question through the frontend, it's sent to the backend API.
    -   The backend creates a vector embedding of the question and uses the FAISS index to find the most similar text chunks.
    -   It then traverses the knowledge graph to retrieve neighboring chunks for added context.
    -   This context, along with the original question, is formatted into a prompt.
    -   Finally, the prompt is sent to the configured LLM (Ollama or OpenAI) to generate a response, which is streamed back to the user.