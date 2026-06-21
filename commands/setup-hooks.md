# /setup-hooks

**KMM Agent Skills** — wire the three provided hooks into your project so the pipeline
enforces architecture rules automatically, without requiring you to remember to run them.

There are two independent integration points: **git hooks** (for your local repo) and
**Claude Code hooks** (for the AI agent). Both are optional but strongly recommended.

---

## The three hooks

| Hook file | What it does | When it runs |
|---|---|---|
| `hooks/pre-commit-audit.sh` | Runs `audit_project.py` before any commit touching `.kt`/`.kts` files. Blocks the commit if architecture smells are found. | `git commit` |
| `hooks/validate-architecture.sh` | Runs `audit_project.py` after any file edit. Surfaces findings inline in the agent's output. | After every `Edit`/`Write` |
| `hooks/check-skill-freshness.sh` | Warns when a skill's `last-updated` is >90 days old. Non-blocking. | Manually or scheduled CI |

---

## Option A — Git pre-commit hook (local repo)

Links `pre-commit-audit.sh` into your project's `.git/hooks/` so it runs automatically
on every `git commit`:

```bash
# Run from your KMP project root (not the skills repo root):
ln -sf "<path-to-skills-repo>/hooks/pre-commit-audit.sh" .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Test it:
```bash
# Should print "Running architecture audit..." and exit 0 on a clean project
git commit --allow-empty -m "test hook"
```

To remove:
```bash
rm .git/hooks/pre-commit
```

---

## Option B — Claude Code PostToolUse hook (agent auto-check)

Configures Claude Code to run `validate-architecture.sh` after every file edit. This
means architecture issues appear in the agent's output immediately after writing code,
not only when a commit is made.

Add to your Claude Code `settings.json` (open via **Claude Code → Settings → Hooks**):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "<path-to-skills-repo>/hooks/validate-architecture.sh \"$CLAUDE_TOOL_INPUT_FILE_PATH\""
          }
        ]
      }
    ]
  }
}
```

Replace `<path-to-skills-repo>` with the absolute path to the skills repo on your machine.

**Effect:** after the agent edits any `.kt`, `.kts`, or `.md` file, the audit runs
automatically. If it finds a smell, the result appears in the tool output and the agent
will address it before continuing.

---

## Option C — CI scheduled check (skill freshness)

Adds `check-skill-freshness.sh` to your CI pipeline as a weekly scheduled job:

```yaml
# .github/workflows/skill-freshness.yml
name: Skill Freshness Check
on:
  schedule:
    - cron: '0 9 * * 1'   # Every Monday at 09:00 UTC
  workflow_dispatch:

jobs:
  freshness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check skill freshness
        run: bash hooks/check-skill-freshness.sh
```

This is non-blocking by default — it prints warnings but does not fail the workflow.
To make it blocking, add `set -e` at the top of `check-skill-freshness.sh`.

---

## Recommended setup for most projects

```
Option A  (pre-commit) — always set up
Option B  (PostToolUse) — set up if you use Claude Code regularly for KMP work
Option C  (CI freshness) — set up once the skills collection stabilises (v2.0+)
```

---

## Verify everything is wired

```bash
# Test pre-commit hook
git stash && git commit --allow-empty -m "hook test" && git stash pop

# Test Claude Code hook — make any edit via the agent and check the tool output
# for "OK: no lightweight architecture smells matched the current scan"

# Test freshness script manually
bash hooks/check-skill-freshness.sh
```
