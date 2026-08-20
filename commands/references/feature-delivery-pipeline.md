# Feature Delivery Pipeline

Use this shared pipeline after the command-specific intake and before its wrap-up steps.

## Plan

1. Load `agents/planner.md` with the accepted requirements.
2. Map every requirement to a layer, dependency, and test.
3. Show the plan and wait for user approval.

## Implement

1. Load `agents/implementer.md`.
2. Build in order: `:model → :api → :domain → :data → :presenter → :ui`.
3. Add the required Koin wiring and tests with each layer.

## Validate

1. Load `agents/validator.md`.
2. Run the architecture audit, commonMain compilation, and JVM tests.
3. On failure, load `agents/fixer.md`, apply a targeted fix, and re-run validation.

Stop and report after two unsuccessful fix cycles.

## Review

1. Load `agents/reviewer.md`.
2. Review boundaries, Koin wiring, MVI contracts, and test coverage.
3. Allow one targeted fixer cycle for a review blocker, then re-review.
