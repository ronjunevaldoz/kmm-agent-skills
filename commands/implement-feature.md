# /implement-feature $ARGUMENTS

**KMM Agent Skills** — build a new KMP feature end-to-end, layer by layer, with the full
Koin 4 / Ktor 3 / SQLDelight 2 / CMP 1.11 stack wired correctly from the start.

Feature name: **$ARGUMENTS**

---

## Phase 1 — Plan

Load `agents/planner.md`.

The layer planner will inspect `build-logic/`, `gradle/libs.versions.toml`, and any
existing modules under `feature/$ARGUMENTS/`. It will identify which of the 31 skills
apply and produce a build-order plan covering all 6 layers:

```
:model → :api → :domain → :data → :presenter → :ui
```

The plan includes every Koin binding, every test class, and every `libs.versions.toml`
addition needed before a line of code is written.

**Show the plan. Wait for confirmation before continuing.**

---

## Phase 2 — Implement

Load `agents/implementer.md`.

Generates complete, runnable Kotlin for each layer in build order. Every file is fully
written — no stubs, no `// TODO`. Includes:

- `build.gradle.kts` for each new module
- All Kotlin source files per layer
- Koin module wiring (platform modules for `:data`, common module for `:presenter`)
- `:presenter` unit tests with `runTest` + Turbine
- `:ui` interaction tests with `createComposeRule` + `onNodeWithTag`
- `:ui` Roborazzi screenshot tests for each meaningful visual state

---

## Phase 3 — Validate

Load `agents/validator.md`.

Runs in order — stops at the first failure:

1. Architecture audit: `python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py .`
2. `commonMain` metadata compilation
3. `jvmTest` — presenter unit tests + UI tests in parallel

On failure → load `agents/fixer.md`, apply targeted fixes, re-validate.
Maximum 2 fix cycles. If still failing, stop and report to user.

---

## Phase 4 — Review

Load `agents/reviewer.md`.

Reviews layer boundaries, Koin wiring, MVI contracts, and testTag coverage on all files
created during implementation. Any blocker → load `agents/fixer.md` for one fix cycle.

---

## Phase 5 — Wrap up

Update `.claude/pipeline-context.json` with patterns learned during this feature.

Report:
```
Feature:        $ARGUMENTS
Layers built:   <list>
Files created:  <N>
Tests written:  <N> unit + <N> UI
Validation:     PASS
Review:         APPROVE
```
