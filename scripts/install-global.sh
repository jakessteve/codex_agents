#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"
mkdir -p "$CODEX_HOME"
mkdir -p "$LOCAL_BIN"

link_force() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ] || [ -e "$dst" ]; then
    rm -rf "$dst"
  fi
  ln -s "$src" "$dst"
}

link_force "$REPO_ROOT/codex-home/AGENTS.md" "$CODEX_HOME/AGENTS.md"
link_force "$REPO_ROOT/codex-home/agents" "$CODEX_HOME/agents"
link_force "$REPO_ROOT/codex-home/rules" "$CODEX_HOME/rules"
link_force "$REPO_ROOT/codex-home/workflows" "$CODEX_HOME/workflows"

# Link repo-managed CLI launchers into ~/.local/bin so shared runtime policy stays centralized.
declare -A ACTIVE_BINS=()
while IFS= read -r -d '' bin_file; do
  bin_name="$(basename "$bin_file")"
  ACTIVE_BINS["$bin_name"]=1
  chmod +x "$bin_file"
  link_force "$bin_file" "$LOCAL_BIN/$bin_name"
done < <(find "$REPO_ROOT/codex-home/bin" -mindepth 1 -maxdepth 1 -type f -print0 2>/dev/null || true)

# Prune stale repo-managed launcher links while leaving user-managed binaries alone.
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

# Do not replace ~/.codex/skills entirely because it may contain system or plugin skills.
mkdir -p "$CODEX_HOME/skills"
declare -A ACTIVE_SKILLS=()
while IFS= read -r -d '' skill_dir; do
  skill_name="$(basename "$skill_dir")"
  ACTIVE_SKILLS["$skill_name"]=1
  link_force "$skill_dir" "$CODEX_HOME/skills/$skill_name"
done < <(find "$REPO_ROOT/codex-home/skills" -mindepth 1 -maxdepth 1 -type d -print0)

# Prune stale repo-managed skill links while leaving system and plugin entries alone.
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

# Remove unmanaged duplicate top-level model keys so the managed block stays authoritative.
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

rm -f "$RAW_TMP"
rm -f "$TMP"

echo "Installed global symlinks, linked CLI launchers, and merged managed config block into: $CONFIG_FILE"
