# /kmm-new-project $ARGUMENTS

**KMM Agent Skills** — scaffold a complete KMP project from a natural language description.

`$ARGUMENTS` is optional:
- Omitted: the command asks what the app does before proceeding
- Plain description: `build a todo app in kmm`
- A path to a sample spec: `samples/todo-app.md`

This command drives the full pipeline end-to-end across 11 steps:
intake → infer → **plan (MVP + sprints, gated approval)** → scaffold → infrastructure → design system → screen layouts + previews → features → verify → agent setup → summary.
Any assumptions made are printed before implementation begins.

---

## Step 1 — Read the description and collect the intake

If `$ARGUMENTS` is empty, ask first:
```
What does your app do? (describe in one sentence or a few words)
```
Wait for the answer and use it as the description before continuing.

If `$ARGUMENTS` ends in `.md` and the file exists, read it as the full project spec.
Otherwise treat `$ARGUMENTS` as the raw description.

Print:
```
PROJECT: <description summary, one line>
TARGET:  <current working directory>
```

If the working directory is not empty (contains files other than `.git`, `.claude`, `README.md`),
print a warning:
```
WARNING: directory is not empty — scaffolding will add files alongside existing content.
         If you want a clean project, run this from an empty directory.
```
Do not stop — continue regardless.

Then collect the project intake. Ask for the minimum information needed to start a
consumer project cleanly:

| Field | Ask | Default if omitted |
|---|---|---|
| `PROJECT_NAME` | What is the app/project name? | Derived from the description |
| `GROUP_ID` | What package/group ID should the project use? | `com.example.<project>` |
| `APP_TYPE` | What kind of app is this? | Derived from the description |
| `WHAT_IT_DOES` | What does the app do in one sentence? | Derived from the description |
| `PLATFORMS` | Which targets should we scaffold? | Android + iOS |
| `MIN_SDK` | Minimum Android SDK version? | 26 |
| `IOS_TARGET` | Minimum iOS deployment target? | 16.0 |
| `PERSISTENCE` | Does it need local storage, settings, or neither? | Inferred |
| `BACKEND` | Does it talk to an API, auth service, or server? | none |
| `AUTH` | Does it have login / sign-in / identity? | none |
| `DI_APPROACH` | Annotated or manual DI? | annotated |

If the user omits a field, state the assumption before proceeding and keep moving.

---

## Step 2 — Infer feature set and load expert routing

Pass the description and intake answers to `kotlin-multiplatform-expert` to identify which skills are needed.

From the description, extract:
- **App type** (todo, social feed, e-commerce, etc.)
- **Platforms** — default: Android + iOS if not stated
- **Features** — derive from the app type; list each as a ticket-sized unit
- **Data layer** — default: SQLDelight (offline-first) if persistence is implied; DataStore if settings/preferences only
- **Backend** — default: none (local-only) unless the description mentions API, server, sync, or auth
- **Auth** — default: none unless mentioned

Print the raw feature list — do not start implementation yet:

```
INFERRED FEATURES
─────────────────
Platforms:  <platforms from intake>
Features (raw):
  F-01  Project scaffold
  F-02  Clean architecture
  F-03  <feature name>
  ...
Data:       SQLDelight (offline-first)
Backend:    none (local-only)
Auth:       none

→ Proceeding to planning phase...
```

---

## Step 3 — Plan: MVP, phases, tasks, sprints

This is the gate before any code is written. Always produce a **fully drafted plan with
recommendations pre-selected** — never present a blank template or ask the user to
fill things in. The user should only need to say "looks good" or tweak one item.

### 3a — Draft the MVP scope (always recommend first)

Apply these rules to auto-select the MVP cut, then label each choice as recommended:

- Every MVP needs: navigation shell + at least one data-bearing screen
- Auth is MVP only if the app cannot work anonymously (otherwise post-MVP)
- Nice-to-haves (settings, profile, onboarding, notifications) → post-MVP by default
- No analytics, crash reporting, or push notifications in MVP unless explicitly stated

