# Scope Lock Gate

Alias of `revision_gate` with SOL scope-lock semantics.

## Purpose
Freeze the atomic task list after exploration. No new task may be added without an explicit scope change request.

## Gate Check
1. All atomic tasks have acceptance criteria.
2. Validation target is explicit.
3. Scope drift budget is recorded.
4. PM or user approval is recorded.
5. Open uncertainties are either resolved or represented as residual risk.

## Exit Criteria
- Task list is locked.
- Later scope changes re-open this gate.
