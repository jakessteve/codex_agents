# Gate Taxonomy

## Purpose
Define all gate types in the development pipeline, when each is triggered, what it checks, and what verdicts it can return. This is the single source of truth for gate definitions.

## Gate Overview Table

| Gate | When Triggered | Purpose | Possible Verdicts | Required Predecessor |
|------|---------------|---------|-------------------|----------------------|
| **preflight_gate** | Before starting implementation | Check readiness: task contract completeness, context availability, AOP consistency, budget sufficiency, tool availability | `GO` / `NO-GO` / `CONDITIONAL` | None |
| **revision_gate** | After implementation, before Oracle review | Check if output meets task contract scope and evidence requirements | `REVISE` / `PROCEED` | Implementation complete |
| **escalation_gate** | When runtime cannot decide safely | Escalate ambiguous or high-cost decisions to the user | `USER_DECISION` | Any point (interrupt) |
| **abort_gate** | When continuing increases risk or wastes resources | Stop execution and checkpoint state for recovery | `ABORT` | Any point (interrupt) |
| **oracle_review_gate** | After implementation, before release | Independent review of correctness, scope adherence, minimalism, AOP consistency | `PASS` / `CONDITIONAL` / `FAIL` | `preflight_gate` passed |
| **release_gate** | Before shipping | Final check: diff matches contract, validation passed, no secrets, no surprises | `SHIP` / `HOLD` / `BLOCK` | `oracle_review_gate` passed |

---

## Gate Flow Diagram

```
┌─────────────────┐
│   Task Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  preflight_gate │────▶│   NO-GO /       │
│                 │     │   CONDITIONAL   │
└────────┬────────┘     └─────────────────┘
         │ GO                    │
         ▼                       └──▶ Enrich / Re-scope / Fix issues
┌─────────────────┐
│  Implementation │
│  (Builder works)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  revision_gate  │────▶│     REVISE      │
│                 │     └─────────────────┘
└────────┬────────┘              │
         │ PROCEED              └──▶ Builder revises output
         │                              (re-run revision_gate)
         ▼
┌─────────────────┐     ┌─────────────────┐
│ oracle_review_  │────▶│  CONDITIONAL /  │
│     gate        │     │      FAIL       │
└────────┬────────┘     └─────────────────┘
         │ PASS                │
         │                     └──▶ Fix issues / Revise output
         ▼                         (re-run oracle_review_gate)
┌─────────────────┐
│   release_gate  │────▶┌─────────────────┐
│                 │     │   HOLD / BLOCK  │
└────────┬────────┘     └─────────────────┘
         │ SHIP              │
         │                   └──▶ Fix issues / Re-run release_gate
         ▼
┌─────────────────┐
│      Ship       │
│   (Complete)    │
└─────────────────┘

Interrupt Gates (can fire at any point):
┌─────────────────┐
│  escalation_    │────▶ User makes decision ──▶ Resume at appropriate gate
│     gate        │
└─────────────────┘
┌─────────────────┐
│   abort_gate    │────▶ Checkpoint state ────▶ Recovery or Close
│                 │
└─────────────────┘
```

---

## Gate Definitions

### preflight_gate

**Trigger:** Automatically before any builder begins implementation.

**Checks:**
1. Task contract is complete and valid (`planner_review_task_contract`)
2. Required context is available (`codex_knowledge_project_context`)
3. AOP consistency of the planned approach (`codex_knowledge_graph_query`)
4. Context budget is sufficient (`token_health_check`)
5. Required tools are available and functional (`bash` with tool verification)
6. No unresolved blockers from previous tasks (`codex_knowledge_settings_review_queue`)

**Verdicts:**
- `GO`: All checks pass. Proceed to implementation.
- `NO-GO`: Critical check failed. Pipeline cannot start. Fix issues and re-run.
- `CONDITIONAL`: Minor issues that can be addressed during implementation. Document conditions and proceed with caution.

**Output:**
```yaml
preflight_gate:
  task_ref: <task contract ID>
  timestamp: <ISO-8601>
  checks:
    - check: <name>
      status: <pass|fail|warn>
      detail: <result or error>
  verdict: <GO|NO-GO|CONDITIONAL>
  conditions: <list of conditions if CONDITIONAL>
  blockers: <list of blockers if NO-GO>
```

---

### revision_gate

**Trigger:** After builder completes implementation of a slice, before Oracle review.

**Checks:**
1. Output matches task contract scope (`planner_review_task_contract`)
2. All claimed functionality has test evidence (`bash` with test runner)
3. AOP consistency check passes (`codex_knowledge_graph_query`)
4. Minimalism review passes (`minimalist_review_change`)
5. No unapproved files were modified (`minimalist_diff_budget`)

**Verdicts:**
- `PROCEED`: Output is ready for Oracle review.
- `REVISE`: Output has issues. Return to builder with specific feedback.

**Output:**
```yaml
revision_gate:
  task_ref: <task contract ID>
  slice_ref: <slice identifier>
  timestamp: <ISO-8601>
  checks:
    - check: <name>
      status: <pass|fail>
      detail: <result>
  verdict: <PROCEED|REVISE>
  revision_items:
    - issue: <description>
      severity: <critical|major|minor>
      recommendation: <how to fix>
  revision_scope: <minor|major|critical>
```

---

### escalation_gate

**Trigger:** When PM or agent encounters a decision with high cost of being wrong.

**Checks:**
1. Decision is not covered by task contract
2. Cost of wrong decision is HIGH
3. Multiple valid options exist

**Verdicts:**
- `USER_DECISION`: Pipeline paused until user responds.

**Output:** See `gates/escalation_gate.md` for full schema.

