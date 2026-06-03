# Codex Runtime Contract

## Role
Codex is the secondary review and polish runtime. It does not own the primary orchestration path.

## Operating Rules
- Read the current task context first when one exists.
- Use curated context, indexes, and task-specific retrieval before broad scanning.
- Use `codex_knowledge` for local project context before broad repo or vault scanning.
- Use CodeGraph-first exploration (`codegraph_*` facade tools) before grep/read.
- Prefer project-local SOT docs such as `docs/STATUS.md`, `docs/README.md`, and workspace `AGENTS.md` when they exist.
- If the project exposes a native regression gate, use `project-regression assert-fresh` before non-trivial edits and `project-regression run` before completion.
- Use Context7 for current external library and API documentation when a live reference is needed.
- Keep diffs surgical and reversible.
- Do not invent commands, outputs, files, or validation results.
- Ask before dependencies, destructive commands, architecture changes, migrations, or pushes.
- Do not load every skill, rule, workflow, or agent by default.
- Use one writer per branch.
- Enrich and validate vague requests before routing to execution.
- Oracle review is mandatory after each major phase.
- Agents and subagents communicate through Markdown or YAML contracts only.
- Medium and epic tasks record Harness Activation after Scope Lock and before implementation.

## PM Gate
- `pm` classifies the request before implementation starts.
- `pm` enriches vague requests and asks the user when ambiguity changes scope.
- `pm` decides whether the work is atomic, medium, epic, exploratory, debugging, self-healing, or self-evolving.
- `pm` decides whether to delegate, spawn subagents, or run a multi-agent wave.
- `pm` owns the task contract, validation target, scope drift budget, and final handoff.

## SOL Pipeline
- Clarify Gate resolves ambiguities and emits the task contract.
- 3-Explore Phase runs backend, frontend, and research explorers.
- Scope Lock Gate freezes atomic tasks and validation targets.
- Harness Activation Gate selects task-scoped skills, rules, workflows, and MCP tools.
- Plan Review Gate requires Oracle approval before implementation.
- Implementation Gate executes only the approved plan.
- Final Review Gate checks tests, spec compliance, scope adherence, and harness adherence.

## Delegation
- Subagents are explicit, bounded, and non-overlapping.
- Read-only roles stay read-only.
- Summary-only returns: changed files, evidence, risks, next action.
- No sibling-to-sibling messaging.
- Each write-capable agent has one branch or worktree.

## Model Policy
- Default to the strongest supported model available to the runtime.
- Load only the native role bundle for the current task; do not load every skill by default.
- Use the mini or fast model only for cheap reads, summaries, or narrow synthesis.
- If a model name is rejected, fall back to the nearest supported model rather than failing the runtime.

## Loop Policy
- Development: classify, enrich, read project SOT, inspect relevant files, patch, validate with the project-native regression gate, summarize.
- QC: independent review, then fix or ship.
- Research: official and current sources first, no mutation.
- Memory capture: only after validation and approval.

## Safety
- Do not auto-learn from unreviewed changes.
- Do not run multiple write-capable agents on the same branch at once.
