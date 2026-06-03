---
name: scope-drift-control
description: Compare actual output against validated intent. Record drift and stop when the budget is exceeded.
---

# Scope Drift Control

## Purpose
Prevent scope creep by measuring actual output against the validated task contract and stopping when the drift budget is exceeded.

## Drift Budget
- Default: 5% of original scope
- Can be adjusted per task in the task contract
- Measured as: (actual files changed - planned files) / planned files × 100

## Steps

### 1. Establish Baseline
- At task start, record the planned scope:
  ```yaml
  scope_baseline:
    planned_files: <list of files to be changed>
    planned_features: <list of features to implement>
    planned_tests: <list of tests to add>
    drift_budget_percent: <5>
  ```

### 2. Monitor During Implementation
- After each significant change, compare actual vs. planned:
  - Use `minimalist_diff_budget` to compare file counts
  - Use `planner_review_task_contract` to validate scope
  - Track new files, new features, new dependencies

### 3. Calculate Drift
- Drift percentage = (actual scope - planned scope) / planned scope × 100
- Include: new files, new features, new dependencies, new tests
- Exclude: bug fixes within scope, refactoring within scope

### 4. Escalate When Budget Exceeded
- If drift > budget:
  - STOP implementation
  - Record the drift in `codex_knowledge_knowledge_capture`
  - Escalate to PM for re-scoping
  - Do NOT continue without PM approval

### 5. Output Format
```yaml
scope_drift:
  task_ref: <reference>
  planned_files: <count>
  actual_files: <count>
  planned_features: <count>
  actual_features: <count>
  drift_percent: <percentage>
  drift_budget_percent: <percentage>
  status: <within_budget|at_budget|over_budget>
  action: <continue|escalate>
```
