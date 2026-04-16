from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.schemas.retrieval import EvidenceItem


class AnswerRequest(BaseModel):
    repository_id: str
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=8, ge=1, le=50)


class AnswerResponse(BaseModel):
    repository_id: str
    question: str
    answer: str
    evidence: List[EvidenceItem]
    reasoning_trace: List[str]
