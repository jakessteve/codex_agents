from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/treesitter.") from exc

mcp = FastMCP("treesitter")

ROOT = Path(__file__).resolve().parent


@dataclass
class FileMetrics:
    path: str
    language: str
    line_count: int
    symbol_count: int
    class_count: int
    function_count: int
    heading_count: int
    parse_backend: str


def _iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files: list[Path] = []
    for pattern in ("*.py", "*.sh", "*.md", "*.toml", "*.yaml", "*.yml", "*.json"):
        files.extend(sorted(path.rglob(pattern)))
    return sorted(set(files))


def _language(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix in {".sh"}:
        return "shell"
    if suffix in {".md"}:
        return "markdown"
    if suffix in {".toml"}:
        return "toml"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix in {".json"}:
        return "json"
    return "text"


def _tree_sitter_summary(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        proc = subprocess.run(
            ["tree-sitter", "parse", "--json-summary", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None, "fallback"
    if proc.returncode != 0:
        return None, "fallback"
    raw = proc.stdout.strip()
    if not raw:
        return None, "fallback"
    try:
        data = json.loads(raw)
        return data, "tree-sitter-cli"
    except Exception:
        return None, "fallback"


def _python_metrics(path: Path, text: str) -> tuple[int, int, int]:
    try:
        tree = ast.parse(text)
    except Exception:
        return 0, 0, 0
    classes = 0
    functions = 0
    symbols = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes += 1
            symbols += 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1
            symbols += 1
    return symbols, classes, functions


def _shell_metrics(text: str) -> tuple[int, int]:
    functions = len(re.findall(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\)\s*\{", text, flags=re.M))
    return functions, functions


def _markdown_headings(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))


def _metrics_for(path: Path) -> FileMetrics:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lang = _language(path)
    line_count = len(text.splitlines())
    parse_data, backend = _tree_sitter_summary(path)
    if lang == "python":
        symbol_count, class_count, function_count = _python_metrics(path, text)
        heading_count = 0
        if parse_data and isinstance(parse_data, dict):
            function_count = int(parse_data.get("functions", function_count) or function_count)
        return FileMetrics(str(path), lang, line_count, symbol_count, class_count, function_count, heading_count, backend)
    if lang == "shell":
        symbol_count, function_count = _shell_metrics(text)
        return FileMetrics(str(path), lang, line_count, symbol_count, 0, function_count, 0, backend)
    if lang == "markdown":
        headings = _markdown_headings(text)
        return FileMetrics(str(path), lang, line_count, headings, 0, 0, headings, backend)
    return FileMetrics(str(path), lang, line_count, 0, 0, 0, 0, backend)


@mcp.tool()
def summarize_path(path: str) -> dict[str, Any]:
    """Summarize structural metrics for a file or directory."""
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return {"error": "path_not_found", "path": str(target)}
    files = _iter_files(target)
    metrics = [_metrics_for(file_path) for file_path in files]
    return {
        "path": str(target),
        "file_count": len(files),
        "files": [metric.__dict__ for metric in metrics],
        "language_counts": {
            lang: sum(1 for metric in metrics if metric.language == lang)
            for lang in sorted({metric.language for metric in metrics})
        },
    }


@mcp.tool()
def changed_symbols(diff_text: str) -> dict[str, Any]:
    """Extract symbol-like names from a diff."""
    added = re.findall(r"^\+\s*(?:def|class|function)\s+([A-Za-z_][A-Za-z0-9_]*)", diff_text, flags=re.M)
    removed = re.findall(r"^\-\s*(?:def|class|function)\s+([A-Za-z_][A-Za-z0-9_]*)", diff_text, flags=re.M)
    return {
        "added_symbols": sorted(set(added)),
        "removed_symbols": sorted(set(removed)),
        "count_added": len(set(added)),
        "count_removed": len(set(removed)),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
