#!/usr/bin/env bash
# update-consumer-skills.sh — pull the latest kmm-agent-skills and re-deploy
# to the current consumer project.
#
# Skills (skills/) are copied automatically — they are passive reference docs.
# Commands (commands/) are NOT copied automatically — each file becomes an
# agent-executable slash command and must be reviewed and approved explicitly.
#
# Run from your KMP project root:
#   bash path/to/kmm-agent-skills/scripts/update-consumer-skills.sh
#
# Options:
#   --source PATH        Path to kmm-agent-skills clone (auto-detected if omitted).
#                         Auto-detect checks $KMM_AGENT_SKILLS_SOURCE first — set it
#                         once in your shell profile so every consumer project on this
#                         machine finds the clone without re-prompting.
#   --agent-dir PATH     Destination skills directory (auto-detected if omitted)
#   --commands-dir PATH  Destination for slash commands (default: .claude/commands)
#   --install-commands   List available commands and prompt to install each one
#   --dry-run            Show what would change without writing anything

set -euo pipefail

SKILLS_SOURCE=""
AGENT_DIR=""
COMMANDS_DIR=""
INSTALL_COMMANDS=false
SETUP_AGENTS=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)           SKILLS_SOURCE="$2"; shift 2 ;;
    --agent-dir)        AGENT_DIR="$2"; shift 2 ;;
    --commands-dir)     COMMANDS_DIR="$2"; shift 2 ;;
    --install-commands) INSTALL_COMMANDS=true; shift ;;
    --setup-agents)     SETUP_AGENTS=true; shift ;;
    --dry-run)          DRY_RUN=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ── Locate the skills source ──────────────────────────────────────────────────

