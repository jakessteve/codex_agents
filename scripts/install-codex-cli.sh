#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"
NPM_PREFIX="${NPM_PREFIX:-$(npm config get prefix)}"
NPM_BIN_DIR="$NPM_PREFIX/bin"
STANDALONE_CODEX="$NPM_BIN_DIR/codex"
PUBLIC_CODEX="$LOCAL_BIN/codex"
BEFORE_CODEX="$(command -v codex || true)"
BEFORE_VERSION="$(codex --version 2>/dev/null || true)"
BEFORE_LOGIN="$(codex login status 2>/dev/null || true)"

mkdir -p "$LOCAL_BIN"

echo "Current codex on PATH: ${BEFORE_CODEX:-missing}"
if [ -n "$BEFORE_VERSION" ]; then
  echo "Current codex version: $BEFORE_VERSION"
fi
if [ -n "$BEFORE_LOGIN" ]; then
  echo "$BEFORE_LOGIN"
fi

echo "Installing standalone Codex CLI with npm into: $NPM_PREFIX"
npm i -g @openai/codex@latest

if [ ! -x "$STANDALONE_CODEX" ]; then
  echo "Expected standalone Codex binary missing at $STANDALONE_CODEX" >&2
  exit 1
fi

ln -sfn "$STANDALONE_CODEX" "$PUBLIC_CODEX"

"$REPO_ROOT/scripts/install-global.sh"

AFTER_CODEX="$(command -v codex || true)"
AFTER_VERSION="$(codex --version 2>/dev/null || true)"
AFTER_LOGIN="$(codex login status 2>/dev/null || true)"

echo
echo "Standalone codex symlink: $PUBLIC_CODEX -> $(readlink "$PUBLIC_CODEX")"
echo "Resolved codex on PATH: ${AFTER_CODEX:-missing}"
if [ -n "$AFTER_VERSION" ]; then
  echo "Resolved codex version: $AFTER_VERSION"
fi
if [ -n "$AFTER_LOGIN" ]; then
  echo "$AFTER_LOGIN"
fi

if [ "$AFTER_CODEX" != "$PUBLIC_CODEX" ]; then
  echo "Warning: PATH does not currently resolve codex to $PUBLIC_CODEX" >&2
fi

echo "Run 'which -a codex' to confirm the standalone CLI precedes the VS Code extension bundle."
