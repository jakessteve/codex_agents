#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
FAILED=0

pass() { printf "[PASS] %s\n" "$1"; }
fail() { printf "[FAIL] %s\n" "$1"; FAILED=1; }
warn() { printf "[WARN] %s\n" "$1"; }

check_cmd() {
  local c="$1"
  if command -v "$c" >/dev/null 2>&1; then pass "command '$c' found"; else warn "command '$c' missing"; fi
}

check_cmd codex
check_cmd codex-safe
check_cmd codex-power
check_cmd codex-yolo
check_cmd codex-exec-power
check_cmd bash
check_cmd sqlite3
check_cmd uv
check_cmd rg

if [ -L "$HOME/.local/bin/codex" ]; then
  pass "standalone codex symlink exists"
else
  fail "standalone codex symlink missing from ~/.local/bin/codex"
fi

if [ -L "$HOME/.local/bin/codex" ]; then
  codex_target="$(readlink "$HOME/.local/bin/codex")"
  case "$codex_target" in
    *".vscode/extensions/"*)
      fail "standalone codex symlink still points at VS Code extension bundle"
      ;;
    *)
      pass "standalone codex symlink avoids VS Code extension bundle"
      ;;
  esac
fi

if [ -L "$CODEX_HOME/AGENTS.md" ]; then pass "AGENTS.md symlink exists"; else fail "AGENTS.md symlink missing"; fi
if [ -L "$CODEX_HOME/agents" ]; then pass "agents symlink exists"; else fail "agents symlink missing"; fi
if [ -L "$CODEX_HOME/rules" ]; then pass "rules symlink exists"; else fail "rules symlink missing"; fi
if [ -L "$CODEX_HOME/workflows" ]; then pass "workflows symlink exists"; else fail "workflows symlink missing"; fi
if [ -d "$CODEX_HOME/skills" ]; then pass "skills directory exists"; else fail "skills directory missing"; fi
if [ -L "$CODEX_HOME/skills/delegate-task" ]; then pass "custom skill symlink exists"; else fail "custom skill symlink missing"; fi

for agent in pm researcher sa dev-fe dev-be designer devops reviewer debugger whitehat user-tester librarian; do
  if [ -f "$CODEX_HOME/agents/$agent.toml" ]; then
    pass "canonical agent '$agent' present"
  else
    fail "canonical agent '$agent' missing"
  fi
done

if [ ! -e "$CODEX_HOME/agents/biz.toml" ]; then pass "retired agent 'biz' absent"; else fail "retired agent 'biz' still present"; fi
if [ ! -e "$CODEX_HOME/agents/explore.toml" ]; then pass "retired agent 'explore' absent"; else fail "retired agent 'explore' still present"; fi

if [ -f "$CODEX_HOME/config.toml" ] && rg -q "BEGIN CODEX_AGENTS_MANAGED" "$CODEX_HOME/config.toml"; then
  pass "managed config block found"
else
  fail "managed config block missing"
fi

if rg -q '^\[mcp_servers\.codex_knowledge\]' "$CODEX_HOME/config.toml"; then
  pass "codex_knowledge MCP config found"
else
  fail "codex_knowledge MCP config missing"
fi

if python3 - "$CODEX_HOME/config.toml" <<'PY' >/dev/null
from pathlib import Path
import sys
path = Path(sys.argv[1])
inside = False
seen_section = False
for line in path.read_text(encoding="utf-8").splitlines():
    if line == "# BEGIN CODEX_AGENTS_MANAGED":
        inside = True
        continue
    if line == "# END CODEX_AGENTS_MANAGED":
        inside = False
        continue
    if inside:
        continue
    stripped = line.strip()
    if stripped.startswith("["):
        seen_section = True
    if not seen_section and stripped.startswith(("model = ", "model_reasoning_effort = ")):
        raise SystemExit(1)
PY
then
  pass "no unmanaged duplicate top-level model keys"
else
  fail "unmanaged duplicate top-level model keys found"
fi

if find "$REPO_ROOT/codex-home" -print | rg -n "antigravity|Antigravity|antigravity_" >/dev/null 2>&1; then
  fail "antigravity marker found in active runtime paths"
else
  pass "no antigravity markers in active runtime paths"
fi

if rg -n "^compatibility:\s*.*antigravity" -S "$REPO_ROOT/codex-home/skills" >/dev/null 2>&1; then
  fail "antigravity compatibility marker found in active skill frontmatter"
else
  pass "no antigravity compatibility marker in active skill frontmatter"
fi

if python3 - "$REPO_ROOT" "$CODEX_HOME" <<'PY' >/dev/null
from pathlib import Path
import sys
repo_root = Path(sys.argv[1]).resolve()
codex_home = Path(sys.argv[2]).resolve()
active = {p.name for p in (repo_root / "codex-home" / "skills").iterdir() if p.is_dir()}
for entry in (codex_home / "skills").iterdir():
    if not entry.is_symlink():
        continue
    target = Path(entry.readlink())
    if str(target).startswith(str(repo_root / "codex-home")) and entry.name not in active:
        raise SystemExit(1)
PY
then
  pass "no stale repo-managed skill symlinks"
else
  fail "stale repo-managed skill symlinks found"
fi

if command -v python3 >/dev/null 2>&1; then
  python3 -m py_compile "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/server.py" && pass "codex_knowledge server.py compiles"
  python3 -m py_compile "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/graph_layer.py" && pass "graph_layer.py compiles"
  python3 -m py_compile "$REPO_ROOT/runtime/codex_knowledge/src/codex_knowledge/workflows.py" && pass "workflows.py compiles"
else
  warn "python3 not found; skipped compile check"
fi

if command -v uv >/dev/null 2>&1; then
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
  warn "uv not found; skipped codex_knowledge helper smoke test"
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
