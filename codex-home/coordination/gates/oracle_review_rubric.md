# Oracle Review Rubric

The Oracle is the independent review gate. Every major phase must pass Oracle review before proceeding.

## Review Checklist

### 1. Correctness
- [ ] All acceptance criteria met
- [ ] No type errors (LSP diagnostics clean)
- [ ] No dead code or unreachable branches
- [ ] Edge cases handled

### 2. Scope Drift
- [ ] Implementation matches task contract scope
- [ ] No feature creep beyond original request
- [ ] Scope drift budget not exceeded (default: 5%)
- [ ] Use `planner_review_task_contract` to validate

### 3. Regression Risk
- [ ] Existing tests still pass
- [ ] No breaking API changes without migration
- [ ] Dependency changes are minimal and justified

### 4. Test Evidence
- [ ] Unit tests cover new logic
- [ ] Integration tests cover happy paths
- [ ] Edge case tests exist for critical paths

### 5. Document Alignment
- [ ] Code matches documentation
- [ ] Changelog updated if needed
- [ ] SOT (vault/wiki) updated if architectural change

### 6. AOP Consistency Gate (MANDATORY)
- [ ] Run `cognition_codex_check_aop_consistency` with all claims from the implementation
- [ ] Verify no logical contradictions in:
  - Design claims vs. implementation reality
  - Stated constraints vs. actual behavior
  - Inter-module contracts vs. actual interfaces
- [ ] If AOP check returns conflicts, they MUST be resolved before passing Oracle
- [ ] Record AOP check result in the review output

### 7. Minimalism Gate
- [ ] `minimalist_review_change` score is acceptable
- [ ] No unnecessary abstractions
- [ ] Diff is surgical (minimal added/removed lines)

## Oracle Verdict

| Verdict | Condition |
|---------|-----------|
| PASS | All checklist items pass, AOP clean |
| CONDITIONAL | Minor issues that can be fixed in-place |
| FAIL | Scope drift, AOP conflicts, or regression detected |

## Output Format

```yaml
oracle_review:
  task_ref: <task contract reference>
  verdict: <PASS|CONDITIONAL|FAIL>
  checklist:
    correctness: <pass|fail>
    scope_drift: <pass|fail>
    regression_risk: <pass|fail>
    test_evidence: <pass|fail>
    document_alignment: <pass|fail>
    aop_consistency: <pass|fail|conflicts_found>
    minimalism: <pass|fail>
  aop_result:
    conflicts: <number>
    details: <list of conflicts if any>
  scope_drift_budget_used: <percentage>
  recommendations: <list>
```
