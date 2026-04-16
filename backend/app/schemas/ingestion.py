from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class IngestRepositoryRequest(BaseModel):
    local_repo_path: str = Field(..., description="Absolute or relative local repository path")


class ManifestFileItem(BaseModel):
    path: str
    file_type: str
    language: str
    size: int
    content: str


class IngestRepositoryResponse(BaseModel):
    repository_path: str
    status: str
    message: str
    file_count: int
    manifest: List[ManifestFileItem]
    indexed_chunks: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
