---
name: verification-before-completion
description: Mandatory verification gate before declaring any implementation done. Includes PyRAG reasoning verification and AOP consistency checks. Use before every completion claim.
---

# Verification Before Completion

Use before declaring any implementation done. This is a MANDATORY gate.

## Verification Process

### Step 1: Capture Baseline
- Record current test state (passing/failing counts)
- Record current build/type-check state
- Record current LSP diagnostic state

### Step 2: Run Tests
- Execute relevant test suites
- Verify no regressions from baseline
- Check coverage for new code

### Step 3: Build & Type Checks
- Run build command
- Run type checker (TypeScript: `tsc --noEmit`, Rust: `cargo check`, C++: clangd diagnostics)
- Verify zero new errors

### Step 4: Acceptance Criteria
- Check each acceptance criterion from the task contract
- Use `planner_review_task_contract` to validate scope
- Confirm all criteria are met

### Step 5: PyRAG Reasoning Verification (MANDATORY)
For any non-trivial implementation, compose a PyRAG reasoning program:

1. Call `codex_knowledge_memory_store` with:
   - goal: "Verify implementation correctness for [task description]"
   - retrieval_sources: ["codex_knowledge", "graphrag", "memory"]
   - constraints: ["Must pass all tests", "Must not regress existing functionality"]
   - max_steps: 5
   - repair_loop: true

2. Execute each step of the composed program:
   - Retrieve evidence from the specified sources
   - Verify claims against retrieved evidence
   - If a step fails, use the repair loop to find alternative evidence

3. Record the PyRAG program result in the verification output

### Step 6: AOP Consistency Check (MANDATORY)
- Call `codex_knowledge_graph_query` with:
  - claims: list of all claims made in the implementation
  - relations: list of all dependency relationships
  - rules: list of all constraints from the task contract
- If conflicts are found, they MUST be resolved before completion

### Step 7: Minimalism Check
- Call `minimalist_review_change` with the diff summary
- Verify the change is minimal and surgical
- Flag any unnecessary abstractions or over-engineering

## Verification Output

```yaml
verification:
  task_ref: <task contract reference>
  baseline:
    tests: <pass/fail counts>
    build: <clean/dirty>
    type_check: <clean/dirty>
  test_results:
    passed: <count>
    failed: <count>
    coverage: <percentage>
  acceptance_criteria:
    - criterion: <description>
      met: <true/false>
      evidence: <how verified>
  pyrag_program:
    goal: <verification goal>
    steps_completed: <count>
    steps_failed: <count>
    repair_attempts: <count>
    verdict: <verified|unverified|conflicts_found>
  aop_check:
    conflicts: <count>
    details: <list if any>
  minimalism:
    score: <minimalist review score>
    verdict: <pass|fail>
  overall_verdict: <PASS|FAIL|CONDITIONAL>
  blockers: <list of must-fix items>
```

## Guardrails
- NEVER skip the PyRAG step for non-trivial changes
- NEVER skip the AOP check
- NEVER declare completion with failing tests
- NEVER declare completion with type errors
- If PyRAG or AOP cannot verify, mark as CONDITIONAL and list what needs manual review