Always print a **numbered list** so the user can reference items by number:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRAFT — MVP SCOPE  (recommended ✦)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MVP (Sprint 1–N):
  [1] ✦ <feature> — <why it's core>
  [2] ✦ <feature> — <why it's core>
  [3]   <feature> — included because auth is required to function

Post-MVP (after first release):
  [4]   <feature> — nice-to-have, not blocking
  [5]   <feature> — can ship without it

→ Recommended: proceed with [1][2][3] in MVP.
  Say a number to move a feature in or out, or "looks good" to confirm.
```

### 3b — Draft the roadmap (always pre-fill milestones)

Always generate concrete milestone names, not placeholders. Use the app type to name
them meaningfully (e.g. "Alpha — browse products" not "Milestone 1"):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRAFT — ROADMAP  (recommended ✦)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✦ Milestone 1 — MVP · "<descriptive name>" (internal alpha)
    <feature list with [item numbers]>

  Milestone 2 — v1.1 · "<descriptive name>"
    <feature list with [item numbers]>

  Milestone 3 — v2.0 · "Backlog / TBD"
    <feature list with [item numbers]>

→ Recommended: ship Milestone 1 to internal testers first.
  Move items by number, or "looks good" to confirm.
```

### 3c — Draft the full task list (always pre-filled, numbered)

For every MVP feature, generate the complete task list immediately — never leave blanks.
Each task gets a unique ID (F = foundation, feature initial + number):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRAFT — TASK LIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Foundation (always Sprint 1):
  [F-01] Clone kmp-wizard + configure project name / group ID
  [F-02] Apply 6-layer clean-arch module structure
  [F-03] Set up Koin DI (annotated mode)
  [F-04] Set up Ktlint + Detekt + baseline
  [F-05] Set up GitHub Actions CI (build + test + lint matrix)
  [F-06] Generate design system (AppTheme, tokens, AppScaffold)
  [F-07] Set up type-safe navigation shell + bottom nav (if multiple tabs)

<Feature: e.g. Auth>:
  [A-01] Scaffold :feature:auth:domain / :data / :presenter / :ui
  [A-02] Define AuthContract (State, Intent, Effect)
  [A-03] Implement AuthRepository interface + FakeAuthRepository
  [A-04] Implement AuthRepositoryImpl (Ktor bearer/JWT)
  [A-05] Implement AuthViewModel (MVI)
  [A-06] Wire Koin — authModule.kt
  [A-07] LoginScreen + LoginContent composables
  [A-08] Add /login route to NavHost, auth guard
  [A-09] ViewModel unit tests: login success, error, loading
  [A-10] Roborazzi screenshot tests: empty, loading, error states

<Feature: next MVP feature — same pattern>:
  [B-01] … [B-10]
```

### 3d — Draft the sprint plan (always pre-grouped)

Always pre-assign tasks to sprints — never leave sprint assignment to the user.
Default capacity: 7–10 tasks per sprint. Always end with a Polish sprint.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRAFT — SPRINT PLAN  (recommended ✦)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✦ Sprint 1 — Foundation  (~1 week)
    [F-01] [F-02] [F-03] [F-04] [F-05] [F-06] [F-07]
    Goal: clean build, CI green, design system renders

✦ Sprint 2 — <First MVP feature>  (~1 week)
    [A-01] [A-02] [A-03] [A-04] [A-05] [A-06] [A-07] [A-08] [A-09] [A-10]
    Goal: <feature> works end-to-end, tests green

✦ Sprint 3 — <Second MVP feature>  (~1 week)
    [B-01] … [B-10]
    Goal: <feature> works end-to-end

✦ Sprint N — Polish + QA  (~1 week)
    Layout wireframes reviewed
    Accessibility pass (contentDescription, touch targets)
    Roborazzi golden baselines recorded
    Release build validated (ProGuard, signed APK)
    Goal: ready for internal alpha release

→ Estimated MVP: <N> sprints (~<N> weeks).
  Move tasks between sprints by ID, or "looks good" to confirm.
```

### 3e — Present the full draft and wait for a single confirmation

Print all four sections together as one block, then a **single prompt**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN READY — review and confirm
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[MVP scope above]   [Roadmap above]
[Task list above]   [Sprint plan above]

