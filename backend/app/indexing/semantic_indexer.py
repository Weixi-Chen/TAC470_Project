from __future__ import annotations

from dataclasses import asdict

from app.embeddings.provider import EmbeddingProvider
from app.embeddings.store import get_embedding_store_config
from app.indexing.chunker import CodeChunk
from app.repositories.faiss_repository import FaissRepository
from app.repositories.sqlite_repository import SQLiteRepository


class SemanticIndexer:
    """Create and search semantic vector index for code chunks."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        faiss_repository: FaissRepository | None = None,
        metadata_repository: SQLiteRepository | None = None,
    ) -> None:
        store = get_embedding_store_config()
        self.embedding_provider = embedding_provider or store.provider
        self.metadata_repository = metadata_repository or SQLiteRepository(store.sqlite_path)
        self.faiss_repository = faiss_repository or FaissRepository(
            store.faiss_index_path, self.embedding_provider.dimension
        )
        self.metadata_repository.initialize_schema()

    def index_chunks(self, chunks: list[CodeChunk]) -> int:
        if not chunks:
            return 0

        texts = [self._chunk_to_embedding_text(chunk) for chunk in chunks]
        vectors = self.embedding_provider.embed_texts(texts)
        faiss_ids = self.faiss_repository.add_vectors(vectors)

        metadata_records = [asdict(chunk) for chunk in chunks]
        self.metadata_repository.upsert_chunk_metadata(metadata_records)
        self.metadata_repository.insert_vector_map(
            list(zip(faiss_ids, [chunk.chunk_id for chunk in chunks]))
        )
        return len(chunks)

    def search_chunks(self, query: str, top_k: int) -> list[dict[str, object]]:
        if top_k <= 0:
            return []

        query_vector = self.embedding_provider.embed_query(query)
        faiss_matches = self.faiss_repository.search(query_vector, top_k)
        results: list[dict[str, object]] = []

        for faiss_id, score in faiss_matches:
            metadata = self.metadata_repository.fetch_chunk_by_faiss_id(faiss_id)
            if not metadata:
                continue
            results.append({"score": score, **metadata})
        return results

    @staticmethod
    def _chunk_to_embedding_text(chunk: CodeChunk) -> str:
        doc = chunk.docstring or ""
        parent = chunk.parent_symbol or ""
        return (
            f"file={chunk.file_path}\n"
            f"symbol={chunk.symbol_name}\n"
            f"type={chunk.chunk_type}\n"
            f"parent={parent}\n"
            f"docstring={doc}\n"
            f"content=\n{chunk.content}"
        )
