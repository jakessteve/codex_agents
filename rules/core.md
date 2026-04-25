# Core Rules

## Default Control Flow
- `pm` is the public gate.
- Specialists are internal unless a direct role is explicitly requested.
- Do not start implementation until the task is classified and scoped.

## Context Discipline
- Read curated context first.
- Prefer selected files, task lists, and structured summaries over repo-wide scans.
- Keep raw command output out of the active prompt whenever possible.

## Delegation
- Delegate only bounded work.
- Give each subagent explicit ownership.
- Do not overlap writes across subagents.
- Keep returns summary-only.

## Validation
- Run the task-specific validation command.
- Verify before claiming completion.
- Report what was checked, what passed, and what remains risky.

## Safety
- Ask before adding dependencies, deleting files, changing architecture, or pushing.
- Do not auto-capture durable memory without approval.
- Do not use OpenCode in the default path.
