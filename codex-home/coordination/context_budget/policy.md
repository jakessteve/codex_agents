# Context Budget Policy

## Purpose
Manage token and context window usage across agent interactions to prevent overflow and ensure efficient context utilization.

## Budget Allocation

### Default Budgets (by task complexity)
| Complexity | Max Context Tokens | Max Turns | Max Tools |
|-----------|-------------------|-----------|-----------|
| Atomic | 8,000 | 5 | 10 |
| Medium | 20,000 | 15 | 30 |
| Epic | 50,000 | 30 | 60 |

### Budget Categories
1. **Retrieval Budget**: 30% - for codex_knowledge, graphrag, memory queries
2. **Reasoning Budget**: 40% - for planning, PyRAG, AOP checks
3. **Output Budget**: 30% - for code generation, documentation, reviews

## Monitoring
- Use `token-health-worker` skill to check budget usage
- Use `codex_knowledge_project_context` for efficient context retrieval (avoids broad scanning)
- Use `cognition_codex_parallel_multisearch` for multi-perspective queries in a single call

## Overflow Protocol
1. If context exceeds 80% of budget, trigger compaction
2. If context exceeds 95% of budget, force checkpoint and restart
3. Use `codex_knowledge_handoff_checkpoint` to preserve state across compaction

## Integration with Sequential Pipeline
- Each stage in the pipeline gets a proportional budget slice
- PM stage: 15% of total budget
- Implementation stage: 50% of total budget
- Oracle review stage: 20% of total budget
- Verification stage: 15% of total budget

## Cache Budget Allocation

Of the total context budget, allocate for cacheability:

| Category | % of Budget | Cacheable? | Notes |
|----------|-------------|------------|-------|
| System prefix (rules, tools, identity) | 40% | ✅ Yes | Stable across sessions |
| Task context (contract, files, trajectory) | 30% | ❌ No | Dynamic per task |
| Tool results and output | 30% | ⚠️ Partial | Some results are reusable |

### Cache Hit Rate Targets
- Provider-side prefix cache: ≥ 80% hit rate (system prompt + tools)
- Semantic cache (ChromaDB): ≥ 60% hit rate for similar queries
- Plan cache (PyRAG): ≥ 40% hit rate for recurring goal patterns

### Cache Boundary Protocol
At each pipeline stage transition, emit a cache boundary marker:
```yaml
cache_boundary:
  stage: <stage_name>
  prefix_stable: true
  dynamic_content_start: true
  budget_used: <tokens>
  budget_remaining: <tokens>
```

### Cache Invalidation Rules
1. When a file is modified, invalidate semantic cache entries referencing that file
2. When a PyRAG plan is updated, invalidate the old plan cache entry
3. When the system prefix is updated (new cache_version), all provider-side caches are invalidated
4. Semantic cache entries expire after TTL (default: 3600 seconds)
