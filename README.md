# My Smart Assistant

This project is a RAG (Retrieval-Augmented Generation) application that functions as a smart assistant. It can answer questions based on a collection of documents you provide. The application is built using the FastAPI framework and leverages both local and remote Large Language Models (LLMs) to generate responses.

## Features

- **Document-based Q&A:** Answers questions based on the content of documents stored in the `documents` directory.
- **Multi-format Document Support:** Can process both PDF (.pdf) and Microsoft Word (.docx) files.
- **Vector-based Retrieval:** Utilizes the `text-embedding-3-small` model from OpenAI to create vector embeddings of the document text, enabling efficient similarity search.
- **FAISS Vector Store:** Stores the vector embeddings in a [FAISS](https://github.com/facebookresearch/faiss) index for fast retrieval.
- **Dual LLM Support:** Offers the flexibility to use either a local LLaMA model (via Ollama) or the OpenAI API for generating answers.
- **Easy-to-use API:** Provides a simple API for asking questions and for triggering the document embedding process.

## Project Structure

```
├── DataModels
│   └── Request.py
├── documents
│   └── (Your documents go here)
├── Routers
│   └── chatRouter.py
├── Services
│   └── AIService.py
├── VectorStore
│   ├── textList.json
│   └── vectorDB.faiss
├── main.py
├── requirement.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.7+
- UV project manager
- An Azure OpenAI API key and endpoint
- (Optional) [Ollama](https://ollama.ai/) installed and running for local LLM support

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create and activate a virtual environment:**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   uv add -r requirement.txt
   ```

4. **Set up your environment variables:**

   Create a `.env` file in the root of the project and add your Azure OpenAI credentials:

   ```
   AZURE_OPENAI_KEY="your-azure-openai-key"
   AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
   ```

### Usage

1. **Add your documents:**

   Place the PDF and DOCX files you want to use as the knowledge base into the `documents` directory.

2. **Generate the vector embeddings:**

   Start the application, which will automatically trigger the embedding process for the documents in the `documents` folder.

3. **Run the application:**

   ```bash
   uv run ./main.py
   ```

4. **Access the API:**

   The API documentation will be available at `http://127.0.0.1:8888/docs`.

## API Endpoints

- **`POST /ChatBot/AskLLaMA`**: Sends a question to the local LLaMA model and returns the response.

  **Request Body:**

  ```json
  {
    "question": "Your question here"
  }
  ```

- **`POST /ChatBot/AskOpenAI`**: Sends a question to the OpenAI model and returns the response.

  **Request Body:**

  ```json
  {
    "question": "Your question here"
  }
  ```

- **`GET /ChatBot/embeddingFromFolder`**: Triggers the process of reading the documents in the `documents` folder, creating vector embeddings, and storing them in the vector database.

## How It Works

1. **Document Loading and Chunking:** The application reads the text from the PDF and DOCX files in the `documents` directory. The text is then split into smaller chunks using `tiktoken`.

2. **Vector Embedding:** Each text chunk is converted into a vector embedding using the OpenAI `text-embedding-3-small` model.

3. **Vector Storage:** The vector embeddings are stored in a FAISS index (`vectorDB.faiss`), and the corresponding text chunks are saved in a JSON file (`textList.json`).

4. **Question Answering:**
   - When a question is received, the application creates a vector embedding of the question.
   - It then uses the FAISS index to find the most similar text chunks from the documents.
   - These relevant text chunks are then combined with the original question to form a prompt.
   - Finally, the prompt is sent to either the local LLaMA model or the OpenAI API to generate a response.
