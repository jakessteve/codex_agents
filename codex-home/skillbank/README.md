# SkillBank v1

## Purpose
Store distilled, reviewed skills and failure lessons in a hierarchy that can be retrieved by PM, SkillOpt, Dreaming, and Meta-Evolution.

## Layers

- `general/`: stable skills that apply across projects and task types.
- `task-specific/`: project or domain heuristics with a clear applicability boundary.
- `failure-lessons/`: concise anti-patterns distilled from validated failures.

## Merge Criteria

SkillBank entries may be added or revised only when all criteria pass:

1. Evidence comes from validated traces, Oracle-reviewed outcomes, or explicit user-approved lessons.
2. The entry states when to activate and when not to activate.
3. The entry has a measurable success signal or adherence check.
4. The entry does not conflict with native runtime boundaries.
5. `codex_knowledge` memory or graph stores retain the evidence link.

## Metadata

Each entry uses this header:

```yaml
skillbank_entry:
  id: <stable-id>
  layer: general | task-specific | failure-lessons
  status: active | retired
  source_evidence: [...]
  activation_triggers: [...]
  adherence_checks: [...]
  last_reviewed: <yyyy-mm-dd>
```

## Runtime Boundary

Reviewed entries live in Codex-native SkillBank files; shared evidence lives in MCP-backed memory and graph stores.
