from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, status

from app.schemas.indexing import BuildIndexRequest
from app.schemas.ingestion import IngestRepositoryRequest, IngestRepositoryResponse
from app.services.indexing_service import IndexingService
from app.services.repository_scanner import RepositoryScanner


class IngestionService:
    """Orchestrates repository ingestion workflow."""

    def __init__(self) -> None:
        self.scanner = RepositoryScanner()
        self.indexing = IndexingService()

    def ingest_repository(self, payload: IngestRepositoryRequest) -> IngestRepositoryResponse:
        repo_path = Path(payload.local_repo_path).expanduser().resolve()
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

        manifest = self.scanner.scan(repo_path)
        index_result = self.indexing.build_indexes(
            BuildIndexRequest(
                repository_id=str(repo_path),
                include_graph=True,
                include_semantic=True,
            )
        )
        return IngestRepositoryResponse(
            repository_path=str(repo_path),
            status="completed",
            message=(
                "Repository scanned and search index built "
                f"({index_result.indexed_chunks} chunks, "
                f"{index_result.graph_nodes} graph nodes)."
            ),
            file_count=len(manifest),
            manifest=manifest,
            indexed_chunks=index_result.indexed_chunks,
            graph_nodes=index_result.graph_nodes,
            graph_edges=index_result.graph_edges,
        )
