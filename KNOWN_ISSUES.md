# Known Issues

Tracks confirmed agent behavior gaps, tool limitations, and workarounds.
Resolved issues stay here for reference — they explain *why* a rule exists.

---

## Open

### KI-001 — `pipeline-context.json` is never auto-populated

**Status:** Resolved — see KI-R07 below

---

### KI-002 — Hooks require manual installation; not enforced

**Status:** Resolved — see KI-R08 below

---

### KI-003 — Adaptive layout not adopted retroactively in existing projects

**Status:** Resolved — see KI-R09 below

---

### KI-004 — `hardcoded spacing` audit pattern can false-positive on `padding(0.dp)`

**Status:** Resolved — see KI-R06 below

---

### KI-005 — `krpc_established` flag round-trip has no automated test

**Status:** Resolved — see KI-R12 below

**Symptom:** The implementer sets `krpc_established: true` in `pipeline-context.json`
after confirming kRPC is active; the reviewer reads it to skip the grep. The wiring
is correct, but no unit test verifies the round-trip. A refactor dropping the read
in the reviewer would silently regress — every session would re-run the grep.

**Workaround:** Manually verify `.claude/pipeline-context.json` contains
`"krpc_established": true` after an implementer session on a kRPC project.

**Fix:** Add a `PipelineContextFlagTests` class to `tests/test_skill_scripts.py`.

---

### KI-006 — Hook scripts lack unit tests

**Status:** Resolved — see KI-R13 below

**Symptom:** `validate-architecture.sh` and `check-skill-freshness.sh` are shell scripts
that wrap `audit_project.py` and `check_updates.py`. The Python scripts have 43 tests,
but the shell plumbing — exit code forwarding, argument passing, `STAGED_KT` filter — is
untested. A shell syntax error would go undetected until a developer runs a commit.

**Workaround:** Manually run each hook after any change to confirm it executes.

**Fix:** Add a `HookScriptTests` class using `subprocess.run` to test each hook's
exit code against known inputs (clean dir, dirty dir, no `.kt` files staged).

---

## Resolved

### KI-R01 — Agent not detecting magic color/variable violations in design system

**Resolved:** `987a60a` — `feat(audit): detect magic color literals in UI composables`  
**Was:** `audit_project.py` had no pattern for `Color(0xFF...)`. The design-system
anti-pattern section said "avoid hardcoding colors" but gave no concrete example.
Agent sessions generated `Color(0xFF6200EE)` in composables without warning.  
**Fix:** Added `magic color literal` audit pattern — flags `Color(0x…)` in `/ui/` or
`/presentation/` files, excluding token definition files (`AppColors.kt`, `*Theme.kt`).
Updated design-system anti-pattern to name the literal form explicitly.

---

### KI-R02 — Dark/light mode not verified by agent; muted colors only tested in light

**Resolved:** `f3f2eb5` — `feat(adaptive+theme): add adaptive-layout skill and dark/light mode enforcement`  
**Was:** Roborazzi tests listed dark mode as "one capture among many" (optional). The
reviewer had no check for dark mode coverage. `isSystemInDarkTheme()` was being called
directly inside composables instead of being centralised in the theme entry point.  
**Fix:** Roborazzi skill now requires `_light` + `_dark` captures for every state.
Reviewer Check 6 blocks any screenshot file missing a dark variant (`[THEME]`).
New audit pattern `system dark theme scatter` flags `isSystemInDarkTheme()` outside
theme files. Fixer has concrete before/after fixes for all three violations.

---

### KI-R03 — Cross-session adaptive layout pattern loss

**Resolved:** `f3f2eb5` — `feat(adaptive+theme): add adaptive-layout skill and dark/light mode enforcement`  
**Was:** When one session implemented an adaptive layout (WindowSizeClass, list-detail
split), a subsequent session had no way to know the pattern was established. New screens
were generated without `WindowSizeClass` parameters, breaking layout consistency.  
**Fix:** New `kotlin-multiplatform-adaptive-layout` skill documents the canonical
pattern. Implementer agent runs a grep pre-check before any `:ui` layer —
`grep -r "WindowSizeClass" */src --include="*.kt"` — and replicates the existing
pattern if found. Reviewer Check 7 blocks new screens that omit `WindowSizeClass` when
the project already uses it. `pipeline-context.json` gains an
`adaptive_layout_established` field.

