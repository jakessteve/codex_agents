```yaml
skillbank_entry:
  id: general-harness-activation
  layer: general
  status: active
  source_evidence:
    - SOL integration plan
  activation_triggers:
    - medium-or-epic-task
    - task-requires-more-than-two-harness-artifacts
  adherence_checks:
    - harness_activation record exists before implementation
    - final_review checks active_harness entries
  last_reviewed: 2026-06-03
```

# Harness Activation

Activate task-scoped skills, rules, workflows, and MCP tools after Scope Lock. SkillOpt must review the set before implementation. Final Review treats missing adherence evidence as risk.
