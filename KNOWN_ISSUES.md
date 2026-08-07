# Known Issues

Tracks confirmed agent behavior gaps, tool limitations, and workarounds.
Resolved issues stay here for reference — they explain *why* a rule exists.

---

## Open

### KI-007 — External skill trigger isolation is unverifiable in general (not just inaccessible)

**Status:** Open — re-investigated 2026-07-10, found to be structurally unresolvable, not
just blocked on repo access as originally filed.

**Symptom:** The cross-skill audit (v1.21.6) identified four external skills referenced
in `skills/kmp-jni-pro/SKILL.md` — `cpp-pro`, `kotlin-specialist`, `compose-expert`,
and `android-cli`. Re-checked 2026-07-10: **only `cpp-pro` and `kotlin-specialist` are
still referenced** (see `SKILL.md`'s Related Skills); `compose-expert` and `android-cli`
no longer appear anywhere in the repo, so the original 4-skill list is stale.

For the two that remain, local copies were briefly available on the machine that filed
this issue and confirmed generic naming collisions across the ecosystem: a GitHub code
search for `cpp-pro SKILL.md` and `kotlin-specialist SKILL.md` returns dozens of
**unrelated skill collections** (`paperclipai/companies`, `diegosouzapw/awesome-omni-skills`,
`aldefy/compose-skill`, etc.) each shipping their own version of a skill with that name.
There is no single canonical `cpp-pro` or `kotlin-specialist` to audit — the actual
trigger vocabulary a user gets depends entirely on which collection they installed from.
This makes the original "Fix" (read the four repos, compare triggers) impossible in
principle, not just impractical: there's nothing singular to read.

**Mitigation already in place:** `kmp-jni-pro`'s Related Skills section
already disambiguates the one overlap that's plausible in practice — `cpp-pro`'s generic
"C++ performance/algorithm work" scope vs. `wrapper.cpp` files that JNI-pro also owns:
> `/cpp-pro` *(external skill)* — algorithm-level C++ work inside `*-wrapper.cpp`; pair
> when the task involves changing native processing code rather than bridge wiring

This only helps if both skills are loaded together and the agent actually reads
`jni-pro`'s pairing note — it doesn't prevent a differently-scoped `cpp-pro` install from
firing alone on an ambiguous request without ever consulting `jni-pro`.

**Workaround:** `routing_rules.json`'s `hard_boundaries` and `intent_routes` remain the
authoritative JNI trigger set for *this* repo — that part is unaffected. When integrating
`cpp-pro` or `kotlin-specialist` from any source, inspect **whatever copy is actually
installed locally** at the time (`~/.claude/skills/<name>/SKILL.md` if present) — there is
no fixed upstream reference to check instead.

**Fix:** Not resolvable in general, since it depends on a naming collision in the wider
skill ecosystem this repo doesn't control. The practical mitigation is the disambiguation
note already in `jni-pro`'s Related Skills section; closing this further would mean
renaming the external references to something less generic (not currently planned) or
accepting the residual risk as documented here.

---

### KI-009 — slash commands exceeding the 500-line progressive-disclosure guideline

**Status:** Open, one command remaining. The 500-line guideline now covers `SKILL.md`
(KI-008, resolved), `references/*.md` (v2.10.0), and `commands/*.md` (the
`oversized_command_md` check).

| Command | Was | Now | State |
|---|---|---|---|
| `/kmp-setup-agents` | 638 | **496** | ✅ resolved — `AGENTS.md` + `CLAUDE.md` template bodies moved to `kmp-expert`'s `references/agents-md-templates.md` |
| `/kmp-new-project` | 1390 | 1157 | Open — Step 10's duplicated agent setup was removed (a real drift bug, see below), but the command is still 2.3x over |

**Why the templates went to a skill reference, not a plugin-root `assets/` directory:**
`/kmp-setup-agents` is consumer-facing (README tells users to run it in any existing KMP
project), and `update-consumer-skills.sh --install-commands` copies a command as a single
bare `.md` file. Skills are always deployed; assets are not. A template referenced from
`assets/` would resolve in this repo and be missing in every consumer project.

**Why it matters:** a slash command's whole body loads into context the moment it's
invoked — the same cost the guideline bounds for `SKILL.md`. `/kmp-new-project` is also
the single most likely command to be invoked at the *start* of a session, when the
context it consumes is most valuable.

**Why it isn't a mechanical fix like KI-008 was:** a `SKILL.md` split moves reference
material an agent loads on demand. A command is an *executable procedure* — ordered,
cross-referencing steps where the agent is mid-workflow. Deciding which steps can move
into the owning skill (`kmp-feature-scaffold`, `kmp-setup-agents`' own targets) versus
which must stay inline to keep the procedure followable is a real per-command judgment
call, and getting it wrong breaks the new-project workflow rather than just making a doc
harder to find.

**Mitigation in place:** `scripts/scan_skill_issues.py`'s `oversized_command_md` check
flags any *new* command that crosses the line; these two are in `KNOWN_DEBT` so they're
reported but don't block a release, same handling KI-008 had.

---

## Resolved

### KI-008 — 22 of 64 SKILL.md files exceed agentskills.io's recommended 500-line body

**Resolved:** 2026-08-04 — all 22 skills split into `references/*.md`, one commit/skill
plus a final batch, verified against the full pytest suite and all 6 release gates after
each. `kmp-compose-design-system-extended` (3101 lines, the worst offender at 6.2x over)
went to 443; the rest landed at or under 500. No content was removed, only relocated —
each moved section left a pointer stub (`Full content: references/<file>.md.`) under its
original heading so the table of contents an agent sees on activation is unchanged.

`kmp-expert` kept its two routing tables (`## The 68 Skills and What They Own`, `## Skill
Invocation Map`) inline since `validate_skill_map.py`/`validate_keyword_routing.py` check
that file's own text directly and don't read `references/`.

**Also fixed in the process** — three checks that only ever scanned `SKILL.md` text and
went blind once content moved to `references/`:
- `kmp-audit/scripts/audit_skills_repo.py`'s `_check_design_system` content checks
- `scripts/check_compat_matrix.py` (missed a `roborazzi` version pin moved out of
  `kmp-feature-scaffold`, caught by `tests/test_release.py`'s gate-order test)
- `tests/test_docs_governance.py`'s project-owned-scaffold-contract test (content moved
  out of `kmp-expert`)

All three now concatenate `references/*.md` onto `SKILL.md` text before checking, the
same pattern in each case.

`scripts/scan_skill_issues.py`'s `KNOWN_DEBT` baseline had every `oversized_skill_md`
entry removed; only the unrelated `description_approaching_limit` debt (a different
check — description field length, not body length) remains for 2 skills.

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
**Fix:** New `kmp-compose-adaptive-layout` skill documents the canonical
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
routed to `kmp-compose-graphics-modifiers` instead of
`kmp-roborazzi`. Several other skills had narrow keyword vocabularies
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
`kmp-` prefix) with a `SKIP_PLANNER` set for meta-skills that
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
Reviewer Check 12, implementer Script test maintenance section, and `/kmp-modify-skill` Rule 8
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

### KI-R14 — Keyword routing gaps for `datastore` and `kmp-jni-pro`

**Resolved:** `v1.13.0` — `feat(expert+tests): keyword routing coverage, validate_keyword_routing.py, visual design audit`  
**Was:** Both skills were fully registered (README, expert table, planner routing) but had no rows in the Skill Invocation Map in `kmp-expert/SKILL.md`. The invocation map is the table the expert uses for real-time keyword routing — without rows, queries like "DataStore", "save settings", or "JNI bridge" would not activate the correct skill.  
**Fix:**
- Added two invocation map rows to the expert SKILL.md
- Created `validate_keyword_routing.py` — validates every skill (excluding meta-skills) has at least one invocation map row; returns `OK: N skills` or errors per missing skill
- Added `ValidateKeywordRoutingTests` (5 tests) to `tests/test_skill_scripts.py`

---

### KI-R15 — No tooling to catch visual design regressions in Roborazzi goldens

**Resolved:** `v1.13.0` — `feat(expert+tests): keyword routing coverage, validate_keyword_routing.py, visual design audit`  
**Was:** Roborazzi golden diffs catch pixel-level regressions but could not detect whether a committed golden was design-system-compliant. A developer could record a new golden with a missing TopAppBar, broken dark mode, or hardcoded colors — the screenshot tests would pass, but the screen would violate the design contract.  
**Fix:**
- Created `commands/kmp-audit-screenshots.md` — a `/kmp-audit-screenshots` command that uses Claude vision to analyze light/dark PNG pairs against design-system rules (color tokens, AppScaffold structure, dark mode parity, spacing, typography, contrast)
- Wired as Step 5 of `commands/kmp-verify.md` — runs automatically after `jvmTest` if new/modified PNGs are present
- Wired as Check 13 of `agents/reviewer.md` — reviewer invokes the audit on screenshot goldens modified in the session
- Added Visual Design Audit section to `skills/kmp-roborazzi/SKILL.md`

---

---

### KI-R16 — Design system had no update path once code was copied to a project

**Resolved:** `v1.17.0` — `feat(design-system): ownership model, stability tiers, /kmp-update-design-system command`  
**Was:** The design-system skill generated code by copying snippets from SKILL.md into the project. Once copied, there was no way for the agent to know whether a project's component had drifted from the skill reference, so bug fixes and improvements in the skill were silently ignored by all existing projects.  
**Fix:**
- Added `## Ownership Model` section to base and extended SKILL.md — splits files into project-owned (tokens, theme) and skill-owned (components)
- Created `scripts/update_design_system.py` — parses `### components/AppXxx.kt` blocks from SKILL.md, MD5-compares against project files, reports CURRENT / MODIFIED / MISSING; `--diff AppButton` shows unified diff
- Created `commands/kmp-update-design-system.md` — 5-step command: run script, present report, diff modified files one at a time, apply approved changes, compile
- Added stability tiers (Stable / Experimental) to all 33 components across base and extended skills
- Added routing keywords to expert Skill Invocation Map ("update design system", "sync components", etc.)
- Added 13 tests for `update_design_system.py` (total test suite: 98 tests)

---

---

### KI-R17 — No automated way to find design violations in existing project code

**Resolved:** `v1.18.0` — `feat(design-system): add /kmp-fix-design command with Roborazzi vision verification`  
**Was:** The agent had no systematic way to find hardcoded colors, literal dp values, `MaterialTheme.*` access, `TextStyle()` construction, or nested Card/Surface containers in an existing project. When asked to "fix the design," it improvised — reading a few files and guessing, with no ordered priority and no safety guard.  
**Fix:**
- Created `scripts/scan_design_violations.py` — scans `*.kt` files for 5 violation categories, skips design-system source files, outputs JSON with file/line/severity; exit 0=clean, 1=violations, 2=not found
- Created `commands/kmp-fix-design.md` — 5-step command: scan → summarize → fix each file with per-file diff+confirmation → regenerate Roborazzi screenshots → vision verify
- Vision verification step reads light+dark PNGs with Claude vision and checks: brand color on primary actions, spacing consistency, no nested-card double-shadow, dark mode background, typography hierarchy
- Added routing keywords to expert Skill Invocation Map
- Added 22 tests for `scan_design_violations.py` (total: 120 tests passing)

---

*Add new entries as issues are discovered. Format: `KI-NNN` (open) or `KI-RNNN` (resolved).*
