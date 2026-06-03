#!/usr/bin/env bash
set -euo pipefail

wait_http() {
  local url="$1"
  local label="$2"
  local tries="${3:-20}"
  local delay="${4:-3}"
  local attempt=1
  while [ "$attempt" -le "$tries" ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[PASS] $label reachable at $url"
      return 0
    fi
    sleep "$delay"
    attempt=$((attempt + 1))
  done
  echo "[WARN] $label not reachable at $url"
}

wait_http "http://127.0.0.1:3000" "FalkorDB browser"
wait_http "http://127.0.0.1:6006" "Phoenix UI"
wait_http "http://127.0.0.1:8100/api/v2/heartbeat" "ChromaDB"
