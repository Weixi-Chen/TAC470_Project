from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CodeChunk:
    chunk_id: str
    file_path: str
    symbol_name: str
    chunk_type: str
    start_line: int
    end_line: int
    content: str
    parent_symbol: str | None
    docstring: str | None


class StructureAwareChunker:
    """Parses Python files with AST and creates structure-aware chunks."""

    IGNORED_DIRECTORIES = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "env",
        "build",
        "dist",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
    }

    def chunk_repository(
        self, repository_path: str, metadata_output_path: str | None = None
    ) -> list[CodeChunk]:
        repo_path = Path(repository_path).expanduser().resolve()
        python_files = self._discover_python_files(repo_path)

        all_chunks: list[CodeChunk] = []
        for file_path in python_files:
            all_chunks.extend(self.chunk_python_file(repo_path, file_path))

        if metadata_output_path:
            self.save_chunk_metadata_json(all_chunks, metadata_output_path)
        return all_chunks

    def chunk_python_file(self, repo_path: Path, file_path: Path) -> list[CodeChunk]:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        lines = source.splitlines()
        module_name = str(file_path.relative_to(repo_path).with_suffix("")).replace("/", ".")
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            return []

        chunks: list[CodeChunk] = []
        chunks.append(self._create_file_summary_chunk(repo_path, file_path, source, tree))

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                chunks.append(
                    self._create_symbol_chunk(
                        repo_path=repo_path,
                        file_path=file_path,
                        lines=lines,
                        symbol_name=node.name,
                        chunk_type="class",
                        start_line=node.lineno,
                        end_line=self._node_end_line(node),
                        parent_symbol=module_name,
                        docstring=ast.get_docstring(node),
                    )
                )

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_name = f"{node.name}.{child.name}"
                        chunks.append(
                            self._create_symbol_chunk(
                                repo_path=repo_path,
                                file_path=file_path,
                                lines=lines,
                                symbol_name=method_name,
                                chunk_type="method",
                                start_line=child.lineno,
                                end_line=self._node_end_line(child),
                                parent_symbol=node.name,
                                docstring=ast.get_docstring(child),
                            )
                        )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunks.append(
                    self._create_symbol_chunk(
                        repo_path=repo_path,
                        file_path=file_path,
                        lines=lines,
                        symbol_name=node.name,
                        chunk_type="function",
                        start_line=node.lineno,
                        end_line=self._node_end_line(node),
                        parent_symbol=module_name,
                        docstring=ast.get_docstring(node),
                    )
                )

        return chunks

    def save_chunk_metadata_json(self, chunks: list[CodeChunk], output_path: str) -> None:
        path = Path(output_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(chunk) for chunk in chunks]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _discover_python_files(self, repo_path: Path) -> list[Path]:
        files: list[Path] = []
        for file_path in repo_path.rglob("*.py"):
            if self._is_ignored_path(repo_path, file_path):
                continue
            files.append(file_path)
        files.sort()
        return files

    def _is_ignored_path(self, repo_path: Path, file_path: Path) -> bool:
        return any(
            part in self.IGNORED_DIRECTORIES for part in file_path.relative_to(repo_path).parts
        )

    def _create_file_summary_chunk(
        self, repo_path: Path, file_path: Path, source: str, tree: ast.Module
    ) -> CodeChunk:
        classes = [
            node.name
            for node in tree.body
            if isinstance(node, ast.ClassDef)
        ]
        functions = [
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        summary_lines = [
            f"File: {file_path.relative_to(repo_path)}",
            f"Top-level classes ({len(classes)}): {', '.join(classes) if classes else 'None'}",
            f"Top-level functions ({len(functions)}): {', '.join(functions) if functions else 'None'}",
        ]

        module_symbol = str(file_path.relative_to(repo_path).with_suffix("")).replace("/", ".")
        line_count = max(1, len(source.splitlines()))
        return CodeChunk(
            chunk_id=self._make_chunk_id(file_path, "file_summary", module_symbol, 1, line_count),
            file_path=str(file_path.relative_to(repo_path)),
            symbol_name=module_symbol,
            chunk_type="file_summary",
            start_line=1,
            end_line=line_count,
            content="\n".join(summary_lines),
            parent_symbol=None,
            docstring=ast.get_docstring(tree),
        )

    def _create_symbol_chunk(
        self,
        repo_path: Path,
        file_path: Path,
        lines: list[str],
        symbol_name: str,
        chunk_type: str,
        start_line: int,
        end_line: int,
        parent_symbol: str | None,
        docstring: str | None,
    ) -> CodeChunk:
        start_idx = max(0, start_line - 1)
        end_idx = max(start_idx, end_line)
        content = "\n".join(lines[start_idx:end_idx])
        return CodeChunk(
            chunk_id=self._make_chunk_id(file_path, chunk_type, symbol_name, start_line, end_line),
            file_path=str(file_path.relative_to(repo_path)),
            symbol_name=symbol_name,
            chunk_type=chunk_type,
            start_line=start_line,
            end_line=end_line,
            content=content,
            parent_symbol=parent_symbol,
            docstring=docstring,
        )

    @staticmethod
    def _node_end_line(node: ast.AST) -> int:
        return getattr(node, "end_lineno", getattr(node, "lineno", 1))

    @staticmethod
    def _make_chunk_id(
        file_path: Path, chunk_type: str, symbol_name: str, start_line: int, end_line: int
    ) -> str:
        base = f"{file_path}:{chunk_type}:{symbol_name}:{start_line}:{end_line}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()
