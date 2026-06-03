#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-run}"
PROJECT_DIR="${2:-${PWD}}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

if [ ! -f "$PROJECT_DIR/package.json" ]; then
  echo "No package.json found in $PROJECT_DIR. Project-native regression is unsupported here." >&2
  exit 1
fi

PACKAGE_MANAGER="npm"
if [ -f "$PROJECT_DIR/pnpm-lock.yaml" ] && command -v pnpm >/dev/null 2>&1; then
  PACKAGE_MANAGER="pnpm"
elif [ -f "$PROJECT_DIR/yarn.lock" ] && command -v yarn >/dev/null 2>&1; then
  PACKAGE_MANAGER="yarn"
elif [ -f "$PROJECT_DIR/bun.lock" ] && command -v bun >/dev/null 2>&1; then
  PACKAGE_MANAGER="bun"
fi

has_package_script() {
  local script_name="$1"
  PROJECT_DIR_ENV="$PROJECT_DIR" SCRIPT_NAME_ENV="$script_name" node <<'NODE' >/dev/null
const fs = require('fs');
const path = require('path');

const projectDir = process.env.PROJECT_DIR_ENV;
const scriptName = process.env.SCRIPT_NAME_ENV;
const pkg = JSON.parse(fs.readFileSync(path.join(projectDir, 'package.json'), 'utf8'));
process.exit(pkg.scripts && Object.prototype.hasOwnProperty.call(pkg.scripts, scriptName) ? 0 : 1);
NODE
}

run_package_script() {
  local script_name="$1"
  case "$PACKAGE_MANAGER" in
    pnpm) (cd "$PROJECT_DIR" && pnpm run "$script_name") ;;
    yarn) (cd "$PROJECT_DIR" && yarn "$script_name") ;;
    bun) (cd "$PROJECT_DIR" && bun run "$script_name") ;;
    *) (cd "$PROJECT_DIR" && npm run "$script_name") ;;
  esac
}

case "$MODE" in
  run)
    if has_package_script regression; then
      run_package_script regression
    elif [ -x "$PROJECT_DIR/scripts/regression.sh" ]; then
      (cd "$PROJECT_DIR" && ./scripts/regression.sh)
    elif has_package_script check; then
      run_package_script check
    elif has_package_script test; then
      run_package_script test
    else
      echo "No project-native regression entrypoint found in $PROJECT_DIR." >&2
      exit 1
    fi
    ;;
  assert-fresh)
    if has_package_script regression:assert-fresh; then
      run_package_script regression:assert-fresh
    elif [ -f "$PROJECT_DIR/scripts/regression-gate.js" ]; then
      (cd "$PROJECT_DIR" && node ./scripts/regression-gate.js assert-fresh)
    else
      echo "No project-native regression freshness gate found in $PROJECT_DIR." >&2
      exit 1
    fi
    ;;
  status)
    if has_package_script regression:status; then
      run_package_script regression:status
    elif [ -f "$PROJECT_DIR/scripts/regression-gate.js" ]; then
      (cd "$PROJECT_DIR" && node ./scripts/regression-gate.js status)
    else
      echo "No project-native regression status entrypoint found in $PROJECT_DIR." >&2
      exit 1
    fi
    ;;
  *)
    echo "Unsupported mode: $MODE" >&2
    echo "Usage: project-regression [run|assert-fresh|status] [project_dir]" >&2
    exit 1
    ;;
esac
