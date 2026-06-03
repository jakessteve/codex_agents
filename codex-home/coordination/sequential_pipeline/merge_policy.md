# Sequential Pipeline Merge Policy

## Purpose
Define how outputs are merged in the sequential pipeline. Only validated outputs are merged. Unvalidated or speculative work is discarded.

## Merge Decision Tree

```
Builder has completed a slice and passed revision_gate
    │
    ▼
Has the output passed Oracle review (oracle_review_gate)?
    │
    ├── NO → Do NOT merge. Return to builder for revision.
    │
    └── YES → Does the output conflict with existing code?
                │
                ├── NO → Proceed to merge (Section 3)
                │
                └── YES → Can the conflict be resolved automatically?
                            │
                            ├── YES → Builder resolves, Oracle re-reviews (Section 4)
                            └── NO → PM intervenes, builder resolves, Oracle re-reviews (Section 4)
```

## 1. Only Validated Outputs

**Hard Rule:** Only outputs that have passed Oracle review are eligible for merge.

| Validation Stage | Required Evidence | Tool |
|------------------|-------------------|------|
| Builder self-check | LSP diagnostics clean, unit tests pass | `bash` with test runner |
| Revision gate | Output matches task contract scope | `planner_review_task_contract` |
| Oracle review | Verdict: PASS or CONDITIONAL (with all conditions resolved) | `oracle_review_gate` rubric |

**What is "unvalidated work":**
- Code that has not been run or tested
- Changes that have not been reviewed against the task contract
- Speculative refactors not tied to the current task contract
- Any file modified outside the approved slice scope

**Action on unvalidated work:**
- Discard the changes.
- Record the discard in `trace_export_record_trace`:
  - `trace_class`: "merge_discard"
  - `title`: "Unvalidated work discarded"
  - `payload`: { `reason`: "unvalidated", `files`: [<list>] }

---

## 2. Merge Process

### 2.1 PM Review

Before any merge, PM MUST:
1. Load the validated output via `codex_knowledge_handoff_read`.
2. Compare the output against the task contract:
   - Use `planner_review_task_contract` to verify scope alignment.
   - Check that all acceptance criteria are addressed.
3. Check for conflicts with existing code:
   - Use `bash` with `git diff --check` to detect whitespace conflicts.
   - Use `bash` with `git merge-tree` to predict merge conflicts.
4. Decide:
   - **Approve:** Output is clean and aligned → proceed to merge.
   - **Request Revisions:** Minor issues → return to builder with specific feedback.
   - **Escalate:** Major architectural conflict → invoke `gates/escalation_gate.md`.

### 2.2 Builder Applies the Merge

Once PM approves:
1. Builder switches to the target branch (e.g., `main` or the epic branch).
2. Builder merges the validated branch:
   ```bash
   git merge --no-ff <validated_branch> -m "Merge: <slice_description>"
   ```
3. If merge conflicts arise, builder resolves them per Section 4.
4. Builder runs the post-merge verification suite per Section 5.

**Tool References:**
- `codex_knowledge_handoff_read` — load validated output
- `planner_review_task_contract` — scope alignment check
- `bash` with `git diff`, `git merge-tree` — conflict detection

---

## 3. Conflict Resolution

### 3.1 Conflict Detection

Detect conflicts BEFORE attempting merge:

| Method | Command | When to Use |
|--------|---------|-------------|
| Git diff check | `git diff --check` | Whitespace conflicts only |
| Merge-tree preview | `git merge-tree $(git merge-base A B) A B` | Full conflict preview without touching working tree |
| LSP diagnostics | Run language server on both branches | Semantic conflicts (e.g., renamed function still referenced) |

### 3.2 Conflict Resolution Workflow

If conflicts are detected:

