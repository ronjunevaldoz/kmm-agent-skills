# /verify $ARGUMENTS

**KMM Agent Skills** — verify that a KMP change is correct by running the full
validation pipeline: architecture audit, style, static analysis, unit tests, and
Roborazzi screenshot regression.

Target project: `$ARGUMENTS` (defaults to `.` if empty)

This command replaces the generic `/verify` skill for KMP projects. It does not
use computer-use or launch a device — it runs the same pipeline as `agents/validator.md`
so results are reproducible in CI.

---

## Step 1 — Architecture audit

```bash
python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py "${ARGUMENTS:-.}"
```

Expected: `OK: no lightweight architecture smells matched the current scan`

Any finding is a blocker. List each verbatim — do not proceed to Step 2 until this passes
or the user explicitly overrides.

---

## Step 2 — Code style (ktlint)

```bash
./gradlew ktlintCheck 2>&1 | grep -E "^.*\.kt:[0-9]+" || true
```

Skip silently if ktlint is not configured (`./gradlew tasks --all | grep -q ktlintCheck` returns non-zero).

On failure: print each offending file + line. Suggest `./gradlew ktlintFormat` to auto-fix,
then re-run `ktlintCheck` to confirm clean before continuing.

---

## Step 3 — Static analysis (detekt)

```bash
./gradlew detekt 2>&1 | grep -E "^.*\.kt:[0-9]+" || true
```

Skip silently if detekt is not configured.

On failure: print each finding. Rules that block:
- `TooManyFunctions` — split the class
- `LongMethod` — extract helpers
- `MagicNumber` — named constant
- `ComplexCondition` — named predicate

---

## Step 4 — Unit tests + Roborazzi screenshot diff

```bash
./gradlew jvmTest 2>&1
```

This runs:
- `:presenter` unit tests (`runTest` + Turbine)
- `:ui` interaction tests (`createComposeRule`)
- Roborazzi golden image comparisons

On Roborazzi diff failure:
- List every failing test name and the path to its diff image
- Show the before/after filenames so the user can inspect them
- Ask: **Accept new goldens / Reject (fix the composable) / Skip Roborazzi only**

If the user accepts new goldens:
```bash
./gradlew recordRoborazziJvm 2>&1
```
Then re-run `jvmTest` to confirm the recorded images now pass.

---

## Step 5 — Summary

```
VERIFY: <project path>

  Step 1 — Architecture audit:  PASS | FAIL (<N> findings)
  Step 2 — ktlint:              PASS | FAIL | SKIPPED
  Step 3 — detekt:              PASS | FAIL | SKIPPED
  Step 4 — jvmTest:             PASS | FAIL (<N> tests failed)
            Roborazzi:          PASS | FAIL (<N> diffs) | SKIPPED

RESULT: PASS | FAIL
```

On `FAIL`: list the specific blockers and which step produced them.
On `PASS`: print the result and offer to load `agents/reviewer.md` for a full code review.

---

## Notes

- This command does not launch a device or simulator. For end-to-end device testing,
  run `./gradlew connectedAndroidTest` or the Xcode test scheme manually.
- Roborazzi golden images must be committed to the repo. If they are missing entirely
  (first run on a new screen), run `./gradlew recordRoborazziJvm` first, then verify.
- If any step is blocked and the user wants to skip it, note the skip in the summary
  with the reason — do not silently omit it.
