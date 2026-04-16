from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class HybridRetrieveRequest(BaseModel):
    repository_id: str
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=8, ge=1, le=50)


class EvidenceItem(BaseModel):
    chunk_id: str
    file_path: str
    symbol_name: str
    start_line: int
    end_line: int
    score: float
    relevance_reason: str
    snippet: str


class HybridRetrieveResponse(BaseModel):
    repository_id: str
    query: str
    evidence: List[EvidenceItem]
