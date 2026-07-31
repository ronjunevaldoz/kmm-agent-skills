# kmm-agent-skills

[![skills.sh](https://skills.sh/b/ronjunevaldoz/kmm-agent-skills)](https://skills.sh/ronjunevaldoz/kmm-agent-skills)
[![Agent Skills spec](https://img.shields.io/badge/Agent%20Skills-spec%20compliant-brightgreen)](docs/reference/agentskills-io-standards.md)
[![License](https://img.shields.io/github/license/ronjunevaldoz/kmm-agent-skills)](LICENSE)
[![Repo size](https://img.shields.io/github/repo-size/ronjunevaldoz/kmm-agent-skills)](https://github.com/ronjunevaldoz/kmm-agent-skills)
[![Last commit](https://img.shields.io/github/last-commit/ronjunevaldoz/kmm-agent-skills)](https://github.com/ronjunevaldoz/kmm-agent-skills)

AI agent skills for **Kotlin Multiplatform (KMP)** development — clean module boundaries,
version catalogs, build-logic convention plugins, and explicit review loops before code is generated.

Built on the open [Agent Skills](https://agentskills.io) format. All 65 skills verified
against the real [`skills-ref`](https://github.com/agentskills/agentskills) reference
validator — see [`docs/reference/agentskills-io-standards.md`](docs/reference/agentskills-io-standards.md)
for what was checked and how.

---

## Main Use Cases

### Start a new KMP project

Run `/kmm-new-project` with a natural language description. The agent asks for your group ID, project
name, and what the app does — then scaffolds a full multi-module KMP project with clean architecture,
a design system, and a ready-to-use `.claude/` agent setup.

```
/kmm-new-project "A shopping app with auth, product listing, and orders"
```

The 9-step pipeline handles everything: module graph → clean-arch layers → Koin/Ktor/SQLDelight
wiring → design system → feature scaffolds → `.claude/AGENTS.md` tailored to your modules.

### Set up agents in an existing project

Run `/kmm-setup-agents` in any existing KMP project. It reads your `settings.gradle.kts` and
`libs.versions.toml`, then generates a custom `AGENTS.md` routing table based on the libraries
and feature modules it finds.

```
/kmm-setup-agents
```

Writes: `.claude/AGENTS.md` (tailored skill routing), `CLAUDE.md` (CLI flags), all consumer
commands (`kmm-*.md`), deployed skills, and a `settings.json` Bash allowlist.

### Cross-agent repo policy

Downstream repos should keep canonical collaboration policy in:

- [`docs/reference/ai-collaboration.md`](docs/reference/ai-collaboration.md)
- [`docs/reference/agent-catalog.md`](docs/reference/agent-catalog.md)

Use `docs/*` for stable project design and ownership rules, and `skills/*` for
repo-local agent execution guidance. Keep `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`
thin and pointer-based instead of turning them into the only source of truth.

### Audit an existing project

```
/kmm-run-audit
```

Runs `audit_project.py` across your project and produces per-finding remediation steps using
the relevant skill. Catches architecture boundary violations, missing Koin bindings, layer leaks,
hardcoded colors, and Material theme usage. See [`kotlin-multiplatform-audit`](skills/kotlin-multiplatform-audit/) for what it checks.

---

## Quick Start

```bash
npx skills add ronjunevaldoz/kmm-agent-skills
```

Then in Claude Code:

1. **New project** → `/kmm-new-project <description>`
2. **Existing project** → `/kmm-setup-agents`
3. **Audit** → `/kmm-run-audit`
4. **Implement a feature** → `/kmm-implement-feature <name>`

**Start here:** not sure which skill to use? Ask `kotlin-multiplatform-expert` — it routes you
to the smallest relevant skill set.

---

## Key Features

### Auto-reporting — consumer side
Every consumer project running `/kmm-run-audit` or `/kmm-harvest-lessons` can now surface
issues back to this repo without leaving the terminal:

- `/kmm-run-audit` **Step 7**: detects when a finding points to a *skill gap* (not just bad
  consumer code) and prompts `[y] Submit / [n] Skip / [v] View draft` — submits via `gh` or
  falls back to a browser URL
- `/kmm-harvest-lessons` **Step 6**: after every harvest, each positive pattern that the
  skills don't yet teach triggers the same interactive prompt to file an improvement proposal
- Both flows use `draft_issue.py --submit --repo ronjunevaldoz/kmm-agent-skills`

**Who runs it:** the consumer (any project using kmm-agent-skills).
**Where it goes:** issues land in this repo's GitHub Issues for the skills team to act on.

### Smart versioning — skills-repo side
`scripts/release.py` now has an `auto` bump mode that reads conventional commits and picks
the right tier — no more guessing or accumulating patch releases when a `feat` was shipped:

```bash
python3 scripts/release.py auto           # detects major / minor / patch
python3 scripts/release.py auto --dry-run # preview first
```

| Commit type | Bump |
|---|---|
| `feat!` or `BREAKING CHANGE` | major |
| `feat` | minor |
| `fix`, `chore`, `docs`, `refactor` | patch |

**Who runs it:** only the kmm-agent-skills maintainer when cutting a release.

---

## Skills

65 skills covering the full KMP stack. Load the smallest set that answers the request.
Health at a glance (size, freshness, known issues) without reading every `SKILL.md`:
[`docs/reference/skills-report.md`](docs/reference/skills-report.md).

| Category | Count | Covers |
|---|---|---|
| Foundation | 7 | Module structure, clean architecture, DI, CI, Android CLI |
| Infrastructure | 10 | Auth, networking, database, publishing, JNI |
| Patterns | 21 | MVI, navigation, offline-first, notifications, IAP, and more |
| UI System | 12 | Design system, state hoisting, animation, adaptive layout |
| Testing & Quality | 5 | Unit tests, screenshot tests, lint/static analysis |
| Meta | 9 | Routing, audit, migration, docs, release |

<details>
<summary>Full skill list (click to expand)</summary>

### Foundation
- [`feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) — 6-layer module structure, build-logic, TOML catalog, Koin
- [`clean-architecture`](skills/kotlin-multiplatform-clean-architecture/) — layer contract, `:model` vs `:api`, `internal` rules
- [`presenter-module`](skills/kotlin-multiplatform-presenter-module/) — pure-Kotlin ViewModel, MVI contracts, no Compose dep
- [`dependency-injection`](skills/kotlin-multiplatform-dependency-injection/) — Koin wiring and scopes
- [`flavor-environment`](skills/kotlin-multiplatform-flavor-environment/) — BuildKonfig, secrets, env setup
- [`ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) — CI matrix and release workflow
- [`android-cli`](skills/kotlin-multiplatform-android-cli/) — Google's `android` CLI: emulator, build/deploy, SDK installs, agent bootstrap

### Infrastructure
- [`ktor-auth-service`](skills/kotlin-multiplatform-ktor-auth-service/) — auth service, bearer/JWT, sessions
- [`network-layer`](skills/kotlin-multiplatform-network-layer/) — Ktor client, auth refresh, result mapping
- [`sqldelight-setup`](skills/kotlin-multiplatform-sqldelight-setup/) — SQLDelight schema, drivers, migrations
- [`datastore`](skills/kotlin-multiplatform-datastore/) — Preferences DataStore + Proto DataStore
- [`xcframework-spm`](skills/kotlin-multiplatform-xcframework-spm/) — XCFramework and SPM export
- [`library-publishing`](skills/kotlin-multiplatform-library-publishing/) — Maven Central, GitHub Packages, BOM, binary-compat-validator, GPG signing
- [`docs-site`](skills/kotlin-multiplatform-docs-site/) — GitHub Pages developer guide, MkDocs Material, Dokka HTML API reference, compiler-verified code examples
- [`api-mimicry`](skills/kotlin-multiplatform-api-mimicry/) — mimic a reference API's shape (Modifier chains, slot DSLs) for a from-scratch library on a non-standard runtime
- [`mongodb-database`](skills/kotlin-multiplatform-mongodb-database/) — MongoDB coroutine driver and repositories
- [`kotlin-rpc`](skills/kotlin-multiplatform-kotlin-rpc/) — Kotlin RPC boundaries and scaffolding
- [`jni-pro`](skills/kotlin-multiplatform-jni-pro/) — JVM JNI bridge to native C/C++

### Patterns
- [`mvi`](skills/kotlin-multiplatform-mvi/) — State / Intent / Effect, Channel effects, MviViewModel base
- [`expect-actual`](skills/kotlin-multiplatform-expect-actual/) — platform-specific implementations
- [`repository-pattern`](skills/kotlin-multiplatform-repository-pattern/) — repository boundary, fetch strategy
- [`navigation`](skills/kotlin-multiplatform-navigation/) — type-safe navigation, auth gate
- [`deep-linking`](skills/kotlin-multiplatform-deep-linking/) — App Links, Universal Links, URI schemes
- [`offline-first`](skills/kotlin-multiplatform-offline-first/) — SyncState, optimistic updates, conflict resolution
- [`paging`](skills/kotlin-multiplatform-paging/) — Paging 3, PagingSource, RemoteMediator
- [`logging`](skills/kotlin-multiplatform-logging/) — logger wrapper, kotlin-logging or Kermit
- [`crash-reporting`](skills/kotlin-multiplatform-crash-reporting/) — Crashlytics + Sentry, dSYM symbolication
- [`analytics`](skills/kotlin-multiplatform-analytics/) — sealed AnalyticsEvent, Firebase/Amplitude
- [`feature-flags`](skills/kotlin-multiplatform-feature-flags/) — FeatureFlag enum, Remote Config, A/B variants
- [`form-validation`](skills/kotlin-multiplatform-form-validation/) — ValidationResult, FieldState, submit gating
- [`permissions`](skills/kotlin-multiplatform-permissions/) — PermissionState, expect/actual PermissionController
- [`push-notifications`](skills/kotlin-multiplatform-push-notifications/) — FCM + APNs, PushToken expect/actual
- [`workmanager`](skills/kotlin-multiplatform-workmanager/) — CoroutineWorker, BGTaskScheduler
- [`biometric-auth`](skills/kotlin-multiplatform-biometric-auth/) — BiometricResult, expect/actual BiometricAuthenticator
- [`image-loading`](skills/kotlin-multiplatform-image-loading/) — Coil 3, AsyncImage, image cache
- [`shared-resources`](skills/kotlin-multiplatform-shared-resources/) — shared resources and localization
- [`in-app-purchases`](skills/kotlin-multiplatform-in-app-purchases/) — Play Billing + StoreKit 2, PurchaseState, MVI paywall
- [`proguard-r8`](skills/kotlin-multiplatform-proguard-r8/) — R8 keep rules for KMP libraries, release build validation
- [`desktop-app`](skills/kotlin-multiplatform-desktop-app/) — window management, tray, file picker, packaging

### UI System
- [`design-system`](skills/kotlin-multiplatform-design-system/) — tokens and core components
- [`design-system-extended`](skills/kotlin-multiplatform-design-system-extended/) — bottom sheet, dialog, snackbar, skeleton
- [`shadcn-compose`](skills/kotlin-multiplatform-shadcn-compose/) — published library alternative to `design-system` — 70+ components, real experimental-API dependency risk
- [`compose-state-hoisting`](skills/kotlin-multiplatform-compose-state-hoisting/) — hoisting rules, `@Stable`, `@Immutable`
- [`compose-state-container`](skills/kotlin-multiplatform-compose-state-container/) — `remember` vs `ViewModel`, `rememberUpdatedState`
- [`compose-animation`](skills/kotlin-multiplatform-compose-animation/) — AnimatedVisibility, Crossfade, shared elements
- [`compose-slot-api`](skills/kotlin-multiplatform-compose-slot-api/) — slot-based component APIs, CompositionLocal
- [`adaptive-layout`](skills/kotlin-multiplatform-adaptive-layout/) — WindowSizeClass, list-detail split
- [`graphics-modifiers`](skills/kotlin-multiplatform-graphics-modifiers/) — Canvas, graphicsLayer
- [`preview-driven-development`](skills/kotlin-multiplatform-preview-driven-development/) — Desktop-first `@Preview` workflow, PDD cycle
- [`layout-system`](skills/kotlin-multiplatform-layout-system/) — ASCII wireframe docs per screen + slot-grid layout contracts
- [`imagevector-generator`](skills/kotlin-multiplatform-imagevector-generator/) — raster/SVG → compiled Kotlin ImageVector; no hand-written paths, no PNG icons

### Testing & Quality
- [`unit-testing`](skills/kotlin-multiplatform-unit-testing/) — `runTest`, Turbine, fake-over-mock
- [`roborazzi`](skills/kotlin-multiplatform-roborazzi/) — screenshot tests from `@Preview` on JVM
- [`code-quality`](skills/kotlin-multiplatform-code-quality/) — Ktlint + Detekt, CI gates
- [`accessibility`](skills/kotlin-multiplatform-accessibility/) — semantic roles, contentDescription, WCAG
- [`benchmark`](skills/kotlin-multiplatform-benchmark/) — kotlinx-benchmark setup, @Benchmark conventions, per-target registration

### Meta
- [`expert`](skills/kotlin-multiplatform-expert/) — skill routing and build order
- [`audit`](skills/kotlin-multiplatform-audit/) — repo review, fix sequencing, CI governance gate
- [`migration`](skills/kotlin-multiplatform-migration/) — MVVM→MVI, monolith→multi-module, incremental adoption
- [`project-docs-maintainer`](skills/kotlin-multiplatform-project-docs-maintainer/) — consumer-facing project docs and onboarding
- [`legal-docs`](skills/kotlin-multiplatform-legal-docs/) — privacy policy, terms, GDPR, data-safety labels
- [`lessons`](skills/kotlin-multiplatform-lessons/) — structured lesson files for pattern mismatches
- [`skill-harvester`](skills/kotlin-multiplatform-skill-harvester/) — reads lessons, proposes skill amendments
- [`token-saver`](skills/kotlin-multiplatform-token-saver/) — terse replies, output compression, and smallest-correct-solution checks
- [`release`](skills/kotlin-multiplatform-release/) — versioning, Maven Central, git-cliff, GitHub Release

</details>

---

## Commands

All commands are `kmm-` prefixed so they don't collide with your own `.claude/commands/`.

### Consumer commands — install these in your project

| Command | What it does |
|---|---|
| `/kmm-new-project <description>` | Scaffold a full KMP project from a description |
| `/kmm-setup-agents [path]` | Initialize `.claude/` agent setup in an existing project |
| `/kmm-implement-feature <name>` | Plan → Implement → Validate → Review a feature |
| `/kmm-execute-ticket <id>` | Implement a GitHub Issue end-to-end |
| `/kmm-run-audit [path]` | Architecture audit with per-finding remediation + auto skill-gap reporting |
| `/kmm-harvest-lessons [path]` | Collect positive patterns from consumer project; auto-propose GitHub issues |
| `/kmm-audit-adaptive [path]` | Adaptive layout coverage + redundant title check across Compact/Medium/Expanded |
| `/kmm-verify [path]` | Full pipeline: build, tests, audit, screenshots, design |
| `/kmm-review-changes` | Review git diff against 6-layer rules and anti-patterns |
| `/kmm-generate-palette <name=#HEX ...>` | Generate `AppColors.kt` + Compose palette preview from N brand seed colors |
| `/kmm-vectorize <image>` | Compile a raster/SVG into a Kotlin `ImageVector` — replaces PNG icons and hand-written paths |
| `/kmm-fix-design [path]` | Scan and fix design system violations |
| `/kmm-migrate-to-shadcn [path]` | Migrate a project from the owned design-system to shadcn-compose, file-by-file with confirmation |
| `/kmm-clean-comments [path]` | Refactor documentation by architectural level (class/function/extension/inline) |
| `/kmm-update-design-system [path]` | Pull latest design system components |
| `/kmm-record-design-baselines [path]` | Record Roborazzi golden PNGs |
| `/kmm-audit-screenshots [path]` | Vision audit of screenshot goldens |
| `/kmm-audit-design-visual [path]` | Cross-screen visual consistency check |
| `/kmm-update-skills` | Pull latest skills and re-deploy to `.claude/skills/` |
| `/kmm-check-updates` | Check for a newer version of kmm-agent-skills |
| `/kmm-report-skill-issue` | File a structured skill bug report |

### Repo-internal commands

| Command | What it does |
|---|---|
| `/kmm-new-skill <name>` | Scaffold a new skill with all required sections |
| `/kmm-modify-skill <name>` | Safely edit an existing skill |
| `/kmm-summarize-issues` | Scan all skills for quality gaps |
| `/kmm-submit-issue` | File a structured GitHub issue |
| `/kmm-maintain-docs [scope]` | Reconcile repo docs and routing text |
| `/kmm-release-notes` | Draft release notes for a version bump |
| `/kmm-setup-hooks` | Install git hooks for architecture hygiene |
| `/kmm-sync-local-skills` | Sync this repo release into local Claude / Codex / Gemini skill bundles on this Mac |

---

## Installation

```bash
npx skills add ronjunevaldoz/kmm-agent-skills
```

See [INSTALL.md](INSTALL.md) for setup instructions for Claude Code, OpenAI Codex CLI,
GitHub Copilot, Cursor, Windsurf, Gemini CLI, Aider, and Continue.

---

## Versions

| Library | Version |
|---|---|
| AGP | 9.2.0 |
| Kotlin | 2.4.0 |
| Compose Multiplatform | 1.11.1 |
| Coroutines | 1.11.0 |
| AndroidX Lifecycle | 2.11.0 |
| Navigation Compose | 2.9.2 |
| Koin | 4.2.2 |
| Ktor | 3.5.0 |
| SQLDelight | 2.3.2 |
| Roborazzi | 1.64.0 |

Full compatibility table: [`docs/reference/compatibility-matrix.md`](docs/reference/compatibility-matrix.md)

---

## Docs tasks

Before routing any docs request, classify it as repo-internal or downstream consumer.
Repo docs stay with `docs-maintainer`; downstream project docs go to `project-docs-maintainer`.

---

## Roadmap

See [PLAN.md](PLAN.md) for full scope and priority details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for skill authoring, commit format, and PR checklist.

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates

## Support

- ⭐ Star this repo
- 💬 Share feedback via issues
- 💰 [Support via donation](FUNDING.md)

## License

Apache-2.0 — see [LICENSE](LICENSE)
