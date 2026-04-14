# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

The entire stack runs via Docker Compose from the project root:

```bash
docker-compose up --build
```

- **Frontend:** http://localhost:5173
- **Backend API + Swagger docs:** http://localhost:8888/docs

Ollama must be running locally (the backend connects to `http://host.docker.internal:11434`).

## Backend Development (RagDemo_Server)

Python 3.12+, managed with `uv` (`pyproject.toml`). The Dockerfile uses `requirement.txt` for pip installs inside the container.

```bash
# Run locally (outside Docker)
cd RagDemo_Server
python main.py
```

Environment variables go in `RagDemo_Server/.env`:
```
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=...
```

## Frontend Development (RagDemo_Client)

Vue 3 + Vite + TypeScript, Node 20+.

```bash
cd RagDemo_Client
npm install
npm run dev        # dev server
npm run build      # type-check + build
npm run lint       # ESLint --fix
npm run format     # Prettier
```

## Architecture Overview

### Data Flow

1. **Ingestion (PreTarget):** User uploads `.pdf`, `.docx`, or `.cs` via the Embedding UI → `PreTargetService.SplitText` tokenizes it into chunks using `intfloat/multilingual-e5-large` tokenizer.
2. **Embedding & Storage:** `PreTargetService.EmbeddingTexts` generates embeddings in batches, then writes three files per dataset to `RagDemo_Server/VectorStore/<dataName>/`:
   - `<dataName>.faiss` — FAISS flat-L2 vector index
   - `<dataName>.json` — raw text chunks (list of strings)
   - `<dataName>.graphml` — NetworkX DiGraph where edges connect chunks with cosine similarity ≥ 0.8
3. **Retrieval:** At query time, `AIService` loads these files, rebuilds an in-memory FAISS index, and searches it. Two modes:
   - `EMode.vector` — pure vector similarity (`SearchSimilar`)
   - `EMode.graph` — vector search + graph neighbor expansion (`SearchGraphRag`)
4. **Generation:** Retrieved context chunks are injected into a prompt sent to either Ollama (`AskLlama`) or Azure OpenAI (`AskOpenAI`).

### Backend Structure

```
RagDemo_Server/
├── main.py                  # FastAPI app, router registration
├── Routers/                 # Thin HTTP layer — no business logic
│   ├── chatRouter.py        # POST /ChatBot/AskLLaMA, /AskOpenAI
│   ├── PreTargetRouter.py   # POST /Pretarget/SplitTextFromDoc, /EmbeddingChunksStore
│   └── OptionRouter.py      # GET /Options/... (model list, data list)
├── Services/
│   ├── AIService.py         # Embedding model, FAISS search, prompt building, LLM calls
│   ├── PreTargetService.py  # File parsing, chunking, embedding, file storage
│   └── OptionService.py     # Ollama model enumeration, VectorStore folder scan
├── DataModels/
│   ├── Enums/EMode.py       # vector=1, graph=2
│   └── Models/              # Pydantic models (Request, Option)
└── VectorStore/             # Runtime data — one subfolder per embedded dataset
```

### Frontend Structure

```
RagDemo_Client/src/
├── api/server/              # Axios wrappers for each backend router
├── pages/
│   ├── Home/HomeView.vue    # Main chat interface
│   └── Embedding/EmbeddingView.vue  # Two-step embed wizard (split → store)
├── stores/global.ts         # Pinia store — shared state (splitTexts, dataName, etc.)
└── router/index.ts          # Vue Router config
```

### Key Design Notes

- `AIService` and `PreTargetService` both instantiate the HuggingFace model at startup (slow). They are singletons created at the router level.
- The `GetDataList` in `OptionService` discovers available datasets by scanning `./VectorStore/` subdirectories — adding a new dataset only requires dropping the three files there.
- Graph search loads `.graphml` files and re-maps node IDs when merging multiple datasets to avoid collisions.
