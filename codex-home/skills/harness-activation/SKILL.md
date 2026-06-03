---
name: harness-activation
description: Record task-scoped skills, rules, workflows, and MCP tools after Scope Lock and before implementation.
---

# Harness Activation

## Purpose
Make harness usage explicit so task-solving agents activate and follow the selected harness artifacts through long tasks.

## Protocol
1. PM proposes task-scoped skills, rules, workflows, and MCP tools from the task contract and Explore reports.
2. SkillOpt reviews relevance, overlap, and token cost.
3. Implementer records the active harness before code changes.
4. Final Review checks adherence against the record.

## Record Shape

```yaml
harness_activation:
  task_id: <task-id>
  phase: harness_activation
  selected_by: pm
  skillopt_review: pass | revise
  active_harness:
    skills: [...]
    rules: [...]
    workflows: [...]
    mcp_tools: [...]
  adherence_checks:
    - <specific-check>
  rejected_harness:
    - name: <artifact>
      reason: irrelevant | overlapping | too_expensive | unsafe
```

## Guardrails
- Do not load every skill by default.
- Do not remove a skill required by the task contract.
- Treat missing adherence evidence as a Final Review risk.
