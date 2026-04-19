# RagDemo — Full-Stack RAG Chat Application

A full-stack Retrieval-Augmented Generation (RAG) application that pairs a Vue 3 frontend with a Python FastAPI backend to answer questions grounded in your own documents.

Retrieval is backed by **Postgres + pgvector**, with an optional graph-expansion mode that follows similarity edges between chunks. Generation can be served by a local LLM via **Ollama** or by **Azure OpenAI**.

## Tech Stack

- **Frontend:** Vue 3, Vite, Pinia, Tailwind CSS, TypeScript
- **Backend:** Python 3.12, FastAPI, Hugging Face Transformers
- **Storage / Retrieval:** Postgres 16 with the `pgvector` extension (ivfflat index); NetworkX for in-memory graph traversal at query time
- **LLMs:** Ollama (local) or Azure OpenAI
- **Containerization:** Docker, Docker Compose

## Features

- **Chat UI** — clean web interface for asking questions over your indexed datasets.
- **Multi-format ingestion** — supports `.pdf`, `.docx`, and `.cs` source files.
- **Multilingual embeddings** — `intfloat/multilingual-e5-small` (384-dim, L2-normalized).
- **Two retrieval modes**
  - *Vector* — pgvector L2 nearest-neighbour search.
  - *Graph* — vector hits expanded along precomputed similarity edges (cosine ≥ 0.8).
- **Pluggable LLM** — switch between local Ollama models and Azure OpenAI per request.

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Ollama](https://ollama.com/) running on the host (the backend reaches it via `host.docker.internal:11434`)
- *(Optional)* Azure OpenAI key + endpoint, if you want to use the OpenAI route

### Configuration

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd RagDemo
   ```

2. *(Optional)* Create `RagDemo_Server/.env` with your Azure OpenAI credentials. Skip this file if you only plan to use Ollama.

   ```env
   # RagDemo_Server/.env
   AZURE_OPENAI_KEY="your-azure-openai-key"
   AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
   ```

### Running

From the project root:

```bash
docker-compose up --build
```

This starts three containers:

- `ragdemo_postgres` — Postgres 16 with `pgvector` (port `5432`)
- `ragdemo_backend` — FastAPI service (port `8888`)
- `ragdemo-frontend` — Vite dev server (port `5173`)

Then open:

- **Chat UI:** http://localhost:5173
- **API docs (Swagger):** http://localhost:8888/docs

The backend creates the `vector` extension and required tables on first startup.

## How It Works

1. **Chunking** — `PreTargetService.SplitText` reads the uploaded file and tokenizes it into chunks using the `multilingual-e5-small` tokenizer.
2. **Embedding** — `PreTargetService.EmbeddingTexts` runs the chunks through the e5 model in batches and L2-normalizes the resulting 384-dim vectors.
3. **Storage** — Each ingestion writes:
   - one row in `datasets`,
   - one row per chunk in `chunks` (text + `vector(384)` embedding, indexed with `ivfflat / vector_l2_ops`),
   - similarity edges (cosine ≥ 0.8) in `chunk_edges` for graph-mode retrieval.
4. **Retrieval** — At query time `AIService` embeds the question and runs a pgvector L2 search across the selected datasets. In graph mode, the top hits are expanded by following `chunk_edges` neighbours.
5. **Generation** — Retrieved chunks are stitched into a prompt and sent to either `AskLlama` (Ollama) or `AskOpenAI` (Azure OpenAI). The response is streamed back to the UI.