Options:
  ↩  "looks good" / "yes" / "proceed"  — accept all and start building
  ✏  "move [X-01] to sprint 3"         — adjust a task's sprint
  ✏  "add <thing> to MVP"              — include a feature
  ✏  "remove [3] from MVP"             — defer a feature
  ✏  "split sprint 2 into two sprints" — resize capacity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Do not proceed to Step 4 until the user confirms.**
After each change: re-print only the affected section with the change highlighted,
then re-ask. Never re-print the entire plan after a minor edit — just the delta.

---

## Step 4 — Foundation (always first, always in this order)

Run these two before any feature work. They establish the module graph and layer contract
everything else depends on.

**F-01: Project scaffold — clone kmp-wizard first**
Load `kotlin-multiplatform-feature-scaffold`. The first action is always:

```bash
git clone --depth 1 --branch all-targets \
  https://github.com/Kotlin/kmp-wizard <PROJECT_NAME>
cd <PROJECT_NAME> && rm -rf .git && git init
```

Then configure the clone (rename project, update group ID, update version catalog).
Then add the 6-layer convention plugins on top of what kmp-wizard already ships.
Run `./gradlew help` — must be `BUILD SUCCESSFUL` before any feature work begins.

Never write `build-logic/`, `settings.gradle.kts`, or `gradle.properties` from scratch —
kmp-wizard is the only valid starting point for a new project.

**F-02: Clean architecture**
Load `kotlin-multiplatform-clean-architecture`. Generate the 6-layer module structure
(`:model`, `:api`, `:domain`, `:data`, `:presenter`, `:ui`) for each inferred feature.

After each foundation step: run `validate_module_graph.py` and confirm zero errors before proceeding.

---

## Step 5 — Core infrastructure (if needed)

Only generate what the inferred plan requires. Run each in dependency order:

| Inferred need | Skill | What it generates |
|---|---|---|
| Local persistence | `kotlin-multiplatform-sqldelight-setup` | Schema, drivers, migrations, Flow queries |
| Key-value / settings | `kotlin-multiplatform-datastore` | Preferences DataStore, expect/actual factory |
| REST API | `kotlin-multiplatform-network-layer` | Ktor client, NetworkResult<T>, safeRequest |
| kRPC backend | `kotlin-multiplatform-kotlin-rpc` | Shared contract, Ktor auth integration |
| Auth flow | `kotlin-multiplatform-ktor-auth-service` | Bearer/JWT, login/refresh/logout |
| DI | `kotlin-multiplatform-dependency-injection` | Koin modules, scope rules |
| Logging | `kotlin-multiplatform-logging` | Kermit setup, log levels, Koin wiring |
| CI/CD | `kotlin-multiplatform-ci-github-actions` | GitHub Actions matrix: build, test, detekt, ktlint |
| Code quality | `kotlin-multiplatform-code-quality` | Ktlint + Detekt config, baseline, CI gate |

Always include CI/CD and Code quality — every new project needs them from day one.
Skip the remaining rows if not needed by the inferred plan.

---

## Step 6 — Design system

Always generate the design system before any UI feature — UI layers depend on it.

Load `kotlin-multiplatform-design-system`. Generate:
- `AppTheme` with light and dark color schemes
- `AppColors`, `AppTypography`, `AppSpacing` token objects
- `AppScaffold` and `AppTopAppBar` base components
- `AppThemePreview` wrapper for Roborazzi

If the inferred plan has more than 3 screens, also load
`kotlin-multiplatform-design-system-extended` for Dialog, Sheet, Toast, Tabs.

---

## Step 7 — Screen layouts and design

Before writing any composable, generate layout docs and wireframes for every screen in
the inferred plan. Design must be agreed on before implementation starts — changing
layout after code is written wastes time.

**6a — ASCII wireframes (layout-system)**

Load `kotlin-multiplatform-layout-system`. For each screen in the inferred feature set,
generate a file in `docs/layout-system/<feature>/<ScreenName>.md` containing:

- **Component table** — every visible element, its type, and the design-system component it maps to
- **ASCII wireframe** — structural layout showing slot positions, spacing zones, and scroll regions
- **State variants** — one wireframe per meaningful state (loading, empty, error, filled)

