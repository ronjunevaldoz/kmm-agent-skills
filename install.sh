#!/usr/bin/env bash
# install.sh — clone kmm-agent-skills into a tmp dir and sync the release into
# local assistant skill bundles (~/.claude/skills, ~/.codex/skills, ~/.gemini/skills).
#
# For anyone without a local checkout yet. If you already have this repo cloned,
# just run scripts/sync-local-assistant-skills.sh directly instead — no need to
# clone into tmp again.
#
# Usage: bash install.sh
#    or: curl -fsSL https://raw.githubusercontent.com/ronjunevaldoz/kmm-agent-skills/main/install.sh | bash

set -euo pipefail

REPO_URL="https://github.com/ronjunevaldoz/kmm-agent-skills.git"

if ! command -v git &>/dev/null; then
  echo "  ❌  git not found." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Cloning kmm-agent-skills into $TMP_DIR..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR"

echo ""
bash "$TMP_DIR/scripts/sync-local-assistant-skills.sh" --source "$TMP_DIR"
