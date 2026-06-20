#!/usr/bin/env bash
# Runs the lightweight architecture audit after any file edit.
# Claude Code invokes this as a PostToolUse hook on Edit/Write.
# Exits 0 (clean) or 1 (findings) — Claude Code surfaces failures inline.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIT_SCRIPT="$REPO_ROOT/skills/kotlin-multiplatform-audit/scripts/audit_project.py"

# Only run when a Kotlin or build file was modified
MODIFIED_FILE="${1:-}"
if [[ -n "$MODIFIED_FILE" ]]; then
  case "$MODIFIED_FILE" in
    *.kt|*.kts|*.md) ;;
    *) exit 0 ;;
  esac
fi

if [[ ! -f "$AUDIT_SCRIPT" ]]; then
  echo "audit_project.py not found at $AUDIT_SCRIPT" >&2
  exit 1
fi

python3 "$AUDIT_SCRIPT" "$REPO_ROOT"