---

### KI-R04 — Pages inconsistent; scaffold and TopAppBar not enforced

**Resolved:** `3b613f0` — `feat(layout): enforce screen layout contract and scaffold consistency`  
**Was:** Nothing enforced that every screen uses `AppScaffold` + `AppTopAppBar`. Page
titles, back buttons, and action buttons were placed arbitrarily in the content body,
leading to duplicate chrome, titles that scroll away, and action buttons with
inconsistent tap targets. Hardcoded `padding(16.dp)` was used instead of
`AppTheme.spacing.lg`.  
**Fix:** Screen Layout Contract added to design-system skill with a canonical
`FooContent` template. New audit pattern `hardcoded spacing` flags `padding(N.dp)`
in UI files. Reviewer Check 8 blocks screens missing `AppScaffold`, missing
`PaddingValues` consumption, or with title/action outside the TopAppBar. Fixer
gains `[LAYOUT]` before/after fixes.

---

### KI-R05 — Expert skill routing missed canvas/visual testing queries

**Resolved:** `v1.2.3` — keyword expansion pass  
**Was:** Queries like "test canvas layout", "visual accuracy", "pixel-perfect test"
routed to `kotlin-multiplatform-graphics-modifiers` instead of
`kotlin-multiplatform-roborazzi`. Several other skills had narrow keyword vocabularies
that caused misrouting on natural-language queries.  
**Fix:** Added 14 skills with expanded trigger keyword lines. Added a new routing row
to the expert skill for canvas/layout testing vocabulary.

---

### KI-R06 — `hardcoded spacing` false-positive on `padding(0.dp)`

**Resolved:** `fix(audit): exclude 0.dp from hardcoded spacing pattern`  
**Was:** The regex `\bpadding\([^)]*\d+\.dp` matched `0.dp`, flagging intentional
zero-padding as a spacing token violation even though no `AppTheme.spacing.zero` token
exists.  
**Fix:** Changed regex to `\bpadding\([^)]*[1-9]\d*\.dp` — requires at least one
non-zero leading digit, so `0.dp` is silently ignored.

---

### KI-R07 — `pipeline-context.json` never committed between sessions

**Resolved:** `fix(pipeline): commit pipeline-context.json at end of every pipeline run`  
**Was:** Agents updated `.claude/pipeline-context.json` during a session but never
committed it. The next session always started with null values — `recurring_issues` and
`proven_patterns` were lost on every session boundary.  
**Fix:** Phase 8 of `execute-ticket.md` and Phase 5 of `implement-feature.md` now
include a `git add .claude/pipeline-context.json && git commit` step. The file is only
committed if its values actually changed. Pipeline context now persists across sessions.

---

### KI-R08 — Hooks required manual `ln -sf` per machine

**Resolved:** `fix(hooks): add scripts/install-hooks.sh one-liner`  
**Was:** `pre-commit-audit.sh` and `validate-architecture.sh` were present in `hooks/`
but README only showed a manual `ln -sf` command. Most users skipped it, silently
disabling the architecture audit gate.  
**Fix:** `scripts/install-hooks.sh` symlinks both hooks in one command and makes them
executable. README updated to show `bash scripts/install-hooks.sh` as the primary
install path.

---

### KI-R09 — Adaptive layout reviewer blocked entire existing codebase

**Resolved:** `fix(reviewer): add adaptive_layout_migration_mode to pipeline-context`  
**Was:** Reviewer Check 7 uniformly blocked every screen lacking `WindowSizeClass`,
making it impossible to incrementally adopt adaptive layout in a project with many
existing screens — all changes were blocked until every screen was retrofitted.  
**Fix:** Added `adaptive_layout_migration_mode: true/false` to `pipeline-context.json`.
When `true`, Check 7 downgrades pre-existing screens to `[WARNING]` and only enforces
the full `[ADAPTIVE]` blocker on screens created or modified in the current session.
Documented in the adaptive-layout skill with a 4-step retrofit workflow.

