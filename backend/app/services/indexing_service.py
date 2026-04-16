from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, status

from app.graph.structure_graph import StructureGraphBuilder
from app.indexing.chunker import StructureAwareChunker
from app.indexing.semantic_indexer import SemanticIndexer
from app.schemas.indexing import BuildIndexRequest, BuildIndexResponse


class IndexingService:
    """Coordinates chunking + semantic + structural indexing."""

    def build_indexes(self, payload: BuildIndexRequest) -> BuildIndexResponse:
        repo_path = Path(payload.repository_id).expanduser().resolve()
        if not repo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository path does not exist: {repo_path}",
            )
        if not repo_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Repository path is not a directory: {repo_path}",
            )

        chunker = StructureAwareChunker()
        chunks = chunker.chunk_repository(str(repo_path), metadata_output_path=None)

        indexed_chunks = 0
        if payload.include_semantic:
            indexer = SemanticIndexer()
            indexed_chunks = indexer.index_chunks(chunks)

        graph_nodes = 0
        graph_edges = 0
        if payload.include_graph:
            graph_builder = StructureGraphBuilder()
            graph = graph_builder.build_from_repository(str(repo_path))
            graph_nodes = graph.number_of_nodes()
            graph_edges = graph.number_of_edges()

        return BuildIndexResponse(
            repository_id=str(repo_path),
            indexed_chunks=indexed_chunks,
            graph_nodes=graph_nodes,
            graph_edges=graph_edges,
            status="completed",
        )
