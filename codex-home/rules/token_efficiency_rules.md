# Token Efficiency Rules

## Purpose
Minimize token usage across all agent interactions while maximizing information density and cache hit rates.

## Hard Rules

1. **Prefer Summaries Over Raw Logs**: Never include raw command output, full file contents, or verbose logs in the active context. Summarize first, include details only when explicitly needed.

2. **Prefer Targeted Reads Over Broad Scans**: Use `codex_knowledge_project_context`, `codex_knowledge_memory_query`, and `codex_knowledge_graph_query` instead of `grep` or `read` on entire directories.

3. **Prefer Compact Contracts Over Free-Form Notes**: All inter-agent communication must use YAML or Markdown contracts, not prose.

4. **Cache-Friendly Prompt Construction**: Structure prompts with stable prefixes first, dynamic content last. See `prompt_caching_rules.md` for details.

5. **Semantic Cache Before Search**: Before broad searches, check `codex_knowledge_memory_query` with query prefix `semantic_cache:` for similar queries (threshold ≥ 0.92).

6. **Plan Caching**: Cache composed PyRAG programs by goal hash. Reuse cached plans when goals are semantically similar.

7. **Budget Awareness**: Track token usage per `context_budget/policy.md`. At 80% budget, trigger compaction. At 95%, hard stop.

8. **Compact Output**: When returning results, prefer structured YAML or concise Markdown over prose. Use tables over lists. Use abbreviations defined in the system prefix.

9. **CodeGraph Before Grep**: During SOL Explore, call `codegraph_*` facade tools before broad `grep`/`rg` or file reads. Fallback reads must include a reason.

10. **No Forced Compression For User Teaching**: Concise output is the default for reviews and contracts, but user-facing explanations may be fuller when nuance prevents mistakes.

11. **Never Glob From Home Root**: Always use targeted paths like project directories or `~/.config/`. Never glob from `~` or `/` which can scan Waydroid, `.local`, or other noise directories producing thousands of permission-denied errors.

12. **Use Context7 or API Endpoints Instead of Full Web Fetches**: Prefer `context7_resolve-library-id` + `context7_query-docs` for documentation queries. Use JSON API endpoints instead of fetching entire documentation pages.

13. **Targeted File Reads**: Use `read` with `offset` and `limit` parameters instead of reading entire files. Use `grep` to find specific lines first, then read only the relevant section.

14. **Delegate File Writes to Subagents Sparingly**: Only delegate file writes to subagents when the file is large or complex. For small targeted changes, write directly.

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
