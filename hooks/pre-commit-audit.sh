#!/usr/bin/env bash
# Pre-commit hook: runs the architecture audit before allowing a commit.
# Install: ln -sf ../../hooks/pre-commit-audit.sh .git/hooks/pre-commit
# Or configure as a Claude Code PreToolUse hook on Bash(git commit).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIT_SCRIPT="$REPO_ROOT/skills/kmp-audit/scripts/audit_project.py"
# tests/ was split from one monolithic test_skill_scripts.py into one file per
# script (tests/test_<script-name>.py, plus a shared tests/_helpers.py) — match any
# test file, not one hardcoded name.
TEST_FILE_PATTERN='^tests/test_.*\.py$'

STAGED=$(git diff --cached --name-only)

# --- Check 1: architecture audit on Kotlin files ---
STAGED_KT=$(echo "$STAGED" | grep -E '\.(kt|kts)$' || true)
if [[ -n "$STAGED_KT" ]]; then
  echo "Running architecture audit on staged Kotlin files..."
  python3 "$AUDIT_SCRIPT" "$REPO_ROOT"
  STATUS=$?
  if [[ $STATUS -ne 0 ]]; then
    echo ""
    echo "Commit blocked: architecture audit found issues."
    echo "Run: python3 skills/kmp-audit/scripts/audit_project.py ."
    echo "Or: /run-audit to see findings with remediation steps."
    exit 1
  fi
fi

# --- Check 2: Python script changes must include test updates ---
STAGED_PY=$(echo "$STAGED" | grep -E '^(scripts/|skills/.*/scripts/).*\.py$' || true)
STAGED_TEST=$(echo "$STAGED" | grep -E "$TEST_FILE_PATTERN" || true)
if [[ -n "$STAGED_PY" ]] && [[ -z "$STAGED_TEST" ]]; then
  echo ""
  echo "Commit blocked: Python scripts changed without updating a tests/test_*.py file"
  echo ""
  echo "Changed scripts:"
  echo "$STAGED_PY" | sed 's/^/  /'
  echo ""
  echo "Add or update the matching tests/test_<script-name>.py then re-stage it before committing."
  echo "Pattern: see existing test files under tests/ for examples."
  exit 1
fi

exit 0
