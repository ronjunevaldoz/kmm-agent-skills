# /kmm-setup-agents $ARGUMENTS

**KMM Agent Skills** — initialize `.claude/` in an existing KMP project so the team
gets agent-driven workflows without running the full scaffold.

`$ARGUMENTS` is optional: a path to the project root (defaults to `.`).

Use this when:
- The project already exists and you're adding `kmm-agent-skills` for the first time
- You want to reset or regenerate the `.claude/` setup after major architecture changes
- A teammate needs to onboard to the agent workflow

Do NOT use this for brand-new projects — `/kmm-new-project` handles agent setup as part of scaffold.

---

## Step 1 — Locate and validate the project

Resolve `$ARGUMENTS` as the project root (default `.`). Confirm it is a KMP project by
checking for at least one of:
- `settings.gradle.kts` or `settings.gradle`
- `gradle/libs.versions.toml`
- A `build.gradle.kts` with `kotlin("multiplatform")` or `id("com.android.kotlin.multiplatform.library")`

If none of these exist, stop and tell the user this command is for KMP projects only.

Print:
```
PROJECT: <project root>
```

---

## Step 2 — Discover the module graph

Read `settings.gradle.kts` (or `settings.gradle`) and extract all included modules.
Group them by feature:

```
Modules discovered:
  :app / :androidApp / :desktopApp    — entry points
  :core:common, :core:network, ...    — core modules
  :feature:auth:*                     — auth feature layers
  :feature:home:*                     — home feature layers
  ...
```

Also detect which skills are in play by checking `gradle/libs.versions.toml` for:
- `koin` → dependency-injection
- `ktor` → network-layer
- `sqldelight` → sqldelight-setup
- `androidx.datastore` → datastore
- `roborazzi` → roborazzi
- `turbine` → unit-testing
- navigation libraries → navigation

Print the detected skill set.

---

## Step 3 — Check for existing `.claude/` setup

Look for:
- `.claude/AGENTS.md` — already initialized?
- `.claude/commands/kmm-*.md` — commands already installed?
- `.claude/skills/` — skills already deployed?
- `.claude/settings.json` — permissions already set?

If any exist, print their current state and ask:
```
.claude/AGENTS.md already exists. Overwrite or skip? [overwrite/skip]
.claude/commands/ has N kmm-*.md files. Update or skip? [update/skip]
```

Proceed based on the answer. Default is `skip` if the user presses Enter.

---

## Step 4 — Generate `.claude/AGENTS.md`

Write (or overwrite) `.claude/AGENTS.md` tailored to this project's actual module graph
and detected skills:

```markdown
# AGENTS.md — <project name from settings.gradle>

This project uses [kmm-agent-skills](https://github.com/ronjunevaldoz/kmm-agent-skills).
Skills are installed in `.claude/skills/`.

## Skill routing

| Topic | Skill |
|---|---|
| New feature end-to-end | `kotlin-multiplatform-feature-scaffold` → `kotlin-multiplatform-clean-architecture` → `kotlin-multiplatform-mvi` |
| ViewModel / screen state | `kotlin-multiplatform-mvi` |
| Navigation | `kotlin-multiplatform-navigation` |
| Dependency injection | `kotlin-multiplatform-dependency-injection` |
<include only detected skills below>
| Auth / login | `kotlin-multiplatform-ktor-auth-service` |
| Local database | `kotlin-multiplatform-sqldelight-setup` |
| REST API / network | `kotlin-multiplatform-network-layer` |
| Key-value settings | `kotlin-multiplatform-datastore` |
| Screenshot tests | `kotlin-multiplatform-roborazzi` |
| Design system | `kotlin-multiplatform-design-system` |
| Unit tests | `kotlin-multiplatform-unit-testing` |
| Architecture audit | `kotlin-multiplatform-audit` |
</detected skills>

## Feature modules

<list each :feature:<name> module group>
| Feature | Layers present |
|---|---|
| auth | :domain :data :presenter :ui |
| home | :domain :data :presenter :ui |
...

## Commands installed

See `.claude/commands/kmm-*.md` for available slash commands.
Key commands:
- `/kmm-implement-feature <name>` — plan → implement → validate → review a new feature
- `/kmm-run-audit` — run architecture audit with per-finding remediation
- `/kmm-verify` — full validation pipeline (tests, audit, design, screenshots)
- `/kmm-execute-ticket <id>` — implement a GitHub issue end-to-end
- `/kmm-fix-design` — scan and fix design system violations
- `/kmm-update-skills` — pull latest skills and re-deploy
```

