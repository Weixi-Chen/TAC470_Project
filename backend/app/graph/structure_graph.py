from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

import networkx as nx


@dataclass
class SymbolRef:
    node_id: str
    symbol_name: str
    node_type: str
    file_path: str


class StructureGraphBuilder:
    """Build a directed structural graph for a Python repository."""

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

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self._symbols_by_file: dict[str, dict[str, SymbolRef]] = {}
        self._global_symbols: dict[str, SymbolRef] = {}
        self._class_method_symbols: dict[str, dict[str, SymbolRef]] = {}
        self._file_node_ids: dict[str, str] = {}
        self._module_to_file: dict[str, str] = {}

    def build_from_repository(self, repository_path: str) -> nx.DiGraph:
        self.graph = nx.DiGraph()
        self._symbols_by_file.clear()
        self._global_symbols.clear()
        self._class_method_symbols.clear()
        self._file_node_ids.clear()
        self._module_to_file.clear()

        repo_path = Path(repository_path).expanduser().resolve()
        python_files = self._discover_python_files(repo_path)
        parsed: dict[str, ast.Module] = {}

        for file_path in python_files:
            relative = str(file_path.relative_to(repo_path))
            source = file_path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue
            parsed[relative] = tree
            self._module_to_file[self._module_name_from_relative(relative)] = relative
            self._add_file_node(relative)
            self._index_symbols_in_file(relative, tree)

        for relative, tree in parsed.items():
            self._add_import_edges(relative, tree)
            self._add_call_edges(relative, tree)

        return self.graph

    def export_json(self) -> dict[str, list[dict[str, object]]]:
        nodes = [
            {"id": node_id, **attrs}
            for node_id, attrs in self.graph.nodes(data=True)
        ]
        edges = [
            {"source": source, "target": target, **attrs}
            for source, target, attrs in self.graph.edges(data=True)
        ]
        return {"nodes": nodes, "edges": edges}

    def save_json(self, output_path: str) -> None:
        path = Path(output_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.export_json(), ensure_ascii=False, indent=2), encoding="utf-8")

    def get_symbol_neighbors(self, symbol_id: str) -> list[str]:
        if symbol_id not in self.graph:
            return []
        neighbors = set(self.graph.successors(symbol_id)) | set(self.graph.predecessors(symbol_id))
        return sorted(neighbors)

    def get_callers(self, symbol_id: str) -> list[str]:
        if symbol_id not in self.graph:
            return []
        callers = [
            source
            for source, _, attrs in self.graph.in_edges(symbol_id, data=True)
            if attrs.get("edge_type") == "calls"
        ]
        return sorted(callers)

    def get_callees(self, symbol_id: str) -> list[str]:
        if symbol_id not in self.graph:
            return []
        callees = [
            target
            for _, target, attrs in self.graph.out_edges(symbol_id, data=True)
            if attrs.get("edge_type") == "calls"
        ]
        return sorted(callees)

    def find_entry_candidates(self) -> list[str]:
        candidates: list[tuple[int, str]] = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("node_type")
            if node_type not in {"function", "method"}:
                continue

            symbol_name = str(attrs.get("symbol_name", ""))
            lower_name = symbol_name.lower()
            score = 0
            if any(token in lower_name for token in ("main", "run", "start", "cli", "entry")):
                score += 3
            if not self.get_callers(node_id):
                score += 1
            if self.get_callees(node_id):
                score += 1
            if score > 0:
                candidates.append((score, node_id))

        candidates.sort(key=lambda item: (-item[0], item[1]))
        return [node_id for _, node_id in candidates]

    def _discover_python_files(self, repo_path: Path) -> list[Path]:
        files: list[Path] = []
        for path in repo_path.rglob("*.py"):
            if self._is_ignored_path(repo_path, path):
                continue
            files.append(path)
        files.sort()
        return files

    def _is_ignored_path(self, repo_path: Path, file_path: Path) -> bool:
        return any(part in self.IGNORED_DIRECTORIES for part in file_path.relative_to(repo_path).parts)

    def _add_file_node(self, relative_path: str) -> None:
        node_id = f"file:{relative_path}"
        self._file_node_ids[relative_path] = node_id
        self.graph.add_node(
            node_id,
            node_type="file",
            symbol_name=relative_path,
            file_path=relative_path,
        )

    def _index_symbols_in_file(self, relative_path: str, tree: ast.Module) -> None:
        file_symbols: dict[str, SymbolRef] = {}
        file_node = self._file_node_ids[relative_path]

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_symbol_name = node.name
                class_id = f"class:{relative_path}:{class_symbol_name}"
                class_ref = SymbolRef(
                    node_id=class_id,
                    symbol_name=class_symbol_name,
                    node_type="class",
                    file_path=relative_path,
                )
                file_symbols[class_symbol_name] = class_ref
                self._global_symbols[class_symbol_name] = class_ref
                self.graph.add_node(
                    class_id,
                    node_type="class",
                    symbol_name=class_symbol_name,
                    file_path=relative_path,
                )
                self.graph.add_edge(file_node, class_id, edge_type="defines")
                self.graph.add_edge(file_node, class_id, edge_type="contains")

                class_methods: dict[str, SymbolRef] = {}
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_symbol_name = f"{class_symbol_name}.{child.name}"
                        method_id = f"method:{relative_path}:{method_symbol_name}"
                        method_ref = SymbolRef(
                            node_id=method_id,
                            symbol_name=method_symbol_name,
                            node_type="method",
                            file_path=relative_path,
                        )
                        class_methods[child.name] = method_ref
                        self.graph.add_node(
                            method_id,
                            node_type="method",
                            symbol_name=method_symbol_name,
                            file_path=relative_path,
                        )
                        self.graph.add_edge(class_id, method_id, edge_type="contains")
                        self.graph.add_edge(class_id, method_id, edge_type="defines")
                self._class_method_symbols[f"{relative_path}:{class_symbol_name}"] = class_methods

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_symbol_name = node.name
                function_id = f"function:{relative_path}:{function_symbol_name}"
                function_ref = SymbolRef(
                    node_id=function_id,
                    symbol_name=function_symbol_name,
                    node_type="function",
                    file_path=relative_path,
                )
                file_symbols[function_symbol_name] = function_ref
                self._global_symbols[function_symbol_name] = function_ref
                self.graph.add_node(
                    function_id,
                    node_type="function",
                    symbol_name=function_symbol_name,
                    file_path=relative_path,
                )
                self.graph.add_edge(file_node, function_id, edge_type="defines")
                self.graph.add_edge(file_node, function_id, edge_type="contains")

        self._symbols_by_file[relative_path] = file_symbols

    def _add_import_edges(self, relative_path: str, tree: ast.Module) -> None:
        source_file_id = self._file_node_ids[relative_path]
        module_name = self._module_name_from_relative(relative_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target_rel = self._module_to_file.get(alias.name)
                    if target_rel:
                        self.graph.add_edge(
                            source_file_id,
                            self._file_node_ids[target_rel],
                            edge_type="imports",
                        )
            elif isinstance(node, ast.ImportFrom):
                base_module = self._resolve_relative_import_module(
                    module_name=module_name,
                    imported_module=node.module,
                    level=node.level,
                )
                if base_module in self._module_to_file:
                    target_rel = self._module_to_file[base_module]
                    self.graph.add_edge(
                        source_file_id,
                        self._file_node_ids[target_rel],
                        edge_type="imports",
                    )

    def _add_call_edges(self, relative_path: str, tree: ast.Module) -> None:
        file_symbols = self._symbols_by_file.get(relative_path, {})
        module_name = self._module_name_from_relative(relative_path)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                caller = file_symbols.get(node.name)
                if caller:
                    self._connect_calls_for_scope(caller.node_id, node, relative_path, module_name, None)
            elif isinstance(node, ast.ClassDef):
                class_symbol = file_symbols.get(node.name)
                if not class_symbol:
                    continue
                methods = self._class_method_symbols.get(f"{relative_path}:{node.name}", {})
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        caller = methods.get(child.name)
                        if caller:
                            self._connect_calls_for_scope(
                                caller.node_id,
                                child,
                                relative_path,
                                module_name,
                                node.name,
                            )

    def _connect_calls_for_scope(
        self,
        caller_id: str,
        scope_node: ast.AST,
        relative_path: str,
        module_name: str,
        class_name: str | None,
    ) -> None:
        for node in ast.walk(scope_node):
            if not isinstance(node, ast.Call):
                continue
            callee = self._resolve_call_target(
                call_node=node,
                relative_path=relative_path,
                module_name=module_name,
                class_name=class_name,
            )
            if callee and callee in self.graph:
                self.graph.add_edge(caller_id, callee, edge_type="calls")

    def _resolve_call_target(
        self,
        call_node: ast.Call,
        relative_path: str,
        module_name: str,
        class_name: str | None,
    ) -> str | None:
        func_expr = call_node.func

        # Conservative case 1: direct call by name, e.g. foo()
        if isinstance(func_expr, ast.Name):
            name = func_expr.id
            local = self._symbols_by_file.get(relative_path, {}).get(name)
            if local:
                return local.node_id
            global_ref = self._global_symbols.get(name)
            return global_ref.node_id if global_ref else None

        # Conservative case 2: method call on self/cls, e.g. self.bar()
        if isinstance(func_expr, ast.Attribute) and isinstance(func_expr.value, ast.Name):
            owner = func_expr.value.id
            method = func_expr.attr
            if class_name and owner in {"self", "cls"}:
                class_methods = self._class_method_symbols.get(f"{relative_path}:{class_name}", {})
                if method in class_methods:
                    return class_methods[method].node_id

            # Conservative case 3: module-level attribute call, e.g. module.func()
            imported_module_name = self._resolve_import_alias(relative_path, module_name, owner)
            if imported_module_name and imported_module_name in self._module_to_file:
                target_file = self._module_to_file[imported_module_name]
                target_symbol = self._symbols_by_file.get(target_file, {}).get(method)
                if target_symbol:
                    return target_symbol.node_id
        return None

    def _resolve_import_alias(self, relative_path: str, module_name: str, alias_name: str) -> str | None:
        del relative_path
        del module_name
        # Conservative implementation: this builder does not yet keep full alias tables.
        # Returning None avoids false-positive call edges.
        return None

    @staticmethod
    def _module_name_from_relative(relative_path: str) -> str:
        module_path = relative_path[:-3] if relative_path.endswith(".py") else relative_path
        return module_path.replace("/", ".")

    @staticmethod
    def _resolve_relative_import_module(
        module_name: str, imported_module: str | None, level: int
    ) -> str:
        parts = module_name.split(".")
        if level > 0:
            base = parts[:-level]
        else:
            base = parts
        if imported_module:
            return ".".join(base + imported_module.split("."))
        return ".".join(base)