---

### KI-R10 — Planner routing table silently went stale for 25 skills

**Resolved:** `v1.11.0` — `feat(quality): enforce test maintenance and planner routing validation`  
**Was:** `validate_skill_map.py` checked README and the expert SKILL.md but never
checked `agents/planner.md`. When 25 skills were added across multiple sessions, their
routing rows were never added to the planner. The planner routed correctly for the first
~10 skills but silently failed to load the correct skills for any of the 25 newer ones.
No script caught the drift because validation only covered two of the three indexes.  
**Fix:** `validate_skill_map.py` now validates all three indexes — README, expert
SKILL.md, and `agents/planner.md` — using a short-name lookup (strips the
`kotlin-multiplatform-` prefix) with a `SKIP_PLANNER` set for meta-skills that
intentionally have no routing rows. The check runs on every `release.py` call, blocking
a release if any skill directory is missing from the planner.

---

### KI-R11 — Python script changes could skip unit tests with no enforcement

**Resolved:** `v1.11.0` — `feat(quality): enforce test maintenance and planner routing validation`  
**Was:** When `scripts/` or `skills/*/scripts/` Python files were modified, there was
no gate requiring `tests/test_skill_scripts.py` to be updated in the same commit.
Several test gaps were found during audits (e.g. `check_updates.py main()` had no
test coverage for exit codes 0/1/2 until manually identified and fixed).  
**Fix:** `hooks/pre-commit-audit.sh` now blocks any commit that stages a `.py` file
under `scripts/` or `skills/*/scripts/` without also staging `tests/test_skill_scripts.py`.
The pre-commit message names the changed scripts and explains the requirement.
Reviewer Check 12, implementer Script test maintenance section, and `/modify-skill` Rule 8
all mirror the same rule so the enforcement is layered — the hook is the hard gate,
but agents enforce it before a commit is ever attempted.

---

### KI-R12 — `krpc_established` flag round-trip had no automated test

**Resolved:** `v1.12.0` — `feat(tests): KI-005 + KI-006 — pipeline flag contract tests and hook script tests`  
**Was:** The implementer and reviewer both referenced `krpc_established` in their markdown, but no test verified the contract. A refactor removing either reference would silently break the round-trip — sessions would re-run the kRPC grep every time instead of short-circuiting.  
**Fix:** Added `PipelineContextFlagTests` class to `tests/test_skill_scripts.py` with four tests:
- `pipeline-context.json` has the key and it is a bool
- `agents/implementer.md` references `krpc_established` (set path)
- `agents/reviewer.md` references `krpc_established` (read path)

---

### KI-R13 — Hook scripts had no unit tests

**Resolved:** `v1.12.0` — `feat(tests): KI-005 + KI-006 — pipeline flag contract tests and hook script tests`  
**Was:** `validate-architecture.sh` and `check-skill-freshness.sh` were shell scripts with no test coverage. Three bugs were also discovered and fixed in the process:
- `validate-architecture.sh` had no way to point at a test project root (always used the skills repo itself, causing SKILL.md anti-pattern examples to trigger false positives)
- `check-skill-freshness.sh` used `grep` without `|| true` — `set -e` caused exit 1 when a skill had no `last-updated` line
- `check-skill-freshness.sh` had no `nullglob` — empty skills directories caused a spurious glob match  
**Fix:**
- Added `$2` project root override to `validate-architecture.sh`
- Added `|| true` to `grep` in `check-skill-freshness.sh`
- Added `shopt -s nullglob` to `check-skill-freshness.sh`
- Added `HookScriptTests` class (8 tests covering skip logic, clean-project pass, stale/fresh detection, missing-date warning, empty directory)

---

*Add new entries as issues are discovered. Format: `KI-NNN` (open) or `KI-RNNN` (resolved).*
