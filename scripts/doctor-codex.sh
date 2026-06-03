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

require_file() {
  local path="$1"
  if [ -f "$path" ] && [ ! -L "$path" ]; then
    pass "file present at $path"
  else
    fail "file missing or symlinked at $path"
  fi
}

require_dir() {
  local path="$1"
  if [ -d "$path" ] && [ ! -L "$path" ]; then
    pass "directory present at $path"
  else
    fail "directory missing or symlinked at $path"
  fi
}

check_cmd codex
check_cmd codex-safe
check_cmd codex-power
check_cmd codex-yolo
check_cmd codex-exec-power
check_cmd codex-bootstrap
check_cmd project-regression

require_file "$CODEX_HOME/AGENTS.md"
require_dir "$CODEX_HOME/agents"
require_dir "$CODEX_HOME/coordination"
require_dir "$CODEX_HOME/coordination/gates"
require_dir "$CODEX_HOME/coordination/independent_ensemble"
require_dir "$CODEX_HOME/contracts"
require_dir "$CODEX_HOME/guardrails"
require_file "$CODEX_HOME/guardrails/anti-context-overflow.md"
require_file "$CODEX_HOME/guardrails/claim-verification.md"
require_file "$CODEX_HOME/guardrails/confidence-theater.md"
require_file "$CODEX_HOME/guardrails/dependency-deadlock.md"
require_file "$CODEX_HOME/guardrails/monotonic-progress.md"
require_file "$CODEX_HOME/guardrails/priority-scheduling.md"
require_file "$CODEX_HOME/guardrails/swarm-budget.md"
require_dir "$CODEX_HOME/rules"
require_dir "$CODEX_HOME/skillbank"
require_dir "$CODEX_HOME/workflows"
require_dir "$CODEX_HOME/skills"
require_dir "$CODEX_HOME/skills/delegate-task"
require_dir "$CODEX_HOME/skills/pyrag-reasoning"
require_dir "$CODEX_HOME/skills/multisearch-reasoning"
require_dir "$CODEX_HOME/skills/cognifold-memory"
require_dir "$CODEX_HOME/skills/mcp-knowledge"
require_dir "$CODEX_HOME/skills/graph-memory"
require_dir "$CODEX_HOME/skills/aop-consistency"
require_dir "$CODEX_HOME/skills/dreaming-consolidation"
require_file "$CODEX_HOME/coordination/gates/preflight_gate.md"
require_file "$CODEX_HOME/coordination/gates/oracle_review_rubric.md"
require_file "$CODEX_HOME/coordination/gates/release_gate.md"
require_file "$CODEX_HOME/coordination/gates/abort_gate.md"
require_file "$CODEX_HOME/coordination/gates/revision_gate.md"
require_file "$CODEX_HOME/coordination/gates/escalation_gate.md"
require_file "$CODEX_HOME/coordination/independent_ensemble/orchestrator.md"
require_file "$CODEX_HOME/coordination/independent_ensemble/merge_policy.md"
require_file "$CODEX_HOME/coordination/independent_ensemble/proposal_schema.md"
if [ -e "$CODEX_HOME/skills/cognition-reasoning" ] || [ -e "$CODEX_HOME/skills/cognition-memory" ]; then
  fail "legacy shared cognition skills still present in Codex home"
else
  pass "legacy shared cognition skills removed from Codex home"
fi

for agent in pm researcher sa dev-fe dev-be designer devops reviewer debugger whitehat user-tester librarian minimalist-coder simplifier-reviewer evolution-agent; do
  if [ -f "$CODEX_HOME/agents/$agent.toml" ]; then
    pass "canonical agent '$agent' present"
  else
    fail "canonical agent '$agent' missing"
  fi
done

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

if rg -q '^\[mcp_servers\.graphrag\]' "$CODEX_HOME/config.toml"; then
  pass "graphrag MCP config found"
else
  fail "graphrag MCP config missing"
fi

if rg -q '^\[mcp_servers\.codegraph\]' "$CODEX_HOME/config.toml"; then
  pass "codegraph MCP config found"
else
  fail "codegraph MCP config missing"
fi

if rg -q '^\[mcp_servers\.cognition_codex\]' "$CODEX_HOME/config.toml"; then
  pass "cognition_codex MCP config found"
else
  fail "cognition_codex MCP config missing"
fi

if rg -q '^\[mcp_servers\.chromadb_mcp\]' "$CODEX_HOME/config.toml"; then
  pass "chromadb_mcp MCP config found"
else
  fail "chromadb_mcp MCP config missing"
fi

if rg -q '^\s*memories = true\s*$' "$CODEX_HOME/config.toml"; then
  pass "Codex memories feature enabled"
else
  fail "Codex memories feature disabled"
fi

if rg -q '/mcp/cognition([\"/]|$)' "$CODEX_HOME/config.toml"; then
  fail "Codex config still references legacy shared cognition root"
else
  pass "Codex config avoids legacy shared cognition root"
fi

if [ -f "$REPO_ROOT/mcp/cognition_codex/cognition/server.py" ] && python3 -m py_compile "$REPO_ROOT/mcp/cognition_codex/cognition/server.py"; then
  pass "cognition_codex server.py compiles"
else
  fail "cognition_codex server.py missing or failed to compile"
fi

if [ -f "$REPO_ROOT/mcp/codegraph/codegraph/server.py" ] && python3 -m py_compile "$REPO_ROOT/mcp/codegraph/codegraph/server.py"; then
  pass "codegraph server.py compiles"
else
  fail "codegraph server.py missing or failed to compile"
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

if python3 - "$CODEX_HOME" "$REPO_ROOT" <<'PY' >/dev/null
from pathlib import Path
import sys

codex_home = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
prefix = str(codex_home / "skills")
repo_prefix = str(repo_root / "codex-home" / "skills")
for entry in (codex_home / "agents").glob("*.toml"):
    text = entry.read_text(encoding="utf-8")
    if repo_prefix in text:
        raise SystemExit(1)
    if prefix not in text:
        raise SystemExit(1)
PY
then
  pass "installed Codex agent skill paths point at ~/.codex/skills"
else
  fail "installed Codex agent skill paths still reference repo-local skills"
fi

echo "Codex doctor check complete."
exit "$FAILED"
