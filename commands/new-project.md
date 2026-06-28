# /new-project $ARGUMENTS

**KMM Agent Skills** — scaffold a complete KMP project from a natural language description.

`$ARGUMENTS` is either:
- A plain description: `build a todo app in kmm`
- A path to a sample spec: `samples/todo-app.md`

This command drives the full pipeline end-to-end. It starts with a short intake for the
project identity and product intent, then infers the rest from the description and uses
the skills collection to fill any remaining gaps.
Any assumptions made are printed before implementation begins.

---

## Step 1 — Read the description and collect the intake

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
| `PLATFORMS` | Which targets should we scaffold? | Android + Desktop |
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
- **Platforms** — default: Android + Desktop if not stated
- **Features** — derive from the app type; list each as a ticket-sized unit
- **Data layer** — default: SQLDelight (offline-first) if persistence is implied; DataStore if settings/preferences only
- **Backend** — default: none (local-only) unless the description mentions API, server, sync, or auth
- **Auth** — default: none unless mentioned

Print the inferred plan for transparency — do not wait for approval, proceed immediately:

```
INFERRED PLAN
─────────────
Platforms:  Android, Desktop
Features:
  F-01  Project scaffold          → kotlin-multiplatform-feature-scaffold
  F-02  Clean architecture        → kotlin-multiplatform-clean-architecture
  F-03  <feature name>            → <skill>
  ...
Data:       SQLDelight (offline-first)
Backend:    none (local-only)
Auth:       none

Skills loaded: <N>
Starting implementation...
```

---

## Step 3 — Foundation (always first, always in this order)

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

## Step 4 — Core infrastructure (if needed)

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

Skip any row not needed by the inferred plan.

---

## Step 5 — Design system

Always generate the design system before any UI feature — UI layers depend on it.

Load `kotlin-multiplatform-design-system`. Generate:
- `AppTheme` with light and dark color schemes
- `AppColors`, `AppTypography`, `AppSpacing` token objects
- `AppScaffold` and `AppTopAppBar` base components
- `AppThemePreview` wrapper for Roborazzi

If the inferred plan has more than 3 screens, also load
`kotlin-multiplatform-design-system-extended` for Dialog, Sheet, Toast, Tabs.

---

## Step 6 — Features (in dependency order)

For each feature in the inferred plan (F-03 onwards):

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

## Step 7 — Run `/verify`

After all features are implemented:

```bash
/verify .
```

This runs the full validation pipeline:
- Architecture audit
- ktlint
- detekt
- jvmTest (unit tests + Roborazzi diffs)
- Visual design audit on generated screenshot goldens

Fix any blockers. Do not mark the project complete until `/verify` reports `RESULT: PASS`.

---

## Step 8 — Summary

Print a summary of everything generated:

```
PROJECT COMPLETE
────────────────
App:        <name> — <one-line description>
Platforms:  Android, Desktop
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

Verify:     PASS
Skills used: <list>

Next steps:
  ./gradlew :androidApp:assembleDebug    — build Android
  ./gradlew :desktopApp:run              — run Desktop
  ./gradlew jvmTest                      — run all tests
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
