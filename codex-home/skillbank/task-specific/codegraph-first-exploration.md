```yaml
skillbank_entry:
  id: codex-agents-codegraph-first-exploration
  layer: task-specific
  status: active
  source_evidence:
    - facade-first CodeGraph upgrade
  activation_triggers:
    - SOL Explore phase
    - existing-code impact analysis
  adherence_checks:
    - codegraph_queries listed in exploration report
    - fallback_reads include reason
  last_reviewed: 2026-06-03
```

# CodeGraph-First Exploration

Use `codegraph_symbol_lookup`, `codegraph_callers_callees`, `codegraph_impact_analysis`, and `codegraph_semantic_search` before broad repo reads. Fall back to targeted reads only for misses or exact implementation detail.
