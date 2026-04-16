from __future__ import annotations

from fastapi import APIRouter

from app.schemas.retrieval import HybridRetrieveRequest, HybridRetrieveResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()
service = RetrievalService()


@router.post("/hybrid", response_model=HybridRetrieveResponse)
def hybrid_retrieve(payload: HybridRetrieveRequest) -> HybridRetrieveResponse:
    return service.retrieve(payload)
