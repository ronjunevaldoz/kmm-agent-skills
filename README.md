# kmm-agent-skills

A collection of AI agent skills for **Kotlin Multiplatform (KMP)** development,
targeting Android, iOS, Desktop (JVM), and Web (JS/Wasm).

Each skill is a self-contained `SKILL.md` grounding the agent with production patterns,
architecture decisions, and common pitfalls — not just dependency boilerplate.

The current repo files are the source of truth. Re-read `README.md` and the relevant
`skills/*/SKILL.md` files before making recommendations so each session uses the latest
skill set and wording.

> **Start here:** use `kotlin-multiplatform-expert` first on any new project or feature.
> It maps all skills, their build order, and answers "which skill do I need?" questions.

---

## Skills

### Foundation

| Skill | What it covers |
|---|---|
| [`kotlin-multiplatform-feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) | Project structure, module graph (`:api/:domain/:data/:ui`), AGP 9+, build-logic convention plugins, version catalog, Koin 4 |
| [`kotlin-multiplatform-dependency-injection`](skills/kotlin-multiplatform-dependency-injection/) | Koin module organization, manual vs annotated wiring, constructor injection, app/feature/viewModel scopes, test overrides |
| [`kotlin-multiplatform-flavor-environment`](skills/kotlin-multiplatform-flavor-environment/) | Dev/staging/prod via BuildKonfig, Android product flavors, secrets via `local.properties` or CI env vars, `AppConfig` facade |
| [`kotlin-multiplatform-ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) | GitHub Actions matrix (Android/iOS/Desktop/Web), Gradle cache, XCFramework release workflow |

### Infrastructure

| Skill | What it covers |
|---|---|
| [`kotlin-multiplatform-network-layer`](skills/kotlin-multiplatform-network-layer/) | Ktor 3 client in `:core:network`, `NetworkResult<T>`, `safeRequest {}`, bearer auth with automatic token refresh, platform engines |
| [`kotlin-multiplatform-sqldelight-setup`](skills/kotlin-multiplatform-sqldelight-setup/) | SQLDelight 2 in `:core:database`, schema files, migrations, type adapters, platform drivers, coroutines Flow queries |
| [`kotlin-multiplatform-xcframework-spm`](skills/kotlin-multiplatform-xcframework-spm/) | XCFramework build from `:shared`, Swift Package Manager binary target, local SPM for dev, GitHub Releases for distribution |

### Platform Patterns

| Skill | What it covers |
|---|---|
| [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/) | When to use `expect/actual` vs interface injection, `typealias actual`, "actual everywhere" anti-pattern, `@ObjCName` for Swift API surface, `@Throws`, Kotlin/Native memory model |
| [`kotlin-multiplatform-repository-pattern`](skills/kotlin-multiplatform-repository-pattern/) | Interface in `:api`, impl in `:data`, mapper pattern (DTO → Domain ← Entity), 3 fetch strategies (network-first / cache-first / offline-first), SQLDelight Flow as single source of truth, optimistic updates |

### Feature Architecture

| Skill | What it covers |
|---|---|
| [`kotlin-multiplatform-navigation`](skills/kotlin-multiplatform-navigation/) | Type-safe routes with `@Serializable`, nested graphs, bottom navigation, deep links (JetBrains Navigation Compose) |
| [`kotlin-multiplatform-shared-resources`](skills/kotlin-multiplatform-shared-resources/) | Shared strings, plurals, images, fonts, raw files via CMP Resources; localization |
| [`kotlin-multiplatform-mvi`](skills/kotlin-multiplatform-mvi/) | Contract pattern (State/Intent/Effect), `MviViewModel` with `StateFlow` + `Channel<Effect>`, atomic state updates, Screen/Content split, Turbine testing |

### UI System

| Skill | What it covers |
|---|---|
| [`kotlin-multiplatform-design-system`](skills/kotlin-multiplatform-design-system/) | Tokens (colors / typography / shapes / spacing), `AppTheme`, dark mode, shadcn-inspired sealed variants, 6 core components — no Material dependency |
| [`kotlin-multiplatform-design-system-extended`](skills/kotlin-multiplatform-design-system-extended/) | 27 additional components: Icon, Avatar, TopAppBar, NavigationBar, Tabs, Checkbox, RadioButton, Switch, Slider, Select, Progress, Skeleton, Spinner, Alert, Toast, Dialog, Sheet, Tooltip, Popover, Accordion |
| [`kotlin-multiplatform-compose-slot-api`](skills/kotlin-multiplatform-compose-slot-api/) | `@Composable () -> Unit` slots, named/scoped slots (RowScope/ColumnScope), trailing lambda convention, CompositionLocal, when NOT to use slots |
| [`kotlin-multiplatform-compose-state-hoisting`](skills/kotlin-multiplatform-compose-state-hoisting/) | Hoist-until-shared rule, controlled component pattern (`value` + `onValueChange`), stateful vs stateless, when to stop hoisting |
| [`kotlin-multiplatform-compose-state-container`](skills/kotlin-multiplatform-compose-state-container/) | `remember` vs `rememberSaveable` vs `ViewModel` survival matrix, decision tree, custom `Saver`, graph-scoped ViewModels, `SavedStateHandle` |
| [`kotlin-multiplatform-graphics-modifiers`](skills/kotlin-multiplatform-graphics-modifiers/) | `graphicsLayer` vs Canvas, drawBehind, drawWithCache, workflow node shells, custom drawing performance |

### Meta

| Skill | What it covers |
|---|---|
| [`kotlin-multiplatform-expert`](skills/kotlin-multiplatform-expert/) | Skill dependency graph, phase-by-phase build order, feature-slice checklist, architecture decision trees, 12-point anti-pattern checklist, skill invocation map |
| [`kotlin-multiplatform-audit`](skills/kotlin-multiplatform-audit/) | Existing project review, boundary checks, architecture drift, Compose/MVI/data-layer readiness, fix sequencing |

---

## Targets

| Platform | Target | Entry Point |
|---|---|---|
| Android | `androidTarget()` | `:androidApp` |
| iOS | `iosArm64()`, `iosSimulatorArm64()` | `:iosApp` (Xcode) |
| Desktop | `jvm()` | `:desktopApp` |
| Web | `js { browser() }`, `wasmJs { browser() }` | `:webApp` |

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

## Roadmap

- [ ] `kotlin-multiplatform-datastore` — Multiplatform DataStore (Preferences + Proto)
- [ ] `kotlin-multiplatform-biometric-auth` — Biometric / Face ID / Fingerprint via expect/actual
- [ ] `kotlin-multiplatform-push-notifications` — FCM (Android) + APNs (iOS) with shared KMP handling
- [ ] `kotlin-multiplatform-analytics` — Shared analytics abstraction (Firebase / Amplitude)
- [ ] `kotlin-multiplatform-testing-robot` — UI testing robot pattern for CMP screens

---

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates

---

## License

Apache-2.0