---

### abort_gate

**Trigger:** When continuing execution would increase risk or waste resources.

**Checks:**
1. Context budget exhausted
2. Critical unresolvable conflict
3. Scope drift exceeds budget
4. User cancellation
5. Unrecoverable error

**Verdicts:**
- `ABORT`: Execution halted. State checkpointed.

**Output:** See `gates/abort_gate.md` for full schema.

---

### oracle_review_gate

**Trigger:** After implementation passes revision_gate, before release.

**Checks:**
1. Correctness: Code implements the intended behavior
2. Scope adherence: No unapproved changes
3. Minimalism: Smallest valid solution
4. AOP consistency: No architectural conflicts
5. Test quality: Tests cover the change adequately
6. Security: No obvious vulnerabilities

**Verdicts:**
- `PASS`: Output is approved for release.
- `CONDITIONAL`: Minor issues. Fix and re-review.
- `FAIL`: Major issues. Return to builder for revision or abort.

**Output:**
```yaml
oracle_review_gate:
  task_ref: <task contract ID>
  slice_ref: <slice identifier>
  timestamp: <ISO-8601>
  reviewer: <oracle agent name>
  dimensions:
    - dimension: correctness
      score: <1-10>
      finding: <detailed finding>
    - dimension: scope_adherence
      score: <1-10>
      finding: <detailed finding>
    - dimension: minimalism
      score: <1-10>
      finding: <detailed finding>
    - dimension: aop_consistency
      score: <1-10>
      finding: <detailed finding>
    - dimension: test_quality
      score: <1-10>
      finding: <detailed finding>
    - dimension: security
      score: <1-10>
      finding: <detailed finding>
  verdict: <PASS|CONDITIONAL|FAIL>
  conditions: <list if CONDITIONAL>
  blockers: <list if FAIL>
```

---

### release_gate

**Trigger:** Before shipping the final diff.

**Checks:**
1. Diff matches task contract (`minimalist_diff_budget`)
2. Validation passed (tests, LSP, AOP)
3. No secrets in diff (`grep`)
4. No dependency surprises
5. Oracle review was completed and passed

**Verdicts:**
- `SHIP`: All checks pass. Diff is approved for shipping.
- `HOLD`: Minor issues. Fix before release.
- `BLOCK`: Critical issues. Do not release.

**Output:** See `gates/release_gate.md` for full schema.

---

## Gate Dependencies

```
preflight_gate
    │
    └── REQUIRED BY: oracle_review_gate
    │       (Oracle review assumes preflight checks were done)
    │
    └── RECOMMENDED BY: revision_gate
            (Revision gate is more effective if preflight passed)

oracle_review_gate
    │
    └── REQUIRED BY: release_gate
            (Release gate assumes Oracle has approved the output)

escalation_gate
    │
    └── CAN INTERRUPT: Any gate or implementation phase
            (Escalation is an async interrupt, not a sequential dependency)

abort_gate
    │
    └── CAN INTERRUPT: Any gate or implementation phase
            (Abort is an emergency stop, not a sequential dependency)
```

**Dependency Enforcement:**
- `release_gate` MUST verify that `oracle_review_gate` passed by checking for the Oracle review artifact.
- `oracle_review_gate` SHOULD verify that `preflight_gate` passed, but this is not strictly required (preflight may have been run in a previous session).
- If a required predecessor gate is missing, the current gate should run it or fail with `NO-GO` / `BLOCK`.

---

## Gate State Machine

```
State: idle
    │
    ▼ preflight_gate triggered
State: preflighting
    │
    ├── GO ───────────────▶ State: implementing
    ├── NO-GO ────────────▶ State: blocked
    └── CONDITIONAL ──────▶ State: implementing (with conditions)

State: implementing
    │
    ▼ revision_gate triggered
State: revising
    │
    ├── PROCEED ──────────▶ State: oracle_reviewing
    └── REVISE ───────────▶ State: implementing (return to builder)

State: oracle_reviewing
    │
    ├── PASS ─────────────▶ State: releasing
    ├── CONDITIONAL ──────▶ State: implementing (fix conditions)
    └── FAIL ─────────────▶ State: implementing (major revision) or State: aborting

State: releasing
    │
    ▼ release_gate triggered
    │
    ├── SHIP ─────────────▶ State: shipped
    ├── HOLD ─────────────▶ State: releasing (fix issues)
    └── BLOCK ────────────▶ State: blocked

State: blocked
    │
    └── Can transition to: idle (new task), implementing (re-scope), or aborting

State: aborting
    │
    └── Final state. Recovery requires explicit user action.
```

---

## Tool References

| Tool | Purpose | Gates Using It |
|------|---------|----------------|
| `planner_review_task_contract` | Validate task contract scope | preflight_gate, revision_gate |
| `codex_knowledge_project_context` | Gather project context | preflight_gate |
| `codex_knowledge_graph_query` | Check architectural consistency | preflight_gate, revision_gate, oracle_review_gate |
| `token_health_check` | Monitor context budget | preflight_gate, abort_gate |
| `minimalist_diff_budget` | Compare planned vs. actual files | revision_gate, release_gate |
| `minimalist_review_change` | Score minimalism | revision_gate, oracle_review_gate |
| `bash` with test runner | Run tests | revision_gate, release_gate |
| `grep` | Scan for secrets | release_gate |
| `codex_knowledge_settings_review_queue` | Check for unresolved blockers | preflight_gate |
| `codex_knowledge_handoff_checkpoint` | Audit gate transitions | All gates |
| `codex_knowledge_knowledge_capture` | Persist gate outputs | All gates |
