from __future__ import annotations

from pathlib import Path
from typing import Any


class VectorMemory:
    """Local dynamic memory layer using Chroma with guarded availability."""

    def __init__(self, persist_dir: Path) -> None:
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None

    def _ensure(self) -> bool:
        if self._collection is not None:
            return True
        try:
            import chromadb  # type: ignore
        except Exception:
            return False

        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._collection = self._client.get_or_create_collection("memories")
        return True

    def add(self, item_id: str, text: str, metadata: dict[str, Any] | None = None) -> bool:
        if not self._ensure():
            return False
        assert self._collection is not None
        self._collection.upsert(ids=[item_id], documents=[text], metadatas=[metadata or {}])
        return True

    def query(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self._ensure():
            return []
        assert self._collection is not None
        res = self._collection.query(query_texts=[text], n_results=limit)
        docs = res.get("documents", [[]])[0]
        ids = res.get("ids", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        out: list[dict[str, Any]] = []
        for i, doc in enumerate(docs):
            out.append({"id": ids[i] if i < len(ids) else "", "document": doc, "metadata": metas[i] if i < len(metas) else {}})
        return out
