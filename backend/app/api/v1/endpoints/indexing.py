from __future__ import annotations

from fastapi import APIRouter

from app.schemas.indexing import BuildIndexRequest, BuildIndexResponse
from app.services.indexing_service import IndexingService

router = APIRouter()
service = IndexingService()


@router.post("/build", response_model=BuildIndexResponse)
def build_index(payload: BuildIndexRequest) -> BuildIndexResponse:
    return service.build_indexes(payload)