Example for a product list screen:
```
docs/layout-system/
  products/
    ProductListScreen.md   — list, loading, empty state variants
    ProductDetailScreen.md — hero image, details, CTA button
  auth/
    LoginScreen.md         — form fields, submit, forgot password link
  orders/
    OrderHistoryScreen.md  — grouped list, empty state
  _components.md           — shared component registry (AppButton, AppTextField, etc.)
```

**6b — Design previews (preview-driven-development)**

Load `kotlin-multiplatform-preview-driven-development`. For each screen, generate stub
`Content` composables with `@Preview` annotations covering all state variants — before
the real implementation. This makes layout mistakes visible immediately on Desktop
without running a device or emulator.

```kotlin
// Generated stub — real logic added in Step 7
@Composable
fun ProductListContent(
    state: ProductListContract.State = ProductListContract.State(),
    onIntent: (ProductListContract.Intent) -> Unit = {},
) {
    // TODO: implement — layout spec in docs/layout-system/products/ProductListScreen.md
}

@Preview @Composable
private fun ProductListLoadingPreview() =
    AppThemePreview { ProductListContent(state = ProductListContract.State(isLoading = true)) }

@Preview @Composable
private fun ProductListEmptyPreview() =
    AppThemePreview { ProductListContent(state = ProductListContract.State(products = emptyList())) }

@Preview @Composable
private fun ProductListFilledPreview() =
    AppThemePreview { ProductListContent(state = ProductListContract.State(products = sampleProducts)) }
```

After generating stubs: run `./gradlew :composeApp:jvmRun` (or open Android Studio
previews) and confirm the slot structure looks right before moving to Step 7.

---

## Step 8 — Features (MVP sprint order)

Execute the sprint plan approved in Step 3. Work sprint by sprint, feature by feature.
For each MVP feature task:

1. **Implement** — load the relevant skill(s), generate all 6 layers:
   - `:model` — data classes, sealed results
   - `:api` — repository interface
   - `:domain` — use cases
   - `:data` — repository implementation, mappers, SQLDelight/network calls
   - `:presenter` — MVI ViewModel, UiState, UiEffect, Channel
   - `:ui` — `Screen` (with real ViewModel), `Content` (pure state, injectable)

2. **Wire DI** — add all new bindings to the Koin module for this feature.

3. **Add navigation** — if the feature has a screen, add a type-safe route to the
   NavHost. Load `kotlin-multiplatform-navigation` on first screen, reuse pattern on subsequent ones.

4. **Write tests** — for every feature:
   - `:presenter` unit tests with `runTest` + Turbine (load `kotlin-multiplatform-unit-testing`)
   - Roborazzi screenshot tests — all states, light + dark (load `kotlin-multiplatform-roborazzi`)

5. **Validate** — after each feature, run:
   ```bash
   python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py .
   ```
   Fix any findings before moving to the next feature.

Skills to load per common feature type:

| Feature type | Skills |
|---|---|
| List + detail | `repository-pattern`, `mvi`, `paging` (if list is large) |
| Create / edit form | `mvi`, `form-validation` |
| Settings / preferences | `datastore`, `mvi` |
| Auth / login | `ktor-auth-service`, `mvi`, `form-validation`, `biometric-auth` (if mentioned) |
| Offline list | `sqldelight-setup`, `offline-first`, `mvi` |

---

## Step 9 — Run `/kmm-verify`

After all features are implemented:

```bash
/kmm-verify .
```

This runs the full validation pipeline:
- Architecture audit
- ktlint
- detekt
- jvmTest (unit tests + Roborazzi diffs)
- Visual design audit on generated screenshot goldens

Fix any blockers. Do not mark the project complete until `/kmm-verify` reports `RESULT: PASS`.

---

## Step 10 — Generate agent setup

After verify passes, generate a `.claude/` directory in the scaffolded project so the team
gets agent-driven workflows on day one.

**Write `.claude/AGENTS.md`** — route the skills the project actually uses:

