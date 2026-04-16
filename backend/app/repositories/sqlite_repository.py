from __future__ import annotations

import re
import sqlite3
from pathlib import Path


class SQLiteRepository:
    """Metadata persistence boundary for repositories, files, and chunks."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def initialize_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunk_metadata (
                    chunk_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    symbol_name TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    parent_symbol TEXT,
                    docstring TEXT,
                    content TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_map (
                    faiss_id INTEGER PRIMARY KEY,
                    chunk_id TEXT NOT NULL,
                    FOREIGN KEY(chunk_id) REFERENCES chunk_metadata(chunk_id)
                )
                """
            )

    def upsert_chunk_metadata(self, records: list[dict[str, object]]) -> None:
        if not records:
            return
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO chunk_metadata (
                    chunk_id, file_path, symbol_name, chunk_type, start_line,
                    end_line, parent_symbol, docstring, content
                ) VALUES (
                    :chunk_id, :file_path, :symbol_name, :chunk_type, :start_line,
                    :end_line, :parent_symbol, :docstring, :content
                )
                ON CONFLICT(chunk_id) DO UPDATE SET
                    file_path=excluded.file_path,
                    symbol_name=excluded.symbol_name,
                    chunk_type=excluded.chunk_type,
                    start_line=excluded.start_line,
                    end_line=excluded.end_line,
                    parent_symbol=excluded.parent_symbol,
                    docstring=excluded.docstring,
                    content=excluded.content
                """,
                records,
            )

    def insert_vector_map(self, mapping: list[tuple[int, str]]) -> None:
        if not mapping:
            return
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO vector_map (faiss_id, chunk_id)
                VALUES (?, ?)
                """,
                mapping,
            )

    def fetch_chunk_by_faiss_id(self, faiss_id: int) -> dict[str, object] | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    cm.chunk_id,
                    cm.file_path,
                    cm.symbol_name,
                    cm.chunk_type,
                    cm.start_line,
                    cm.end_line,
                    cm.parent_symbol,
                    cm.docstring,
                    cm.content
                FROM vector_map vm
                JOIN chunk_metadata cm ON vm.chunk_id = cm.chunk_id
                WHERE vm.faiss_id = ?
                """,
                (faiss_id,),
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
        }

    _LEXICAL_STOPWORDS = frozenset(
        {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "dare",
            "ought",
            "used",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "and",
            "but",
            "if",
            "or",
            "because",
            "until",
            "while",
            "this",
            "that",
            "these",
            "those",
            "what",
            "which",
            "who",
            "whom",
            "it",
            "its",
            "they",
            "them",
            "their",
            "implemented",
            "implementation",
            "function",
            "class",
            "method",
            "file",
            "code",
            "repo",
            "repository",
        }
    )

    @classmethod
    def extract_lexical_tokens(cls, query: str) -> list[str]:
        raw = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query)
        out: list[str] = []
        for t in raw:
            tl = t.lower()
            if len(tl) < 2 or tl in cls._LEXICAL_STOPWORDS:
                continue
            out.append(tl)
        return out

    def search_chunks_matching_tokens(
        self,
        tokens: list[str],
        *,
        per_token_limit: int = 12,
        total_limit: int = 32,
    ) -> list[dict[str, object]]:
        """Lexical retrieval: path / symbol / content substring match (helps exact names like cpop)."""
        if not tokens:
            return []
        seen: set[str] = set()
        ranked: list[tuple[float, dict[str, object]]] = []
        with self.connect() as conn:
            for token in tokens:
                rows = conn.execute(
                    """
                    SELECT chunk_id, file_path, symbol_name, chunk_type, start_line, end_line,
                           parent_symbol, docstring, content
                    FROM chunk_metadata
                    WHERE instr(lower(file_path), ?) > 0
                       OR instr(lower(symbol_name), ?) > 0
                       OR instr(lower(content), ?) > 0
                    LIMIT ?
                    """,
                    (token, token, token, per_token_limit),
                ).fetchall()
                for row in rows:
                    cid = str(row[0])
                    if cid in seen:
                        continue
                    fp = str(row[1]).lower()
                    sym = str(row[2]).lower()
                    content = str(row[8]).lower()
                    if token in fp and (token + ".py" in fp or fp.endswith(token + ".py") or f"/{token}.py" in fp):
                        boost = 0.98
                    elif token in fp:
                        boost = 0.95
                    elif token in sym:
                        boost = 0.90
                    elif token in content:
                        boost = 0.82
                    else:
                        boost = 0.75
                    seen.add(cid)
                    ranked.append(
                        (
                            -boost,
                            {
                                "chunk_id": row[0],
                                "file_path": row[1],
                                "symbol_name": row[2],
                                "chunk_type": row[3],
                                "start_line": row[4],
                                "end_line": row[5],
                                "parent_symbol": row[6],
                                "docstring": row[7],
                                "content": row[8],
                                "score": boost * 2.0 - 1.0,
                                "_lexical": True,
                            },
                        )
                    )
        ranked.sort(key=lambda x: x[0])
        return [item[1] for item in ranked[:total_limit]]
