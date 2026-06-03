#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"

mkdir -p "$CODEX_HOME" "$LOCAL_BIN"

copy_force() {
  local src="$1" dst="$2"
  rm -rf "$dst"
  mkdir -p "$(dirname "$dst")"
  cp -f "$src" "$dst"
}

copy_tree_force() {
  local src="$1" dst="$2"
  rm -rf "$dst"
  mkdir -p "$(dirname "$dst")"
  cp -a "$src" "$dst"
}

rewrite_agent_skill_paths() {
  local src="$1" dst="$2" from_prefix="$3" to_prefix="$4"
  python3 - "$src" "$dst" "$from_prefix" "$to_prefix" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
from_prefix = sys.argv[3]
to_prefix = sys.argv[4]

text = src.read_text(encoding="utf-8").replace(from_prefix, to_prefix)
dst.write_text(text, encoding="utf-8")
PY
}

rewrite_repo_root_placeholder() {
  local path="$1"
  python3 - "$path" "$REPO_ROOT" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
repo_root = sys.argv[2]
text = path.read_text(encoding="utf-8")
placeholder = "__CODEX_AGENTS_REPO_ROOT__"
if placeholder in text:
    path.write_text(text.replace(placeholder, repo_root), encoding="utf-8")
PY
}

copy_force "$REPO_ROOT/codex-home/AGENTS.md" "$CODEX_HOME/AGENTS.md"
for dir in coordination contracts guardrails rules skillbank workflows; do
  copy_tree_force "$REPO_ROOT/codex-home/$dir" "$CODEX_HOME/$dir"
done

mkdir -p "$CODEX_HOME/skills"
rm -rf "$CODEX_HOME/skills/cognition-reasoning" "$CODEX_HOME/skills/cognition-memory"
declare -A ACTIVE_SKILLS=()
while IFS= read -r -d '' skill_dir; do
  skill_name="$(basename "$skill_dir")"
  ACTIVE_SKILLS["$skill_name"]=1
  copy_tree_force "$skill_dir" "$CODEX_HOME/skills/$skill_name"
done < <(find "$REPO_ROOT/codex-home/skills" -mindepth 1 -maxdepth 1 -type d -print0)

mkdir -p "$CODEX_HOME/agents"
while IFS= read -r -d '' agent_file; do
  agent_name="$(basename "$agent_file")"
  rewrite_agent_skill_paths \
    "$agent_file" \
    "$CODEX_HOME/agents/$agent_name" \
    "$REPO_ROOT/codex-home/skills/" \
    "$CODEX_HOME/skills/"
done < <(find "$REPO_ROOT/codex-home/agents" -mindepth 1 -maxdepth 1 -type f -name '*.toml' -print0)

declare -A ACTIVE_BINS=()
while IFS= read -r -d '' bin_file; do
  bin_name="$(basename "$bin_file")"
  ACTIVE_BINS["$bin_name"]=1
  copy_force "$bin_file" "$LOCAL_BIN/$bin_name"
  rewrite_repo_root_placeholder "$LOCAL_BIN/$bin_name"
done < <(find "$REPO_ROOT/codex-home/bin" -mindepth 1 -maxdepth 1 -type f -print0)

while IFS= read -r -d '' bin_link; do
  bin_name="$(basename "$bin_link")"
  target="$(readlink "$bin_link" || true)"
  case "$target" in
    "$REPO_ROOT"/codex-home/bin/*)
      if [ -z "${ACTIVE_BINS[$bin_name]:-}" ]; then
        rm -f "$bin_link"
      fi
      ;;
  esac
done < <(find "$LOCAL_BIN" -maxdepth 1 -mindepth 1 -type l -print0)

while IFS= read -r -d '' skill_link; do
  skill_name="$(basename "$skill_link")"
  target="$(readlink "$skill_link" || true)"
  case "$target" in
    "$REPO_ROOT"/codex-home/skills/*|"$REPO_ROOT"/codex-home/archive/skills/*)
      if [ -z "${ACTIVE_SKILLS[$skill_name]:-}" ]; then
        rm -f "$skill_link"
      fi
      ;;
  esac
done < <(find "$CODEX_HOME/skills" -maxdepth 1 -mindepth 1 -type l -print0)

CONFIG_FILE="$CODEX_HOME/config.toml"
TEMPLATE_FILE="$REPO_ROOT/codex-home/config.template.toml"
BEGIN="# BEGIN CODEX_AGENTS_MANAGED"
END="# END CODEX_AGENTS_MANAGED"

touch "$CONFIG_FILE"

RAW_TMP="$(mktemp)"
TMP="$(mktemp)"
awk -v b="$BEGIN" -v e="$END" '
  $0==b {skip=1; next}
  $0==e {skip=0; next}
  skip==0 {print}
' "$CONFIG_FILE" > "$RAW_TMP"

awk '
  BEGIN { in_section=0 }
  /^\[/ { in_section=1; print; next }
  /^[[:space:]]*#/ { print; next }
  /^[[:space:]]*$/ { print; next }
  !in_section && ($0 ~ /^model = / || $0 ~ /^model_reasoning_effort = /) { next }
  { print }
' "$RAW_TMP" > "$TMP"

{
  cat "$TMP"
  echo
  echo "$BEGIN"
  cat "$TEMPLATE_FILE"
  echo "$END"
} > "$CONFIG_FILE"

rm -f "$RAW_TMP" "$TMP"

echo "Installed Codex runtime into: $CODEX_HOME and $LOCAL_BIN"
