from __future__ import annotations

from fastapi import APIRouter

from app.schemas.ingestion import IngestRepositoryRequest, IngestRepositoryResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()
service = IngestionService()


@router.post("/repositories", response_model=IngestRepositoryResponse)
def ingest_repository(payload: IngestRepositoryRequest) -> IngestRepositoryResponse:
    return service.ingest_repository(payload)
