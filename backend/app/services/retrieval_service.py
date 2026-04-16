from __future__ import annotations

from app.schemas.retrieval import (
    HybridRetrieveRequest,
    HybridRetrieveResponse,
)
from app.retrieval.hybrid_retriever import HybridRetriever


class RetrievalService:
    """Hybrid retrieval across vector and graph/search signals."""

    def __init__(self) -> None:
        self.hybrid_retriever = HybridRetriever()

    def retrieve(self, payload: HybridRetrieveRequest) -> HybridRetrieveResponse:
        return HybridRetrieveResponse(
            repository_id=payload.repository_id,
            query=payload.query,
            evidence=self.hybrid_retriever.retrieve(
                repository_id=payload.repository_id,
                query=payload.query,
                top_k=payload.top_k,
            ),
        )
