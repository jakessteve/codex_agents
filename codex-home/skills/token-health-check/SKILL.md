---
name: token-health-check
description: Measure context load, use efficient retrieval, and checkpoint when context pressure rises. Mandatory check at each pipeline stage.
---

# Token Health Check

## Purpose
Monitor context window usage and take action before overflow degrades reasoning quality.

## When to Check
- Before starting any task (baseline measurement)
- After every 5 tool calls (progressive monitoring)
- Before Oracle review (pre-review check)
- When context "feels heavy" (subjective check)

## Steps

### 1. Measure Context Load
- Estimate current context usage as a percentage of allocated budget
- Compare against the budget per `context_budget/policy.md`

### 2. Use Efficient Retrieval
- Replace broad file reads with targeted queries:
  - `codex_knowledge_project_context` instead of reading entire docs
  - `codex_knowledge_memory_query` instead of re-reading history
  - `codex_knowledge_graph_query` instead of searching all files
  - `codex_knowledge_project_context` for multi-perspective queries

### 3. Take Action Based on Load

| Load Level | Action |
|-----------|--------|
| 0-60% | Continue normally |
| 60-80% | Prefer indexed retrieval, avoid broad reads |
| 80-95% | Checkpoint and compact |
| 95%+ | Hard stop, checkpoint and restart |

### 4. Checkpoint Procedure
- Use `codex_knowledge_handoff_checkpoint` to save state
- Summarize key context into memory via `codex_knowledge_memory_store`
- Let Codex auto-compaction handle the rest

### 5. Output Format
```yaml
token_health:
  budget_allocated: <tokens>
  budget_used: <tokens>
  percent_used: <percentage>
  action: <continue|prefer_indexed_retrieval|compact|checkpoint_and_restart>
  checkpoint_ref: <name if saved>
```
