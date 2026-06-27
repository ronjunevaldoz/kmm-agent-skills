#!/usr/bin/env bash
# update-consumer-skills.sh — pull the latest kmm-agent-skills and re-deploy
# to the current consumer project.
#
# Run from your KMP project root:
#   bash path/to/kmm-agent-skills/scripts/update-consumer-skills.sh
#
# Options:
#   --source PATH     Path to kmm-agent-skills clone (auto-detected if omitted)
#   --agent-dir PATH  Destination skills directory (auto-detected if omitted)
#   --dry-run         Show what would change without writing anything

set -euo pipefail

SKILLS_SOURCE=""
AGENT_DIR=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)    SKILLS_SOURCE="$2"; shift 2 ;;
    --agent-dir) AGENT_DIR="$2"; shift 2 ;;
    --dry-run)   DRY_RUN=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ── Locate the skills source ──────────────────────────────────────────────────

if [[ -z "$SKILLS_SOURCE" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  CANDIDATE="$(cd "$SCRIPT_DIR/.." && pwd)"

  if [[ -f "$CANDIDATE/skills.json" ]]; then
    SKILLS_SOURCE="$CANDIDATE"
  elif [[ -f "skills/skills.json" ]]; then
    SKILLS_SOURCE="$(cd skills && pwd)"
  elif [[ -f "../kmm-agent-skills/skills.json" ]]; then
    SKILLS_SOURCE="$(cd ../kmm-agent-skills && pwd)"
  elif [[ -f "$HOME/dev/kmm-agent-skills/skills.json" ]]; then
    SKILLS_SOURCE="$HOME/dev/kmm-agent-skills"
  else
    echo "" >&2
    echo "  ❌  Could not find kmm-agent-skills." >&2
    echo "  Pass --source PATH to specify the clone location." >&2
    echo "" >&2
    exit 1
  fi
fi

# ── Detect agent destination ──────────────────────────────────────────────────

if [[ -z "$AGENT_DIR" ]]; then
  if   [[ -d ".claude/skills" ]];             then AGENT_DIR=".claude/skills"
  elif [[ -d ".codex/skills" ]];              then AGENT_DIR=".codex/skills"
  elif [[ -d ".github/copilot/skills" ]];     then AGENT_DIR=".github/copilot/skills"
  elif [[ -d ".cursor/skills" ]];             then AGENT_DIR=".cursor/skills"
  elif [[ -d ".continue/skills" ]];           then AGENT_DIR=".continue/skills"
  else
    echo "" >&2
    echo "  ❌  Could not detect an agent skills directory in the current project." >&2
    echo "  Pass --agent-dir PATH (e.g. --agent-dir .claude/skills)." >&2
    echo "" >&2
    exit 1
  fi
fi

echo ""
echo "  Skills source : $SKILLS_SOURCE"
echo "  Deploy target : $AGENT_DIR"
if $DRY_RUN; then echo "  Mode          : DRY RUN"; fi
echo ""

# ── Read current local version ────────────────────────────────────────────────

OLD_VERSION="?"
if command -v python3 &>/dev/null && [[ -f "$SKILLS_SOURCE/skills.json" ]]; then
  OLD_VERSION=$(python3 -c \
    "import json,sys; print(json.load(open('$SKILLS_SOURCE/skills.json'))['version'])" \
    2>/dev/null || echo "?")
fi

# ── Pull latest ───────────────────────────────────────────────────────────────

echo "Checking for updates…"
git -C "$SKILLS_SOURCE" fetch origin main --quiet 2>/dev/null || {
  echo "  ⚠️  Could not reach remote — running with local skills (v$OLD_VERSION)"
  exit 0
}

BEHIND=$(git -C "$SKILLS_SOURCE" rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

if [[ "$BEHIND" == "0" ]]; then
  echo "  ✅  Already up to date (v$OLD_VERSION)"
  echo ""
  exit 0
fi

if $DRY_RUN; then
  echo "  [dry-run] would pull $BEHIND commit(s) from origin/main"
else
  git -C "$SKILLS_SOURCE" pull origin main --ff-only --quiet
  echo "  ✅  Pulled $BEHIND commit(s) from origin/main"
fi

NEW_VERSION="?"
if command -v python3 &>/dev/null; then
  NEW_VERSION=$(python3 -c \
    "import json,sys; print(json.load(open('$SKILLS_SOURCE/skills.json'))['version'])" \
    2>/dev/null || echo "?")
fi

echo "  ✅  v$OLD_VERSION → v$NEW_VERSION"
echo ""

# ── Deploy skills ─────────────────────────────────────────────────────────────

echo "Deploying skills to $AGENT_DIR…"

if $DRY_RUN; then
  CHANGED=$(git -C "$SKILLS_SOURCE" diff "HEAD@{1}..HEAD" --name-only -- skills/ 2>/dev/null | wc -l | tr -d ' ')
  echo "  [dry-run] would copy $CHANGED changed skill file(s) → $AGENT_DIR/"
else
  cp -r "$SKILLS_SOURCE/skills/"* "$AGENT_DIR/"
  echo "  ✅  Skills deployed"
fi

# ── Changelog excerpt ─────────────────────────────────────────────────────────

CHANGELOG="$SKILLS_SOURCE/CHANGELOG.md"
if [[ -f "$CHANGELOG" ]]; then
  echo ""
  echo "  What changed:"
  awk "/^## \[v$NEW_VERSION\]/{found=1} found && /^---$/{exit} found{print \"    \" \$0}" \
    "$CHANGELOG" | head -20
fi

echo ""
echo "  Done. Run your audit to verify: python3 .claude/skills/kotlin-multiplatform-audit/scripts/audit_project.py ."
echo ""
