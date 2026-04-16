from __future__ import annotations

from abc import ABC, abstractmethod
from hashlib import sha256


class EmbeddingProvider(ABC):
    """Pluggable interface for embedding model providers."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


class DeterministicHashEmbeddingProvider(EmbeddingProvider):
    """Local deterministic fallback embedding for development/testing."""

    def __init__(self, dimension: int = 256) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_single(text)

    def _embed_single(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        if not text:
            return vector
        for token in text.split():
            digest = sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], byteorder="big") % self._dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[idx] += sign

        norm = sum(value * value for value in vector) ** 0.5
        if norm > 0.0:
            vector = [value / norm for value in vector]
        return vector
