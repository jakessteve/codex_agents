from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Missing MCP runtime dependency. Install with: uv sync --project runtime/codex_knowledge"
    ) from exc

from .graph_layer import GraphLayer
from .registry import REGISTRY
from .vector_memory import VectorMemory
from .workflows import ENGINE

mcp = FastMCP("codex_knowledge")


def _project_layers(slug: str):
    pp = REGISTRY.resolve(slug)
    if not pp:
        return None, None, None
    vector = VectorMemory(pp.data_root / "vector")
    graph = GraphLayer(pp.data_root / "graph")
    return pp, vector, graph


def _document_category(relative_path: str) -> str:
    if relative_path.startswith("sot/"):
        return "sot"
    if relative_path.startswith("plans/"):
        return "plans"
    if relative_path.startswith("wiki/"):
        return "wiki"
    if relative_path.startswith("raw/"):
        return "raw"
    if relative_path.startswith(".wiki/") or relative_path in {"index.md", "log.md"}:
        return "meta"
    return "other"


def _document_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("#"):
                return line.lstrip("#").strip() or path.stem
    except Exception:
        pass
    return path.stem


def _refresh_document_inventory(slug: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}

    rows: list[tuple[str, str, str, str, int]] = []
    for md in sorted(pp.vault_root.rglob("*.md")):
        rel = str(md.relative_to(pp.vault_root))
        rows.append(
            (
                slug,
                rel,
                _document_category(rel),
                _document_title(md),
                int(md.stat().st_mtime),
            )
        )

    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        conn.execute("DELETE FROM documents WHERE slug = ?", (slug,))
        conn.executemany(
            """
            INSERT INTO documents (slug, relative_path, category, title, file_mtime)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )

    return {"slug": slug, "indexed": len(rows), "refreshed": True}


def _ensure_document_inventory(slug: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}

    md_files = [p for p in pp.vault_root.rglob("*.md")]
    fs_count = len(md_files)
    fs_latest = max((int(p.stat().st_mtime) for p in md_files), default=0)

    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        row = conn.execute(
            """
            SELECT COUNT(*) AS count, COALESCE(MAX(file_mtime), 0) AS latest
            FROM documents
            WHERE slug = ?
            """,
            (slug,),
        ).fetchone()

    indexed_count = int(row["count"]) if row else 0
    indexed_latest = int(row["latest"]) if row else 0
    if indexed_count != fs_count or indexed_latest != fs_latest:
        return _refresh_document_inventory(slug)

    return {"slug": slug, "indexed": indexed_count, "refreshed": False}


def _settings_review_rows(slug: str, include_resolved: bool = False, limit: int = 10) -> list[dict[str, Any]]:
    query = """
        SELECT id, reason, event_count, created_at, resolved_at
        FROM settings_reviews
        WHERE slug = ?
    """
    params: list[Any] = [slug]
    if not include_resolved:
        query += " AND resolved_at IS NULL"
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        rows = conn.execute(query, tuple(params)).fetchall()
    return [dict(r) for r in rows]


def _text_score(query_lower: str, *parts: str) -> float:
    text = " ".join(part for part in parts if part).lower()
    if not text:
        return 0.0
    if text == query_lower:
        return 3.0
    score = 0.0
    if query_lower in text:
        score += 1.5
    for word in query_lower.split():
        if word and word in text:
            score += 0.3
    return score


def _rerank_hits(
    query: str,
    wiki_hits: list[dict[str, Any]],
    keyword_hits: list[dict[str, Any]],
    semantic_hits: list[dict[str, Any]],
    graph_hits: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    query_lower = query.lower()
    scored: list[dict[str, Any]] = []

    for hit in wiki_hits:
        score = 2.0 + _text_score(
            query_lower,
            hit.get("relative_path", ""),
            hit.get("title", ""),
            hit.get("excerpt", ""),
        )
        scored.append(
            {
                "source": "wiki",
                "score": round(score, 3),
                "label": hit.get("title") or hit.get("name") or hit.get("relative_path", ""),
                "path": hit.get("relative_path") or hit.get("path", ""),
                "detail": hit.get("excerpt", ""),
            }
        )

    for hit in keyword_hits:
        score = 3.0 + _text_score(query_lower, hit.get("key", ""), hit.get("value", ""))
        scored.append(
            {
                "source": "memory_keyword",
                "score": round(score, 3),
                "label": hit.get("key", ""),
                "path": hit.get("key", ""),
                "detail": hit.get("value", "")[:240],
            }
        )

    for hit in semantic_hits:
        score = 1.5 + _text_score(
            query_lower,
            str(hit.get("metadata", {}).get("key", "")),
            hit.get("document", ""),
        )
        scored.append(
            {
                "source": "memory_semantic",
                "score": round(score, 3),
                "label": str(hit.get("metadata", {}).get("key", "")),
                "path": str(hit.get("id", "")),
                "detail": hit.get("document", "")[:240],
            }
        )

    for hit in graph_hits:
        score = 2.2 + _text_score(
            query_lower,
            hit.get("src", ""),
            hit.get("rel", ""),
            hit.get("dst", ""),
            hit.get("payload", ""),
        )
        scored.append(
            {
                "source": "graph",
                "score": round(score, 3),
                "label": f"{hit.get('src', '')} -[{hit.get('rel', '')}]-> {hit.get('dst', '')}",
                "path": hit.get("src", ""),
                "detail": hit.get("payload", "")[:240],
            }
        )

    scored.sort(key=lambda item: (-item["score"], item["source"], item["label"]))
    return scored[:limit]


@mcp.tool()
def project_register(project_path: str, slug: str | None = None) -> dict[str, Any]:
    pp = REGISTRY.ensure_project(project_path, slug)
    inventory = _ensure_document_inventory(pp.slug)
    return {
        "slug": pp.slug,
        "data_root": str(pp.data_root),
        "vault_root": str(pp.vault_root),
        "document_count": inventory.get("indexed", 0),
    }


@mcp.tool()
def project_resolve(slug: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    return {"slug": pp.slug, "data_root": str(pp.data_root), "vault_root": str(pp.vault_root)}


@mcp.tool()
def project_index(slug: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}

    inventory = _ensure_document_inventory(slug)
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        docs = conn.execute(
            """
            SELECT relative_path, category, title, file_mtime
            FROM documents
            WHERE slug = ?
            ORDER BY category, relative_path
            """,
            (slug,),
        ).fetchall()
        checkpoints = conn.execute(
            """
            SELECT name, created_at
            FROM checkpoints
            WHERE slug = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (slug,),
        ).fetchall()
        handoffs = conn.execute(
            """
            SELECT name, created_at
            FROM handoffs
            WHERE slug = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (slug,),
        ).fetchall()
        memory_keys = conn.execute(
            """
            SELECT key, MAX(created_at) AS created_at, MAX(id) AS latest_id
            FROM memory
            WHERE slug = ?
            GROUP BY key
            ORDER BY latest_id DESC
            LIMIT 10
            """,
            (slug,),
        ).fetchall()

    key_docs: dict[str, list[dict[str, Any]]] = {
        "sot": [],
        "plans": [],
        "wiki": [],
        "raw": [],
        "meta": [],
        "other": [],
    }
    for row in docs:
        category = row["category"]
        if category not in key_docs:
            category = "other"
        if len(key_docs[category]) >= 6:
            continue
        key_docs[category].append(
            {
                "relative_path": row["relative_path"],
                "title": row["title"],
                "path": str((pp.vault_root / row["relative_path"]).resolve()),
            }
        )

    return {
        "slug": slug,
        "project": {
            "slug": pp.slug,
            "data_root": str(pp.data_root),
            "vault_root": str(pp.vault_root),
        },
        "index_stats": {
            "document_count": inventory.get("indexed", 0),
            "refreshed": inventory.get("refreshed", False),
        },
        "key_docs": key_docs,
        "recent_checkpoints": [dict(r) for r in checkpoints],
        "recent_handoffs": [dict(r) for r in handoffs],
        "recent_memory_keys": [dict(r) for r in memory_keys],
        "settings_reviews": _settings_review_rows(slug, include_resolved=False, limit=5),
    }


@mcp.tool()
def project_context(slug: str, query: str, limit: int = 3) -> dict[str, Any]:
    """Return a compact layered context bundle from wiki, memory, and graph stores."""
    index = project_index(slug)
    if index.get("error"):
        return index

    wiki = vault_search(slug, query, limit=limit)
    memory = memory_query(slug, query, limit=limit)
    graph = graph_query(slug, query, limit=limit)
    top_hits = _rerank_hits(
        query,
        wiki.get("hits", [])[:limit],
        memory.get("keyword_results", [])[:limit],
        memory.get("semantic_results", [])[:limit],
        graph.get("results", [])[:limit],
        limit=limit,
    )

    return {
        "slug": slug,
        "project": index["project"],
        "query": query,
        "index_summary": {
            "document_count": index["index_stats"]["document_count"],
            "recent_memory_keys": index.get("recent_memory_keys", [])[:limit],
            "settings_reviews": index.get("settings_reviews", [])[:limit],
        },
        "top_hits": top_hits,
        "wiki_hits": wiki.get("hits", [])[:limit],
        "memory_keyword_hits": memory.get("keyword_results", [])[:limit],
        "memory_semantic_hits": memory.get("semantic_results", [])[:limit],
        "graph_hits": graph.get("results", [])[:limit],
    }


@mcp.tool()
def vault_search(slug: str, query: str, limit: int = 20) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}

    _ensure_document_inventory(slug)
    query_like = f"%{query.lower()}%"
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        rows = conn.execute(
            """
            SELECT relative_path, category, title
            FROM documents
            WHERE slug = ?
              AND (
                LOWER(relative_path) LIKE ?
                OR LOWER(title) LIKE ?
                OR LOWER(category) LIKE ?
              )
            ORDER BY category, relative_path
            LIMIT ?
            """,
            (slug, query_like, query_like, query_like, limit),
        ).fetchall()

    inventory_hits = [
        {
            "relative_path": row["relative_path"],
            "path": str((pp.vault_root / row["relative_path"]).resolve()),
            "name": Path(row["relative_path"]).name,
            "title": row["title"],
            "category": row["category"],
        }
        for row in rows
    ]
    if inventory_hits:
        return {
            "slug": slug,
            "query": query,
            "count": len(inventory_hits),
            "search_mode": "inventory",
            "hits": inventory_hits,
        }

    hits: list[dict[str, Any]] = []
    query_lower = query.lower()
    for md in pp.vault_root.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        idx = text.lower().find(query_lower)
        if idx < 0:
            continue
        excerpt = text[max(0, idx - 80) : idx + len(query) + 120].replace("\n", " ").strip()
        rel = str(md.relative_to(pp.vault_root))
        hits.append(
            {
                "relative_path": rel,
                "path": str(md),
                "name": md.name,
                "title": _document_title(md),
                "category": _document_category(rel),
                "excerpt": excerpt,
            }
        )

    return {
        "slug": slug,
        "query": query,
        "count": len(hits),
        "search_mode": "full_scan",
        "hits": hits[:limit],
    }


@mcp.tool()
def vault_read(slug: str, relative_path: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    fp = (pp.vault_root / relative_path).resolve()
    if not str(fp).startswith(str(pp.vault_root.resolve())):
        return {"error": "invalid_path"}
    if not fp.exists():
        return {"error": "not_found", "path": str(fp)}
    return {"path": str(fp), "content": fp.read_text(encoding="utf-8")}


@mcp.tool()
def vault_write(slug: str, relative_path: str, content: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    fp = (pp.vault_root / relative_path).resolve()
    if not str(fp).startswith(str(pp.vault_root.resolve())):
        return {"error": "invalid_path"}
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    inventory = _refresh_document_inventory(slug)
    return {
        "path": str(fp),
        "bytes": len(content.encode("utf-8")),
        "document_count": inventory.get("indexed", 0),
    }


def _wiki_ingest_raw(slug: str, source_path: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    src = Path(source_path)
    if not src.exists() or not src.is_file():
        return {"error": "invalid_source", "source_path": source_path}
    dst = pp.vault_root / "raw" / "docs" / src.name
    dst.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
    log = pp.vault_root / "log.md"
    log.write_text(log.read_text(encoding="utf-8") + f"\n- ingest: {src.name}\n", encoding="utf-8")
    return {"slug": slug, "source": str(src), "target": str(dst)}


def _wiki_rebuild_raw(slug: str) -> dict[str, Any]:
    pp = REGISTRY.resolve(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    md_files = [p for p in pp.vault_root.rglob("*.md") if p.name not in {"index.md"}]
    lines = ["# Index", ""]
    for p in sorted(md_files):
        rel = p.relative_to(pp.vault_root)
        lines.append(f"- {rel}")
    (pp.vault_root / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"slug": slug, "indexed": len(md_files)}


@mcp.tool()
def wiki_ingest(slug: str, source_path: str) -> dict[str, Any]:
    """Ingest docs and run wiki rebuild in LangGraph-backed workflow path."""
    result = ENGINE.run_wiki_ingest(slug, source_path, _wiki_ingest_raw, _wiki_rebuild_raw)
    result["inventory"] = _refresh_document_inventory(slug)
    return result


@mcp.tool()
def wiki_rebuild(slug: str) -> dict[str, Any]:
    result = _wiki_rebuild_raw(slug)
    result["inventory"] = _refresh_document_inventory(slug)
    return result


@mcp.tool()
def memory_store(slug: str, key: str, value: str) -> dict[str, Any]:
    pp, vector, _graph = _project_layers(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}

    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        conn.execute("INSERT INTO memory (slug, key, value) VALUES (?, ?, ?)", (slug, key, value))

    item_id = hashlib.sha256(f"{slug}:{key}:{value}".encode("utf-8")).hexdigest()[:24]
    vector_ok = vector.add(item_id=item_id, text=value, metadata={"key": key, "slug": slug})

    return {"slug": slug, "key": key, "stored": True, "vector_indexed": vector_ok}


@mcp.tool()
def knowledge_capture(
    slug: str,
    key: str,
    value: str,
    entity_id: str = "",
    source_ref: str = "",
) -> dict[str, Any]:
    """Persist a lesson into memory and mirror a compact graph link for retrieval."""
    memory_result = memory_store(slug, key, value)
    if memory_result.get("error"):
        return memory_result

    target = entity_id or f"memory:{key}"
    graph_results = [
        graph_upsert(slug, f"project:{slug}", "HAS_MEMORY", target, key),
    ]
    if source_ref:
        graph_results.append(graph_upsert(slug, target, "SOURCE", source_ref, key))

    return {
        "slug": slug,
        "key": key,
        "stored": True,
        "vector_indexed": memory_result.get("vector_indexed", False),
        "graph_links": graph_results,
    }


@mcp.tool()
def orchestration_lesson(
    slug: str,
    category: str,
    summary: str,
    severity: str = "minor",
    source_ref: str = "",
) -> dict[str, Any]:
    if not REGISTRY.resolve(slug):
        return {"error": "project_not_found", "slug": slug}
    if severity not in {"minor", "major", "critical"}:
        return {"error": "invalid_severity", "severity": severity}

    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        cursor = conn.execute(
            """
            INSERT INTO orchestration_events (slug, category, severity, summary, source_ref)
            VALUES (?, ?, ?, ?, ?)
            """,
            (slug, category, severity, summary, source_ref),
        )
        event_id = int(cursor.lastrowid)
        counts = conn.execute(
            """
            SELECT
              SUM(CASE WHEN severity = 'critical' AND settings_review_id IS NULL THEN 1 ELSE 0 END) AS critical_open,
              SUM(CASE WHEN severity != 'critical' AND settings_review_id IS NULL THEN 1 ELSE 0 END) AS noncritical_open
            FROM orchestration_events
            WHERE slug = ?
            """,
            (slug,),
        ).fetchone()

        critical_open = int(counts["critical_open"] or 0)
        noncritical_open = int(counts["noncritical_open"] or 0)
        settings_review_required = critical_open >= 1 or noncritical_open >= 3
        settings_review: dict[str, Any] | None = None

        if settings_review_required:
            reason = (
                f"settings review required after orchestration lessons: "
                f"{critical_open} critical, {noncritical_open} noncritical open events"
            )
            cursor = conn.execute(
                """
                INSERT INTO settings_reviews (slug, reason, event_count)
                VALUES (?, ?, ?)
                """,
                (slug, reason, critical_open + noncritical_open),
            )
            review_id = int(cursor.lastrowid)
            conn.execute(
                """
                UPDATE orchestration_events
                SET settings_review_id = ?
                WHERE slug = ? AND settings_review_id IS NULL
                """,
                (review_id, slug),
            )
            settings_review = {
                "id": review_id,
                "reason": reason,
                "event_count": critical_open + noncritical_open,
            }

    capture = None
    if settings_review:
        capture = knowledge_capture(
            slug,
            key=f"settings-review:{settings_review['id']}",
            value=settings_review["reason"],
            entity_id=f"settings-review:{settings_review['id']}",
            source_ref=source_ref or f"orchestration:{category}",
        )

    return {
        "slug": slug,
        "event_id": event_id,
        "category": category,
        "severity": severity,
        "settings_review_required": settings_review is not None,
        "settings_review": settings_review,
        "capture": capture,
    }


@mcp.tool()
def settings_review_queue(slug: str, include_resolved: bool = False) -> dict[str, Any]:
    if not REGISTRY.resolve(slug):
        return {"error": "project_not_found", "slug": slug}
    return {
        "slug": slug,
        "include_resolved": include_resolved,
        "reviews": _settings_review_rows(slug, include_resolved=include_resolved, limit=25),
    }


@mcp.tool()
def memory_query(slug: str, query: str, limit: int = 20) -> dict[str, Any]:
    pp, vector, _graph = _project_layers(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}

    q = f"%{query}%"
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        rows = conn.execute(
            """
            SELECT key, value, created_at
            FROM memory
            WHERE slug = ? AND (key LIKE ? OR value LIKE ?)
            ORDER BY id DESC
            LIMIT ?
            """,
            (slug, q, q, limit),
        ).fetchall()

    semantic = vector.query(query, limit=limit)
    return {
        "slug": slug,
        "query": query,
        "keyword_results": [dict(r) for r in rows],
        "semantic_results": semantic,
    }


@mcp.tool()
def graph_upsert(slug: str, src: str, rel: str, dst: str, payload: str = "") -> dict[str, Any]:
    pp, _vector, graph = _project_layers(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    assert graph is not None
    graph.upsert(src=src, rel=rel, dst=dst, payload=payload)
    return {"slug": slug, "src": src, "rel": rel, "dst": dst, "upserted": True}


@mcp.tool()
def graph_query(slug: str, term: str, limit: int = 50) -> dict[str, Any]:
    pp, _vector, graph = _project_layers(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    assert graph is not None
    return {"slug": slug, "term": term, "results": graph.query(term, limit=limit)}


@mcp.tool()
def graph_neighbors(slug: str, entity_id: str, limit: int = 10) -> dict[str, Any]:
    pp, _vector, graph = _project_layers(slug)
    if not pp:
        return {"error": "project_not_found", "slug": slug}
    assert graph is not None
    return {"slug": slug, "entity_id": entity_id, "results": graph.neighbors(entity_id, limit=limit)}


@mcp.tool()
def checkpoint_save(slug: str, name: str, payload: str) -> dict[str, Any]:
    if not REGISTRY.resolve(slug):
        return {"error": "project_not_found", "slug": slug}
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        conn.execute(
            "INSERT INTO checkpoints (slug, name, payload) VALUES (?, ?, ?)",
            (slug, name, payload),
        )
    return {"slug": slug, "name": name, "saved": True}


@mcp.tool()
def checkpoint_restore(slug: str, name: str) -> dict[str, Any]:
    if not REGISTRY.resolve(slug):
        return {"error": "project_not_found", "slug": slug}
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        row = conn.execute(
            "SELECT payload, created_at FROM checkpoints WHERE slug = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (slug, name),
        ).fetchone()
    if not row:
        return {"error": "checkpoint_not_found", "slug": slug, "name": name}
    return {"slug": slug, "name": name, "payload": row["payload"], "created_at": row["created_at"]}


@mcp.tool()
def handoff_write(slug: str, name: str, payload: str) -> dict[str, Any]:
    if not REGISTRY.resolve(slug):
        return {"error": "project_not_found", "slug": slug}
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        conn.execute("INSERT INTO handoffs (slug, name, payload) VALUES (?, ?, ?)", (slug, name, payload))
    return {"slug": slug, "name": name, "saved": True}


@mcp.tool()
def handoff_checkpoint(slug: str, name: str, payload: str) -> dict[str, Any]:
    """Persist the same summary as both handoff and checkpoint for cheap resume paths."""
    handoff = handoff_write(slug, name, payload)
    if handoff.get("error"):
        return handoff
    checkpoint = checkpoint_save(slug, name, payload)
    return {
        "slug": slug,
        "name": name,
        "handoff_saved": handoff.get("saved", False),
        "checkpoint_saved": checkpoint.get("saved", False),
    }


@mcp.tool()
def handoff_read(slug: str, name: str) -> dict[str, Any]:
    if not REGISTRY.resolve(slug):
        return {"error": "project_not_found", "slug": slug}
    with REGISTRY._conn() as conn:  # type: ignore[attr-defined]
        row = conn.execute(
            "SELECT payload, created_at FROM handoffs WHERE slug = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (slug, name),
        ).fetchone()
    if not row:
        return {"error": "handoff_not_found", "slug": slug, "name": name}
    return {"slug": slug, "name": name, "payload": row["payload"], "created_at": row["created_at"]}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
