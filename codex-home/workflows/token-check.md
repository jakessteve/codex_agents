---
name: token-check
summary: Measure context load, use efficient retrieval, and checkpoint when context pressure rises.
---

# Token Check

## Purpose
Monitor and manage context window usage to prevent overflow and degraded reasoning.

## When to Run
- Before starting any task (baseline measurement)
- After every 5 tool calls (progressive monitoring)
- When context feels heavy (subjective check)
- Before Oracle review (pre-review check)

## Steps

### 1. Measure Context Load
- Estimate current context usage
- Compare against allocated budget per `context_budget/policy.md`
- Calculate percentage used

### 2. Use Efficient Retrieval
- Replace broad file reads with targeted queries:
  - Use `codex_knowledge_project_context` instead of reading entire docs
  - Use `codex_knowledge_memory_query` instead of re-reading conversation history
  - Use `codex_knowledge_graph_query` instead of searching all files
  - Use `codex_knowledge_project_context` for multi-perspective queries

### 3. Checkpoint When Pressure Rises
- At 80% budget: trigger compaction
  - Use `codex_knowledge_handoff_checkpoint` to save state
  - Summarize key context into memory
  - Let Codex auto-compaction handle the rest
- At 95% budget: hard stop
  - Checkpoint immediately
  - Restart from checkpoint
  - Do NOT attempt to continue with degraded context

### 4. Report Context Status
```yaml
token_check:
  budget_allocated: <tokens>
  budget_used: <tokens>
  percent_used: <percentage>
  action: <continue|compact|checkpoint_and_restart>
  checkpoint_ref: <name if saved>
  retrieval_optimizations: <list of efficient retrievals used>
```
