# Deep Technical Audit — kmm-agent-skills

Date: 2026-08-02 · HEAD: `3181873` (v1.118.0) · Mode: **diagnose only, no code changed**

Every finding below was verified against an actual file lookup or command run — three
candidate findings from intermediate scans were discarded as false positives after
verification (`validate_module_graph.py`, `harvest_lessons.py`, and `publish.sh`
"missing script" hits: the first two exist in other skills' `scripts/` dirs, the third
is a template the skill *generates*, not a bundled file).

## Baseline (all green)

- 552 tests pass; all 6 release gates pass (audit, skill scan, shell portability,
  skill map, keyword routing, compat matrix)
- Every shell script (`bash -n`) and Python script (`ast.parse`) parses clean
- Zero dangling `kotlin-multiplatform-*` skill references across skills/commands/agents
- Zero skills with stale `last-updated` (>60 days)
- 66 skills indexed consistently across README, expert map, planner

---

## Critical

**None found.**

---

## High

### H-1 — Version drift: `library-publishing` Step 2 pins Kotlin 2.1.21
`skills/kotlin-multiplatform-library-publishing/SKILL.md:274` — the Step 2
`libs.versions.toml` example pins `kotlin = "2.1.21"` while the collection's canonical
baseline is 2.4.0 (`feature-scaffold` pins `kotlin = "2.4.0"`, PLAN.md line 169 says
2.4.0). Same block pins `vanniktech-publish = "0.30.0"` while
`kotlin-multiplatform-release/SKILL.md:261` pins `0.37.0` — two skills a library author
uses *together* disagree by 7 minor versions. A library scaffolded from this block
starts 3 Kotlin minors behind the rest of its own project.

### H-2 — PLAN.md's canonical version table is stale, and skills point at it
`PLAN.md:168-172` says AGP `9.0.1` and Ktor `3.1.3`. Real current pins in skills:
AGP `9.2.0` (`feature-scaffold:174,323`), Ktor `3.5.0` (`feature-scaffold:179`,
`network-layer:151`). This matters more than ordinary drift because
`feature-scaffold`'s own freshness rule says to check "the version table in `PLAN.md`
… before scaffolding" — the designated source of truth is the stalest copy.
(Kotlin 2.4.0 and CMP 1.11.1 rows are correct.)

---

## Medium

### M-1 — Command H1 names don't match installed filenames (19 of 29 files)
`commands/kmm-verify.md` declares `# /verify`, `kmm-run-audit.md` declares
`# /run-audit`, etc. Real invocation is by filename (`/kmm-verify`), so 19 headers
display a command name that doesn't exist as written. 10 files are consistent
(`kmm-new-project`, `kmm-setup-agents`, `kmm-generate-palette`, …) — the inconsistency
is the split itself. Verified by listing every file's first line.

### M-2 — Stale detached-HEAD git worktree checked into the working dir
`.claude/worktrees/lucid-euclid-69a5c1` — 4.1 MB full repo copy at detached commit
`98a1f05`, listed by `git worktree list`. Excluded from audit scans (so it causes no
false findings) but it's dead weight and a confusing duplicate source tree.
`git worktree remove` candidate.

### M-3 — Three genuinely untested scripts
Verified per-script against `tests/` contents (an initial list of 8 shrank to 3 after
checking actual test file references):
- `scripts/check_compat_matrix.py` — mitigated: runs inside every release gate, so a
  crash is caught, but its *logic* has no regression test
- `skills/kotlin-multiplatform-design-system/scripts/generate_palette.py`
- `skills/kotlin-multiplatform-skill-harvester/scripts/harvest_lessons.py`

### M-4 — Audit skill's own checklist contradicts repo reality on exec bits
`skills/kotlin-multiplatform-audit/SKILL.md:194` says "Check that scripts are
executable" — but effectively **no** bundled script has the executable bit set
(20 checked, all `not executable`). No functional break (everything is invoked via
`python3 …`/`bash …`), but the skill's own hygiene rule fails against its own repo.
Either chmod them all or amend the checklist line to match the real invocation
convention.

### M-5 — Detekt pinned to 1.23.7; current doc line is 2.0.0-alpha
`code-quality/SKILL.md:143` pins `detekt = "1.23.7"`. Detekt's own docs site now
documents 2.0.0-alpha.x (observed while verifying rules this session). 1.23.x is the
stable line, so the pin is defensible — but the skill has no freshness note saying the
2.x migration is coming, unlike other fast-moving-dependency skills that carry one.

### M-6 — `benchmark` skill states "Kotlin 2.2.0+" minimum
`skills/kotlin-multiplatform-benchmark/SKILL.md:68`. A minimum bound, not a pin, so
not wrong per se — but it reads stale beside the 2.4.0 baseline and was likely copied
from kotlinx-benchmark docs at writing time. Verify the library's real current minimum
before bumping the text.

---

## Low

### L-1 — Duplicate tokens inside single skills' own trigger-keyword lists
Verified in context:
- `form-validation`: "input validation" listed twice (`SKILL.md:35,36`)
- `design-system-extended`: "dialog" listed twice (`SKILL.md:62` + later "button, dialog,")
- `adaptive-layout`: "FlexBox, flexbox" — case-variant duplicate

Harmless (routing is effectively case-insensitive set matching) but sloppy; trivial trim.

### L-2 — 37 cross-skill trigger-keyword overlaps
Most are intentional companion pairs (`mvi`/`presenter-module` share the whole
screen-state vocabulary by design; `library-publishing`/`release` share
`vanniktech`/`sonatype`). The keyword-routing validator only checks documented
*alternative* pairs, so these pass. Worth a look only where the overlap crosses
genuinely different domains: `database` (mongodb vs sqldelight — server vs local, a
disambiguation row like the existing jni/cinterop one would help), `ktor rpc`
(kotlin-rpc vs ktor-auth-service), `token refresh` (network-layer vs
push-notifications — different tokens entirely).

### L-3 — Known debt, already tracked (restated for completeness)
22 skills over the 500-line agentskills.io guideline + 3 descriptions approaching the
1024-char limit — all in `scan_skill_issues.py`'s `KNOWN_DEBT` baseline (KI-008),
reported but non-blocking, unchanged this audit.

---

## Scope gaps (skills not yet covering)

From PLAN.md's own backlog (`:156-160`), still open and accurate: Kotlin 2.x/K2
verification pass (HIGH in backlog — matches H-1/H-2 above, same root cause), AGP 10
migration prep, CMP 2.x readiness, `testing-robot` (deliberately deferred). Held off
by explicit decision this session: cross-platform obfuscation beyond Android R8
(iOS/Wasm sections need better sourcing before writing). No other unscoped domain
surfaced in this pass that isn't already tracked.

## Maintainability verdict

Standards-compliant (agentskills.io validated, all gates green) and actively
maintainable — versioning drift (H-1/H-2) is the one systemic weakness: version pins
live in ~6 places (PLAN.md table, per-skill TOML snippets) with no mechanical check
that they agree. A `check_version_pins.py` gate comparing every `= "x.y.z"` pin for
agp/kotlin/ktor/compose across skills against PLAN.md's table would prevent H-1/H-2
recurring — recommended as the first fix, before touching the individual stale values.

---
*Diagnose-only report. No code, config, or doc files were modified. Awaiting review
before any fixes.*