```
PM identifies conflict type
    │
    ▼
Is it a trivial conflict (whitespace, import ordering)?
    │
    ├── YES → Builder resolves automatically
    │           └── Run tests → Pass? → Merge
    │
    └── NO → Is it a semantic conflict (logic change vs. logic change)?
                │
                ├── YES → PM decides which logic to keep
                │           └── Builder applies decision
                │           └── Oracle reviews resolution
                │           └── Pass? → Merge
                │
                └── NO → Is it an architectural conflict?
                            │
                            ├── YES → Escalate to user via escalation_gate.md
                            └── NO → Builder investigates and resolves
                                        └── Oracle reviews resolution
                                        └── Pass? → Merge
```

### 3.3 Resolution Standards
- Builder MUST NOT resolve conflicts by accepting both versions blindly.
- Builder MUST document the resolution rationale in a commit message or comment.
- After resolution, the full test suite MUST pass before merge proceeds.

**Tool References:**
- `bash` with `git diff --check`, `git merge-tree` — conflict detection
- `read` — inspect conflicting files
- `edit` — apply resolutions

---

## 4. Merge Verification

After merge, run the following checks in order:

### 4.1 Full Test Suite
```bash
# Example for Python
pytest --tb=short -q
```
- All tests MUST pass.
- If tests fail, builder fixes them BEFORE the merge is considered complete.
- Record results: `tests_passing: <count>`, `tests_failing: <count>`.

### 4.2 LSP Diagnostics
- Run the language server on all changed files.
- Zero errors, zero warnings that are relevant to the change.
- Warnings in untouched files are out of scope.

### 4.3 AOP Consistency Check
Invoke `cognition_codex_check_aop_consistency`:
- `claims`: list of architectural claims introduced by the merge
- `rules`: project-specific rules from memory or vault
- If conflicts are found, builder resolves them or escalates.

### 4.4 Minimalism Review
Invoke `minimalist_review_change`:
- `change_summary`: description of the merged change
- `added_lines`: total added lines in the merge
- `removed_lines`: total removed lines in the merge
- `file_count`: number of files touched
- If the review flags over-engineering, builder simplifies or justifies.

### 4.5 Knowledge Capture
Record the merge in `codex_knowledge_knowledge_capture`:
- `key`: `merge_<task_ref>_<timestamp>`
- `value`: JSON with merge metadata, test results, and verification status

**Tool References:**
- `bash` with test runner — test execution
- `cognition_codex_check_aop_consistency` — architectural consistency
- `minimalist_review_change` — minimalism check
- `codex_knowledge_knowledge_capture` — merge persistence

---

## 5. Merge Output

Every merge MUST produce the following artifact:

```yaml
merge:
  # Identity
  merge_id: <unique identifier>
  task_ref: <task contract reference>
  slice_ref: <slice identifier>
  timestamp: <ISO-8601>

  # Source
  source_branch: <branch that was merged>
  target_branch: <branch merged into>
  validated_by: <oracle review reference>

  # Conflicts
  conflicts:
    - file: <path>
      type: <whitespace|semantic|architectural>
      resolution: <how it was resolved>
      resolver: <builder|pm|oracle>
    # Use "none" if no conflicts

  # Verification Results
  tests_after_merge:
    passing: <count>
    failing: <count>
    skipped: <count>
  lsp_diagnostics:
    errors: <count>
    warnings: <count>
  aop_after_merge: <pass|fail>
  minimalism_after_merge: <pass|fail>

  # Scope
  files_changed: <count>
  lines_added: <count>
  lines_removed: <count>
  scope_drift_percent: <percentage>

  # Status
  status: <merged|reverted|pending_fix>
  next_action: <close_slice|start_next_slice|escalate>
```

**Persistence:**
- Save the merge artifact to `codex_knowledge_knowledge_capture` with key `merge_<task_ref>`.
- If `status` is `merged` and `next_action` is `close_slice`, PM closes the slice and advances the pipeline.
- If `status` is `pending_fix`, the slice remains open and builder addresses issues.
- If `next_action` is `escalate`, invoke `gates/escalation_gate.md`.
