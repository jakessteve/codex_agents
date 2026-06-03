# Codex Runtime Contract

## Role
This repository is the Codex-only source of truth for the local Codex runtime.

## Fresh Setup
From a fresh clone, run:

```bash
./scripts/install-global.sh
./scripts/doctor.sh
```

This installs the native Codex home from `codex-home/`, installs Codex launchers from `codex-home/bin/`, and validates the shared Codex MCP/runtime services.

## Native Source Of Truth
- Codex home source: `codex-home/`
- Installed Codex home: `~/.codex`
- Shared Codex runtime services: `runtime/codex_knowledge/` and `mcp/`
- Install entrypoint: `scripts/install-codex-runtime.sh`
- Health entrypoint: `scripts/doctor-codex.sh`

## SOL Pipeline
Follow the Structured Orchestration Lifecycle for medium-to-epic tasks:
1. **Clarify Gate**: resolve ambiguities and emit task contract.
2. **3-Explore Phase**: run backend, frontend, and research exploration.
3. **Scope Lock Gate**: freeze atomic tasks and validation targets.
4. **Harness Activation Gate**: select task-scoped skills, rules, workflows, and MCP tools.
5. **Plan Review Gate**: Oracle reviews plan completeness and scope fit.
6. **Implementation Gate**: execute only the approved plan.
7. **Final Review Gate**: verify tests, scope adherence, harness adherence, and release readiness.

## Operating Rules
- Read the current task context first when one exists.
- Use `codex_knowledge` for local project context before broad repo or vault scanning.
- Use CodeGraph-first exploration through `codegraph_*` facade tools before grep/read.
- Use Context7 for current external library/API documentation when a live reference is needed.
- Keep diffs surgical and reversible.
- Do not invent commands, outputs, files, validation results, or tool availability.
- Ask before dependencies, destructive commands, architecture changes, migrations, or pushes.
- Do not load every skill, rule, workflow, or agent by default.
- Use one writer per branch or worktree.
- Oracle review is mandatory after each major phase.
- Agents and subagents communicate through Markdown or YAML contracts only.

## Safety
- Do not auto-learn from unreviewed changes.
- Record memory only after validation and approval.
- If the project exposes a native regression gate, use `project-regression assert-fresh` before broad edits and `project-regression run` before completion.
