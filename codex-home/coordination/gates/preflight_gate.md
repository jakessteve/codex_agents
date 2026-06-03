# Preflight Gate

Run before starting any implementation. Checks readiness and prevents wasted effort.

## Preflight Checklist

### 1. Task Contract Exists
- [ ] Task contract created via `planner_review_task_contract`
- [ ] Scope, complexity, and topology defined
- [ ] Allowed files and required tests listed

### 2. Context Available
- [ ] Project registered in codex_knowledge
- [ ] Relevant context retrieved via `codex_knowledge_project_context`
- [ ] No stale data (check last update timestamp)

### 3. AOP Consistency Pre-check
- [ ] Run `cognition_codex_check_aop_consistency` with:
  - claims: stated requirements and constraints
  - relations: known dependencies
  - rules: project guardrails
- [ ] No critical conflicts detected
- [ ] If conflicts found, resolve before proceeding

### 4. Budget Available
- [ ] Context budget allocated per `context_budget/policy.md`
- [ ] Token health check passed

### 5. Tools Available
- [ ] Required MCP servers are running
- [ ] LSP servers are responsive
- [ ] No blocking issues

## Preflight Verdict

| Verdict | Condition |
|---------|-----------|
| GO | All checks pass |
| NO-GO | Critical conflicts, missing context, or budget exceeded |
| CONDITIONAL | Minor issues that can be resolved in-flight |

## Output Format
```yaml
preflight:
  task_ref: <reference>
  verdict: <GO|NO-GO|CONDITIONAL>
  checks:
    contract: <pass|fail>
    context: <pass|fail>
    aop_consistency: <pass|fail|conflicts>
    budget: <pass|fail>
    tools: <pass|fail>
  blockers: <list>
  warnings: <list>
```
