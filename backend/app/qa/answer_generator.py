from __future__ import annotations

import json
import os
from dataclasses import dataclass

from app.schemas.retrieval import EvidenceItem


@dataclass
class QAResult:
    answer: str
    reasoning_trace: list[str]


class EvidenceGroundedAnswerGenerator:
    """Generate answers constrained to retrieved evidence only."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    def generate(self, question: str, evidence: list[EvidenceItem]) -> QAResult:
        if not evidence:
            return QAResult(
                answer=(
                    "Insufficient evidence to answer the question from the repository context. "
                    "Please index more relevant files or broaden retrieval scope."
                ),
                reasoning_trace=["No retrieved evidence chunks available."],
            )

        llm_result = self._try_llm_answer(question, evidence)
        if llm_result is not None:
            return llm_result
        return self._fallback_answer(question, evidence)

    def _try_llm_answer(self, question: str, evidence: list[EvidenceItem]) -> QAResult | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            from openai import OpenAI
        except ImportError:
            return None

        client = OpenAI(api_key=api_key)
        evidence_text = self._format_evidence(evidence)
        system_prompt = (
            "You are a repository QA assistant. You MUST answer only using provided evidence.\n"
            "Rules:\n"
            "1) Do not use prior knowledge.\n"
            "2) If evidence is insufficient, explicitly say it is insufficient.\n"
            "3) Include file paths and line ranges in the answer.\n"
            "4) Return strict JSON with keys: answer (string), reasoning_trace (string array).\n"
            "5) reasoning_trace must reference evidence IDs and cross-file links when used.\n"
        )
        user_prompt = (
            f"Question:\n{question}\n\n"
            f"Evidence:\n{evidence_text}\n\n"
            "Return only valid JSON."
        )

        response = client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        data = self._parse_json(content)
        if not isinstance(data, dict):
            return None

        answer = data.get("answer")
        trace = data.get("reasoning_trace")
        if not isinstance(answer, str) or not isinstance(trace, list) or not all(
            isinstance(item, str) for item in trace
        ):
            return None

        # Hard guard: enforce citation presence in final answer.
        if not self._contains_citation(answer):
            answer = f"{answer}\n\nEvidence references: {self._citation_footer(evidence)}"
        return QAResult(answer=answer, reasoning_trace=trace)

    def _fallback_answer(self, question: str, evidence: list[EvidenceItem]) -> QAResult:
        del question
        top = evidence[:3]
        trace = [
            f"Selected {len(top)} highest-ranked evidence chunks from retrieval results."
        ]
        trace.extend(
            f"Used {item.file_path}:{item.start_line}-{item.end_line} ({item.symbol_name}) as support."
            for item in top
        )
        answer_lines = [
            "Insufficient evidence for a fully confident answer.",
            "Most relevant grounded context found:",
        ]
        for idx, item in enumerate(top, start=1):
            answer_lines.append(
                f"{idx}. {item.file_path}:{item.start_line}-{item.end_line} "
                f"[{item.symbol_name}] - {item.relevance_reason}"
            )
        return QAResult(answer="\n".join(answer_lines), reasoning_trace=trace)

    @staticmethod
    def _format_evidence(evidence: list[EvidenceItem]) -> str:
        blocks: list[str] = []
        for idx, item in enumerate(evidence, start=1):
            blocks.append(
                "\n".join(
                    [
                        f"[E{idx}] file={item.file_path}",
                        f"symbol={item.symbol_name}",
                        f"lines={item.start_line}-{item.end_line}",
                        f"reason={item.relevance_reason}",
                        f"snippet={item.snippet}",
                    ]
                )
            )
        return "\n\n".join(blocks)

    @staticmethod
    def _parse_json(content: str) -> dict | list | None:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _contains_citation(answer: str) -> bool:
        return ".py:" in answer or "README.md:" in answer or "requirements.txt:" in answer

    @staticmethod
    def _citation_footer(evidence: list[EvidenceItem]) -> str:
        return "; ".join(
            f"{item.file_path}:{item.start_line}-{item.end_line}" for item in evidence[:3]
        )
