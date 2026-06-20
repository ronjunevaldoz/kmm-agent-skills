# /review-changes

Review all staged and unstaged changes in the current working tree against the KMP 6-layer architecture and skill anti-patterns.

---

## Step 1: Identify changed files

```bash
git diff --name-only HEAD
git diff --name-only --cached
```

Group the changed files by layer:
- `*/model/**` → `:model`
- `*/api/**` → `:api`
- `*/domain/**` → `:domain`
- `*/data/**` → `:data`
- `*/presenter/**` → `:presenter`
- `*/ui/**` → `:ui`
- `build-logic/**` or `*.gradle.kts` → build
- `*.yml` or `.github/**` → CI

---

## Step 2: Load relevant skills

Based on the changed layers, load only the skills that apply:

| Changed layer | Skill to load |
|---|---|
| `:model`, `:api`, `:domain` | `clean-architecture` |
| `:data` | `repository-pattern`, `network-layer`, `sqldelight-setup`, or `datastore` (whichever applies) |
| `:presenter` | `presenter-module`, `mvi` |
| `:ui` | `mvi`, `design-system`, `roborazzi` |
| `build-logic/` | `feature-scaffold` |
| `.github/` | `ci-github-actions` |

---

## Step 3: Run the audit script

```bash
python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py .
```

Any finding is an automatic blocker.

---

## Step 4: Load `agents/reviewer.md` and review all changed files

Focus on:
- Layer boundary violations
- Koin wiring gaps
- MVI contract correctness
- Test tag coverage on new composables
- Missing or stale golden images (if `:ui` changed)

---

## Step 5: Output

```
CHANGED FILES: <count> across <layers>
SKILLS LOADED: <list>
AUDIT: PASS | <N findings>

BLOCKERS: <count>
WARNINGS: <count>
VERDICT: APPROVE | NEEDS_FIXES

<full reviewer output>
```

If `NEEDS_FIXES`, list the exact changes required. Do not apply them automatically — let the user decide.
