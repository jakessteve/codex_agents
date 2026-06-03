# Sequential Pipeline Termination

## Purpose
Define when and how the sequential pipeline terminates. Termination is a controlled, auditable event—not an abrupt stop.

## Termination Decision Tree

```
Oracle has completed review
    │
    ▼
What is the Oracle verdict?
    │
    ├── PASS → Did all acceptance criteria pass?
    │               │
    │               ├── YES → Did scope drift stay within budget?
    │               │           │
    │               │           ├── YES → SUCCESS TERMINATION (Section 1)
    │               │           └── NO → SCOPE DRIFT TERMINATION (Section 2)
    │               │
    │               └── NO → Which criteria failed?
    │                           │
    │                           ├── Minor failures → CONDITIONAL PASS → Fix and re-review
    │                           └── Major failures → FAILURE TERMINATION (Section 3)
    │
    ├── CONDITIONAL → Were all conditions resolved?
    │                   │
    │                   ├── YES → Treat as PASS above
    │                   └── NO → FAILURE TERMINATION (Section 3)
    │
    └── FAIL → Can the issues be fixed within context budget?
                │
                ├── YES → Return to builder for revision
                └── NO → FAILURE TERMINATION (Section 3)
```

## 1. Success Termination

The pipeline terminates successfully when ALL of the following are true:

| Condition | Verification Method | Threshold |
|-----------|---------------------|-----------|
| Oracle approves implementation | `oracle_review_gate` verdict | PASS |
| All acceptance criteria met | `planner_review_task_contract` | 100% coverage |
| All tests pass | Test runner (`bash`) | 0 failures |
| Scope drift within budget | `minimalist_diff_budget` | ≤5% |
| AOP consistency check passes | `cognition_codex_check_aop_consistency` | 0 critical conflicts |
| No secrets in diff | `grep` for secret patterns | 0 findings |
| LSP diagnostics clean | Language server check | 0 errors in changed files |

### Success Termination Steps

1. **Final Verification:**
   - Run full test suite: `bash` with `pytest` / `jest` / etc.
   - Run `minimalist_diff_budget` to confirm scope drift ≤5%.
   - Run `cognition_codex_check_aop_consistency` one final time.
   - Run secret scan: `grep` for `API_KEY`, `SECRET`, `PASSWORD`, `TOKEN`, `BEGIN PRIVATE KEY`.

2. **Knowledge Capture:**
   - Record success in `codex_knowledge_knowledge_capture`:
     - `key`: `termination_success_<task_ref>`
     - `value`: termination YAML (see Output Format)
   - Record in `trace_export_record_trace`:
     - `trace_class`: "pipeline_termination"
     - `title`: "Sequential pipeline success"
     - `payload`: termination summary

3. **Cleanup:**
   - Close all open handoff checkpoints: `codex_knowledge_handoff_checkpoint` with recovery action.
   - Archive slice branches (optional): `bash` with `git branch -d <slice_branch>`.
   - Update project index: `codex_knowledge_project_index`.

4. **Notify PM:**
   - PM receives termination artifact.
   - PM decides next task or closes the epic.

---

## 2. Scope Drift Termination

The pipeline terminates with scope drift when:

| Condition | Detection Method |
|-----------|------------------|
| Scope drift exceeds budget (>5%) | `minimalist_diff_budget` |
| PM cannot resolve drift within budget | PM assessment after 2 reduction attempts |
| Drift is structural (new epic-level concerns) | `planner_review_task_contract` flags new domains |

### Scope Drift Termination Steps

1. **Measure Drift:**
   - Invoke `minimalist_diff_budget`:
     - `planned_files`: from original task contract
     - `actual_files`: all files touched during pipeline
     - `allowed_slack`: 1
   - Calculate drift percentage: `(actual - planned) / planned * 100`.

2. **Attempt Resolution:**
   - **Attempt 1:** Builder removes non-essential files/changes. Re-run `minimalist_diff_budget`.
   - **Attempt 2:** PM re-scopes the task contract to absorb the drift. Re-run `planner_review_task_contract`.
   - If both attempts fail, proceed to termination.

3. **Checkpoint State:**
   - Use `codex_knowledge_handoff_checkpoint` to save current state.
   - Record what was accomplished and what remains.

4. **Terminate with Drift Report:**
   - Produce termination YAML (see Output Format).
   - `next_action`: `revise` (re-scope and restart) or `escalate` (ask user for guidance).

---

## 3. Failure Termination

The pipeline terminates with failure when ANY of the following occur:

| Condition | Detection Method | Severity |
|-----------|------------------|----------|
| Oracle verdict is FAIL | `oracle_review_gate` | Critical |
| AOP consistency finds critical, unresolvable conflicts | `cognition_codex_check_aop_consistency` | Critical |
| Context budget exhausted (>95% used) | `token_health_check` | Critical |
| User explicitly cancels | User message | Critical |
| Security vulnerability discovered in merged code | Security review / `grep` | Critical |
| Data loss or corruption risk identified | Builder or Oracle assessment | Critical |

