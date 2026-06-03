---
name: sol-sequential
summary: Phase-gated Structured Orchestration Lifecycle for medium and epic tasks.
---

# SOL Sequential Pipeline Workflow

## Overview
The Structured Orchestration Lifecycle reduces scope drift, hallucinations, and coordination failures by separating clarification, exploration, scope lock, harness activation, plan review, implementation, and final review.

## Phases

### Phase 1: Clarify Gate
- Owner: PM.
- Output: task contract with intent, success criteria, constraints, validation target, and known unknowns.
- Exit: no unresolved ambiguity that changes scope.

### Phase 2: 3-Explore Phase
- Owner: PM dispatches backend, frontend, and research explorers.
- Method: CodeGraph facade first, then targeted fallback reads.
- Output: three exploration reports with affected files, candidate tests, fallback reads, and uncertainty.

### Phase 3: Scope Lock Gate
- Owner: PM.
- Output: frozen atomic task list with acceptance criteria, file ownership expectations, and scope drift budget.
- Exit: PM or user approval recorded.

### Phase 4: Harness Activation Gate
- Owner: PM and SkillOpt reviewer.
- Output: active skills, rules, workflows, MCP tools, and adherence checks.
- Exit: implementer knows exactly which harness artifacts apply.

### Phase 5: Plan Review Gate
- Owner: Oracle.
- Output: approved plan or revision request.
- Exit: plan matches locked scope and includes validation evidence requirements.

### Phase 6: Implementation Gate
- Owner: builder agent.
- Output: code, docs, tests, and recorded deviations.
- Exit: all accepted tasks completed or BreakRequest emitted.

### Phase 7: Final Review Gate
- Owner: Oracle and PM.
- Output: test evidence, scope adherence, harness adherence, AOP/PyRAG consistency, and release verdict.

## Transition Rules
- Each phase must pass before the next begins.
- Break/Resume is used only when genuinely blocked.
- Scope changes after Scope Lock re-open the gate.
- Waves are allowed only after Explore proves independent file ownership.
