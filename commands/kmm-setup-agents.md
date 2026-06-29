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

## Step 2 — Detect project type and discover the module graph

### 2a — Determine: app or library?

Read `settings.gradle.kts` and all root/module `build.gradle.kts` files.

**Library signals** (if any are present → treat as library project):
- `com.vanniktech.maven.publish` plugin applied
- `org.jetbrains.kotlinx.binary-compatibility-validator` plugin applied
- `maven-publish` plugin applied without `com.android.application` anywhere
- No module with `com.android.application` or `androidApplication` plugin
- No `:composeApp`, `:androidapp`, `:app` module that uses the application plugin

**App signals** (default if no library signals detected):
- `com.android.application` or `androidApplication` plugin present
- `:composeApp`, `:app`, or `:androidApp` module exists with application plugin

Print:
```
Project type: APP | LIBRARY
```

### 2b — Module graph

Read `settings.gradle.kts` and extract all included modules. Group them:

**For APP projects:**
```
Modules discovered:
  :app / :composeApp / :androidApp    — entry points
  :core:common, :core:network, ...    — core modules
  :feature:auth:*                     — feature layers
  ...
```

**For LIBRARY projects:**
```
Modules discovered:
  :library (or main artifact module)  — published artifact
  :library-testing                    — test helpers for consumers (if present)
  :bom                                — Bill of Materials (if present)
  :sample / :sample:androidApp        — sample app (not published)
```

### 2c — Detect active skills from `gradle/libs.versions.toml`

**App projects check for:**
- `koin` → dependency-injection
- `ktor` → network-layer
- `sqldelight` → sqldelight-setup
- `androidx.datastore` → datastore
- `roborazzi` → roborazzi
- `turbine` → unit-testing
- navigation libraries → navigation

**Library projects check for:**
- `vanniktech` or `maven.publish` → library-publishing
- `binary-compatibility-validator` → library-publishing (apiCheck)
- `dokka` → library-publishing (Javadoc jars)
- `roborazzi` or `turbine` → unit-testing
- `iosX64`, `iosArm64` targets in build files → xcframework-spm

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

Write (or overwrite) `.claude/AGENTS.md` tailored to the detected project type,
module graph, and skill set.

### For APP projects

```markdown
# AGENTS.md — <project name>

This project uses [kmm-agent-skills](https://github.com/ronjunevaldoz/kmm-agent-skills).
Skills are installed in `.claude/skills/`.

## Project overview

<1–2 sentences describing what the app does, its platforms, and group ID>

## Skill routing

| Topic | Skill |
|---|---|
| New feature end-to-end | `kotlin-multiplatform-feature-scaffold` → `kotlin-multiplatform-clean-architecture` → `kotlin-multiplatform-mvi` |
| ViewModel / screen state | `kotlin-multiplatform-mvi` |
| Navigation | `kotlin-multiplatform-navigation` |
| Dependency injection | `kotlin-multiplatform-dependency-injection` |
<include only skills detected in Step 2c>
| Auth / login | `kotlin-multiplatform-ktor-auth-service` |
| Local database | `kotlin-multiplatform-sqldelight-setup` |
| REST API / network | `kotlin-multiplatform-network-layer` |
| Key-value settings | `kotlin-multiplatform-datastore` |
| Screenshot tests | `kotlin-multiplatform-roborazzi` |
| Design system | `kotlin-multiplatform-design-system` |
| Unit tests | `kotlin-multiplatform-unit-testing` |
| Architecture audit | `kotlin-multiplatform-audit` |
| Harvest consumer lessons | `kotlin-multiplatform-audit` (`--harvest` mode via `/kmm-harvest-lessons`) |
</end detected skills>

## Module graph

<list each module group>
| Module | Purpose |
|---|---|
| :composeApp | CMP entry point (Android / iOS / Desktop / Web) |
| :core:common | Shared utilities |
| :feature:auth | Auth feature (domain / data / presenter / ui) |
...

## Commands installed

See `.claude/commands/kmm-*.md` for available slash commands.
Key commands:
- `/kmm-implement-feature <name>` — plan → implement → validate → review
- `/kmm-run-audit` — architecture audit with per-finding remediation
- `/kmm-harvest-lessons` — collect good patterns to upstream to skills
- `/kmm-verify` — full validation pipeline
- `/kmm-execute-ticket <id>` — implement a GitHub issue end-to-end
- `/kmm-fix-design` — scan and fix design system violations
```

### For LIBRARY projects

```markdown
# AGENTS.md — <library name>

This project uses [kmm-agent-skills](https://github.com/ronjunevaldoz/kmm-agent-skills).
Skills are installed in `.claude/skills/`.

## Project overview

<1–2 sentences: what the library does, target consumers, Maven coordinates>
Group ID: <groupId>   Artifact: <artifactId>   Published to: Maven Central | GitHub Packages

## Skill routing

| Topic | Skill |
|---|---|
| Publishing to Maven Central | `kotlin-multiplatform-library-publishing` |
| iOS / SPM distribution | `kotlin-multiplatform-xcframework-spm` |
| API surface management | `kotlin-multiplatform-library-publishing` (apiCheck / apiDump) |
| Platform-specific implementations | `kotlin-multiplatform-expect-actual` |
| Unit / integration tests | `kotlin-multiplatform-unit-testing` |
| Code quality (detekt, ktlint) | `kotlin-multiplatform-code-quality` |
| CI automation | `kotlin-multiplatform-ci-github-actions` |
| Architecture audit | `kotlin-multiplatform-audit` |
| Harvest consumer lessons | `kotlin-multiplatform-audit` (`--harvest` mode via `/kmm-harvest-lessons`) |
<add only if detected>
| Screenshot / visual tests | `kotlin-multiplatform-roborazzi` |
| BOM / multi-artifact | `kotlin-multiplatform-library-publishing` (Step 4) |
</end>

## Published artifacts

| Artifact | Module |
|---|---|
| <groupId>:<artifactId> | :library |
| <groupId>:<artifactId>-testing | :library-testing (if present) |
| <groupId>:<artifactId>-bom | :bom (if present) |

## API surface rules

- Never remove or rename public symbols without a major version bump
- Run `./gradlew apiDump` after any public API change; commit the `.api` file
- `./gradlew apiCheck` runs in CI and blocks merge if API diff is uncommitted
- Mark internal symbols with `@InternalApi` to exclude from the dump

## Commands installed

See `.claude/commands/kmm-*.md` for available slash commands.
Key commands:
- `/kmm-run-audit` — architecture audit with per-finding remediation
- `/kmm-harvest-lessons` — collect patterns to upstream to skills
- `/kmm-verify` — full validation pipeline (build + test + apiCheck)
- `/kmm-check-updates` — check for skill updates
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
  kmm-run-audit.md              — architecture audit + auto skill-gap reporting
  kmm-harvest-lessons.md        — collect positive patterns; auto-propose GitHub issues
  kmm-review-changes.md         — review git diff against architecture rules
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

## Step 8 — Write `.claude/settings.json`

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

## Step 9 — Summary

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
  /kmm-run-audit                 — check architecture health (auto-reports skill gaps)
  /kmm-harvest-lessons           — collect good patterns; propose GitHub issues upstream
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
