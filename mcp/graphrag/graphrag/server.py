from __future__ import annotations

import json
import os
import socket
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/graphrag.") from exc

mcp = FastMCP("graphrag")
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "state" / "graph.sqlite"
FALKOR_HOST = os.environ.get("GRAPHRAG_FALKOR_HOST", "127.0.0.1")
FALKOR_PORT = int(os.environ.get("GRAPHRAG_FALKOR_PORT", "6379"))
FALKOR_GRAPH = os.environ.get("GRAPHRAG_FALKOR_GRAPH", "codex_graphrag")
FALKOR_TIMEOUT = float(os.environ.get("GRAPHRAG_FALKOR_TIMEOUT", "1.5"))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            relation TEXT NOT NULL,
            target TEXT NOT NULL,
            evidence TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            tags_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _encode_resp(parts: list[str]) -> bytes:
    chunks = [f"*{len(parts)}\r\n".encode("ascii")]
    for part in parts:
        data = part.encode("utf-8")
        chunks.append(f"${len(data)}\r\n".encode("ascii"))
        chunks.append(data + b"\r\n")
    return b"".join(chunks)


def _read_line(sock_file: Any) -> bytes:
    line = sock_file.readline()
    if not line:
        raise ConnectionError("FalkorDB closed the connection")
    return line.rstrip(b"\r\n")


def _read_resp(sock_file: Any) -> Any:
    prefix = sock_file.read(1)
    if not prefix:
        raise ConnectionError("FalkorDB returned an empty response")
    if prefix == b"+":
        return _read_line(sock_file).decode("utf-8", errors="replace")
    if prefix == b"-":
        raise RuntimeError(_read_line(sock_file).decode("utf-8", errors="replace"))
    if prefix == b":":
        return int(_read_line(sock_file))
    if prefix == b"$":
        length = int(_read_line(sock_file))
        if length == -1:
            return None
        data = sock_file.read(length)
        sock_file.read(2)
        return data.decode("utf-8", errors="replace")
    if prefix == b"*":
        length = int(_read_line(sock_file))
        if length == -1:
            return None
        return [_read_resp(sock_file) for _ in range(length)]
    raise RuntimeError(f"Unexpected FalkorDB RESP prefix: {prefix!r}")


def _falkor_command(parts: list[str]) -> Any:
    with socket.create_connection((FALKOR_HOST, FALKOR_PORT), timeout=FALKOR_TIMEOUT) as sock:
        sock.sendall(_encode_resp(parts))
        with sock.makefile("rb") as sock_file:
            return _read_resp(sock_file)


def _cypher_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _falkor_query(query: str, readonly: bool = False) -> Any:
    command = "GRAPH.RO_QUERY" if readonly else "GRAPH.QUERY"
    return _falkor_command([command, FALKOR_GRAPH, query])


def _falkor_available() -> bool:
    try:
        return _falkor_command(["PING"]) == "PONG"
    except Exception:
        return False


def _falkor_rows(response: Any) -> list[list[Any]]:
    if isinstance(response, list) and len(response) >= 2 and isinstance(response[1], list):
        return response[1]
    return []


def _falkor_count() -> int:
    rows = _falkor_rows(_falkor_query("MATCH (f:Fact) RETURN count(f)", readonly=True))
    if rows and rows[0]:
        return int(rows[0][0])
    return 0


def _fact_from_row(row: list[Any]) -> dict[str, Any]:
    keys = ["subject", "relation", "target", "evidence", "source", "tags_json", "created_at"]
    fact = dict(zip(keys, row, strict=False))
    fact["tags_json"] = fact.get("tags_json") or "[]"
    return fact


