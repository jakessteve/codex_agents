---
name: monotonic-progress
description: Ensure progress is measurable and non-regressing. If progress stalls or regresses, the task must be re-evaluated.
---

# Monotonic Progress

## Purpose
Ensure that every action in a task moves the project forward. If progress stalls or regresses, re-evaluate the approach rather than repeating failed actions.

## Hard Rules

1. **Progress Must Be Measurable**: Every task contract must define measurable acceptance criteria:
   ```yaml
   acceptance_criteria:
     - criterion: <description>
       measurement: <how to verify>
       baseline: <current state>
       target: <desired state>
   ```

2. **No Regression**: After each action, verify that:
   - Existing tests still pass
   - No new type errors introduced (LSP diagnostics clean)
   - No previously working functionality broken
   - Use `treesitter_changed_symbols` to verify changes are minimal

3. **Progress Check Every 5 Actions**: After every 5 tool calls in a task:
   - Ask: "Has the task actually progressed toward the acceptance criteria?"
   - If no measurable progress, reframe the approach
   - Use `codex_knowledge_handoff_checkpoint` to save state before reframing

4. **Stall Detection**: If the same approach is attempted 3 times without progress:
   - STOP and reframe (see `anti_loop` guardrail)
   - Consider alternative approaches
   - Escalate to PM if no alternative exists

5. **Metric Tracking**: Record progress metrics after each stage:
   ```yaml
   progress:
     stage: <stage_name>
     criteria_met: <count>/<total>
     tests_passing: <count>
     type_errors: <count>
     scope_drift_percent: <percentage>
     action: <continue|reframe|escalate>
   ```

## Mechanisms

- `minimalist_review_change` — verify changes are minimal and non-regressing
- `treesitter_changed_symbols` — verify symbol changes are intentional
- `codex_knowledge_handoff_checkpoint` — save state before reframing
- `planner_review_task_contract` — validate scope hasn't drifted
- `trace_export_record_trace` — record progress metrics

## Enforcement

- Builder agents report progress after every 5 actions
- Oracle checks progress metrics during review
- PM re-evaluates stalled tasks
- Evolution agent classifies repeated failures via `evolution_classify_repetition`
