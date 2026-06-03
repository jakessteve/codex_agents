# Core Rules

## Default Control Flow
- `pm` is the public gate.
- Codex owns this runtime path.
- Codex is the secondary review and polish path.
- Do not start implementation until the request is enriched, classified, and scoped.

## Context Discipline
- Read curated context first.
- Prefer selected files, task lists, and structured summaries over repo-wide scans.
- Keep raw command output out of the active prompt whenever possible.
- Use `codex_knowledge` before broad search.

## Model Routing
- Codex uses the configured primary model and falls back through configured profiles.
- Subagents use the smallest approved Go role model and only their matching bundle.
- Do not load every skill or bundle at once.

## Delegation
- Delegate only bounded work.
- Give each subagent explicit ownership.
- Do not overlap writes across subagents.
- Keep returns summary-only.
- Use Markdown or YAML contracts only.

## Validation
- Run the task-specific validation command.
- Verify before claiming completion.
- Report what was checked, what passed, and what remains risky.
- Oracle review is required after planning, implementation, validation, and release.

## Safety
- Ask before adding dependencies, deleting files, changing architecture, or pushing.
- Do not auto-capture durable memory without approval.
- Do not run multiple write-capable agents on the same branch at once.
- Keep scope drift under the approved threshold.
