from __future__ import annotations

from dataclasses import dataclass, field

from app.graph.structure_graph import StructureGraphBuilder
from app.indexing.semantic_indexer import SemanticIndexer
from app.repositories.sqlite_repository import SQLiteRepository
from app.schemas.retrieval import EvidenceItem


@dataclass
class CandidateScore:
    semantic: float = 0.0
    graph_proximity: float = 0.0
    symbol_importance: float = 0.0
    reasons: set[str] = field(default_factory=set)


class HybridRetriever:
    """Combine semantic retrieval and structural expansion with weighted reranking."""

    SEMANTIC_WEIGHT = 0.65
    GRAPH_WEIGHT = 0.25
    IMPORTANCE_WEIGHT = 0.10

    def __init__(
        self,
        semantic_indexer: SemanticIndexer | None = None,
        graph_builder: StructureGraphBuilder | None = None,
    ) -> None:
        self.semantic_indexer = semantic_indexer or SemanticIndexer()
        self.graph_builder = graph_builder or StructureGraphBuilder()

    def retrieve(self, repository_id: str, query: str, top_k: int) -> list[EvidenceItem]:
        repo = self.semantic_indexer.metadata_repository
        tokens = SQLiteRepository.extract_lexical_tokens(query)
        lexical_hits = repo.search_chunks_matching_tokens(tokens)

        semantic_hits = self.semantic_indexer.search_chunks(
            query=query, top_k=max(top_k, 24)
        )
        if not semantic_hits and not lexical_hits:
            return []

        graph = self.graph_builder.build_from_repository(repository_id)
        if graph.number_of_nodes() == 0:
            merged = self._merge_hits_for_display(semantic_hits, lexical_hits, top_k)
            return self._semantic_only_evidence(merged)

        scored: dict[str, CandidateScore] = {}
        metadata_by_chunk_id: dict[str, dict[str, object]] = {}

        for hit in semantic_hits:
            self._seed_from_hit(
                hit=hit,
                graph=graph,
                scored=scored,
                metadata_by_chunk_id=metadata_by_chunk_id,
                lexical=False,
            )
        for hit in lexical_hits:
            self._seed_from_hit(
                hit=hit,
                graph=graph,
                scored=scored,
                metadata_by_chunk_id=metadata_by_chunk_id,
                lexical=True,
            )

        ranked = sorted(
            scored.items(),
            key=lambda item: -self._final_score(item[1]),
        )[:top_k]

        evidence: list[EvidenceItem] = []
        for chunk_id, score in ranked:
            metadata = metadata_by_chunk_id.get(chunk_id)
            if not metadata:
                continue
            evidence.append(
                EvidenceItem(
                    chunk_id=chunk_id,
                    file_path=str(metadata["file_path"]),
                    symbol_name=str(metadata["symbol_name"]),
                    start_line=int(metadata["start_line"]),
                    end_line=int(metadata["end_line"]),
                    score=self._final_score(score),
                    relevance_reason=self._reason_text(score),
                    snippet=self._snippet(str(metadata["content"])),
                )
            )
        return evidence

    def _merge_hits_for_display(
        self,
        semantic_hits: list[dict[str, object]],
        lexical_hits: list[dict[str, object]],
        top_k: int,
    ) -> list[dict[str, object]]:
        by_id: dict[str, dict[str, object]] = {}
        scores: dict[str, float] = {}
        for hit in semantic_hits:
            cid = str(hit["chunk_id"])
            by_id[cid] = hit
            scores[cid] = max(scores.get(cid, 0.0), self._normalized_semantic_score(hit))
        for hit in lexical_hits:
            cid = str(hit["chunk_id"])
            by_id[cid] = hit
            scores[cid] = max(scores.get(cid, 0.0), self._normalized_semantic_score(hit))
        ordered = sorted(by_id.keys(), key=lambda c: -scores[c])
        return [by_id[c] for c in ordered[:top_k]]

    def _seed_from_hit(
        self,
        hit: dict[str, object],
        graph,
        scored: dict[str, CandidateScore],
        metadata_by_chunk_id: dict[str, dict[str, object]],
        *,
        lexical: bool,
    ) -> None:
        chunk_id = str(hit["chunk_id"])
        metadata_by_chunk_id[chunk_id] = hit
        candidate = scored.setdefault(chunk_id, CandidateScore())
        norm = self._normalized_semantic_score(hit)
        candidate.semantic = max(candidate.semantic, norm)
        if lexical or hit.get("_lexical"):
            candidate.reasons.add("lexical match (file path, symbol name, or code text)")
        else:
            candidate.reasons.add("high semantic similarity to query")
        self._add_symbol_importance(candidate, hit)

        node_id = self._chunk_to_graph_node_id(hit)
        if not node_id or node_id not in graph:
            return
        self._add_graph_expansion(
            base_hit=hit,
            base_node_id=node_id,
            graph=graph,
            metadata_by_chunk_id=metadata_by_chunk_id,
            scored=scored,
        )

    def _add_graph_expansion(
        self,
        base_hit: dict[str, object],
        base_node_id: str,
        graph,
        metadata_by_chunk_id: dict[str, dict[str, object]],
        scored: dict[str, CandidateScore],
    ) -> None:
        # Same-file neighbors.
        same_file_id = f"file:{base_hit['file_path']}"
        if same_file_id in graph:
            for neighbor in self.graph_builder.get_symbol_neighbors(same_file_id):
                self._boost_node_candidate(
                    neighbor,
                    graph,
                    metadata_by_chunk_id,
                    scored,
                    0.75,
                    "same file neighborhood context",
                )

        # Call graph context.
        for caller in self.graph_builder.get_callers(base_node_id):
            self._boost_node_candidate(
                caller,
                graph,
                metadata_by_chunk_id,
                scored,
                0.85,
                "caller relation in structural graph",
            )
        for callee in self.graph_builder.get_callees(base_node_id):
            self._boost_node_candidate(
                callee,
                graph,
                metadata_by_chunk_id,
                scored,
                0.85,
                "callee relation in structural graph",
            )

        # Parent symbol context.
        for parent, _, attrs in graph.in_edges(base_node_id, data=True):
            if attrs.get("edge_type") == "contains":
                self._boost_node_candidate(
                    parent,
                    graph,
                    metadata_by_chunk_id,
                    scored,
                    0.70,
                    "parent symbol containment context",
                )

    def _boost_node_candidate(
        self,
        node_id: str,
        graph,
        metadata_by_chunk_id: dict[str, dict[str, object]],
        scored: dict[str, CandidateScore],
        graph_score: float,
        reason: str,
    ) -> None:
        chunk_metadata = self._fetch_chunk_metadata_for_node(node_id, graph)
        if not chunk_metadata:
            return
        chunk_id = str(chunk_metadata["chunk_id"])
        metadata_by_chunk_id.setdefault(chunk_id, chunk_metadata)
        candidate = scored.setdefault(chunk_id, CandidateScore())
        candidate.graph_proximity = max(candidate.graph_proximity, graph_score)
        candidate.reasons.add(reason)
        self._add_symbol_importance(candidate, chunk_metadata)

    def _fetch_chunk_metadata_for_node(self, node_id: str, graph) -> dict[str, object] | None:
        attrs = graph.nodes[node_id]
        node_type = attrs.get("node_type")
        if node_type == "file":
            return None
        file_path = attrs.get("file_path")
        symbol_name = attrs.get("symbol_name")
        if not file_path or not symbol_name or not node_type:
            return None
        with self.semantic_indexer.metadata_repository.connect() as conn:
            row = conn.execute(
                """
                SELECT chunk_id, file_path, symbol_name, chunk_type, start_line, end_line, parent_symbol, docstring, content
                FROM chunk_metadata
                WHERE file_path = ? AND symbol_name = ? AND chunk_type = ?
                LIMIT 1
                """,
                (str(file_path), str(symbol_name), str(node_type)),
            ).fetchone()
        if row is None:
            return None
        return {
            "chunk_id": row[0],
            "file_path": row[1],
            "symbol_name": row[2],
            "chunk_type": row[3],
            "start_line": row[4],
            "end_line": row[5],
            "parent_symbol": row[6],
            "docstring": row[7],
            "content": row[8],
            "score": 0.0,
        }

    @staticmethod
    def _chunk_to_graph_node_id(hit: dict[str, object]) -> str | None:
        file_path = str(hit.get("file_path", ""))
        symbol_name = str(hit.get("symbol_name", ""))
        chunk_type = str(hit.get("chunk_type", ""))
        if chunk_type == "class":
            return f"class:{file_path}:{symbol_name}"
        if chunk_type == "method":
            return f"method:{file_path}:{symbol_name}"
        if chunk_type == "function":
            return f"function:{file_path}:{symbol_name}"
        if chunk_type == "file_summary":
            return f"file:{file_path}"
        return None

    @staticmethod
    def _normalized_semantic_score(hit: dict[str, object]) -> float:
        raw = float(hit.get("score", 0.0))
        return max(0.0, min(1.0, (raw + 1.0) / 2.0))

    @staticmethod
    def _add_symbol_importance(candidate: CandidateScore, metadata: dict[str, object]) -> None:
        chunk_type = str(metadata.get("chunk_type", ""))
        symbol_name = str(metadata.get("symbol_name", "")).lower()
        importance = 0.2
        if chunk_type in {"function", "method"}:
            importance += 0.2
        if chunk_type == "class":
            importance += 0.1
        if any(token in symbol_name for token in ("main", "run", "entry", "api", "service")):
            importance += 0.2
            candidate.reasons.add("symbol appears to be operationally important")
        candidate.symbol_importance = max(candidate.symbol_importance, min(1.0, importance))

    def _final_score(self, score: CandidateScore) -> float:
        return (
            self.SEMANTIC_WEIGHT * score.semantic
            + self.GRAPH_WEIGHT * score.graph_proximity
            + self.IMPORTANCE_WEIGHT * score.symbol_importance
        )

    @staticmethod
    def _reason_text(score: CandidateScore) -> str:
        if not score.reasons:
            return "retrieved by semantic relevance"
        return "; ".join(sorted(score.reasons))

    @staticmethod
    def _snippet(content: str, max_chars: int = 320) -> str:
        if len(content) <= max_chars:
            return content
        return f"{content[:max_chars]}..."

    def _semantic_only_evidence(self, semantic_hits: list[dict[str, object]]) -> list[EvidenceItem]:
        return [
            EvidenceItem(
                chunk_id=str(hit["chunk_id"]),
                file_path=str(hit["file_path"]),
                symbol_name=str(hit["symbol_name"]),
                start_line=int(hit["start_line"]),
                end_line=int(hit["end_line"]),
                score=self._normalized_semantic_score(hit),
                relevance_reason="high semantic similarity to query",
                snippet=self._snippet(str(hit["content"])),
            )
            for hit in semantic_hits
        ]
