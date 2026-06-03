# Token Efficiency Rules

## Purpose
Minimize token usage across all agent interactions while maximizing information density and cache hit rates.

## Hard Rules

1. **Prefer Summaries Over Raw Logs**: Never include raw command output, full file contents, or verbose logs in the active context. Summarize first, include details only when explicitly needed.

2. **Prefer Targeted Reads Over Broad Scans**: Use `codex_knowledge_project_context`, `codex_knowledge_memory_query`, and `codex_knowledge_graph_query` instead of `grep` or `read` on entire directories.

3. **Prefer Compact Contracts Over Free-Form Notes**: All inter-agent communication must use YAML or Markdown contracts, not prose.

4. **Cache-Friendly Prompt Construction**: Structure prompts with stable prefixes first, dynamic content last. See `prompt_caching_rules.md` for details.

5. **Semantic Cache Before Search**: Before broad searches, check `chromadb_mcp_query_collection` with collection `semantic_cache` for similar queries (threshold ≥ 0.92).

6. **Plan Caching**: Cache composed PyRAG programs by goal hash. Reuse cached plans when goals are semantically similar.

7. **Budget Awareness**: Track token usage per `context_budget/policy.md`. At 80% budget, trigger compaction. At 95%, hard stop.

8. **Compact Output**: When returning results, prefer structured YAML or concise Markdown over prose. Use tables over lists. Use abbreviations defined in the system prefix.

9. **CodeGraph Before Grep**: During SOL Explore, call `codegraph_*` facade tools before broad `grep`/`rg` or file reads. Fallback reads must include a reason.

10. **No Forced Compression For User Teaching**: Concise output is the default for reviews and contracts, but user-facing explanations may be fuller when nuance prevents mistakes.

## Output Format

When reporting token efficiency:
```yaml
token_efficiency:
  budget_allocated: <tokens>
  budget_used: <tokens>
  cache_hit_rate: <percentage>
  semantic_cache_hits: <count>
  plan_cache_hits: <count>
  graph_first_rate: <percentage>
  grep_fallback_rate: <percentage>
  tool_output_tokens: <number>
  output_compression_savings: <number>
  action: <continue|compact|checkpoint>
```
