---
name: veto-protocol
description: Any veto must include evidence and a remediation path. No veto without actionable alternatives.
---

# Veto Protocol

## Purpose
Ensure that vetoes (rejections of proposed changes) are constructive, evidence-based, and include a clear path forward.

## Hard Rules

1. **No Veto Without Evidence**: Every veto must cite specific evidence:
   ```yaml
   veto:
     what: <what is being vetoed>
     why: <specific reason>
     evidence:
       - source: <tool or document>
         finding: <what was found>
       - source: <tool or document>
         finding: <what was found>
     severity: <critical|major|minor>
   ```

2. **No Veto Without Remediation**: Every veto must include at least one actionable alternative:
   ```yaml
   remediation:
     - option: <alternative approach>
       effort: <estimated effort>
       risk: <risk level>
     - option: <simpler alternative>
       effort: <estimated effort>
       risk: <risk level>
   ```

3. **Veto Severity Levels**:
   - **Critical**: Security vulnerability, data loss risk, or production outage. Must be fixed before proceeding.
   - **Major**: Scope drift, regression, or missing test coverage. Must be addressed before merge.
   - **Minor**: Style issue, minor optimization, or documentation gap. Can be addressed in a follow-up.

4. **Veto Escalation**: If the vetoed party disagrees with the veto:
   - Both parties present evidence to PM
   - PM makes the final decision
   - PM's decision is recorded in the task contract

5. **Veto Scope**: Vetoes can only be issued within the reviewer's domain:
   - Oracle: correctness, scope drift, regression, minimalism
   - Security reviewer: security vulnerabilities, unsafe paths
   - Hallucination auditor: factual errors, scope drift, logical inconsistencies
   - Simplifier reviewer: unnecessary complexity, duplication

6. **Veto Resolution Tracking**: All vetoes and their resolutions must be recorded:
   ```yaml
   veto_resolution:
     veto_id: <unique id>
     vetoed_by: <agent>
     vetoed_at: <timestamp>
     resolution: <accepted|overridden|compromised>
     resolved_by: <agent or user>
     resolved_at: <timestamp>
     final_action: <what was done>
   ```

## Mechanisms

- `planner_review_task_contract` — validates scope and acceptance criteria
- `minimalist_review_change` — provides evidence for minimalism vetoes
- `cognition_codex_check_aop_consistency` — provides evidence for logical consistency vetoes
- `treesitter_changed_symbols` — provides evidence for scope vetoes
- `codex_knowledge_knowledge_capture` — records veto resolutions

## Enforcement

- Oracle reviews must include veto evidence and remediation
- Security reviews must include vulnerability details and fix suggestions
- Simplifier reviews must include specific simplification suggestions
- All vetoes are tracked in the task contract
