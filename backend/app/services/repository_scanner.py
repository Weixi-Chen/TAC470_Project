from __future__ import annotations

from pathlib import Path

from app.schemas.ingestion import ManifestFileItem


class RepositoryScanner:
    """Scans Python repositories and builds a manifest of relevant text files."""

    MAX_FILE_SIZE_BYTES = 1_000_000

    IGNORED_DIRECTORIES = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "env",
        ".mypy_cache",
        ".pytest_cache",
        "build",
        "dist",
        "node_modules",
    }

    IGNORED_FILE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".whl",
        ".so",
        ".dylib",
        ".dll",
        ".exe",
        ".class",
        ".jar",
        ".pyc",
    }

    def scan(self, repo_path: Path) -> list[ManifestFileItem]:
        manifest: list[ManifestFileItem] = []

        for path in repo_path.rglob("*"):
            if not path.is_file():
                continue
            if self._should_ignore_path(path, repo_path):
                continue
            if not self._is_relevant_python_repo_file(path):
                continue
            if path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
                continue
            if self._is_binary_file(path):
                continue

            content = path.read_text(encoding="utf-8", errors="replace")
            manifest.append(
                ManifestFileItem(
                    path=str(path.relative_to(repo_path)),
                    file_type=self._file_type(path),
                    language=self._language(path),
                    size=path.stat().st_size,
                    content=content,
                )
            )

        manifest.sort(key=lambda item: item.path)
        return manifest

    def _should_ignore_path(self, path: Path, repo_path: Path) -> bool:
        relative_parts = path.relative_to(repo_path).parts
        for part in relative_parts:
            if part in self.IGNORED_DIRECTORIES or part.endswith(".egg-info"):
                return True
        return path.suffix.lower() in self.IGNORED_FILE_EXTENSIONS

    @staticmethod
    def _is_relevant_python_repo_file(path: Path) -> bool:
        filename = path.name.lower()
        return (
            path.suffix.lower() == ".py"
            or filename == "readme.md"
            or filename == "requirements.txt"
        )

    @staticmethod
    def _is_binary_file(path: Path) -> bool:
        sample = path.read_bytes()[:1024]
        if b"\x00" in sample:
            return True

        # Heuristic: if too many non-text bytes appear in a sample, treat as binary.
        text_chars = bytes(range(32, 127)) + b"\n\r\t\f\b"
        non_text_count = sum(byte not in text_chars for byte in sample)
        return bool(sample) and (non_text_count / len(sample)) > 0.30

    @staticmethod
    def _file_type(path: Path) -> str:
        name = path.name.lower()
        if name == "readme.md":
            return "documentation"
        if name == "requirements.txt":
            return "dependency"
        return "source"

    @staticmethod
    def _language(path: Path) -> str:
        name = path.name.lower()
        if path.suffix.lower() == ".py":
            return "python"
        if name == "readme.md":
            return "markdown"
        return "text"
