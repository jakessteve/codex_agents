# Prompt Caching Rules

## Purpose
Maximize provider-side prompt cache hit rates by enforcing stable prefix discipline and strategic content ordering in all agent sessions.

## Hard Rules

1. **Stable Prefix First**: Every agent session MUST start with the content of `codex-home/system_prefix.md` (or the configured `prefix_file`). This prefix contains identity, core rules, model policy, loop policy, safety, and cache discipline — all of which are session-stable.

2. **Dynamic Content Last**: Task-specific context (current task, recent trajectory, tool results, file contents) MUST be appended AFTER the stable prefix. Never interleave dynamic content into the prefix section.

3. **Never Modify the Prefix Mid-Session**: Reordering, editing, or appending to the system prefix within a session invalidates the provider-side cache. If the prefix needs updating, start a new session.

4. **Cache Boundary Markers**: At each major pipeline stage transition, emit a cache boundary marker:
   ```yaml
   cache_boundary:
     stage: <stage_name>
     prefix_stable: true
     dynamic_content_start: true
   ```

5. **Prefer Indexed Retrieval Over Re-reading**: Use `codex_knowledge_project_context`, `codex_knowledge_memory_query`, `codex_knowledge_graph_query`, and `codex_knowledge_project_context` instead of re-reading files that were already read in the current session.

6. **Semantic Cache Before Broad Search**: Before doing a broad file search or web search, check the semantic cache via `codex_knowledge_memory_query` with query prefix `semantic_cache:`. If a similar query was answered before (similarity ≥ 0.92), reuse the cached result.

7. **Plan Caching**: When composing a PyRAG program via `codex_knowledge_memory_store`, check if a similar goal has been composed before. Cache composed plans by goal hash in `codex_knowledge_memory_store` with key `pyrag_plan:<goal_hash>`.

8. **Budget Allocation for Cacheable Content**: Of the total context budget:
   - 40% should be cacheable prefix (system rules, tool definitions, project context)
   - 30% should be task-specific dynamic content
   - 30% should be reserved for tool results and output

9. **Cache Hit Rate KPI**: Track cache hit rate as a KPI. Record via `codex_knowledge_memory_store` with key `kpi:cache_hit_rate:<date>` and value as JSON:
   ```json
   {
     "value": <percentage>,
     "unit": "percent",
     "source": "prompt_caching",
     "context": "provider-side cache hit rate for the session"
   }
   ```

10. **Invalidate on File Change**: When a file is modified, invalidate any semantic cache entries that reference that file. Use `codex_knowledge_memory_store` with key `semantic_cache:<file_path>` to update or invalidate the entry.

## Integration Points

- **Sequential Pipeline**: Each stage starts with a cache boundary marker
- **Dreaming Cron**: Analyzes cache hit rates and evolves prompts for better cacheability
- **Meta-Evolution Agent**: Includes cache efficiency as an evolution KPI
- **Token Health Worker**: Reports cache hit rate alongside token budget usage

## Output Format

When reporting cache status:
```yaml
cache_status:
  prefix_stable: true|false
  cache_hit_rate: <percentage>
  semantic_cache_hits: <count>
  semantic_cache_misses: <count>
  plan_cache_hits: <count>
  budget_cacheable_percent: <percentage>
```
