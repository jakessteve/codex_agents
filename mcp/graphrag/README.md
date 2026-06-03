# GraphRAG MCP

status: operational
owner: librarian
summary: Graph query and traceability service over project facts and FalkorDB.

## Backend

GraphRAG prefers FalkorDB at `127.0.0.1:6379` using graph `codex_graphrag`.
If FalkorDB is unavailable, it falls back to `graphrag/state/graph.sqlite`.
The first successful FalkorDB status/use migrates existing SQLite facts when the
FalkorDB graph is empty.

Optional environment overrides:

- `GRAPHRAG_FALKOR_HOST`
- `GRAPHRAG_FALKOR_PORT`
- `GRAPHRAG_FALKOR_GRAPH`
- `GRAPHRAG_FALKOR_TIMEOUT`
