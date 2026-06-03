#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Phase 2 doctor"

if command -v docker >/dev/null 2>&1; then
  echo "[PASS] docker found"
  if docker info >/dev/null 2>&1; then
    echo "[PASS] docker socket accessible"
  else
    echo "[WARN] docker socket not accessible to current user; phase 2 scripts will fall back to sudo"
  fi
else
  echo "[WARN] docker missing"
fi

if command -v docker-compose >/dev/null 2>&1 || (command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1); then
  echo "[PASS] docker compose available"
else
  echo "[WARN] docker compose missing"
fi

if command -v tree-sitter >/dev/null 2>&1; then
  echo "[PASS] tree-sitter found"
else
  echo "[WARN] tree-sitter missing"
fi

if command -v ast-grep >/dev/null 2>&1; then
  echo "[PASS] ast-grep found"
else
  echo "[WARN] ast-grep missing"
fi

check_mcp_service() {
  local service="$1"
  local module="$2"
  local project_root="$REPO_ROOT/mcp/$service"
  if [ -f "$project_root/pyproject.toml" ]; then
    if uv run --project "$project_root" python - <<PY >/dev/null 2>&1
from $module import mcp
assert getattr(mcp, "name", "") == "$service"
PY
    then
      echo "[PASS] mcp service '$service' imports"
    else
      echo "[FAIL] mcp service '$service' failed to import"
    fi
  else
    echo "[WARN] mcp service '$service' pyproject missing"
  fi
}

check_mcp_service planner planner.server
check_mcp_service codegraph codegraph.server
check_mcp_service graphrag graphrag.server
check_mcp_service minimalist minimalist.server
check_mcp_service treesitter treesitter.server
check_mcp_service cognition_codex cognition.server
check_mcp_service evolution evolution.server
check_mcp_service trace_export trace_export.server
check_mcp_service chromadb chromadb_mcp.server

python3 - <<'PY' "$REPO_ROOT/docker-compose.yml"
import sys
from pathlib import Path
try:
    import yaml
except Exception:
    print("[WARN] PyYAML missing")
    raise SystemExit(0)
path = Path(sys.argv[1])
data = yaml.safe_load(path.read_text(encoding="utf-8"))
services = sorted(data.get("services", {}).keys())
print("[PASS] compose services:", ", ".join(services))
PY

echo "Phase 2 doctor complete."
