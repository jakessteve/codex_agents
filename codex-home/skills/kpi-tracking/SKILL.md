---
name: kpi-tracking
description: Track and query system KPIs including hallucination rate, scope drift rate, minimalism score, and token efficiency. Use when reviewing system health or evolution metrics.
---

# KPI Tracking Skill

## Purpose
Provide a structured way to record, query, and trend system KPIs over time.

## KPI Definitions

| KPI | Source | Measurement |
|-----|--------|-------------|
| hallucination_rate | hallucination_auditor findings | % of claims that are contradicted |
| scope_drift_rate | drift-checker reports | % of tasks that exceed scope budget |
| minimalism_score | minimalist_review_change | Average diff efficiency (added/removed ratio) |
| token_efficiency | codex_knowledge summaries | Tokens per completed task |
| cache_hit_rate | semantic_cache queries | % of queries that hit the semantic cache |
| graph_first_rate | explore reports | % of exploration tasks that used CodeGraph before fallback reads |
| grep_fallback_rate | explore reports | % of exploration tasks that required broad or targeted grep fallback |
| harness_activation_rate | harness activation records | % of medium/epic tasks with activation before implementation |
| harness_adherence_score | final review | % of active harness checks satisfied |
| tool_output_tokens | codex_knowledge summaries | Estimated tool-response tokens per task |
| output_compression_savings | final response/review summaries | Estimated tokens saved by concise output contracts |

## Recording KPIs

Use `codex_knowledge_memory_store` with key format `kpi:<name>:<date>` and value as JSON:
```json
{
  "value": <number>,
  "unit": "<unit>",
  "source": "<auditor|drift_checker|minimalist|trace>",
  "context": "<what was being measured>"
}
```

Use `codex_knowledge_knowledge_capture` with key `kpi_snapshot` to store periodic snapshots.

## Querying KPIs

Use `codex_knowledge_memory_query` with query `kpi` to retrieve all KPI entries.

Use `codex_knowledge_graph_query` with term `kpi_trend` to find trend relationships.

## Trend Analysis

When reviewing KPIs:
1. Retrieve last 7 entries for each KPI
2. Calculate trend direction (improving, stable, degrading)
3. Flag any metric that changed >20% in a single step
4. Correlate changes with codex_knowledge_knowledge_capture entries
5. Report to meta_evolution agent if degradation detected

## Integration Points
- After each hallucination_auditor run → record hallucination_rate
- After each drift-checker run → record scope_drift_rate
- After each minimalist_review_change → record minimalism_score
- After each session → record token_efficiency from codex_knowledge
- After each SOL Explore phase → record graph_first_rate and grep_fallback_rate
- After each Harness Activation gate → record harness_activation_rate
- After each Final Review gate → record harness_adherence_score
- After each trace summary → record tool_output_tokens and output_compression_savings when available

## Cache Hit Rate KPI

### Recording
Use `codex_knowledge_memory_store` with key format `kpi:cache_hit_rate:<date>` and value as JSON:
```json
{
  "value": <percentage>,
  "unit": "percent",
  "source": "semantic_cache",
  "context": "provider-side and semantic cache hit rate for the session"
}
```

### Calculation
```
cache_hit_rate = (semantic_cache_hits + provider_prefix_hits) / total_queries * 100
```

### Thresholds
- ≥ 80%: Excellent — most queries are served from cache
- 60-80%: Good — cache is working but could be improved
- 40-60%: Fair — consider restructuring prompts for better cacheability
- < 40%: Poor — investigate cache-busting patterns and fix them

### Integration with Dreaming
- Dreaming cron analyzes cache hit rate trends
- If cache_hit_rate drops below 60%, dreaming proposes prompt restructuring
- If cache_hit_rate drops below 40%, dreaming proposes system prefix optimization
