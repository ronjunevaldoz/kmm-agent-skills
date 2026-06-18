# kmm-agent-skills

[![skills.sh](https://skills.sh/b/ronjunevaldoz/kmm-agent-skills)](https://skills.sh/ronjunevaldoz/kmm-agent-skills)
[![License](https://img.shields.io/github/license/ronjunevaldoz/kmm-agent-skills)](LICENSE)
[![Repo size](https://img.shields.io/github/repo-size/ronjunevaldoz/kmm-agent-skills)](https://github.com/ronjunevaldoz/kmm-agent-skills)
[![Last commit](https://img.shields.io/github/last-commit/ronjunevaldoz/kmm-agent-skills)](https://github.com/ronjunevaldoz/kmm-agent-skills)

AI agent skills for **Kotlin Multiplatform (KMP)** development.

Goal: keep KMM architecture clean, repeatable, and easy to audit. The skills here
favor clear module boundaries, version catalogs, build-logic convention plugins,
and explicit review loops before code is generated.

The repo files are the source of truth. Re-read this README and the relevant
`skills/*/SKILL.md` files before making recommendations so each session uses the
latest skill set and wording.

**Start here:** use `kotlin-multiplatform-expert` first on any new project or feature.
It maps the skills, build order, and the best next step.

---

## Quick Start

1. Use `kotlin-multiplatform-expert` to choose the next skill.
2. Use `kotlin-multiplatform-feature-scaffold` to start a new project from `Kotlin/kmp-wizard` `all-targets`.
3. Use the domain skills below to fill in auth, data, UI, navigation, and audits.

## Skill Map

### Foundation

- [`kotlin-multiplatform-feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) - 6-layer module structure, build-logic, TOML catalog, Koin
- [`kotlin-multiplatform-clean-architecture`](skills/kotlin-multiplatform-clean-architecture/) - layer contract, `:model` vs `:api`, `internal` rules, Detekt enforcement
- [`kotlin-multiplatform-presenter-module`](skills/kotlin-multiplatform-presenter-module/) - pure-Kotlin ViewModel, MVI contracts, no Compose dep, Koin wiring
- [`kotlin-multiplatform-dependency-injection`](skills/kotlin-multiplatform-dependency-injection/) - Koin wiring and scopes
- [`kotlin-multiplatform-flavor-environment`](skills/kotlin-multiplatform-flavor-environment/) - BuildKonfig, secrets, env setup
- [`kotlin-multiplatform-ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) - CI matrix and release workflow

### Infrastructure

- [`kotlin-multiplatform-ktor-auth-service`](skills/kotlin-multiplatform-ktor-auth-service/) - auth service, bearer/JWT, sessions, RPC
- [`kotlin-multiplatform-mongodb-database`](skills/kotlin-multiplatform-mongodb-database/) - MongoDB coroutine driver and repositories
- [`kotlin-multiplatform-kotlin-rpc`](skills/kotlin-multiplatform-kotlin-rpc/) - Kotlin RPC boundaries and scaffolding
- [`kotlin-multiplatform-network-layer`](skills/kotlin-multiplatform-network-layer/) - Ktor client, auth refresh, result mapping
- [`kotlin-multiplatform-sqldelight-setup`](skills/kotlin-multiplatform-sqldelight-setup/) - SQLDelight schema, drivers, migrations
- [`kotlin-multiplatform-datastore`](skills/kotlin-multiplatform-datastore/) - Preferences DataStore + Proto DataStore, expect/actual factory, Koin wiring, SharedPreferences migration
- [`kotlin-multiplatform-xcframework-spm`](skills/kotlin-multiplatform-xcframework-spm/) - XCFramework and SPM export

### Patterns

- [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/) - platform differences
- [`kotlin-multiplatform-repository-pattern`](skills/kotlin-multiplatform-repository-pattern/) - repository boundary and fetch strategy
- [`kotlin-multiplatform-navigation`](skills/kotlin-multiplatform-navigation/) - type-safe navigation
- [`kotlin-multiplatform-shared-resources`](skills/kotlin-multiplatform-shared-resources/) - shared resources and localization
- [`kotlin-multiplatform-mvi`](skills/kotlin-multiplatform-mvi/) - State / Intent / Effect flow
- [`kotlin-multiplatform-logging`](skills/kotlin-multiplatform-logging/) - Kermit, log levels, crash boundary, Koin wiring

### UI System

- [`kotlin-multiplatform-design-system`](skills/kotlin-multiplatform-design-system/) - tokens and core components
- [`kotlin-multiplatform-design-system-extended`](skills/kotlin-multiplatform-design-system-extended/) - extended component set
- [`kotlin-multiplatform-compose-slot-api`](skills/kotlin-multiplatform-compose-slot-api/) - slot-based component APIs
- [`kotlin-multiplatform-compose-state-hoisting`](skills/kotlin-multiplatform-compose-state-hoisting/) - hoisting rules
- [`kotlin-multiplatform-compose-state-container`](skills/kotlin-multiplatform-compose-state-container/) - `remember` vs `ViewModel`
- [`kotlin-multiplatform-graphics-modifiers`](skills/kotlin-multiplatform-graphics-modifiers/) - canvas and graph surfaces
- [`kotlin-multiplatform-preview-driven-development`](skills/kotlin-multiplatform-preview-driven-development/) - Desktop-first `@Preview` workflow, `PreviewParameterProvider`, PDD cycle

### Testing & Quality

- [`kotlin-multiplatform-unit-testing`](skills/kotlin-multiplatform-unit-testing/) - `runTest`, Turbine, fake-over-mock, `:core:testing` fixtures
- [`kotlin-multiplatform-roborazzi`](skills/kotlin-multiplatform-roborazzi/) - screenshot tests from `@Preview` on JVM, golden images, CI diff
- [`kotlin-multiplatform-code-quality`](skills/kotlin-multiplatform-code-quality/) - Ktlint (formatting) + Detekt (architecture rules), CI gates

### Meta

- [`kotlin-multiplatform-expert`](skills/kotlin-multiplatform-expert/) - skill routing and build order
- [`kotlin-multiplatform-audit`](skills/kotlin-multiplatform-audit/) - repo review and fix sequencing

---

## Targets

- Android - `androidTarget()` - `:androidApp`
- iOS - `iosArm64()`, `iosSimulatorArm64()` - `:iosApp`
- Desktop - `jvm()` - `:desktopApp`
- Web - `js { browser() }`, `wasmJs { browser() }` - `:webApp`

---

## Installation

See **[RELEASING.md](RELEASING.md)** for the release process (used by both humans and agents).

See **[INSTALL.md](INSTALL.md)** for full setup instructions for every assistant:
Claude Code, OpenAI Codex CLI, GitHub Copilot, Cursor, Windsurf, Gemini CLI, Aider, and Continue.

Quickest install (auto-detects your agent):
```bash
npx skills add ronjunevaldoz/kmm-agent-skills
```

---

## Versions

- AGP 9.0.1
- Kotlin 2.4.0
- Compose Multiplatform 1.11.1
- Koin 4.2.1
- Ktor 3.1.3
- SQLDelight 2.0.2
- BuildKonfig 0.21.2
- Turbine 1.2.1

---

## Roadmap

- `kotlin-multiplatform-biometric-auth` - BiometricPrompt (Android) + LocalAuthentication (iOS)
- `kotlin-multiplatform-push-notifications` - FCM token (Android) + APNs token (iOS)
- `kotlin-multiplatform-analytics` - shared Analytics interface, Firebase/Amplitude platform impls

See [PLAN.md](PLAN.md) for full scope and priority details.

---

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates; use the `all-targets` branch for Android, iOS, Web, Desktop, and Server

---

## License

Apache-2.0