```markdown
# AGENTS.md — <PROJECT_NAME>

This project uses [kmm-agent-skills](https://github.com/ronjunevaldoz/kmm-agent-skills).
Skills are installed in `.claude/skills/`.

## Skill routing

| Topic | Skill |
|---|---|
| New feature end-to-end | `kotlin-multiplatform-feature-scaffold` → `kotlin-multiplatform-clean-architecture` → `kotlin-multiplatform-mvi` |
| ViewModel / screen state | `kotlin-multiplatform-mvi` |
| Navigation | `kotlin-multiplatform-navigation` |
| Dependency injection | `kotlin-multiplatform-dependency-injection` |
<if auth was scaffolded>| Auth / login | `kotlin-multiplatform-ktor-auth-service` |</if>
<if SQLDelight was scaffolded>| Local database | `kotlin-multiplatform-sqldelight-setup` |</if>
<if network was scaffolded>| REST API / network | `kotlin-multiplatform-network-layer` |</if>
| Design system | `kotlin-multiplatform-design-system` |
| Unit tests | `kotlin-multiplatform-unit-testing` |
| Architecture audit | `kotlin-multiplatform-audit` |

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

**Copy the consumer command set** into `.claude/commands/`:

```
Commands to copy (these are safe for consumer projects):
  kmm-implement-feature.md
  kmm-run-audit.md
  kmm-verify.md
  kmm-execute-ticket.md
  kmm-fix-design.md
  kmm-audit-screenshots.md
  kmm-record-design-baselines.md
  kmm-audit-design-visual.md
  kmm-update-design-system.md
  kmm-update-skills.md
  kmm-report-skill-issue.md
  kmm-check-updates.md
```

Do NOT copy repo-internal commands (`kmm-new-skill.md`, `kmm-modify-skill.md`,
`kmm-maintain-docs.md`, `kmm-release-notes.md`, `kmm-setup-hooks.md`) —
those are for maintaining this skills repo, not consumer projects.

**Write `.claude/pipeline-context.json`** — seed the project planner with initial context:

```json
{
  "project": "<PROJECT_NAME>",
  "group_id": "<GROUP_ID>",
  "platforms": ["<platform list>"],
  "skills_used": ["<skill list from this run>"],
  "recurring_issues": [],
  "proven_patterns": []
}
```

The `planner` agent reads this to avoid known pitfalls and reuse proven approaches.
Update `recurring_issues` and `proven_patterns` manually as the project evolves.

**Write `.claude/settings.json`** with allowlist for common read operations:

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

---

## Step 11 — Summary

Print a summary of everything generated:

```
PROJECT COMPLETE
────────────────
App:        <name> — <one-line description>
Platforms:  <platforms from intake>
Features:   <N> implemented
  ✅ F-01  Project scaffold
  ✅ F-02  Clean architecture
  ✅ F-03  <feature>
  ...

Generated:
  Modules:      <N> Gradle modules
  Source files: <N> .kt files
  Tests:        <N> unit tests, <N> Roborazzi screenshot tests
  Screenshots:  <N> PNG goldens (<N> light, <N> dark)

Agent setup:
  .claude/AGENTS.md                — skill routing for this project
  .claude/commands/kmm-*.md        — <N> slash commands installed
  .claude/pipeline-context.json    — project context for the planner agent
  .claude/settings.json            — Bash allowlist

Verify:     PASS
Skills used: <list>

Next steps:
  ./gradlew :androidApp:assembleDebug    — build Android
  ./gradlew :desktopApp:run              — run Desktop
  ./gradlew jvmTest                      — run all tests
  /kmm-implement-feature <name>          — add your first feature
```

---

## Notes

- Always generate `Content` composables (pure state, no ViewModel) — they are what
  Roborazzi tests inject. Never screenshot a `Screen` directly.
- Every screen needs `AppScaffold` + `AppTopAppBar`. The visual audit will catch missing chrome.
- Roborazzi golden images must be recorded and committed:
  `./gradlew recordRoborazziJvm` — run this before Step 7.
- This command is the consumer-facing entry point. For E2E testing the skills themselves,
  use a spec from `samples/` as the `$ARGUMENTS` input in a clean sandbox directory.
