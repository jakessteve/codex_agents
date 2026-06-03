# Skill Registry

## Purpose
Index native Codex skills for task-scoped loading and SkillOpt review.

## Native Additions

| Skill | Type | Roles | Task Types |
|-------|------|-------|------------|
| codegraph-explorer | standalone | backend-explorer, frontend-explorer, research-explorer, architect | exploration, impact-analysis |
| break-resume | standalone | pm, all subagents | clarification, human-loop |
| harness-activation | standalone | pm, builders, reviewer | harness-activation, review |
| kpi-tracking | standalone | meta-evolution, reviewer | kpi, evolution |

## Rules
- Load only skills relevant to the task contract.
- Prefer bundle skills when they cover the required behavior.
- Store SkillBank evidence in `codex_knowledge` memory or graph.
- Do not reference non-Codex runtime skill paths from Codex agents.
