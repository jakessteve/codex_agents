---
name: self-evolving
summary: Propose and apply harness improvements from validated lessons and traces.
---

# Self Evolving

## Purpose
Improve the development harness (skills, prompts, guardrails, workflows) based on validated lessons and traces.

## Prerequisites
- Lessons must be validated (post-Oracle review)
- Traces must be recorded (via `trace_export_record_trace`)
- No unapproved changes to core workflows

## Steps

### 1. Gather Validated Lessons and Traces
- Use `trace_export_summarize_exports` to review recent traces
- Use `codex_knowledge_memory_query` to retrieve lessons
- Use `evolution_classify_repetition` to identify repeated failure patterns
- Use `cognition_codex_consolidate_dreaming` to consolidate patterns

### 2. Write Proposal Manifest
- Use `evolution_propose_harness_change` to draft a proposal:
  ```yaml
  evolution_proposal:
    trigger: <what triggered this proposal>
    evidence: <list of traces, lessons, patterns>
    desired_change: <what should change>
    constraints: <what must not change>
  ```

### 3. Gate with Oracle and Human Approval
- Submit proposal to Oracle for review
- Oracle checks:
  - Does the change improve the stated metric?
  - Does it introduce new risks?
  - Is it minimal and reversible?
- If Oracle approves, submit for human approval
- Use `human_approval_interrupt` workflow for critical changes

### 4. Apply Approved Changes
- Apply only the approved harness change
- Record the change in `codex_knowledge_knowledge_capture`
- Update the relevant skill, guardrail, or workflow file
- Use `evolution_record_retrospective` to record the outcome

### 5. Monitor Results
- Track KPIs after the change:
  - `kpi:hallucination_rate:<date>`
  - `kpi:scope_drift_rate:<date>`
  - `kpi:minimalism_score:<date>`
  - `kpi:token_efficiency:<date>`
  - `kpi:harness_activation_rate:<date>`
  - `kpi:harness_adherence_score:<date>`
  - `kpi:graph_first_rate:<date>`
  - `kpi:grep_fallback_rate:<date>`
- If metrics worsen, revert the change and record the regression

### 6. Distill SkillBank Entries
- Convert validated successes into `skillbank/general` or `skillbank/task-specific` entries.
- Convert validated failures into `skillbank/failure-lessons` entries.
- Require SkillOpt and Oracle review before a SkillBank entry becomes active.
- Store evidence links in `codex_knowledge` memory or graph.

## Guardrails
- Never edit runtime files directly without an approved task contract
- Never propose more than 2 changes per evolution cycle
- Always include rollback criteria
- Require human approval for procedure changes
- Never add active SkillBank entries from unreviewed traces
