#!/usr/bin/env bash
# Pre-commit hook: runs the architecture audit before allowing a commit.
# Install: ln -sf ../../hooks/pre-commit-audit.sh .git/hooks/pre-commit
# Or configure as a Claude Code PreToolUse hook on Bash(git commit).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIT_SCRIPT="$REPO_ROOT/skills/kotlin-multiplatform-audit/scripts/audit_project.py"

# Only run if Kotlin files are staged
STAGED_KT=$(git diff --cached --name-only | grep -E '\.(kt|kts)$' || true)
if [[ -z "$STAGED_KT" ]]; then
  exit 0
fi

echo "Running architecture audit on staged Kotlin files..."
python3 "$AUDIT_SCRIPT" "$REPO_ROOT"
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
  echo ""
  echo "Commit blocked: architecture audit found issues."
  echo "Run: python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py ."
  echo "Or: /run-audit to see findings with remediation steps."
  exit 1
fi

exit 0
