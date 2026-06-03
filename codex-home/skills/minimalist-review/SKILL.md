---
name: minimalist-review
description: Judge whether the implementation is the smallest valid solution. Require the smallest valid diff that satisfies the task.
---

# Minimalist Review

## Purpose
Enforce minimalism by requiring the smallest valid diff that satisfies the task contract.

## Review Criteria

### 1. Diff Size
- Use `minimalist_review_change` to score the diff
- Use `minimalist_diff_budget` to compare planned vs. actual file count
- Acceptable: added lines ≤ 2× removed lines, file count within budget

### 2. No Unnecessary Abstractions
- No speculative generalizations
- No "just in case" code
- No premature optimization
- Each abstraction must be justified by a current requirement

### 3. No Duplication
- Use `minimalist_simplification_notes` to identify duplicate terms
- If similar code appears in 3+ places, extract a shared utility
- If similar code appears in 1-2 places, keep it inline

### 4. Surgical Changes
- Changes should be minimal and targeted
- No unrelated refactoring in the same diff
- No style changes mixed with functional changes

### 5. Output Format
```yaml
minimalist_review:
  diff_summary: <what changed>
  file_count: <count>
  added_lines: <count>
  removed_lines: <count>
  score: <minimalist review score>
  unnecessary_abstractions: <list>
  duplications: <list>
  verdict: <pass|fail>
  recommendations: <list>
```
