from __future__ import annotations

from pydantic import BaseModel, Field


class BuildIndexRequest(BaseModel):
    repository_id: str = Field(..., description="Repository identifier")
    include_graph: bool = Field(default=True, description="Build structural graph index")
    include_semantic: bool = Field(default=True, description="Build semantic vector index")


class BuildIndexResponse(BaseModel):
    repository_id: str
    indexed_chunks: int
    graph_nodes: int
    graph_edges: int
    status: str
