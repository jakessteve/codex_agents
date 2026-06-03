#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

compose_args=(-f "$REPO_ROOT/docker-compose.yml" down)

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    exec docker compose "${compose_args[@]}"
  fi
  exec sudo docker compose "${compose_args[@]}"
fi

if command -v docker-compose >/dev/null 2>&1; then
  if docker-compose version >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    exec docker-compose "${compose_args[@]}"
  fi
  exec sudo docker-compose "${compose_args[@]}"
fi

echo "Docker Compose is not available. Nothing to stop." >&2
exit 1
