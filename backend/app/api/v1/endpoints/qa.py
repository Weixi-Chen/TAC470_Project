from __future__ import annotations

from fastapi import APIRouter

from app.schemas.qa import AnswerRequest, AnswerResponse
from app.services.qa_service import QAService

router = APIRouter()
service = QAService()


@router.post("/answer", response_model=AnswerResponse)
def answer_question(payload: AnswerRequest) -> AnswerResponse:
    return service.answer(payload)
