# Changelog

All notable changes to kmm-agent-skills are documented here.

## [v1.25.0] — 2026-06-23

### Added

- feat(governance): add CI enforcement gate for skill consumers

---

## [v1.24.1] — 2026-06-23

### Added

- feat(release): add development versioning guidance

---

## [v1.24.0] — 2026-06-23

### Added

- feat(release): add kotlin-multiplatform-release skill

---

## [v1.23.2] — 2026-06-23

### Added

- feat(ci): add Maven Central publish, Doppler, git-cliff changelog, versioning

### Fixed

- fix(report-skill-issue): add Step 0 triage gate — skill vs project issue

### Other

- Revert "feat(ci): add Maven Central publish, Doppler, git-cliff changelog, versioning"
- Release v1.23.1

---

## [v1.23.1] — 2026-06-23

### Fixed

- fix(report-skill-issue): add Step 0 triage gate — skill vs project issue

---

## [v1.23.0] — 2026-06-23

### Added

- feat(consumer): GitHub issue templates, /report-skill-issue command, draft_issue --submit

---

## [v1.22.0] — 2026-06-22

### Added

- feat(design-system): detect cross-screen layout inconsistency

---

## [v1.21.9] — 2026-06-22

### Docs

- docs(known-issues): add KI-007 — external skill trigger isolation unverifiable

---

## [v1.21.8] — 2026-06-22

### Other

- refactor(AGENTS.md): pointer model — remove embedded rule copies

---

## [v1.21.7] — 2026-06-22

### Other

- refactor(jni-kotlin-pro): compress B1/B2 bloat — merge stack sections, table-ify anti-patterns

---

## [v1.21.6] — 2026-06-22

### Fixed

- fix(routing): correct JNI skill vocabulary, cross-ref immutability rule, add routing matrix

### Chore

- chore: workspace agent config (AGENTS.md persona + CLAUDE.md CLI profile)

---

## [v1.21.5] — 2026-06-22

### Added

- feat(jni-kotlin-pro): header compatibility matrix + architectural feedback schema

---

## [v1.21.4] — 2026-06-22

### Added

- feat(jni-kotlin-pro): cmake-jni-setup.md + wrapper-patterns.md references

---

## [v1.21.3] — 2026-06-22

### Added

- feat(jni-kotlin-pro): Phase 0 discovery gate + wrapper-call pattern

---

## [v1.21.2] — 2026-06-22

### Fixed

- fix(jni-kotlin-pro): hard stop rule for 3rd party file modification

---

## [v1.21.1] — 2026-06-22

### Added

- feat(design-system): add references/design-system-template.md

### Docs

- docs(design-system): add References section for references/ directory

---

## [v1.21.0] — 2026-06-22

### Added

- feat(design-system): RedundantScreenTitleRule + HardcodedGridColumnsRule + MultiDevicePreview

---

## [v1.20.1] — 2026-06-22

### Fixed

- fix(design-system): use GROUP_ID placeholder in detekt-rules module

---

## [v1.20.0] — 2026-06-22

### Added

- feat(design-system): PSI-based detekt scanner + Roborazzi baselines + visual audit

### Chore

- chore: consolidate v1.19.1 CHANGELOG into single detailed entry

---

## [v1.19.1] — 2026-06-22

### Fixed

- fix(release): release script no longer prepends a duplicate CHANGELOG entry when a detailed one was already written manually; version guard now runs before git log so no subprocess call is made
- fix(audit): `_check_design_system()` now flags missing `## Component Previews` section and `### previews/` blocks in the base design-system skill
- test: update `_DS_GOOD_CONTENT` fixture to include previews section; add `test_ds_flags_missing_component_previews` (total: 126 tests)

---

## [v1.19.0] — 2026-06-22

### Added

- feat(design-system): add per-component preview files — `previews/AppThemePreviewWrapper.kt` + one preview file per base component (AppButton, AppBadge, AppCard, AppChip, AppTextField, AppText) with light/dark and key-state variants
- feat(design-system): extend `update_design_system.py` to sync `previews/` blocks alongside `components/` blocks; `find_component_dir` now returns parent dir so both subdirectories are covered
- feat(fix-design): add component-level Roborazzi step — run `:core:designsystem:jvmTest` first to verify components in isolation before feature tests
- test: add 7 tests for preview block parsing and syncing (total: 125 tests)

