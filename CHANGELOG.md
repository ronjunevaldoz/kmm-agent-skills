# Changelog

All notable changes to kmm-agent-skills are documented here.

## [v1.5.1] — 2026-06-21

### Fixed

- Fix: add kRPC transport pre-check to prevent HTTP bypass when RPC already owns the boundary

---

## [v1.5.0] — 2026-06-21

### Other

- Add 11 new skills: analytics, form-validation, image-loading, permissions, deep-linking, compose-animation, biometric-auth, push-notifications, workmanager, feature-flags, accessibility

---

## [v1.4.0] — 2026-06-21

### Added

- feat(paging): add kotlin-multiplatform-paging skill

### Fixed

- fix(reviewer): add adaptive_layout_migration_mode to pipeline-context (KI-003)
- fix(pipeline): commit pipeline-context.json at end of every pipeline run (KI-001) fix(hooks): add scripts/install-hooks.sh one-liner (KI-002)

---

## [v1.3.0] — 2026-06-21

### Added

- feat(layout): enforce screen layout contract and scaffold consistency
- feat(adaptive+theme): add adaptive-layout skill and dark/light mode enforcement
- feat(audit): detect magic color literals in UI composables

### Fixed

- fix(audit): exclude 0.dp from hardcoded spacing pattern (KI-004)

### Docs

- docs: add KNOWN_ISSUES.md with 4 open and 5 resolved issues

### Chore

- chore(release): add CHANGELOG.md generation and GitHub Release to release script
- chore(plan): mark datastore shipped, document 6 undiscovered gaps

---

---

## [v1.2.3] — 2026-06-20

### Added
- `jni-kotlin-pro` skill — JNI bridge engineering between Kotlin/JVM and native C++; 4-layer stack, memory safety, symbol isolation, GPU sync

### Fixed
- Added `## References` section header to satisfy `audit_skills_repo` check for skills with a `references/` directory

---

## [v1.2.2] — 2026-06-18

### Chore
- Rebranded all pipeline agent/command/hook files with KMM Agent Skills identity; removed structural similarity to external repos

---

## [v1.2.1] — 2026-06-18

### Added
- `/execute-ticket` command — 9-phase pipeline: fetch GitHub Issue → plan → branch → implement → validate → review → commit → pipeline-context update → summary

---

## [v1.2.0] — 2026-06-18

### Added
- `agents/planner.md` — Layer Planner with work-type skill loading matrix and 6-layer build order
- `agents/implementer.md` — Layer Implementer with stack declaration, layer rules, Koin wiring, test generation
- `agents/reviewer.md` — Architecture Reviewer with 5 checks and APPROVE/NEEDS_FIXES verdict
- `agents/validator.md` — Build Validator with 4 graduated levels
- `agents/fixer.md` — Targeted Fixer with per-blocker fix rules and confidence ratings
- `commands/implement-feature.md`, `commands/review-changes.md`, `commands/run-audit.md`
- `hooks/pre-commit-audit.sh`, `hooks/validate-architecture.sh`, `hooks/check-skill-freshness.sh`
- `.claude/pipeline-context.json` — pipeline state store

---

## [v1.1.7] — 2026-06-17

### Added
- `## Trigger Keywords` table in README (31 rows, 3–4 phrases per skill)

---

## [v1.1.6] — 2026-06-17

### Fixed
- Expanded trigger keywords across 14 skills to close natural-language routing gaps

---

## [v1.1.5] — 2026-06-17

### Fixed
- Roborazzi skill routing for canvas/layout testing queries (`visual accuracy`, `pixel-perfect`, `canvas test`, etc.)

---

## [v1.1.4] — 2026-06-17

### Added
- `manual screen capture` audit pattern in `audit_project.py` — flags `playwright`, `adb screencap`, `xcrun simctl io`

---

## [v1.1.3] — 2026-06-17

### Added
- Expanded `kotlin-multiplatform-roborazzi` to cover full UI testing stack

---

## [v1.1.2] — 2026-06-17

### Fixed
- YAML parse error in roborazzi and preview-driven-development skills (`@Preview` unquoted)
- Added `.claude-plugin/plugin.json` for marketplace submission

---

## [v1.1.1] — 2026-06-17

### Fixed
- Full audit and cleanup pass across all 31 skills — missing sections, stale frontmatter

---

## [v1.1.0] — 2026-06-17

### Added
- `kotlin-multiplatform-datastore` skill — Preferences DataStore, `createDataStore {}` expect/actual, Flow reads, Koin wiring

---

## [v1.0.2] — 2026-06-17

### Fixed
- Test coverage expanded: 12 → 16 tests covering two high-priority gaps

---

## [v1.0.1] — 2026-06-17

### Added
- `skills.sh.json` and `npx skills add` install path
- `scripts/release.py` and `RELEASING.md`

---

## [v1.0.0] — 2026-06-17

### Added
- Initial release — 6-layer clean architecture, 31 skills, `skills.json` manifest, `audit_project.py`, `audit_skills_repo.py`
