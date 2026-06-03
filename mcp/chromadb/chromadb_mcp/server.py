from __future__ import annotations

import os
from typing import Any

import hashlib

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/chromadb.") from exc

try:
    import chromadb
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing ChromaDB dependency. Run uv sync in mcp/chromadb.") from exc

mcp = FastMCP("chromadb")
CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "127.0.0.1")
CHROMADB_PORT = int(os.environ.get("CHROMADB_PORT", "8100"))
CHROMADB_SSL = os.environ.get("CHROMADB_SSL", "false").lower() in {"true", "1", "yes"}


def _get_client() -> Any:
    return chromadb.HttpClient(
        host=CHROMADB_HOST,
        port=CHROMADB_PORT,
        ssl=CHROMADB_SSL,
    )


@mcp.tool()
def status() -> dict[str, Any]:
    """Check ChromaDB connection and list collections."""
    try:
        client = _get_client()
        client.heartbeat()
        collections = []
        for coll in client.list_collections():
            if isinstance(coll, str):
                name = coll
                count = client.get_collection(name).count()
            else:
                name = coll.name
                count = coll.count()
            collections.append({"name": name, "count": count})
        return {
            "service": "chromadb",
            "host": CHROMADB_HOST,
            "port": CHROMADB_PORT,
            "ssl": CHROMADB_SSL,
            "connected": True,
            "collections": collections,
        }
    except Exception as exc:
        return {
            "service": "chromadb",
            "host": CHROMADB_HOST,
            "port": CHROMADB_PORT,
            "ssl": CHROMADB_SSL,
            "connected": False,
            "error": str(exc),
        }


@mcp.tool()
def create_collection(name: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create or get a named collection. If it already exists, return it."""
    client = _get_client()
    collection = client.get_or_create_collection(name=name, metadata=metadata)
    return {
        "name": collection.name,
        "id": getattr(collection, "id", None),
        "count": collection.count(),
    }


@mcp.tool()
def add_documents(
    collection_name: str,
    documents: list[str],
    ids: list[str],
    metadatas: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Add documents with auto-generated embeddings to a collection."""
    client = _get_client()
    collection = client.get_collection(name=collection_name)
    collection.add(documents=documents, ids=ids, metadatas=metadatas)
    return {
        "collection": collection_name,
        "added": len(documents),
    }


@mcp.tool()
def query_collection(
    collection_name: str,
    query_texts: list[str],
    n_results: int = 10,
    where: dict[str, Any] | None = None,
    where_document: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Query documents by text similarity."""
    client = _get_client()
    collection = client.get_collection(name=collection_name)
    results = collection.query(
        query_texts=query_texts,
        n_results=n_results,
        where=where,
        where_document=where_document,
    )
    return {
        "collection": collection_name,
        "query_texts": query_texts,
        "results": results,
    }


@mcp.tool()
def delete_documents(
    collection_name: str,
    ids: list[str] | None = None,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Delete documents by ID or filter."""
    client = _get_client()
    collection = client.get_collection(name=collection_name)
    if ids:
        existing = collection.get(ids=ids, include=[])
        count = len(existing["ids"])
        collection.delete(ids=ids)
        return {
            "collection": collection_name,
            "deleted": count,
        }
    if where:
        existing = collection.get(where=where, include=[])
        count = len(existing["ids"])
        collection.delete(where=where)
        return {
            "collection": collection_name,
            "deleted": count,
        }
    return {
        "collection": collection_name,
        "deleted": 0,
        "error": "Either ids or where must be provided.",
    }


@mcp.tool()
def list_collections() -> dict[str, Any]:
    """List all collections with their names and counts."""
    client = _get_client()
    collections = []
    for coll in client.list_collections():
        if isinstance(coll, str):
            name = coll
            count = client.get_collection(name).count()
        else:
            name = coll.name
            count = coll.count()
        collections.append({"name": name, "count": count})
    return {
        "collections": collections,
    }


@mcp.tool()
def get_collection_info(collection_name: str) -> dict[str, Any]:
    """Get collection name, id, count, and sample of first 5 documents."""
    client = _get_client()
    collection = client.get_collection(name=collection_name)
    count = collection.count()
    sample = collection.get(limit=5)
    return {
        "name": collection.name,
        "id": getattr(collection, "id", None),
        "count": count,
        "sample": sample,
    }


@mcp.tool()
def semantic_cache_store(
    query: str,
    response: str,
    source: str = "manual",
    goal_hash: str = "",
    ttl_seconds: int = 3600,
) -> dict[str, Any]:
    """Store a prompt-response pair in the semantic cache for future reuse."""
    client = _get_client()
    collection = client.get_or_create_collection(name="semantic_cache")
    import hashlib
    doc_id = f"cache_{hashlib.sha256(query.encode()).hexdigest()[:16]}"
    metadata = {
        "response": response[:1000],  # Truncate long responses
        "source": source,
        "ttl_seconds": str(ttl_seconds),
    }
    if goal_hash:
        metadata["goal_hash"] = goal_hash
    collection.add(
        documents=[query],
        ids=[doc_id],
        metadatas=[metadata],
    )
    return {
        "collection": "semantic_cache",
        "stored": True,
        "doc_id": doc_id,
        "query_length": len(query),
    }


@mcp.tool()
def semantic_cache_query(
    query: str,
    n_results: int = 3,
    similarity_threshold: float = 0.92,
) -> dict[str, Any]:
    """Query the semantic cache for similar prompts. Returns results above the similarity threshold."""
    client = _get_client()
    try:
        collection = client.get_collection(name="semantic_cache")
    except Exception:
        return {
            "collection": "semantic_cache",
            "hits": [],
            "count": 0,
            "message": "semantic_cache collection does not exist yet",
        }
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    hits = []
    if results and results.get("distances") and results["distances"][0]:
        for i, distance in enumerate(results["distances"][0]):
            similarity = 1.0 - distance
            if similarity >= similarity_threshold:
                hit = {
                    "id": results["ids"][0][i] if results["ids"] else "",
                    "query": results["documents"][0][i] if results["documents"] else "",
                    "response": results["metadatas"][0][i].get("response", "") if results["metadatas"] and results["metadatas"][0] else "",
                    "source": results["metadatas"][0][i].get("source", "") if results["metadatas"] and results["metadatas"][0] else "",
                    "similarity": round(similarity, 4),
                }
                hits.append(hit)
    return {
        "collection": "semantic_cache",
        "hits": hits,
        "count": len(hits),
        "query": query,
    }


@mcp.tool()
def semantic_cache_invalidate(
    source: str | None = None,
    goal_hash: str | None = None,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Invalidate semantic cache entries by source, goal_hash, or source_file."""
    client = _get_client()
    try:
        collection = client.get_collection(name="semantic_cache")
    except Exception:
        return {
            "collection": "semantic_cache",
            "deleted": 0,
            "message": "semantic_cache collection does not exist",
        }
    where = {}
    if source:
        where["source"] = source
    if goal_hash:
        where["goal_hash"] = goal_hash
    if source_file:
        where["source_file"] = source_file
    if not where:
        return {
            "collection": "semantic_cache",
            "deleted": 0,
            "error": "At least one filter (source, goal_hash, or source_file) must be provided.",
        }
    existing = collection.get(where=where, include=[])
    count = len(existing["ids"])
    collection.delete(where=where)
    return {
        "collection": "semantic_cache",
        "deleted": count,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
