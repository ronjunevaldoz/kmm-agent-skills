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

**Status:** Open  
**Affects:** `kotlin-multiplatform-adaptive-layout` skill, Check 7 in `agents/reviewer.md`  
**Symptom:** When adaptive layout skill is loaded in a project that has 10+ existing
screens with no `WindowSizeClass`, the reviewer correctly flags every screen as
`[ADAPTIVE]` — but fixing all of them in one session is impractical.  
**Root cause:** The reviewer applies the consistency rule uniformly; there is no
"migration mode" that only enforces the rule on *new* screens.  
**Workaround:** When retrofitting an existing project, explicitly tell the agent:
*"Only enforce adaptive layout on new screens in this session; track retrofitting as a
separate ticket."* The agent will honour that scope limit.  
**Fix needed:** Add a `adaptive_layout_migration_mode: true` flag to
`pipeline-context.json` that changes the reviewer from blocking to warning-only on
pre-existing screens.

---

### KI-004 — `hardcoded spacing` audit pattern can false-positive on `padding(0.dp)`

**Status:** Resolved — see KI-R06 below

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

*Add new entries as issues are discovered. Format: `KI-NNN` (open) or `KI-RNNN` (resolved).*
