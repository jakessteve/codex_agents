from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class GraphLayer:
    """
    Local graph layer with Kuzu-first writes and SQLite fallback/query mirror.
    This keeps day-1 operability even if Kuzu runtime is unavailable.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.sqlite_path = self.root / "graph.sqlite"
        # Kuzu 0.11 expects a database file path, not a directory path.
        self.kuzu_path = self.root / "kuzu.db"
        self._init_sqlite()
        self._kuzu_conn = None
        self._init_kuzu()

    def _sql(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self) -> None:
        with self._sql() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    src TEXT NOT NULL,
                    rel TEXT NOT NULL,
                    dst TEXT NOT NULL,
                    payload TEXT
                )
                """
            )

    def _init_kuzu(self) -> None:
        try:
            import kuzu  # type: ignore
        except Exception:
            self._kuzu_conn = None
            return
        db = kuzu.Database(str(self.kuzu_path))
        conn = kuzu.Connection(db)
        try:
            conn.execute("CREATE NODE TABLE Entity(id STRING, PRIMARY KEY(id));")
        except Exception:
            pass
        try:
            conn.execute("CREATE REL TABLE Link(FROM Entity TO Entity, rel STRING, payload STRING);")
        except Exception:
            pass
        self._kuzu_conn = conn

    def upsert(self, src: str, rel: str, dst: str, payload: str = "") -> None:
        with self._sql() as conn:
            conn.execute("INSERT INTO edges (src, rel, dst, payload) VALUES (?, ?, ?, ?)", (src, rel, dst, payload))

        if self._kuzu_conn is not None:
            # Best-effort mirror into Kuzu. Keep simple and resilient.
            s_src = src.replace("'", "''")
            s_rel = rel.replace("'", "''")
            s_dst = dst.replace("'", "''")
            s_payload = payload.replace("'", "''")
            try:
                self._kuzu_conn.execute(f"MERGE (a:Entity {{id: '{s_src}'}})")
                self._kuzu_conn.execute(f"MERGE (b:Entity {{id: '{s_dst}'}})")
                self._kuzu_conn.execute(
                    f"MATCH (a:Entity {{id: '{s_src}'}}), (b:Entity {{id: '{s_dst}'}}) "
                    f"CREATE (a)-[:Link {{rel: '{s_rel}', payload: '{s_payload}'}}]->(b)"
                )
            except Exception:
                pass

    def query(self, term: str, limit: int = 50) -> list[dict[str, Any]]:
        q = f"%{term}%"
        with self._sql() as conn:
            rows = conn.execute(
                "SELECT src, rel, dst, payload FROM edges WHERE src LIKE ? OR rel LIKE ? OR dst LIKE ? OR payload LIKE ? ORDER BY id DESC LIMIT ?",
                (q, q, q, q, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def neighbors(self, entity_id: str, limit: int = 10) -> list[dict[str, Any]]:
        with self._sql() as conn:
            rows = conn.execute(
                """
                SELECT src, rel, dst, payload
                FROM edges
                WHERE src = ? OR dst = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (entity_id, entity_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]
