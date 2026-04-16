# AI-Assisted Repository Understanding Tool

Evidence-grounded Q&A for Python repositories.

This project ingests a local Python repo, builds structure-aware chunks, vector and lexical indexes, and a call/containment graph, then answers natural-language questions with traceable code evidence.

## Features

- FastAPI backend for ingestion, indexing, retrieval, and QA APIs
- React + Vite + Tailwind frontend with dark/light theme
- Structure-aware AST chunking (file summaries + symbol chunks)
- Hybrid retrieval: semantic search + lexical token match + graph expansion
- Evidence-grounded answers with citations and reasoning trace
- OpenAI-first embeddings (auto fallback to deterministic hash embedding when no key is set)
- FAISS index dimension safety checks to avoid mixed embedding backends

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers and endpoints
│   │   ├── embeddings/       # OpenAI/hash embedding providers and store config
│   │   ├── graph/            # Structure graph builder (networkx)
│   │   ├── indexing/         # Chunker + semantic indexer
│   │   ├── qa/               # Evidence-grounded answer generation
│   │   ├── repositories/     # SQLite + FAISS persistence
│   │   ├── retrieval/        # Hybrid retriever
│   │   └── services/         # Ingestion/indexing/retrieval/qa orchestration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── README.md
```

## Architecture Pipeline

1. **Ingest** (`/api/v1/ingestion/repositories`)
   - Scan repository files and generate manifest
   - Trigger index build in the same workflow
2. **Index**
   - AST-based chunking (`StructureAwareChunker`)
   - Embeddings + FAISS vector index
   - SQLite chunk metadata and vector mapping
   - Structural graph build (`networkx`)
3. **Retrieve** (`/api/v1/retrieval/hybrid`)
   - Semantic hits (FAISS)
   - Lexical hits (SQLite token substring search)
   - Graph neighborhood expansion and weighted reranking
4. **Answer** (`/api/v1/qa/answer`)
   - Generate answer constrained to retrieved evidence
   - Return citations, snippets, and reasoning trace

## Requirements

- Python 3.8+
- Node.js 18+
- npm

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
# Required for OpenAI chat answer generation and OpenAI embeddings
OPENAI_API_KEY=your_key_here

# Optional
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSION=1536
OPENAI_EMBEDDING_BATCH_SIZE=32

# Optional index paths (set both as a pair when overriding)
EMBEDDING_SQLITE_PATH=code_index_openai.db
EMBEDDING_FAISS_PATH=semantic_openai.index
```

Start backend:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://127.0.0.1:5173`  
Backend default URL: `http://127.0.0.1:8000`

## API Quickstart

### Health

`GET /api/v1/health`

Returns service status and active embedding backend/dimension.

### Ingest and build indexes

`POST /api/v1/ingestion/repositories`

```json
{
  "local_repo_path": "/absolute/path/to/target_repo"
}
```

### Hybrid retrieve

`POST /api/v1/retrieval/hybrid`

```json
{
  "repository_id": "/absolute/path/to/target_repo",
  "query": "How does startup work?",
  "top_k": 8
}
```

### QA

`POST /api/v1/qa/answer`

```json
{
  "repository_id": "/absolute/path/to/target_repo",
  "question": "Where is authentication implemented?",
  "top_k": 8
}
```

## Embedding Behavior

- If `OPENAI_API_KEY` is set, backend uses `OpenAIEmbeddingProvider` by default.
- If not set, backend falls back to deterministic hash embeddings.
- OpenAI and hash embeddings use separate default index files to avoid dimension mixing.
- If an existing FAISS index dimension mismatches the active embedding dimension, backend returns HTTP `409` with recovery instructions.

## Common Issues

- **`Insufficient evidence` with `0 retrieved code chunks`**
  - Usually means current SQLite/FAISS store is empty for the running backend process.
  - Re-ingest the repository after backend restart.
  - Ensure `EMBEDDING_SQLITE_PATH` and `EMBEDDING_FAISS_PATH` point to the same index pair.
- **`No module named 'faiss'`**
  - Install dependencies in the same Python environment running `uvicorn`.
- **Dimension mismatch error**
  - Delete old FAISS/SQLite pair or point to a fresh pair, then ingest again.

## Security Notes

- Never commit real keys into git-tracked files.
- Keep secrets in `backend/.env` (already ignored by `.gitignore`).

## License

For academic/project use unless your course or team policy specifies otherwise.