if [[ -z "$SKILLS_SOURCE" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  CANDIDATE="$(cd "$SCRIPT_DIR/.." && pwd)"

  if [[ -n "${KMM_AGENT_SKILLS_SOURCE:-}" && -f "$KMM_AGENT_SKILLS_SOURCE/skills.json" ]]; then
    SKILLS_SOURCE="$KMM_AGENT_SKILLS_SOURCE"
  elif [[ -f "$CANDIDATE/skills.json" ]]; then
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
    echo "  Pass --source PATH, or set \$KMM_AGENT_SKILLS_SOURCE once in your shell" >&2
    echo "  profile so every consumer project auto-detects it:" >&2
    echo "    export KMM_AGENT_SKILLS_SOURCE=/path/to/your/kmm-agent-skills" >&2
    echo "" >&2
    exit 1
  fi
fi

# ── Detect agent destination ──────────────────────────────────────────────────

if [[ -z "$AGENT_DIR" ]]; then
  if   [[ -d ".claude/skills" ]];         then AGENT_DIR=".claude/skills"
  elif [[ -d ".codex/skills" ]];          then AGENT_DIR=".codex/skills"
  elif [[ -d ".github/copilot/skills" ]]; then AGENT_DIR=".github/copilot/skills"
  elif [[ -d ".cursor/skills" ]];         then AGENT_DIR=".cursor/skills"
  elif [[ -d ".continue/skills" ]];       then AGENT_DIR=".continue/skills"
  else
    echo "" >&2
    echo "  ❌  Could not detect an agent skills directory in the current project." >&2
    echo "  Pass --agent-dir PATH (e.g. --agent-dir .claude/skills)." >&2
    echo "" >&2
    exit 1
  fi
fi

# Default commands dir mirrors the agent dir's parent (e.g. .claude/commands)
if [[ -z "$COMMANDS_DIR" ]]; then
  AGENT_PARENT="$(dirname "$AGENT_DIR")"
  COMMANDS_DIR="$AGENT_PARENT/commands"
fi

echo ""
echo "  Skills source : $SKILLS_SOURCE"
echo "  Skills target : $AGENT_DIR"
echo "  Commands dir  : $COMMANDS_DIR (manual install only)"
if $DRY_RUN; then echo "  Mode          : DRY RUN"; fi
echo ""

# ── Read current local version ────────────────────────────────────────────────

OLD_VERSION="?"
if command -v python3 &>/dev/null && [[ -f "$SKILLS_SOURCE/skills.json" ]]; then
  OLD_VERSION=$(python3 -c \
    "import json; print(json.load(open('$SKILLS_SOURCE/skills.json'))['version'])" \
    2>/dev/null || echo "?")
fi

# ── Pull latest ───────────────────────────────────────────────────────────────

echo "Checking for updates…"
REMOTE_OK=true
git -C "$SKILLS_SOURCE" fetch origin main --quiet 2>/dev/null || {
  echo "  ⚠️  Could not reach remote — continuing with local skills (v$OLD_VERSION)"
  REMOTE_OK=false
}

BEHIND="0"
if $REMOTE_OK; then
  BEHIND=$(git -C "$SKILLS_SOURCE" rev-list HEAD..origin/main --count 2>/dev/null || echo "0")
fi

if [[ "$BEHIND" == "0" ]]; then
  echo "  ✅  Already up to date (v$OLD_VERSION)"
else
  if $DRY_RUN; then
    echo "  [dry-run] would pull $BEHIND commit(s) from origin/main"
  else
    git -C "$SKILLS_SOURCE" pull origin main --ff-only --quiet
    echo "  ✅  Pulled $BEHIND commit(s) from origin/main"
  fi
fi

NEW_VERSION="?"
if command -v python3 &>/dev/null; then
  NEW_VERSION=$(python3 -c \
    "import json; print(json.load(open('$SKILLS_SOURCE/skills.json'))['version'])" \
    2>/dev/null || echo "?")
fi

echo "  ✅  v$OLD_VERSION → v$NEW_VERSION"
echo ""

# ── Deploy skills (auto — passive reference docs) ─────────────────────────────

echo "Deploying skills to ${AGENT_DIR}…"

if $DRY_RUN; then
  CHANGED=$(git -C "$SKILLS_SOURCE" diff "HEAD@{1}..HEAD" --name-only -- skills/ 2>/dev/null | wc -l | tr -d ' ')
  echo "  [dry-run] would copy $CHANGED changed skill file(s) → $AGENT_DIR/"
else
  cp -r "$SKILLS_SOURCE/skills/"* "$AGENT_DIR/"
  echo "  ✅  Skills deployed"
fi

# ── Deploy project-owned custom skills (auto — source of truth at ./skills) ──

echo ""
echo "Syncing project-owned custom skills…"

CUSTOM_SKILLS_COUNT=0
if [[ -d "skills" ]]; then
  for skill_dir in skills/*; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    [[ "$skill_name" == "README.md" ]] && continue
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    CUSTOM_SKILLS_COUNT=$((CUSTOM_SKILLS_COUNT + 1))

    if [[ -d "$SKILLS_SOURCE/skills/$skill_name" ]]; then
      echo "  ❌  project-owned skill '$skill_name' collides with a bundled kmm-agent-skills skill."
      echo "      Rename the project-owned skill (for example, make it app-specific) and run again."
      exit 1
    fi

    target="$AGENT_DIR/$skill_name"
    if $DRY_RUN; then
      echo "  [dry-run] would sync $skill_dir/ → $target/"
      continue
    fi

    mkdir -p "$target"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete "$skill_dir/" "$target/"
    else
      rm -rf "$target"
      mkdir -p "$AGENT_DIR"
      cp -R "$skill_dir" "$AGENT_DIR/"
    fi
    echo "  ✅  project skill synced: $skill_name"
  done
fi

if [[ "$CUSTOM_SKILLS_COUNT" == "0" ]]; then
  echo "  ℹ️   No project-owned custom skills found under ./skills/"
fi

# ── Changelog excerpt ─────────────────────────────────────────────────────────

CHANGELOG="$SKILLS_SOURCE/CHANGELOG.md"
if [[ -f "$CHANGELOG" ]]; then
  echo ""
  echo "  What changed:"
  awk "/^## \[v$NEW_VERSION\]/{found=1} found && /^---$/{exit} found{print \"    \" \$0}" \
    "$CHANGELOG" | head -20
fi

# ── Commands (manual — require explicit approval) ─────────────────────────────

echo ""
echo "  ⚠️  Slash commands were NOT copied automatically."
echo "  Commands tell the agent to run shell operations and must be reviewed"
echo "  before install. Use --install-commands to review and approve each one."
echo ""

if $INSTALL_COMMANDS; then
  COMMANDS_SRC="$SKILLS_SOURCE/commands"
  if [[ ! -d "$COMMANDS_SRC" ]]; then
    echo "  No commands/ directory found in $SKILLS_SOURCE"
  else
    mkdir -p "$COMMANDS_DIR"
    echo "  Available commands (review each before approving):"
    echo ""

    for cmd_file in "$COMMANDS_SRC"/*.md; do
      [[ -f "$cmd_file" ]] || continue
      cmd_name="$(basename "$cmd_file" .md)"
      first_line="$(head -1 "$cmd_file")"
      dest="$COMMANDS_DIR/$(basename "$cmd_file")"

      if [[ -f "$dest" ]]; then
        status="[installed]"
      else
        status="[new]"
      fi

      echo "  $status /$cmd_name"
      echo "         $first_line"
      echo "         Source: $cmd_file"
      echo ""

      if ! $DRY_RUN; then
        printf "  Install /%s? [y/N] " "$cmd_name"
        read -r answer </dev/tty
        if [[ "$answer" =~ ^[Yy]$ ]]; then
          cp "$cmd_file" "$dest"
          echo "  ✅  /$cmd_name installed"
        else
          echo "  —  /$cmd_name skipped"
        fi
        echo ""
      fi
    done

    if $DRY_RUN; then
      echo "  [dry-run] would prompt to install each command above"
    fi
  fi
fi

# ── Agent setup (--setup-agents) ─────────────────────────────────────────────

if $SETUP_AGENTS; then
  CLAUDE_DIR="$(dirname "$AGENT_DIR")"
  AGENTS_MD="$CLAUDE_DIR/AGENTS.md"
  ROOT_CLAUDE_MD="CLAUDE.md"
  AI_COLLAB_DOC="docs/reference/ai-collaboration.md"
  AGENT_CATALOG_DOC="docs/reference/agent-catalog.md"
  SOURCE_READMES=(
    "agents/README.md"
    "rules/README.md"
    "hooks/README.md"
    "commands/README.md"
    "skills/README.md"
  )

  echo ""
  echo "Setting up agent configuration…"

  for readme in "${SOURCE_READMES[@]}"; do
    if [[ -f "$readme" ]]; then
      echo "  ✓  $readme already exists"
      continue
    fi

    if $DRY_RUN; then
      echo "  [dry-run] would create $readme"
      continue
    fi

    mkdir -p "$(dirname "$readme")"
    case "$readme" in
      "agents/README.md")
        cat > "$readme" <<'EOF'
# agents/

Project-specific agent personas live here as the canonical source.
Deploy copies into `.claude/` after edits; do not keep `.claude/` as the only copy.
EOF
        ;;
      "rules/README.md")
        cat > "$readme" <<'EOF'
# rules/

Optional project-specific assistant rules or overlays live here.
Do not duplicate the canonical policy from `docs/reference/ai-collaboration.md`; keep this folder for short assistant-facing overlays only.
EOF
        ;;
      "hooks/README.md")
        cat > "$readme" <<'EOF'
# hooks/

Project-owned hook scripts live here.
Wire them through `.claude/settings.json`; do not author the only copy inside runtime config.
EOF
        ;;
      "commands/README.md")
        cat > "$readme" <<'EOF'
# commands/

Project-specific slash command sources live here.
Deploy copies into `.claude/commands/` after edits.
EOF
        ;;
      "skills/README.md")
        cat > "$readme" <<'EOF'
# skills/

Project-specific skills live flat under `skills/<skill-name>/`.
Keep `SKILL.md` as the canonical source and deploy copies into `.claude/skills/`.

Minimal starter:

```md
skills/my-project-skill/SKILL.md
---
name: my-project-skill
description: Short trigger-oriented description of what this skill handles.
---

## When to Use This Skill
- Use this for project-specific work only.

## Rules
- Keep this skill project-owned.
- Re-deploy after edits so `.claude/skills/my-project-skill/` stays in sync.
```
EOF
        ;;
    esac
    echo "  ✅  $readme created"
  done

  if [[ -f "$AI_COLLAB_DOC" ]]; then
    echo "  ✓  $AI_COLLAB_DOC already exists"
  else
    if $DRY_RUN; then
      echo "  [dry-run] would create $AI_COLLAB_DOC"
    else
      mkdir -p "$(dirname "$AI_COLLAB_DOC")"
      cat > "$AI_COLLAB_DOC" <<'EOF'
# AI Collaboration

## Canonical project-owned sources

- `agents/` — project-specific agent personas
- `rules/` — optional project-specific assistant overlays only
- `hooks/` — hook script source
- `commands/` — slash command source
- `skills/` — project-owned skills

## Docs vs skills

- `docs/*` answers "how is this project designed?"
- `skills/*` answers "how should an agent work in this repo?"

## Claude runtime

- `CLAUDE.md` stays thin and boots Claude into `.claude/AGENTS.md`
- `.claude/AGENTS.md` is the deployed routing/context copy
- `.claude/settings.json` owns runtime permissions and hook wiring
- `.claude/commands/` and `.claude/skills/` are deployed copies, not the only source

## Duplication rule

Keep the collaboration policy canonical in this file.
Use `rules/` only for small assistant-facing overlays; do not mirror this whole document there.

## Maintenance rule

Edit project-owned artifacts first, then re-deploy the changed copy into `.claude/`.
EOF
      echo "  ✅  $AI_COLLAB_DOC created"
    fi
  fi

  if [[ -f "$AGENT_CATALOG_DOC" ]]; then
    echo "  ✓  $AGENT_CATALOG_DOC already exists"
  else
    if $DRY_RUN; then
      echo "  [dry-run] would create $AGENT_CATALOG_DOC"
    else
      mkdir -p "$(dirname "$AGENT_CATALOG_DOC")"
      cat > "$AGENT_CATALOG_DOC" <<'EOF'
# Agent Catalog

Use provider-neutral model tiers:

- `flagship-coding`
- `balanced-coding`
- `fast-utility`
- `precision-review`

Keep provider-specific model mapping in this one canonical doc, not in every agent file.

Thin entrypoints like `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` should point here instead of hardcoding stale provider model names.
EOF
      echo "  ✅  $AGENT_CATALOG_DOC created"
    fi
  fi

  if [[ -f "$AGENTS_MD" ]]; then
    echo "  ⚠️  $AGENTS_MD already exists — skipping (run /kmm-setup-agents to regenerate)."
  else
    # Detect project name from settings.gradle.kts
    PROJECT_NAME="KMP Project"
    for f in settings.gradle.kts settings.gradle; do
      if [[ -f "$f" ]]; then
        PROJECT_NAME=$(grep 'rootProject.name' "$f" | head -1 | sed 's/.*= *"//;s/".*//')
        break
      fi
    done

    if $DRY_RUN; then
      echo "  [dry-run] would write $AGENTS_MD for project: $PROJECT_NAME"
    else
      cat > "$AGENTS_MD" <<AGENTS_EOF
# AGENTS.md — $PROJECT_NAME

This project uses [kmm-agent-skills](https://github.com/ronjunevaldoz/kmm-agent-skills).
Skills are installed in \`.claude/skills/\`.

## Skill routing

| Topic | Skill |
|---|---|
| New feature end-to-end | \`kotlin-multiplatform-feature-scaffold\` → \`kotlin-multiplatform-clean-architecture\` → \`kotlin-multiplatform-mvi\` |
| ViewModel / screen state | \`kotlin-multiplatform-mvi\` |
| Navigation | \`kotlin-multiplatform-navigation\` |
| Dependency injection | \`kotlin-multiplatform-dependency-injection\` |
| Design system | \`kotlin-multiplatform-design-system\` |
| Unit tests | \`kotlin-multiplatform-unit-testing\` |
| Architecture audit | \`kotlin-multiplatform-audit\` |

## Commands installed

See \`.claude/commands/kmm-*.md\` for available slash commands.
Key commands:
- \`/kmm-implement-feature <name>\` — plan → implement → validate → review a new feature
- \`/kmm-run-audit\` — run architecture audit with per-finding remediation
- \`/kmm-verify\` — full validation pipeline (tests, audit, design, screenshots)
- \`/kmm-execute-ticket <id>\` — implement a GitHub issue end-to-end
- \`/kmm-fix-design\` — scan and fix design system violations
- \`/kmm-update-skills\` — pull latest skills and re-deploy
AGENTS_EOF
      echo "  ✅  $AGENTS_MD generated"
      echo "  ℹ️   Run /kmm-setup-agents for a version tailored to your module graph"
    fi
  fi

  if [[ -f "$ROOT_CLAUDE_MD" ]]; then
    echo "  ✓  $ROOT_CLAUDE_MD already exists"
  else
    if $DRY_RUN; then
      echo "  [dry-run] would write $ROOT_CLAUDE_MD"
    else
      cat > "$ROOT_CLAUDE_MD" <<'EOF'
### Claude Code Project Profile

### Load skills context on initialization
--system-prompt-file=".claude/AGENTS.md"

### Default flags
--compact
--verbose=false

### Canonical project-owned agent sources
- docs/reference/ai-collaboration.md
- docs/reference/agent-catalog.md
- agents/
- rules/     (optional overlays only)
- hooks/
- commands/
- skills/

### Ignore generated and vendor directories
--ignore="**/build/**"
--ignore="**/.gradle/**"
--ignore="**/vendor/**"
--ignore="**/third_party/**"
EOF
      echo "  ✅  $ROOT_CLAUDE_MD generated"
    fi
  fi

  SETTINGS_JSON="$CLAUDE_DIR/settings.json"
  if [[ -f "$SETTINGS_JSON" ]]; then
    echo "  ✓  $SETTINGS_JSON already exists"
  else
    if $DRY_RUN; then
      echo "  [dry-run] would write $SETTINGS_JSON"
    else
      mkdir -p "$CLAUDE_DIR"
      cat > "$SETTINGS_JSON" <<'EOF'
{
  "permissions": {
    "allow": [
      "Bash(./gradlew *)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(python3 .claude/skills/kotlin-multiplatform-audit/scripts/*)",
      "Bash(find . -name *.kt*)",
      "Bash(grep *)"
    ]
  }
}
EOF
      echo "  ✅  $SETTINGS_JSON generated"
    fi
  fi
fi

echo "  Done. Run your audit to verify:"
echo "  python3 $AGENT_DIR/kotlin-multiplatform-audit/scripts/audit_project.py ."
echo ""
