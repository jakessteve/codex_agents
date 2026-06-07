---
name: anti-context-overflow
description: Prevent context window overflow by enforcing budget limits, preferring indexed retrieval over broad scanning, and triggering compaction when thresholds are exceeded.
---

# Anti Context Overflow

## Purpose
Prevent the agent from exceeding its context window budget, which causes degraded reasoning, hallucinations, and lost instructions.

## Hard Rules

1. **Budget Thresholds**: Before any task, allocate context budget per `context_budget/policy.md`:
   - Atomic tasks: 8,000 tokens max
   - Medium tasks: 20,000 tokens max
   - Epic tasks: 50,000 tokens max

2. **Retrieval Before Reading**: Always use indexed retrieval tools before broad file scanning:
   - Use `codex_knowledge_project_context` instead of reading entire docs
   - Use `codex_knowledge_memory_query` instead of re-reading conversation history
   - Use `codex_knowledge_graph_query` instead of searching all files
    - Use `codex_knowledge_project_context` for multi-perspective queries

3. **80% Compaction Trigger**: When context reaches 80% of allocated budget:
   - Call `codex_knowledge_handoff_checkpoint` to save state
   - Trigger compaction (Codex auto-compaction handles this if `compaction.auto: true`)
   - Summarize key context into memory before compacting

4. **95% Hard Stop**: When context reaches 95% of allocated budget:
   - STOP all new tool calls
   - Checkpoint immediately via `codex_knowledge_handoff_checkpoint`
   - Compact and restart from the checkpoint
   - Do NOT attempt to continue — degraded context produces worse results than a fresh start

5. **No Broad Re-reading**: Never re-read files that have already been read in the current session. Use memory and graph queries instead.

## Mechanisms

- **Codex compaction**: Configured with `compaction.auto: true, prune: true, reserved: 10000`
- **token-health-worker skill**: Check budget usage at each pipeline stage
- **context_budget/policy.md**: Defines budget allocation per task complexity
- **codex_knowledge_handoff_checkpoint**: Preserves state across compaction events

## Enforcement

- PM checks budget at intake (Stage 1 of sequential pipeline)
- Implementation agent monitors budget during execution (Stage 2)
- Oracle checks budget before review (Stage 3)
- Verification checks budget before completion (Stage 4)
- If budget exceeded at any stage, the stage must checkpoint and compact before continuing

## Output Format

When reporting context status:
```yaml
context_status:
  budget_allocated: <tokens>
  budget_used: <tokens>
  budget_remaining: <tokens>
  percent_used: <percentage>
  action: <continue|compact|checkpoint_and_restart>
  checkpoint_ref: <handoff checkpoint name if saved>
```