---

## [v1.18.0] — 2026-06-22

### Added

- feat(design-system): add `scripts/scan_design_violations.py` — scans Compose files for hardcoded colors, dp literals, MaterialTheme usage, TextStyle construction, and nested containers; exit 0/1/2, `--json` and `--file` modes
- feat(design-system): add `commands/fix-design.md` — fix violations file-by-file with per-file diff confirmation, regenerate Roborazzi screenshots, and verify fixes with Claude vision
- feat(expert): add `/fix-design` routing keywords to Skill Invocation Map
- test: add 22 tests for `scan_design_violations.py` (total: 120 tests passing)

---

## [v1.17.0] — 2026-06-22

### Added

- feat(design-system): add ownership model (project-owned tokens vs skill-owned components), stability tiers for all components, and `scripts/update_design_system.py`
- feat(design-system): add `/update-design-system` command with diff-and-confirm workflow
- feat(expert): add `/update-design-system` routing keywords to Skill Invocation Map
- test: add 13 tests for `update_design_system.py` (total: 98 tests)

---

## [v1.16.5] — 2026-06-22

### Other

- enforce(audit): add design-system content checks to audit_skills_repo

---

## [v1.16.4] — 2026-06-22

### Fixed

- fix(design-system): resolve all 7 audit findings

---

## [v1.16.3] — 2026-06-22

### Fixed

- fix(adaptive-layout): add missing trigger keywords for mobile/desktop/detail-split routing

---

## [v1.16.2] — 2026-06-21

### Other

- enforce(naming): document and audit file naming conventions

---

## [v1.16.1] — 2026-06-21

### Other

- refine(legal-docs): auto-detect data collection + consent gate explanation + CI gate

---

## [v1.16.0] — 2026-06-21

### Added

- feat(legal-docs): add kotlin-multiplatform-legal-docs lawyer agent skill

---

# Changelog

All notable changes to **kmm-agent-skills** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [v1.15.0] — 2026-06-21

### Added
- `CONTRIBUTING.md` — contribution guide covering skill authoring, commit format, PR checklist, and release process
- `agents/changelog.md` — changelog agent: categorizes git + skill diff into Breaking/New/Improved/Fixed and generates consumer-facing release notes
- `commands/release-notes.md` — `/release-notes` command: generates per-skill or collection release notes from git history and `## Changelog` tables
- `scripts/generate_release_notes.py` — reads git log, maps commits to skills, parses per-skill `## Changelog` tables; outputs structured JSON for the changelog agent
- `## Changelog` section added to all 47 skills — consumer-facing release note table travels with each skill when installed

### Changed
- `feature-scaffold` skill: app versioning pattern defined — `VERSION_NAME`/`VERSION_CODE` in `gradle.properties` as single source of truth; `androidApp` reads from properties; `BuildKonfig` exposes `APP_VERSION` to `commonMain`; `libs.versions.toml` is for dependency versions only
- `flavor-environment` skill: `APP_VERSION` added to `BuildKonfig defaultConfigs`; `AppConfig.versionName` added to public facade
- `feature-scaffold` skill Step 3 rewritten: mandatory `Kotlin/kmp-wizard` clone replaces manual file creation
- `feature-scaffold` skill Step 4 rewritten: extend kmp-wizard's build-logic rather than recreate it
- `feature-scaffold` anti-patterns: hand-scaffolding and precompiled `.gradle.kts` script plugins now listed as explicit blockers
- `/new-project` command F-01 step updated to clone-first mandate with `./gradlew help` gate
- `audit_skills_repo.py`: `## Changelog` added to `REQUIRED_MARKERS` — skills without it now fail the audit

### Fixed
- `kotlin-multiplatform-expert` skill: removed private Carpool project reference from docs-first rule

### Docs
- `kotlin-multiplatform-audit` skill: defined `[category] short description` issue title format with category table and examples

---

## [v1.14.0] — 2026-06-21

