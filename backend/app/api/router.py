from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import health, ingestion, indexing, qa, retrieval

api_router = APIRouter()
api_router.include_router(health.router, prefix="/v1", tags=["health"])
api_router.include_router(ingestion.router, prefix="/v1/ingestion", tags=["ingestion"])
api_router.include_router(indexing.router, prefix="/v1/indexing", tags=["indexing"])
api_router.include_router(retrieval.router, prefix="/v1/retrieval", tags=["retrieval"])
api_router.include_router(qa.router, prefix="/v1/qa", tags=["qa"])
