---
name: codegraph-explorer
description: Use CodeGraph-first exploration through the shared codegraph MCP facade before broad grep/read.
---

# CodeGraph Explorer

## Purpose
Use the shared `codegraph` MCP facade before broad file reads. The facade keeps Codex native contracts stable while the implementation can evolve behind `mcp/codegraph`.

## Activation
- Start of every SOL Explore phase.
- Existing-code impact analysis.
- Before widening an edit surface.

## Protocol
1. Use `codegraph_symbol_lookup` for relevant names, routes, files, or concepts.
2. Use `codegraph_callers_callees` for caller/callee hints when a symbol is known.
3. Use `codegraph_impact_analysis` for affected files and candidate tests.
4. Use `codegraph_semantic_search` for structure-aware lexical retrieval.
5. Fall back to targeted `rg`/reads only when the facade misses or exact implementation detail is required.

## Report Shape

```yaml
codegraph_exploration:
  facade_queries:
    - tool: codegraph_symbol_lookup
      query: <symbol-or-topic>
      result_count: <number>
  fallback_reads:
    - path: <path>
      reason: graph_miss | detail_needed | validation
  impact:
    affected_files: [...]
    candidate_tests: [...]
  confidence: high | medium | low
```

## Guardrails
- Do not claim CodeGraph coverage without listing the queries used.
- Do not use broad reads when a facade query can answer the structural question.
- Record misses as evolution evidence when they block or slow the task.