---

## Step 5 — Install consumer commands

Locate the `kmm-agent-skills` clone. Check in order:
1. `$ARGUMENTS/../kmm-agent-skills`
2. `~/dev/kmm-agent-skills`
3. Ask the user for the path

Copy the consumer command set to `.claude/commands/`:

```
Consumer commands (safe to install):
  kmm-implement-feature.md      — implement a new feature
  kmm-run-audit.md              — architecture audit
  kmm-verify.md                 — full validation pipeline
  kmm-execute-ticket.md         — implement a GitHub issue end-to-end
  kmm-fix-design.md             — fix design system violations
  kmm-audit-screenshots.md      — visual audit of Roborazzi goldens
  kmm-record-design-baselines.md — record new golden PNGs
  kmm-audit-design-visual.md    — cross-screen visual consistency check
  kmm-update-design-system.md   — pull latest design system components
  kmm-update-skills.md          — pull latest skills and re-deploy
  kmm-report-skill-issue.md     — file a skill bug report
  kmm-check-updates.md          — check for skill updates
```

Do NOT copy repo-internal commands: `kmm-new-skill.md`, `kmm-modify-skill.md`,
`kmm-maintain-docs.md`, `kmm-release-notes.md`, `kmm-setup-hooks.md`,
`kmm-new-project.md`, `kmm-setup-agents.md`.

For each file: if it already exists in `.claude/commands/` and the content differs,
show a one-line diff summary and ask `[update/skip]` before overwriting.

---

## Step 6 — Deploy skills

If `.claude/skills/` does not exist, create it and copy all skills from the
`kmm-agent-skills/skills/` directory.

If `.claude/skills/` already exists, run the equivalent of `update-consumer-skills.sh`
to sync changed skills without prompting for each file (skills are passive docs).

---

## Step 7 — Write `CLAUDE.md`

If `CLAUDE.md` does not exist in the project root, create a minimal one that tells
Claude Code where the skills live and which conventions to follow:

```markdown
### Claude Code Project Profile

### Load skills context on initialization
--system-prompt-file=".claude/AGENTS.md"

### Default flags
--compact
--verbose=false

### Ignore generated and vendor directories
--ignore="**/build/**"
--ignore="**/.gradle/**"
--ignore="**/vendor/**"
--ignore="**/third_party/**"
```

If `CLAUDE.md` already exists, print its contents and skip — do not overwrite.

---

## Step 9 — Write `.claude/settings.json`

If `.claude/settings.json` does not exist, create it with a Bash allowlist for
common read-only and build operations:

```json
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
```

If it already exists, print the current permissions and skip — do not overwrite.

---

## Step 10 — Summary

```
AGENT SETUP COMPLETE
─────────────────────
Project:   <name> (<root>)
Features:  <N> detected (<list>)
Skills:    <N> deployed → .claude/skills/

Generated:
  ✅ CLAUDE.md                   — project profile (--system-prompt-file, --compact, ignores)
  ✅ .claude/AGENTS.md           — skill routing tailored to this project
  ✅ .claude/commands/           — <N> consumer commands installed
  ✅ .claude/skills/             — <N> skills deployed
  ✅ .claude/settings.json       — Bash allowlist

Detected skill set:
  <list of skills matched from libs.versions.toml>

Try it now:
  /kmm-run-audit                 — check architecture health
  /kmm-implement-feature <name>  — add a new feature
  /kmm-verify                    — run full validation pipeline
```

---

## Notes

- Run this again after major architecture changes (adding/removing features, changing
  the module graph) to regenerate `AGENTS.md` with the current structure.
- Skills are passive docs — re-running always syncs them safely.
- Commands are only overwritten with explicit `[update]` confirmation.
- `settings.json` is never overwritten — add permissions manually if needed.
