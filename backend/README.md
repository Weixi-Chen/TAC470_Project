# Backend Skeleton (FastAPI)

This backend is organized by capabilities needed for the MVP:

- `api/`: HTTP endpoints
- `schemas/`: request/response DTOs (Pydantic)
- `services/`: orchestration/business workflows
- `repositories/`: persistence adapters (SQLite, FAISS)
- `indexing/`: chunking + semantic indexing boundaries
- `graph/`: structural graph builders (networkx)
- `retrieval/`: hybrid retrieval interfaces
- `qa/`: evidence-grounded answer generation interfaces
- `core/`: app configuration and shared setup

Only skeletal implementations are included in this step.
