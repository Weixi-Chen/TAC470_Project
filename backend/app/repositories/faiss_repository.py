from __future__ import annotations

from pathlib import Path
from typing import Optional

import faiss
import numpy as np


class FaissIndexDimensionMismatchError(RuntimeError):
    """On-disk FAISS index was built with a different embedding dimension than the active provider."""

    def __init__(self, index_path: Path, found_dim: Optional[int], expected_dim: int) -> None:
        self.index_path = index_path
        self.found_dim = found_dim
        self.expected_dim = expected_dim
        super().__init__(
            f"FAISS index at {index_path} has dimension {found_dim}, "
            f"but the active embedding provider uses {expected_dim}. "
            f"Delete that index file (and use a matching SQLite DB / re-ingest) "
            f"or set EMBEDDING_FAISS_PATH / EMBEDDING_SQLITE_PATH to a fresh pair."
        )


class FaissRepository:
    """Semantic vector index repository backed by FAISS IndexFlatIP."""

    def __init__(self, index_path: str, dimension: int) -> None:
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index = self.load_or_create()

    def load_or_create(self) -> faiss.IndexFlatIP:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        if self.index_path.exists():
            index = faiss.read_index(str(self.index_path))
            found = int(getattr(index, "d", -1))
            if found != self.dimension:
                raise FaissIndexDimensionMismatchError(self.index_path, found, self.dimension)
            return index
        return faiss.IndexFlatIP(self.dimension)

    def add_vectors(self, vectors: list[list[float]]) -> list[int]:
        if not vectors:
            return []
        matrix = self._to_normalized_matrix(vectors)
        start_pos = self.index.ntotal
        self.index.add(matrix)
        self.persist()
        return list(range(start_pos, start_pos + matrix.shape[0]))

    def search(self, query_vector: list[float], top_k: int) -> list[tuple[int, float]]:
        if self.index.ntotal == 0:
            return []
        matrix = self._to_normalized_matrix([query_vector])
        scores, ids = self.index.search(matrix, top_k)
        results: list[tuple[int, float]] = []
        for idx, score in zip(ids[0], scores[0]):
            if idx == -1:
                continue
            results.append((int(idx), float(score)))
        return results

    def persist(self) -> None:
        faiss.write_index(self.index, str(self.index_path))

    def _to_normalized_matrix(self, vectors: list[list[float]]) -> np.ndarray:
        matrix = np.array(vectors, dtype=np.float32)
        if matrix.ndim != 2 or matrix.shape[1] != self.dimension:
            raise ValueError(
                f"Vector shape mismatch. Expected (*, {self.dimension}), got {matrix.shape}."
            )
        faiss.normalize_L2(matrix)
        return matrix
