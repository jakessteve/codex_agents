#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

pass() { printf "[PASS] %s\n" "$1"; }
fail() { printf "[FAIL] %s\n" "$1"; FAILED=1; }
warn() { printf "[WARN] %s\n" "$1"; }

check_cmd() {
  local c="$1"
  if command -v "$c" >/dev/null 2>&1; then pass "command '$c' found"; else warn "command '$c' missing"; fi
}

check_cmd bash
check_cmd sqlite3
check_cmd uv
check_cmd rg
check_cmd tree-sitter
check_cmd ast-grep
check_cmd grpcurl
check_cmd ctx7

"$REPO_ROOT/scripts/doctor-codex.sh" || FAILED=1

if [ -f "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/server.py" ]; then
  python3 -m py_compile "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/server.py" && pass "codex_knowledge server.py compiles" || FAILED=1
  python3 -m py_compile "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/graph_layer.py" && pass "graph_layer.py compiles" || FAILED=1
  python3 -m py_compile "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/workflows.py" && pass "workflows.py compiles" || FAILED=1
else
  warn "codex_knowledge runtime sources missing; skipped compile checks"
fi

if command -v uv >/dev/null 2>&1 && [ -f "$REPO_ROOT/runtime/codex_knowledge/pyproject.toml" ]; then
  uv run --project "$REPO_ROOT/runtime/codex_knowledge" python - <<'PY' >/dev/null
from codex_knowledge.server import (
    graph_neighbors,
    handoff_checkpoint,
    knowledge_capture,
    orchestration_lesson,
    project_context,
    project_index,
)
assert callable(project_index)
assert callable(project_context)
assert callable(graph_neighbors)
assert callable(knowledge_capture)
assert callable(handoff_checkpoint)
assert callable(orchestration_lesson)
PY
  pass "codex_knowledge router and persistence helpers import"
else
  warn "uv or codex_knowledge project missing; skipped codex_knowledge helper smoke test"
fi

if command -v codex >/dev/null 2>&1; then
  if codex login status >/tmp/codex-login-status.$$ 2>/dev/null; then
    pass "codex login status succeeded"
    cat /tmp/codex-login-status.$$
  else
    warn "codex login status failed; re-auth may be required"
  fi
  rm -f /tmp/codex-login-status.$$
fi

echo "Doctor check complete."
exit "$FAILED"
