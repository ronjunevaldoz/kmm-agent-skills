# kmm-agent-skills

A collection of AI agent skills for **Kotlin Multiplatform (KMP)** development,
targeting Android, iOS, Desktop (JVM), and Web (JS/Wasm).

Skills follow the [Agent Skills open standard](https://agentskills.io) — self-contained
`SKILL.md` files that ground AI agents with domain-specific knowledge and production-ready
templates. Each skill fills a gap where LLMs consistently underperform without explicit guidance.

---

## Available Skills

| Skill | Description |
|---|---|
| [`kotlin-multiplatform-feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) | Scaffold a full KMP multi-module project or add a new feature module group (`:api/:domain/:data/:ui`). AGP 9+, build-logic convention plugins, version catalog, CMP, Koin 4. |
| [`kotlin-multiplatform-network-layer`](skills/kotlin-multiplatform-network-layer/) | Production-ready Ktor 3 network layer in `:core:network`. Bearer auth with automatic token refresh, `NetworkResult<T>`, `safeRequest {}`, platform engines for Android/iOS/Desktop/Web. |
| [`kotlin-multiplatform-ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) | GitHub Actions CI: lint, Android tests (Ubuntu), iOS tests (macOS), Desktop/Web tests, Gradle cache. Release workflow: XCFramework build + GitHub Release. |
| [`kotlin-multiplatform-sqldelight-setup`](skills/kotlin-multiplatform-sqldelight-setup/) | SQLDelight 2 setup in `:core:database`. Schema files, migrations, type adapters, platform drivers (Android/iOS/Desktop/Web), coroutines Flow queries, Koin wiring. |
| [`kotlin-multiplatform-navigation`](skills/kotlin-multiplatform-navigation/) | Type-safe KMP navigation using Navigation Compose (JetBrains fork) with `@Serializable` routes, nested graphs, bottom navigation, and deep links. Decompose alternative covered. |
| [`kotlin-multiplatform-shared-resources`](skills/kotlin-multiplatform-shared-resources/) | Compose Multiplatform Resources for shared strings, plurals, images, fonts, and raw files across Android/iOS/Desktop/Web. Localization and theme wiring included. |
| [`kotlin-multiplatform-flavor-environment`](skills/kotlin-multiplatform-flavor-environment/) | Multi-environment config (dev/staging/prod) via BuildKonfig. Android product flavors, secrets via `local.properties` or CI env vars, `AppConfig` facade in commonMain. |
| [`kotlin-multiplatform-xcframework-spm`](skills/kotlin-multiplatform-xcframework-spm/) | Build an XCFramework from `:shared` and publish it as a Swift Package Manager binary target. Local SPM for dev, GitHub Releases for distribution, automated via CI. |

---

## Targets

All skills support the full KMP target matrix:

| Platform | Target | Entry Point |
|---|---|---|
| Android | `androidTarget()` | `:androidApp` |
| iOS | `iosArm64()`, `iosSimulatorArm64()` | `:iosApp` (Xcode) |
| Desktop | `jvm()` | `:desktopApp` |
| Web | `js { browser() }`, `wasmJs { browser() }` | `:webApp` |

---

## Installation

### Via skills CLI

```bash
npx skills add ronjunevaldoz/kmm-agent-skills
```

### Manual

Copy the desired skill folder into your agent's skills directory:

```bash
# Claude Code
cp -r skills/kotlin-multiplatform-feature-scaffold .claude/skills/

# All skills at once
cp -r skills/* .claude/skills/
```

---

## Versioning

| Tool | Version |
|---|---|
| AGP | 9.0.1 |
| Kotlin | 2.4.0 |
| Compose Multiplatform | 1.11.1 |
| Koin | 4.2.1 |
| Ktor | 3.1.3 |
| SQLDelight | 2.0.2 |
| BuildKonfig | 0.21.2 |
| Turbine | 1.2.1 |

---

## Skill Naming Convention

Skills in this repo follow `kotlin-multiplatform-<functional-name>`.

---

## Roadmap

- [ ] `kotlin-multiplatform-datastore` — Multiplatform DataStore (Preferences + Proto) for key-value and typed storage
- [ ] `kotlin-multiplatform-biometric-auth` — Biometric / Face ID / Fingerprint authentication via expect/actual
- [ ] `kotlin-multiplatform-push-notifications` — FCM (Android) + APNs (iOS) wiring with KMP shared handling
- [ ] `kotlin-multiplatform-analytics` — Shared analytics abstraction with Firebase / Amplitude platform implementations
- [ ] `kotlin-multiplatform-testing-robot` — UI testing robots pattern for Compose Multiplatform screens

---

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates
- [agentskills.io](https://agentskills.io) — Agent Skills open standard

---

## License

Apache-2.0
