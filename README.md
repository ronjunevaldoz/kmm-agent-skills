# kmm-agent-skills

A collection of AI agent skills for **Kotlin Multiplatform (KMP)** development,
targeting Android, iOS, Desktop (JVM), and Web (JS/Wasm).

Skills follow the [Agent Skills open standard](https://agentskills.io) — self-contained
`SKILL.md` files that ground AI agents with domain-specific knowledge and production-ready
templates. Each skill fills a gap where LLMs consistently underperform without explicit guidance.

---

## Available Skills

| Skill | Description | Trigger Keywords |
|---|---|---|
| [`kotlin-multiplatform-feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) | Scaffold a full KMP multi-module project or add a new feature module group (`:api/:domain/:data/:ui`). AGP 9+, build-logic convention plugins, version catalog, CMP, Koin 4. | create KMP project, scaffold feature module, new module, set up KMP, add :feature:x, kmp-wizard, AGP 9 multiplatform |
| [`kotlin-multiplatform-network-layer`](skills/kotlin-multiplatform-network-layer/) | Production-ready Ktor 3 network layer in `:core:network`. Bearer auth with automatic token refresh, `NetworkResult<T>`, `safeRequest {}`, platform engines for Android/iOS/Desktop/Web. | add networking, set up Ktor, HTTP client, API calls, network layer, token refresh, auth header, safeRequest |
| [`kotlin-multiplatform-ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) | GitHub Actions CI: lint, Android tests (Ubuntu), iOS tests (macOS), Desktop/Web tests, Gradle cache. Release workflow: XCFramework build + GitHub Release. | set up CI, GitHub Actions, CI pipeline, automated tests, build workflow, release workflow, KMP CI |
| [`kotlin-multiplatform-sqldelight-setup`](skills/kotlin-multiplatform-sqldelight-setup/) | SQLDelight 2 setup in `:core:database`. Schema files, migrations, type adapters, platform drivers (Android/iOS/Desktop/Web), coroutines Flow queries, Koin wiring. | local database, SQLDelight, SQLite, offline storage, database schema, SQL queries, migrations, cache data locally |
| [`kotlin-multiplatform-navigation`](skills/kotlin-multiplatform-navigation/) | Type-safe KMP navigation using Navigation Compose (JetBrains fork) with `@Serializable` routes, nested graphs, bottom navigation, and deep links. Decompose alternative covered. | add navigation, screen routing, NavHost, bottom nav, deep links, type-safe routes, nested graph, navigation compose |
| [`kotlin-multiplatform-shared-resources`](skills/kotlin-multiplatform-shared-resources/) | Compose Multiplatform Resources for shared strings, plurals, images, fonts, and raw files across Android/iOS/Desktop/Web. Localization and theme wiring included. | shared strings, localization, add fonts, image assets, composeResources, i18n, string resources, shared images |
| [`kotlin-multiplatform-flavor-environment`](skills/kotlin-multiplatform-flavor-environment/) | Multi-environment config (dev/staging/prod) via BuildKonfig. Android product flavors, secrets via `local.properties` or CI env vars, `AppConfig` facade in commonMain. | dev/staging/prod, environment config, BuildKonfig, product flavors, API key secrets, build variants, AppConfig, env switching |
| [`kotlin-multiplatform-xcframework-spm`](skills/kotlin-multiplatform-xcframework-spm/) | Build an XCFramework from `:shared` and publish it as a Swift Package Manager binary target. Local SPM for dev, GitHub Releases for distribution, automated via CI. | XCFramework, Swift Package Manager, SPM, iOS binary, publish iOS framework, Xcode integration, local SPM, release framework |
| [`kotlin-multiplatform-design-system`](skills/kotlin-multiplatform-design-system/) | Custom CMP design system in `:core:designsystem` using the Compose Styles API (`@ExperimentalStylesApi`). Shadcn-inspired sealed variants, design tokens (colors/typography/shapes/spacing), StyleScope extensions, dark mode, 6 core components — no Material dependency. | design system, custom theme, AppTheme, design tokens, shadcn KMP, no Material, custom components, ButtonVariant, dark mode tokens, Compose Styles API, ExperimentalStylesApi, AppColors, AppTypography |
| [`kotlin-multiplatform-compose-slot-api`](skills/kotlin-multiplatform-compose-slot-api/) | Slot API pattern — designing Compose components with `@Composable () -> Unit` parameters instead of data parameters. Covers single/named/scoped slots (RowScope/ColumnScope), trailing lambda convention, nullable optional slots, CompositionLocal as a deep-slot alternative, slot performance, and when NOT to use slots. | slot API, composable slot, content lambda, named slots, scoped slot, RowScope slot, trailing lambda, flexible component, inversion of control Compose, CompositionLocal |
| [`kotlin-multiplatform-compose-state-hoisting`](skills/kotlin-multiplatform-compose-state-hoisting/) | State hoisting in CMP — moving state to the lowest common ancestor that needs it. Covers stateful vs stateless composables, the controlled component pattern (value + onValueChange), hoist-until-shared rule, when to stop hoisting, UI state vs business state, and the stateful convenience wrapper pattern. | state hoisting, lift state, stateless composable, controlled component, value onValueChange, single source of truth, state sharing, Compose state management, where does state go |
| [`kotlin-multiplatform-compose-state-container`](skills/kotlin-multiplatform-compose-state-container/) | Choosing the right state container in CMP: `remember` vs `rememberSaveable` vs `ViewModel`. Covers what survives recomposition / config change / process death, the decision tree, custom Saver for non-Bundle types, ViewModel + SavedStateHandle, nav back-stack vs graph-scoped ViewModels, and `rememberCoroutineScope`. | remember vs ViewModel, rememberSaveable, state container, when to use ViewModel, ephemeral state, config change, process death, custom Saver, nav-scoped ViewModel, state lost on rotation |
| [`kotlin-multiplatform-mvi`](skills/kotlin-multiplatform-mvi/) | MVI architecture pattern for KMP + CMP. Contract pattern (State/Intent/Effect), `MviViewModel` base class with `StateFlow` + `Channel<Effect>`, atomic state updates, Screen/Content split, Koin wiring, Turbine-based ViewModel testing. Zero new dependencies. | MVI, Model-View-Intent, screen state, UiState, UiIntent, UiEffect, unidirectional data flow, ViewModel state, one-shot effects, side effects, StateFlow, Channel, Contract pattern |
| [`kotlin-multiplatform-design-system-extended`](skills/kotlin-multiplatform-design-system-extended/) | Extends the core design system with 27 production-ready components. Icon, IconButton, Label, Separator, Avatar, Spinner, Skeleton, Progress, TopAppBar, NavigationBar, Tabs (3 variants), Checkbox, RadioButton, Switch, Slider, Select, Alert, Toast/Snackbar (ToastHostState + AppScaffold), Dialog, AlertDialog, Sheet, Tooltip, Popover, Accordion. All on CMP primitives, no Material3. | dialog, bottom sheet, toast, snackbar, tabs, top app bar, bottom navigation, checkbox, radio button, switch, slider, select, dropdown, progress bar, skeleton, spinner, tooltip, popover, accordion, collapsible, avatar, separator, icon button, extended design system |
| [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/) | The expect/actual mechanism — when to use it, when NOT to, and how to do it correctly. Covers: the 4 categories that warrant expect/actual vs interface injection, `typealias actual` for platform types, "actual everywhere" anti-pattern, `@ObjCName` for clean Swift API surfaces, `@Throws` for Swift error bridging, and Kotlin/Native memory model (new MM since 1.7.20). | expect actual, platform-specific code, iOS implementation, actual class, expect fun, platform API, ObjCName, Swift interop, typealias actual, Kotlin Native memory, platform dispatcher, platform UUID |
| [`kotlin-multiplatform-repository-pattern`](skills/kotlin-multiplatform-repository-pattern/) | Repository pattern in the KMP data layer. Covers: interface in `:feature:x:api`, implementation in `:feature:x:data`, mapper pattern (DTO → Domain ← Entity), three fetch strategies (network-first, cache-first, offline-first), SQLDelight Flow as single source of truth, optimistic updates, and the common mistakes of leaking network types to domain and skipping local cache. | repository pattern, data layer, offline-first, cache-first, network-first, single source of truth, local cache, domain mapping, NetworkResult, optimistic update, sync strategy |
| [`kotlin-multiplatform-expert`](skills/kotlin-multiplatform-expert/) | KMP Expert Orchestrator meta-skill. Maps all 17 skills, their dependency graph, build order for new projects, feature-slice assembly checklist, decision trees for state/expect-actual/architecture questions, and the anti-pattern checklist. Use this first to plan which skills to invoke and in what order. | KMP expert, orchestrator, skill order, KMP architecture, what skill should I use, KMP project plan, KMP checklist, feature assembly, KMP decision tree, KMM expert |

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
- [x] `kotlin-multiplatform-design-system-extended` — Extended component set for the design system skill (Dialog, BottomSheet, Snackbar, TopAppBar, Tabs, Progress, Skeleton)

---

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates
- [agentskills.io](https://agentskills.io) — Agent Skills open standard

---

## License

Apache-2.0
