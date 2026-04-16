from __future__ import annotations

import os

from app.embeddings.provider import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider implementation."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        dimension: int = 1536,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._dimension = dimension
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIEmbeddingProvider.")

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        batch_size_raw = os.getenv("OPENAI_EMBEDDING_BATCH_SIZE", "32")
        try:
            batch_size = max(1, int(batch_size_raw))
        except ValueError:
            batch_size = 32
        client = self._create_client()
        out: list[list[float]] = []
        for offset in range(0, len(texts), batch_size):
            batch = texts[offset : offset + batch_size]
            response = client.embeddings.create(model=self.model, input=batch)
            ordered = sorted(response.data, key=lambda item: item.index)
            for item in ordered:
                emb = item.embedding
                if len(emb) != self._dimension:
                    raise ValueError(
                        f"OpenAI returned embedding length {len(emb)} but provider "
                        f"dimension is {self._dimension}. Set OPENAI_EMBEDDING_DIMENSION "
                        "to match the model output, delete the FAISS index, and re-ingest."
                    )
                out.append(emb)
        return out

    def embed_query(self, text: str) -> list[float]:
        client = self._create_client()
        response = client.embeddings.create(model=self.model, input=[text])
        return response.data[0].embedding

    def _create_client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is not installed. Install it to use OpenAIEmbeddingProvider."
            ) from exc
        return OpenAI(api_key=self.api_key)
