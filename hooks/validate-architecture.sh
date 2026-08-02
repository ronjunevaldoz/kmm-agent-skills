#!/usr/bin/env bash
# Runs the lightweight architecture audit after any file edit.
# Claude Code invokes this as a PostToolUse hook on Edit/Write.
# Exits 0 (clean) or 1 (findings) — Claude Code surfaces failures inline.
#
# Usage: validate-architecture.sh [modified-file] [project-root]
#   modified-file  Path of the file that was just edited (optional).
#                  Non-.kt/.kts/.md files are skipped immediately.
#   project-root   Directory to audit (optional, default: repo root).
#                  Useful for tests that need to point at a clean temp project.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIT_SCRIPT="$REPO_ROOT/skills/kmp-audit/scripts/audit_project.py"

# Optional overrides for testability
MODIFIED_FILE="${1:-}"
PROJECT_ROOT="${2:-$REPO_ROOT}"

# Only run when a Kotlin or build file was modified
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

python3 "$AUDIT_SCRIPT" "$PROJECT_ROOT"
