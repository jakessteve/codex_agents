---
name: semantic-cache
description: Store and query semantically similar prompts and responses in ChromaDB for cache hit optimization. Use before broad searches or repeated queries.
---

# Semantic Cache Skill

## Purpose
Reduce token usage and latency by caching prompt→response mappings in ChromaDB and reusing semantically similar results.

## When to Use
- Before making a broad file search or web search
- Before composing a new PyRAG program (check if a similar goal was composed before)
- Before running a costly tool call (check if a similar query was answered before)
- During dreaming cron to analyze cache hit rates

## Cache Operations

### Store a Cache Entry
```
chromadb_mcp_add_documents(
  collection_name="semantic_cache",
  documents=["<prompt or query text>"],
  ids=["cache_<hash>"],
  metadatas=[{
    "response": "<response summary>",
    "source": "<tool_name>",
    "timestamp": "<ISO timestamp>",
    "ttl_seconds": "3600",
    "goal_hash": "<hash if PyRAG plan>"
  }]
)
```

### Query the Cache
```
chromadb_mcp_query_collection(
  collection_name="semantic_cache",
  query_texts=["<current prompt or query>"],
  n_results=3,
  where={"source": "<optional_filter>"},
)
```

### Invalidate Cache Entries
```
chromadb_mcp_delete_documents(
  collection_name="semantic_cache",
  where={"source_file": "<modified_file_path>"}
)
```

## Cache Hit Criteria
- Similarity threshold: ≥ 0.92 (configurable in `config.toml` or `config.toml`)
- TTL: 3600 seconds (1 hour) by default
- If a cached entry is within TTL and above similarity threshold, reuse it

## Integration Points
- `auto_ingest.ts` plugin: Creates `semantic_cache` collection on startup
- `prompt_caching_rules.md`: Defines cache discipline rules
- `kpi_tracking` skill: Records `cache_hit_rate` KPI
- `dreaming_cron` workflow: Analyzes cache hit rates and evolves prompts

## Output Format
When reporting cache status:
```yaml
cache_status:
  collection: semantic_cache
  total_entries: <count>
  hit_rate: <percentage>
  last_query_similarity: <score>
  action: <use_cache|search_fresh>
```
