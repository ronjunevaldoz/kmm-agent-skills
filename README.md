# kmm-agent-skills

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

- [`kotlin-multiplatform-feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) - project structure, build-logic, TOML catalog, Koin
- [`kotlin-multiplatform-dependency-injection`](skills/kotlin-multiplatform-dependency-injection/) - Koin wiring and scopes
- [`kotlin-multiplatform-flavor-environment`](skills/kotlin-multiplatform-flavor-environment/) - BuildKonfig, secrets, env setup
- [`kotlin-multiplatform-ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) - CI matrix and release workflow

### Infrastructure

- [`kotlin-multiplatform-ktor-auth-service`](skills/kotlin-multiplatform-ktor-auth-service/) - auth service, bearer/JWT, sessions, RPC
- [`kotlin-multiplatform-mongodb-database`](skills/kotlin-multiplatform-mongodb-database/) - MongoDB coroutine driver and repositories
- [`kotlin-multiplatform-kotlin-rpc`](skills/kotlin-multiplatform-kotlin-rpc/) - Kotlin RPC boundaries and scaffolding
- [`kotlin-multiplatform-network-layer`](skills/kotlin-multiplatform-network-layer/) - Ktor client, auth refresh, result mapping
- [`kotlin-multiplatform-sqldelight-setup`](skills/kotlin-multiplatform-sqldelight-setup/) - SQLDelight schema, drivers, migrations
- [`kotlin-multiplatform-xcframework-spm`](skills/kotlin-multiplatform-xcframework-spm/) - XCFramework and SPM export

### Patterns

- [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/) - platform differences
- [`kotlin-multiplatform-repository-pattern`](skills/kotlin-multiplatform-repository-pattern/) - repository boundary and fetch strategy
- [`kotlin-multiplatform-navigation`](skills/kotlin-multiplatform-navigation/) - type-safe navigation
- [`kotlin-multiplatform-shared-resources`](skills/kotlin-multiplatform-shared-resources/) - shared resources and localization
- [`kotlin-multiplatform-mvi`](skills/kotlin-multiplatform-mvi/) - State / Intent / Effect flow

### UI System

- [`kotlin-multiplatform-design-system`](skills/kotlin-multiplatform-design-system/) - tokens and core components
- [`kotlin-multiplatform-design-system-extended`](skills/kotlin-multiplatform-design-system-extended/) - extended component set
- [`kotlin-multiplatform-compose-slot-api`](skills/kotlin-multiplatform-compose-slot-api/) - slot-based component APIs
- [`kotlin-multiplatform-compose-state-hoisting`](skills/kotlin-multiplatform-compose-state-hoisting/) - hoisting rules
- [`kotlin-multiplatform-compose-state-container`](skills/kotlin-multiplatform-compose-state-container/) - `remember` vs `ViewModel`
- [`kotlin-multiplatform-graphics-modifiers`](skills/kotlin-multiplatform-graphics-modifiers/) - canvas and graph surfaces

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

```bash
# All skills at once (Claude Code)
cp -r skills/* .claude/skills/

# Single skill
cp -r skills/kotlin-multiplatform-feature-scaffold .claude/skills/
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

- `kotlin-multiplatform-datastore` - Multiplatform DataStore
- `kotlin-multiplatform-biometric-auth` - Biometric auth via expect/actual
- `kotlin-multiplatform-push-notifications` - FCM + APNs handling
- `kotlin-multiplatform-analytics` - shared analytics abstraction
- `kotlin-multiplatform-testing-robot` - CMP UI testing robot pattern

---

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates; use the `all-targets` branch for Android, iOS, Web, Desktop, and Server

---

## License

Apache-2.0
