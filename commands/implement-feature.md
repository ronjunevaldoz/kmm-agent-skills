# /implement-feature $ARGUMENTS

Implement a new KMP feature end-to-end using the 6-layer clean architecture.

The feature name is: **$ARGUMENTS**

---

## Phase 1: PLAN

Load `agents/planner.md` and execute it for feature `$ARGUMENTS`.

The planner will:
1. Identify which skills to load based on feature scope
2. Inspect `build-logic/`, `gradle/libs.versions.toml`, and any existing modules
3. Produce a layer-by-layer plan (`:model` → `:api` → `:domain` → `:data` → `:presenter` → `:ui`)

**Gate: show the plan to the user and wait for approval before proceeding.**

---

## Phase 2: IMPLEMENT

Load `agents/implementer.md` and execute the approved plan.

The implementer will generate code for all 6 layers in build order, including:
- Gradle module declarations and `build.gradle.kts` files
- All Kotlin source files per layer
- Koin module wiring
- `:presenter` unit tests
- `:ui` interaction tests and Roborazzi screenshot tests

---

## Phase 3: VALIDATE

Load `agents/validator.md` and run:
- Level 1: architecture audit (`audit_project.py`)
- Level 2: metadata compilation
- Level 3: JVM compile + tests

If validation fails → load `agents/fixer.md`, apply fixes, re-validate.
Maximum 2 fix cycles. If still failing after 2 cycles, stop and report to user.

---

## Phase 4: REVIEW

Load `agents/reviewer.md` and review all files created or modified during implementation.

If verdict is `NEEDS_FIXES` → load `agents/fixer.md`, apply fixes, re-validate (one cycle only).

---

## Phase 5: CONTEXT UPDATE

Update `.claude/pipeline-context.json`:

```json
{
  "last_feature": "<feature_name>",
  "last_run": "<ISO date>",
  "successful_validations": <incremented count>,
  "recurring_issues": [ "<any blocker seen more than once>" ],
  "proven_patterns": {
    "<blocker_type>": "<fix strategy that worked>"
  }
}
```

If the file does not exist, create it.

---

## Phase 6: SUMMARY

Report:
```
Feature: <name>
Layers created: <list>
Files created: <count>
Tests written: <count>
Validation: PASS
Review: APPROVE
```