### Added
- `/new-project` command — natural language to full KMP scaffold, 8-step pipeline, no user gates; infers platforms, features, data, backend from a single prompt
- `samples/todo-app.md` — E2E test spec for the todo app: 4 features, SQLDelight persistence, 12 skills, objective pass/fail quality bar (audit + jvmTest + Roborazzi + visual audit)

### Changed
- `/verify` command: added Step 5 visual design audit (runs `/audit-screenshots` when PNGs modified)
- `agents/reviewer.md`: added Check 13 visual design audit on Roborazzi screenshots
- `kotlin-multiplatform-roborazzi` skill: documented visual design audit and dynamic path resolution

---

## [v1.13.0] — 2026-06-18

### Added
- `validate_keyword_routing.py` script — ensures every skill has at least one trigger keyword registered; now part of CI gate
- Visual design audit step integrated into `/verify` and `agents/reviewer.md`

### Fixed
- `/audit-screenshots` command: Roborazzi output directory resolved dynamically from `build.gradle.kts` instead of hardcoded path; falls back to `src/jvmTest/snapshots/` or `src/test/snapshots/`

---

## [v1.12.0] — 2026-06-21

### Added
- Tests for pipeline flag contract (KI-005) and hook script behaviour (KI-006)

---

## [v1.11.1] — 2026-06-21

### Added
- `/verify` command — KMP validation pipeline: module graph, unit tests, screenshot tests, architecture audit, summary

### Docs
- Updated `PLAN.md` and `KNOWN_ISSUES.md` to reflect v1.11.0 state

---

## [v1.11.0] — 2026-06-21

### Added
- Test maintenance enforcement: planner routing validation and skill freshness gates added to pipeline

---

## [v1.10.0] — 2026-06-21

### Added
- 7 pipeline gap fixes: planner routing, `/new-skill` command, Detekt rule reference, PR template, hooks guide, test additions, 2 new skills

---

## [v1.9.0] — 2026-06-21

### Added
- ktlint enforcement gate in CI and reviewer pipeline
- Proactive issue tracking: reviewer now creates `[build]` issues for lint failures

---

## [v1.8.0] — 2026-06-21

### Added
- `## Testing` sections added to 18 skills that were missing them
- Contribution rules added to `AGENTS.md`

### Fixed
- Medium-priority audit findings resolved across 6 skills

---

## [v1.7.1] — 2026-06-21

### Fixed
- `[TRANSPORT]` fixer rule for kRPC boundary enforcement
- Stale shipped-skill count in `PLAN.md`
- kRPC context flag added to `pipeline-context.json`
- Run-audit quality scan added to release gate

---

## [v1.7.0] — 2026-06-21

### Added
- `/summarize-issues` command — scans all skills for quality gaps and outputs copy-paste fix prompts
- `scan_skill_issues.py` script — automated gap detection across the skills repo

---

## [v1.6.0] — 2026-06-21

### Added
- Skills freshness check at pipeline start — auto-detects when local skills are behind `origin/main` and prompts the user to pull before proceeding

---

## [v1.5.2] — 2026-06-21

### Fixed
- `kotlin-multiplatform-mongodb-database`: added `## Testing` section covering `FakeRepository`, Flapdoodle integration tests, change stream testing, and document mapping

---

## [v1.5.1] — 2026-06-21

### Fixed
- `kotlin-multiplatform-kotlin-rpc`: added kRPC transport pre-check to prevent HTTP bypass when RPC already owns the boundary

---

## [v1.5.0] — 2026-06-21

### Added
- 11 new skills: `analytics`, `form-validation`, `image-loading`, `permissions`, `deep-linking`, `compose-animation`, `biometric-auth`, `push-notifications`, `workmanager`, `feature-flags`, `accessibility`

---

## [v1.4.0] — 2026-06-21

### Added
- `kotlin-multiplatform-paging` skill — Paging 3 for KMP: `PagingSource`, `Pager`, `PagingData`, cursor vs offset, `RemoteMediator`, load-state handling

### Fixed
- `adaptive_layout_migration_mode` flag added to `pipeline-context.json` (KI-003)
- Pipeline context committed at end of every pipeline run (KI-001)
- `scripts/install-hooks.sh` one-liner added (KI-002)

