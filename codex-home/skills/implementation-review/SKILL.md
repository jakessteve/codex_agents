---
name: implementation-review
description: Review implementation quality, debt introduced, and residual risk before release. Run after implementation and validation.
---

# Implementation Review

## Purpose
Review the approach quality, technical debt introduced, and residual risk after implementation and before release.

## Steps

### 1. Gather Materials
- Retrieve the task contract
- Retrieve the implementation diff
- Retrieve validation evidence (test results, LSP diagnostics)

### 2. Review Approach Quality
- Is the implementation the simplest valid solution?
- Use `minimalist_review_change` to score minimalism
- Use `minimalist_simplification_notes` to identify duplication
- Check for unnecessary abstractions, premature optimization, over-engineering

### 3. Review Debt Introduced
- New dependencies added?
- New complexity introduced?
- Technical debt items created?
- Use `treesitter_summarize_path` to measure structural complexity
- Record debt:
  ```yaml
  debt:
    new_dependencies: <list>
    complexity_change: <increase|stable|decrease>
    items: <list of debt items>
    paydown_plan: <when and how to address>
  ```

### 4. Review Residual Risk
- What could still go wrong?
- Are there edge cases not covered by tests?
- Are there known limitations documented?
- Use `cognition_codex_check_aop_consistency` for logical gaps

### 5. Record Verdict
```yaml
implementation_review:
  task_ref: <reference>
  approach_quality: <excellent|good|acceptable|poor>
  minimalism_score: <score>
  debt_introduced: <none|minor|moderate|major>
  residual_risk: <low|medium|high>
  verdict: <approve|request_changes|reject>
  required_follow_up: <list of items>
```
