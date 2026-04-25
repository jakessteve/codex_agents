#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLUG="${1:-codex-agents}"
PROJECT_PATH="${2:-$REPO_ROOT}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Run ./scripts/install-deps.sh first." >&2
  exit 1
fi

echo "Bootstrapping 4 elements for slug: $SLUG"

uv run --project "$REPO_ROOT/runtime/codex_knowledge" python - <<PY
from codex_knowledge.server import project_register, memory_store, graph_upsert

r = project_register("$PROJECT_PATH", "$SLUG")
print("project_register:", r)
memory_store("$SLUG", "bootstrap", "4-element stack initialized")
graph_upsert("$SLUG", "project:$SLUG", "HAS_STACK", "obsidian+memory+graph+langgraph", "{}")
print("bootstrap complete")
PY
