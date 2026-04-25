# Codex Native Runtime Contract

## Role
`pm` is the public gate for this runtime. Treat it as the first stop for new work.

## Operating Rules
- Read the current task context first when one exists.
- Prefer curated context, explicit file lists, and task-specific retrieval over broad scanning.
- Use `codex_knowledge` for local SOT/project context before broad repo or vault scanning.
- Use Context7 for current third-party library/API documentation when implementation depends on external docs.
- Keep diffs surgical and reversible.
- Do not invent commands, outputs, files, or validation results.
- Ask before dependencies, destructive commands, architecture changes, migrations, or pushes.
- Do not load every skill, rule, workflow, or agent by default.
- Do not use OpenCode in the core path.
- Use one writer per branch.

## PM Gate
- `pm` classifies the request before implementation starts.
- `pm` decides whether the work is atomic, medium, or epic.
- `pm` decides whether to delegate, and to whom.
- `pm` owns the task contract, validation target, and final handoff.

## Delegation
- Subagents are explicit, bounded, and non-overlapping.
- Read-only roles stay read-only.
- Summary-only returns: changed files, evidence, risks, next action.
- No sibling-to-sibling messaging.

## Model Policy
- Default to the strongest Codex-supported coding model available to the account.
- Use the mini/fast model only for cheap reads, summaries, or narrow synthesis.
- If a model name is rejected, fall back to the nearest supported Codex model rather than failing the runtime.

## Loop Policy
- Development: classify, inspect relevant files, patch, validate, summarize.
- QC: independent review, then fix or ship.
- Research: official/current sources first, no mutation.
- Memory capture: only after validation and approval.

## Safety
- Do not auto-learn from unreviewed changes.
- Do not run multiple write-capable agents on the same branch at once.