---

## [v1.3.0] — 2026-06-21

### Added
- Screen layout contract and scaffold consistency enforcement in reviewer
- `kotlin-multiplatform-adaptive-layout` skill — WindowSizeClass breakpoints, list-detail, adaptive navigation
- Magic color literal detection in `audit_project.py`

### Fixed
- `audit_project.py`: excluded `0.dp` from hardcoded spacing pattern (KI-004)

### Docs
- `KNOWN_ISSUES.md` created with 4 open and 5 resolved issues

---

## [v1.2.3] — 2026-06-20

### Added
- `jni-kotlin-pro` skill — JNI bridge from Kotlin/JVM to native C/C++; 4-layer stack, memory safety, symbol isolation, GPU sync

### Fixed
- Added `## References` section to skills that have a `references/` directory

---

## [v1.2.2] — 2026-06-18

### Changed
- Rebranded all pipeline agent, command, and hook files with `kmm-agent-skills` identity

---

## [v1.2.1] — 2026-06-18

### Added
- `/execute-ticket` command — 9-phase pipeline: fetch GitHub Issue → plan → branch → implement → validate → review → commit → pipeline-context update → summary

---

## [v1.2.0] — 2026-06-18

### Added
- `agents/planner.md` — Layer Planner with work-type skill loading matrix and 6-layer build order
- `agents/implementer.md` — Layer Implementer with stack declaration, layer rules, Koin wiring, test generation
- `agents/reviewer.md` — Architecture Reviewer with 5 checks and APPROVE / NEEDS_FIXES verdict
- `agents/validator.md` — Build Validator with 4 graduated validation levels
- `agents/fixer.md` — Targeted Fixer with per-blocker fix rules and confidence ratings
- `commands/implement-feature.md`, `commands/review-changes.md`, `commands/run-audit.md`
- `hooks/pre-commit-audit.sh`, `hooks/validate-architecture.sh`, `hooks/check-skill-freshness.sh`
- `.claude/pipeline-context.json` — pipeline state store shared across agents

---

## [v1.1.7] — 2026-06-17

### Docs
- `## Trigger Keywords` table added to README — 31 rows, 3–4 phrases per skill

---

## [v1.1.6] — 2026-06-17

### Fixed
- Expanded trigger keywords across 14 skills to close natural-language routing gaps

---

## [v1.1.5] — 2026-06-17

### Fixed
- `kotlin-multiplatform-roborazzi` trigger keywords expanded to cover canvas/layout testing queries

---

## [v1.1.4] — 2026-06-17

### Added
- `manual screen capture` audit pattern in `audit_project.py` — flags Playwright, `adb screencap`, `xcrun simctl io`

---

## [v1.1.3] — 2026-06-17

### Changed
- `kotlin-multiplatform-roborazzi` expanded to cover the full UI testing stack including `@Preview` screenshot workflow

---

## [v1.1.2] — 2026-06-17

### Fixed
- YAML parse error in `roborazzi` and `preview-driven-development` skills (`@Preview` value unquoted)

### Added
- `.claude-plugin/plugin.json` for marketplace submission

---

## [v1.1.1] — 2026-06-17

### Fixed
- Full audit pass across all 31 skills — missing sections, stale `last-updated` frontmatter

---

## [v1.1.0] — 2026-06-17

### Added
- `kotlin-multiplatform-datastore` skill — Preferences DataStore, `createDataStore {}` expect/actual factory, Flow reads, Koin wiring, SharedPreferences migration

---

## [v1.0.2] — 2026-06-17

### Fixed
- Test coverage expanded from 12 to 16 tests covering two high-priority gaps

---

## [v1.0.1] — 2026-06-17

### Added
- `skills.sh.json` manifest and `npx skills add` install path
- `scripts/release.py` release automation
- `RELEASING.md` release guide

---

## [v1.0.0] — 2026-06-17

### Added
- Initial release — 6-layer clean architecture, 31 skills, `skills.json` manifest
- `audit_project.py` — KMP architecture smell detector
- `audit_skills_repo.py` — skills repo metadata and freshness checker
