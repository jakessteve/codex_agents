# Sequential Pipeline Orchestrator

Use for medium and epic work. PM owns request enrichment, routing, scope lock, and Oracle handoff. Keep execution linear unless the Explore phase proves that a wave has no write overlap.

## SOL Gates

1. **Clarify Gate**: PM classifies the request, resolves ambiguity, and emits a Markdown or YAML task contract.
2. **3-Explore Phase**: PM dispatches backend, frontend, and research explorers. Each explorer starts with `codex_knowledge_project_context` and CodeGraph facade queries.
3. **Scope Lock Gate**: PM freezes the atomic task list, acceptance criteria, validation target, file ownership expectations, and scope drift budget.
4. **Harness Activation Gate**: PM proposes task-scoped skills, SkillOpt reviews the set, and the implementer records active harness artifacts.
5. **Plan Review Gate**: Oracle reviews the plan against locked scope, source trust, no-shortcuts rules, and validation evidence requirements.
6. **Implementation Gate**: Builder executes only the approved plan and records CodeGraph misses, fallback reads, tests, and deviations.
7. **Final Review Gate**: Oracle verifies tests, AOP/PyRAG consistency, scope adherence, harness adherence, and release readiness.

## Required Contracts

### Explore Report

```yaml
explore_report:
  phase: explore
  agent: backend_explorer | frontend_explorer | research_explorer
  context_sources: [...]
  codegraph_queries:
    - tool: codegraph_symbol_lookup | codegraph_callers_callees | codegraph_impact_analysis | codegraph_semantic_search
      query: <query-or-symbol>
      result_count: <number>
  fallback_reads:
    - path: <path>
      reason: graph_miss | detail_needed | validation
  affected_files: [...]
  candidate_tests: [...]
  uncertainties: [...]
```

### Harness Activation Record

```yaml
harness_activation:
  phase: harness_activation
  task_id: <task-id>
  recommended_skills: [...]
  skillopt_review: pass | revise
  active_harness:
    skills: [...]
    rules: [...]
    workflows: [...]
    mcp_tools: [...]
  adherence_checks:
    - <check-that-final-review-can-verify>
```

## Cache And Token Discipline

- Emit a cache boundary at each gate.
- Check semantic cache before drafting a new task contract, plan, or verification program.
- Prefer concise Markdown/YAML reports over raw logs.
- Record `graph_first_rate`, `grep_fallback_rate`, `harness_activation_rate`, `harness_adherence_score`, `tool_output_tokens`, `output_compression_savings`, `token_efficiency`, and `cache_hit_rate` when evidence is available.

## Break/Resume

Use `coordination/break_resume_protocol.md` when a phase is genuinely blocked. PM presents one question to the user. Any `scope_change` in the ResumePackage re-opens Scope Lock.

## Abort Conditions

- Critical AOP/PyRAG consistency failure.
- Scope drift exceeds the locked budget.
- Oracle verdict is FAIL.
- Harness Activation is missing for medium or epic work.
- Implementation starts before Plan Review approval.
