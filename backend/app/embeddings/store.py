from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from app.embeddings.openai_provider import OpenAIEmbeddingProvider
from app.embeddings.provider import DeterministicHashEmbeddingProvider, EmbeddingProvider

logger = logging.getLogger(__name__)


def _backend_root() -> Path:
    """Directory that contains the ``app`` package (backend project root)."""
    return Path(__file__).resolve().parent.parent.parent


def _resolve_storage_path(path_str: str) -> str:
    """Anchor relative paths to backend root so ingest/QA use the same DB regardless of cwd."""
    p = Path(path_str)
    if p.is_absolute():
        return str(p)
    return str(_backend_root() / p)


@dataclass(frozen=True)
class EmbeddingStoreConfig:
    """Embedding provider and the SQLite + FAISS paths that must stay in sync."""

    provider: EmbeddingProvider
    sqlite_path: str
    faiss_index_path: str
    backend: str


def _optional_env_path(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is not None and raw.strip():
        return raw.strip()
    return default


def get_embedding_store_config() -> EmbeddingStoreConfig:
    """
    Resolve embedding backend and storage paths.

    If ``OPENAI_API_KEY`` is set (non-empty), uses ``OpenAIEmbeddingProvider`` with
    default files ``code_index_openai.db`` and ``semantic_openai.index`` so hash
    (256-dim) indexes are not mixed with OpenAI vectors.

    Relative default paths (and relative ``EMBEDDING_SQLITE_PATH`` /
    ``EMBEDDING_FAISS_PATH``) are resolved under the backend project root so
    indexing and retrieval see the same files even if the process cwd differs.

    Set both env vars to absolute paths when switching models/dimensions or to
    reuse an existing index in another directory.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    use_openai = bool(api_key.strip())

    if use_openai:
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip()
        try:
            dimension = int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536"))
        except ValueError:
            dimension = 1536
        provider: EmbeddingProvider = OpenAIEmbeddingProvider(
            model=model,
            api_key=api_key.strip(),
            dimension=dimension,
        )
        sqlite_default = "code_index_openai.db"
        faiss_default = "semantic_openai.index"
        backend = "openai"
    else:
        provider = DeterministicHashEmbeddingProvider()
        sqlite_default = "code_index.db"
        faiss_default = "semantic.index"
        backend = "hash"

    sqlite_path = _resolve_storage_path(
        _optional_env_path("EMBEDDING_SQLITE_PATH", sqlite_default)
    )
    faiss_index_path = _resolve_storage_path(
        _optional_env_path("EMBEDDING_FAISS_PATH", faiss_default)
    )

    logger.info(
        "Embedding store: backend=%s sqlite=%s faiss=%s dim=%s",
        backend,
        sqlite_path,
        faiss_index_path,
        provider.dimension,
    )
    return EmbeddingStoreConfig(
        provider=provider,
        sqlite_path=sqlite_path,
        faiss_index_path=faiss_index_path,
        backend=backend,
    )