### Failure Termination Steps

1. **Halt All Work:**
   - Builder stops all edits immediately.
   - PM freezes the pipeline.

2. **Preserve Evidence:**
   - Save all intermediate work to `codex_knowledge_handoff_checkpoint`.
   - Record failure details in `trace_export_record_trace`:
     - `trace_class`: "pipeline_failure"
     - `title`: "Sequential pipeline failure"
     - `payload`: { `reason`, `task_ref`, `evidence` }

3. **Root Cause Analysis (if applicable):**
   - If failure is due to a bug or misconfiguration, builder performs RCA.
   - Use `debugger-core` skill for systematic debugging.
   - Record findings in `codex_knowledge_knowledge_capture`.

4. **Terminate with Failure Report:**
   - Produce termination YAML (see Output Format).
   - `next_action`: `close` (abandon), `restart` (begin fresh), or `escalate` (user decides).

---

## 4. Escalation Termination

The pipeline terminates with escalation when:

| Condition | Trigger |
|-----------|---------|
| Runtime cannot decide safely | PM or Oracle detects ambiguity with high cost of wrong decision |
| Human approval required for critical decision | Security, architecture, or scope changes affecting multiple epics |
| User explicitly requests pause | User message |

### Escalation Termination Steps

1. **Prepare Escalation Package:**
   - Gather all relevant context: task contract, Oracle reviews, test results, scope drift report.
   - Use `gates/escalation_gate.md` workflow.

2. **Checkpoint State:**
   - Use `codex_knowledge_handoff_checkpoint` to save exact state.
   - Include: current branch, open files, pending decisions.

3. **Present to User:**
   - Use `question` tool to present options with tradeoffs.
   - Wait for user decision.

4. **Resume or Close:**
   - If user provides decision, update task contract and resume.
   - If user requests close, produce termination YAML with `next_action: close`.

---

## Termination Output Format

Every termination MUST produce the following artifact:

```yaml
termination:
  # Identity
  termination_id: <unique identifier>
  task_ref: <task contract reference>
  timestamp: <ISO-8601>

  # Reason
  reason: <success|scope_drift|failure|escalation>
  reason_detail: <specific explanation>

  # Oracle
  oracle_verdict: <PASS|CONDITIONAL|FAIL>
  oracle_review_ref: <reference to Oracle review artifact>

  # Scope
  scope_drift_percent: <percentage>
  planned_files: <count>
  actual_files: <count>
  new_dependencies: <list or none>

  # Acceptance Criteria
  acceptance_criteria_met: <count>/<total>
  unmet_criteria:
    - criterion: <description>
      reason: <why it was not met>

  # Tests
  tests_passing: <count>
  tests_failing: <count>
  tests_skipped: <count>
  test_coverage_percent: <percentage>

  # Quality Checks
  aop_conflicts: <count>
  aop_conflict_details:
    - conflict: <description>
      severity: <critical|major|minor>
  lsp_errors: <count>
  lsp_warnings: <count>
  secrets_found: <count>

  # Resources
  context_budget_used: <percentage>
  context_budget_total: <token count>
  waves_executed: <count>
  slices_completed: <count>/<total>

  # Next Action
  next_action: <close|revise|escalate|restart>
  next_action_rationale: <why this action was chosen>

  # Recovery
  checkpoint_ref: <handoff checkpoint name or "none">
  resumable: <true|false>
  resumption_instructions: <how to resume if applicable>
```

**Persistence:**
- Save termination artifact to `codex_knowledge_knowledge_capture` with key `termination_<task_ref>`.
- If `resumable: true`, ensure `checkpoint_ref` is valid and documented.
- If `next_action: restart`, PM creates a new task contract and begins a fresh pipeline.
- If `next_action: close`, PM archives the task and updates the project index.

---

## Tool References

| Tool | Purpose | When to Invoke |
|------|---------|----------------|
| `oracle_review_gate` | Final quality review | Before any termination |
| `planner_review_task_contract` | Scope and acceptance criteria check | During success and drift termination |
| `minimalist_diff_budget` | File count drift measurement | During success and drift termination |
| `cognition_codex_check_aop_consistency` | Architectural consistency | During success and failure termination |
| `token_health_check` | Context budget monitoring | During failure termination |
| `grep` | Secret pattern scanning | During success termination |
| `codex_knowledge_handoff_checkpoint` | State preservation | During drift, failure, and escalation termination |
| `trace_export_record_trace` | Audit trail | All termination types |
| `codex_knowledge_knowledge_capture` | Termination persistence | All termination types |
| `question` | User escalation | During escalation termination |
