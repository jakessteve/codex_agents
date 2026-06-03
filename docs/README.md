# Codex Runtime Setup

This repository is the source of truth for the local Codex runtime.

## Fresh Install

```bash
./scripts/install-global.sh
./scripts/doctor.sh
```

## What Gets Installed

- `codex-home/AGENTS.md` -> `~/.codex/AGENTS.md`
- `codex-home/agents` -> `~/.codex/agents`
- `codex-home/coordination` -> `~/.codex/coordination`
- `codex-home/contracts` -> `~/.codex/contracts`
- `codex-home/guardrails` -> `~/.codex/guardrails`
- `codex-home/rules` -> `~/.codex/rules`
- `codex-home/skillbank` -> `~/.codex/skillbank`
- `codex-home/skills` -> `~/.codex/skills`
- `codex-home/workflows` -> `~/.codex/workflows`
- `codex-home/config.template.toml` -> managed block in `~/.codex/config.toml`
- `codex-home/bin/*` -> `~/.local/bin/*`

## Codex MCP Services

The managed Codex config wires these services:

- `codex_knowledge`
- `planner`
- `codegraph`
- `graphrag`
- `treesitter`
- `minimalist`
- `cognition_codex`
- `evolution`
- `trace_export`
- `chromadb_mcp`
- `context7`

## Validation

Run:

```bash
./scripts/doctor-codex.sh
./scripts/phase2-health.sh
```

`phase2-health.sh` may warn when optional services such as Phoenix or ChromaDB are not running. The Codex install itself is validated by `doctor-codex.sh`.
