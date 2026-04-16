from __future__ import annotations

from app.schemas.qa import AnswerRequest, AnswerResponse
from app.schemas.retrieval import HybridRetrieveRequest
from app.qa.answer_generator import EvidenceGroundedAnswerGenerator
from app.services.retrieval_service import RetrievalService


class QAService:
    """Produces evidence-grounded answers using retrieved context."""

    def __init__(self) -> None:
        self.retrieval_service = RetrievalService()
        self.answer_generator = EvidenceGroundedAnswerGenerator()

    def answer(self, payload: AnswerRequest) -> AnswerResponse:
        retrieval = self.retrieval_service.retrieve(
            HybridRetrieveRequest(
                repository_id=payload.repository_id,
                query=payload.question,
                top_k=payload.top_k,
            )
        )
        qa_result = self.answer_generator.generate(payload.question, retrieval.evidence)
        return AnswerResponse(
            repository_id=payload.repository_id,
            question=payload.question,
            answer=qa_result.answer,
            evidence=retrieval.evidence,
            reasoning_trace=qa_result.reasoning_trace,
        )
