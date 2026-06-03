---
name: context-budget
description: Manage token and context window usage. Enforce budget limits, prefer indexed retrieval, and trigger compaction when thresholds are exceeded.
---

# Context Budget

## Purpose
Manage token and context window usage across agent interactions to prevent overflow and ensure efficient context utilization.

## Budget Thresholds

| Complexity | Max Context | Max Turns | Max Tools |
|-----------|------------|-----------|-----------|
| Atomic | 8,000 | 5 | 10 |
| Medium | 20,000 | 15 | 30 |
| Epic | 50,000 | 30 | 60 |

## Budget Allocation
- **Retrieval**: 30% — codex_knowledge, graphrag, memory queries
- **Reasoning**: 40% — planning, PyRAG, AOP checks
- **Output**: 30% — code generation, documentation, reviews

## Steps

### 1. Allocate Budget
- At task start, determine complexity (atomic/medium/epic)
- Allocate budget per the table above
- Record allocation in task contract

### 2. Monitor Usage
- Use `token-health-worker` skill to check budget usage
- After every 5 tool calls, estimate remaining budget
- Use `codex_knowledge_project_context` for efficient retrieval (avoids broad scanning)
- Use `cognition_codex_parallel_multisearch` for multi-perspective queries

### 3. Trigger Compaction at 80%
- When context reaches 80% of budget:
  - Call `codex_knowledge_handoff_checkpoint` to save state
  - Summarize key context into memory
  - Let Codex auto-compaction handle the rest

### 4. Hard Stop at 95%
- When context reaches 95% of budget:
  - STOP all new tool calls
  - Checkpoint immediately via `codex_knowledge_handoff_checkpoint`
  - Compact and restart from checkpoint

## Output Format
```yaml
context_status:
  budget_allocated: <tokens>
  budget_used: <tokens>
  budget_remaining: <tokens>
  percent_used: <percentage>
  action: <continue|compact|checkpoint_and_restart>
```