def _sqlite_rows(limit: int | None = None) -> list[dict[str, Any]]:
    suffix = " ORDER BY id ASC"
    params: tuple[Any, ...] = ()
    if limit is not None:
        suffix += " LIMIT ?"
        params = (limit,)
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT subject, relation, target, evidence, source, tags_json, created_at
            FROM facts
            """
            + suffix,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def _falkor_create_fact(row: dict[str, Any]) -> None:
    query = (
        "CREATE (:Fact {"
        f"subject: {_cypher_string(row['subject'])}, "
        f"relation: {_cypher_string(row['relation'])}, "
        f"target: {_cypher_string(row['target'])}, "
        f"evidence: {_cypher_string(row.get('evidence', ''))}, "
        f"source: {_cypher_string(row.get('source', 'manual'))}, "
        f"tags_json: {_cypher_string(row.get('tags_json', '[]'))}, "
        f"created_at: {_cypher_string(row.get('created_at', _now()))}"
        "})"
    )
    _falkor_query(query)


def _migrate_sqlite_to_falkor_if_empty() -> int:
    if _falkor_count() != 0:
        return 0
    rows = _sqlite_rows()
    for row in rows:
        _falkor_create_fact(row)
    return len(rows)


def _use_falkor() -> bool:
    if not _falkor_available():
        return False
    _migrate_sqlite_to_falkor_if_empty()
    return True


@mcp.tool()
def status() -> dict[str, Any]:
    """Return service and storage status."""
    if _falkor_available():
        migrated = _migrate_sqlite_to_falkor_if_empty()
        return {
            "service": "graphrag",
            "backend": "falkordb",
            "host": FALKOR_HOST,
            "port": FALKOR_PORT,
            "graph": FALKOR_GRAPH,
            "fact_count": _falkor_count(),
            "migrated_from_sqlite": migrated,
            "fallback_db_path": str(DB_PATH),
        }
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS count FROM facts").fetchone()["count"]
    return {
        "service": "graphrag",
        "backend": "sqlite_fallback",
        "db_path": str(DB_PATH),
        "fact_count": int(count),
        "preferred_backend": "falkordb",
    }


@mcp.tool()
def upsert_fact(
    subject: str,
    relation: str,
    target: str,
    evidence: str = "",
    source: str = "manual",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Store a graph fact for later lookup."""
    row = {
        "subject": subject.strip(),
        "relation": relation.strip(),
        "target": target.strip(),
        "evidence": evidence.strip(),
        "source": source.strip(),
        "tags_json": json.dumps(tags or [], ensure_ascii=True),
        "created_at": _now(),
    }
    if _use_falkor():
        _falkor_create_fact(row)
        return {"stored": True, "backend": "falkordb", "fact": row}
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO facts (subject, relation, target, evidence, source, tags_json, created_at)
            VALUES (:subject, :relation, :target, :evidence, :source, :tags_json, :created_at)
            """,
            row,
        )
        conn.commit()
    return {"stored": True, "backend": "sqlite_fallback", "fact": row}


@mcp.tool()
def neighbors(subject: str, limit: int = 20) -> dict[str, Any]:
    """Return direct neighbors for a subject."""
    if _use_falkor():
        query = (
            "MATCH (f:Fact) "
            f"WHERE toLower(f.subject) = toLower({_cypher_string(subject)}) "
            "RETURN f.subject, f.relation, f.target, f.evidence, f.source, f.tags_json, f.created_at "
            f"ORDER BY f.created_at DESC LIMIT {int(limit)}"
        )
        rows = [_fact_from_row(row) for row in _falkor_rows(_falkor_query(query, readonly=True))]
        return {"subject": subject, "backend": "falkordb", "neighbors": rows}
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT subject, relation, target, evidence, source, tags_json, created_at
            FROM facts
            WHERE lower(subject) = lower(?)
            ORDER BY id DESC
            LIMIT ?
            """,
            (subject, limit),
        ).fetchall()
    return {"subject": subject, "backend": "sqlite_fallback", "neighbors": [dict(row) for row in rows]}


@mcp.tool()
def query_graph(query: str, limit: int = 10) -> dict[str, Any]:
    """Search stored facts using a simple text match."""
    if _use_falkor():
        needle = _cypher_string(query.lower())
        cypher = (
            "MATCH (f:Fact) "
            "WHERE toLower(f.subject) CONTAINS " + needle + " "
            "OR toLower(f.relation) CONTAINS " + needle + " "
            "OR toLower(f.target) CONTAINS " + needle + " "
            "OR toLower(f.evidence) CONTAINS " + needle + " "
            "OR toLower(f.tags_json) CONTAINS " + needle + " "
            "RETURN f.subject, f.relation, f.target, f.evidence, f.source, f.tags_json, f.created_at "
            f"ORDER BY f.created_at DESC LIMIT {int(limit)}"
        )
        rows = [_fact_from_row(row) for row in _falkor_rows(_falkor_query(cypher, readonly=True))]
        return {"query": query, "backend": "falkordb", "hits": rows}
    needle = f"%{query.lower()}%"
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT subject, relation, target, evidence, source, tags_json, created_at
            FROM facts
            WHERE lower(subject) LIKE ?
               OR lower(relation) LIKE ?
               OR lower(target) LIKE ?
               OR lower(evidence) LIKE ?
               OR lower(tags_json) LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (needle, needle, needle, needle, needle, limit),
        ).fetchall()
    return {"query": query, "backend": "sqlite_fallback", "hits": [dict(row) for row in rows]}


if __name__ == "__main__":
    mcp.run(transport="stdio")
