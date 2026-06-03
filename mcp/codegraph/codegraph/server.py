from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/codegraph.") from exc

mcp = FastMCP("codegraph")

CODE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".kts",
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    "target",
}


def _root(root: str) -> Path:
    target = Path(root).expanduser().resolve()
    if not target.exists():
        raise ValueError(f"root_not_found: {target}")
    return target


def _iter_files(root: Path, limit: int = 2000) -> list[Path]:
    files: list[Path] = []
    if root.is_file():
        return [root] if root.suffix in CODE_SUFFIXES else []
    for path in root.rglob("*"):
        if len(files) >= limit:
            break
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in CODE_SUFFIXES:
            files.append(path)
    return sorted(files)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _symbol_kind_from_context(line: str, suffix: str) -> str:
    stripped = line.strip()
    if suffix == ".py":
        if stripped.startswith("class "):
            return "class"
        if stripped.startswith("def ") or stripped.startswith("async def "):
            return "function"
    if re.search(r"\b(class|interface|type|enum)\s+\w+", stripped):
        return "type"
    if re.search(r"\b(function|const|let|var)\s+\w+", stripped):
        return "function"
    if stripped.startswith("#"):
        return "heading"
    return "reference"


def _python_defs(path: Path, text: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            rows.append({"symbol": node.name, "kind": "class", "line": node.lineno, "path": str(path)})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rows.append({"symbol": node.name, "kind": "function", "line": node.lineno, "path": str(path)})
    return rows


def _regex_defs(path: Path, text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    patterns = [
        (r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\b", "function"),
        (r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)\b", "class"),
        (r"^\s*(?:export\s+)?(?:interface|type|enum)\s+([A-Za-z_$][\w$]*)\b", "type"),
        (r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", "binding"),
        (r"^\s*#+\s+(.+?)\s*$", "heading"),
    ]
    for pattern, kind in patterns:
        for match in re.finditer(pattern, text, flags=re.M):
            symbol = match.group(1).strip()
            if symbol:
                rows.append({"symbol": symbol, "kind": kind, "line": _line_at(text, match.start()), "path": str(path)})
    return rows


def _definitions(path: Path, text: str) -> list[dict[str, Any]]:
    if path.suffix == ".py":
        return _python_defs(path, text)
    return _regex_defs(path, text)


@mcp.tool()
def symbol_lookup(root: str, query: str, limit: int = 20) -> dict[str, Any]:
    """Find likely symbol definitions and references in a project."""
    try:
        base = _root(root)
    except ValueError as exc:
        return {"error": str(exc)}
    needle = query.lower().strip()
    if not needle:
        return {"error": "empty_query"}
    results: list[dict[str, Any]] = []
    for path in _iter_files(base):
        text = _read(path)
        for row in _definitions(path, text):
            symbol = str(row["symbol"])
            if needle in symbol.lower():
                row["match"] = "definition"
                results.append(row)
        if len(results) >= limit:
            continue
        for match in re.finditer(re.escape(query), text, flags=re.I):
            line = text.splitlines()[_line_at(text, match.start()) - 1]
            results.append(
                {
                    "symbol": query,
                    "kind": _symbol_kind_from_context(line, path.suffix),
                    "line": _line_at(text, match.start()),
                    "path": str(path),
                    "match": "reference",
                    "excerpt": line.strip()[:180],
                }
            )
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
    return {"root": str(base), "query": query, "count": len(results[:limit]), "results": results[:limit]}


@mcp.tool()
def callers_callees(root: str, symbol: str, limit: int = 40) -> dict[str, Any]:
    """Return local caller and callee hints for a symbol using source structure."""
    try:
        base = _root(root)
    except ValueError as exc:
        return {"error": str(exc)}
    if not symbol.strip():
        return {"error": "empty_symbol"}
    callers: list[dict[str, Any]] = []
    callees: Counter[str] = Counter()
    call_pattern = re.compile(rf"\b{re.escape(symbol)}\s*\(")
    callee_pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for path in _iter_files(base):
        text = _read(path)
        definitions = _definitions(path, text)
        definition_lines = {int(row["line"]): row for row in definitions}
        lines = text.splitlines()
        current = {"symbol": "<module>", "kind": "module", "line": 1, "path": str(path)}
        for index, line in enumerate(lines, start=1):
            if index in definition_lines:
                current = definition_lines[index]
            if call_pattern.search(line) and current.get("symbol") != symbol:
                callers.append(
                    {
                        "caller": current.get("symbol", "<module>"),
                        "caller_kind": current.get("kind", "unknown"),
                        "path": str(path),
                        "line": index,
                        "excerpt": line.strip()[:180],
                    }
                )
            if current.get("symbol") == symbol:
                for match in callee_pattern.finditer(line):
                    name = match.group(1)
                    if name != symbol:
                        callees[name] += 1
        if len(callers) >= limit:
            break
    return {
        "root": str(base),
        "symbol": symbol,
        "callers": callers[:limit],
        "callees": [{"symbol": name, "count": count} for name, count in callees.most_common(limit)],
    }


@mcp.tool()
def impact_analysis(root: str, changed_paths: list[str] | None = None, symbols: list[str] | None = None, limit: int = 60) -> dict[str, Any]:
    """Estimate files and tests affected by changed paths or symbols."""
    try:
        base = _root(root)
    except ValueError as exc:
        return {"error": str(exc)}
    changed_paths = changed_paths or []
    symbols = symbols or []
    affected: dict[str, dict[str, Any]] = {}
    tests: list[str] = []
    for rel in changed_paths:
        path = (base / rel).resolve() if not Path(rel).is_absolute() else Path(rel).resolve()
        if path.exists():
            affected[str(path)] = {"reason": "changed_path", "score": 3}
            stem = path.stem.lower()
            for candidate in _iter_files(base):
                name = candidate.name.lower()
                if "test" in name or "spec" in name:
                    if stem in name or any(part in str(candidate).lower() for part in path.parts[-3:]):
                        tests.append(str(candidate))
    for symbol in symbols:
        lookup = symbol_lookup(str(base), symbol, limit=limit)
        for row in lookup.get("results", []):
            path = row["path"]
            entry = affected.setdefault(path, {"reason": "symbol_reference", "score": 0})
            entry["score"] += 1
            entry["reason"] = "symbol_reference"
            if "test" in Path(path).name.lower() or "spec" in Path(path).name.lower():
                tests.append(path)
    ranked = sorted(
        [{"path": path, **meta} for path, meta in affected.items()],
        key=lambda item: (-int(item["score"]), item["path"]),
    )[:limit]
    return {"root": str(base), "changed_paths": changed_paths, "symbols": symbols, "affected_files": ranked, "candidate_tests": sorted(set(tests))[:limit]}


@mcp.tool()
def semantic_search(root: str, query: str, limit: int = 20) -> dict[str, Any]:
    """Run lightweight structure-aware lexical search as the facade fallback."""
    try:
        base = _root(root)
    except ValueError as exc:
        return {"error": str(exc)}
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9_.$/-]+", query) if len(term) > 1]
    if not terms:
        return {"error": "empty_query"}
    hits: list[dict[str, Any]] = []
    for path in _iter_files(base):
        text = _read(path)
        lower = text.lower()
        score = sum(lower.count(term) for term in terms)
        if score <= 0:
            continue
        lines = text.splitlines()
        excerpts: list[dict[str, Any]] = []
        for index, line in enumerate(lines, start=1):
            line_lower = line.lower()
            if any(term in line_lower for term in terms):
                excerpts.append({"line": index, "text": line.strip()[:180]})
            if len(excerpts) >= 3:
                break
        hits.append({"path": str(path), "score": score, "excerpts": excerpts})
    hits.sort(key=lambda item: (-int(item["score"]), item["path"]))
    return {"root": str(base), "query": query, "count": len(hits[:limit]), "results": hits[:limit]}


if __name__ == "__main__":
    mcp.run(transport="stdio")
