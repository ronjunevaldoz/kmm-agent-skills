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
| [`kotlin-multiplatform-mvi`](skills/kotlin-multiplatform-mvi/) | MVI architecture pattern for KMP + CMP. Contract pattern (State/Intent/Effect), `MviViewModel` base class with `StateFlow` + `Channel<Effect>`, atomic state updates, Screen/Content split, Koin wiring, Turbine-based ViewModel testing. Zero new dependencies. | MVI, Model-View-Intent, screen state, UiState, UiIntent, UiEffect, unidirectional data flow, ViewModel state, one-shot effects, side effects, StateFlow, Channel, Contract pattern |
| [`kotlin-multiplatform-design-system-extended`](skills/kotlin-multiplatform-design-system-extended/) | Extends the core design system with 27 production-ready components. Icon, IconButton, Label, Separator, Avatar, Spinner, Skeleton, Progress, TopAppBar, NavigationBar, Tabs (3 variants), Checkbox, RadioButton, Switch, Slider, Select, Alert, Toast/Snackbar (ToastHostState + AppScaffold), Dialog, AlertDialog, Sheet, Tooltip, Popover, Accordion. All on CMP primitives, no Material3. | dialog, bottom sheet, toast, snackbar, tabs, top app bar, bottom navigation, checkbox, radio button, switch, slider, select, dropdown, progress bar, skeleton, spinner, tooltip, popover, accordion, collapsible, avatar, separator, icon button, extended design system |

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
