#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_PATH="${1:-${PWD:-}}"
SLUG="${2:-}"

if [ -z "$PROJECT_PATH" ] || [ ! -d "$PROJECT_PATH" ]; then
  echo "Usage: $0 <project-path> [slug]" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Run ./scripts/install-deps.sh first." >&2
  exit 1
fi

uv run --project "$REPO_ROOT/runtime/codex_knowledge" python - "$PROJECT_PATH" "$SLUG" <<'PY'
from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from codex_knowledge.server import graph_upsert, memory_store, project_register, project_index, vault_write

project_path = Path(sys.argv[1]).resolve()
slug_arg = sys.argv[2].strip() or None

pp = project_register(str(project_path), slug_arg)
slug = pp["slug"]
vault_root = Path(pp["vault_root"])

ignored_parts = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".turbo",
    ".venv",
    "venv",
    "vendor",
}
imported = 0
source_docs = []

for md in sorted(project_path.rglob("*.md")):
    if any(part in ignored_parts for part in md.parts):
        continue
    rel = md.relative_to(project_path)
    dest = vault_root / "raw" / "docs" / slug / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(md, dest)
    imported += 1
    source_docs.append(str(rel))

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
bootstrap_note = f"""# Bootstrap

status: initialized
slug: {slug}
project_path: {project_path}
vault_root: {vault_root}
imported_markdown_files: {imported}
initialized_at: {timestamp}

## Stack

- local SOT
- dynamic memory
- graphDB
- LangGraph workflows

## Notes

This project was registered through codex-bootstrap.
"""
vault_write(slug, "sot/bootstrap.md", bootstrap_note)

memory_store(
    slug,
    "bootstrap:stack",
    f"Bootstrap initialized for {project_path} with {imported} markdown files imported into local SOT.",
)
graph_upsert(slug, f"project:{slug}", "HAS_STACK", "local-sot+dynamic-memory+graphdb+langgraph", "bootstrap")
graph_upsert(slug, f"project:{slug}", "HAS_BOOTSTRAP_NOTE", "sot/bootstrap.md", "bootstrap")
if source_docs:
    graph_upsert(slug, f"project:{slug}", "HAS_SOURCE_DOCS", f"raw/docs/{slug}", str(len(source_docs)))

index = project_index(slug)

print("project_register:", pp)
print("bootstrap_note:", str(vault_root / "sot/bootstrap.md"))
print("imported_markdown_files:", imported)
print("document_count:", index.get("index_stats", {}).get("document_count", 0))
PY
