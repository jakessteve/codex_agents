# ChromaDB MCP Service

status: operational
owner: pm
summary: Vector store MCP service for semantic search over wiki content and project knowledge. Connects to ChromaDB running in Docker on port 8100.

## Tools

- `status` — Check ChromaDB connection and list collections
- `create_collection` — Create or get a named collection
- `add_documents` — Add documents with auto-generated embeddings to a collection
- `query_collection` — Query documents by text similarity
- `delete_documents` — Delete documents by ID from a collection
- `list_collections` — List all collections with counts
- `get_collection_info` — Get collection metadata and document count

## Environment Variables

- `CHROMADB_HOST` — ChromaDB server host (default: `127.0.0.1`)
- `CHROMADB_PORT` — ChromaDB server port (default: `8100`)
- `CHROMADB_SSL` — Use HTTPS (default: `false`)
