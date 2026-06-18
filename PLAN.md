# Development Plan

This file tracks the build status of every skill in this collection and the roadmap
for future work. Update it as skills are added, revised, or completed.

---

## Status Key

| Symbol | Meaning |
|---|---|
| ✅ | Shipped — skill is in `main`, production-ready |
| 🔧 | Known issues — skill exists but has open defects (see notes) |
| 🚧 | In progress — actively being written |
| 📋 | Planned — scoped and ready to start |
| 💡 | Idea — not yet scoped |

---

## Shipped Skills (31)

### Foundation
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-feature-scaffold` | ✅ | AGP 9, build-logic, version catalog, Koin 4, 6-layer model |
| `kotlin-multiplatform-clean-architecture` | ✅ | 6-layer contract, :model vs :api, internal visibility, Detekt rules |
| `kotlin-multiplatform-presenter-module` | ✅ | Pure Kotlin ViewModel, MVI contracts, no Compose dep, Koin wiring |
| `kotlin-multiplatform-flavor-environment` | ✅ | BuildKonfig, AppConfig, Android product flavors |
| `kotlin-multiplatform-ci-github-actions` | ✅ | Android/iOS/Desktop/Web matrix, XCFramework release |

### Infrastructure
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-network-layer` | ✅ | Ktor 3, NetworkResult<T>, safeRequest, token refresh |
| `kotlin-multiplatform-sqldelight-setup` | ✅ | SQLDelight 2, platform drivers, Flow queries |
| `kotlin-multiplatform-xcframework-spm` | ✅ | XCFramework, SPM binary target, CI release |

### Platform Patterns
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-expect-actual` | ✅ | 4 categories, typealias actual, @ObjCName, KN memory |
| `kotlin-multiplatform-repository-pattern` | ✅ | Interface/:data impl, mapper pattern, 3 fetch strategies, optimistic updates |

### Feature Architecture
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-navigation` | ✅ | JetBrains Nav Compose, type-safe routes, nested graphs |
| `kotlin-multiplatform-shared-resources` | ✅ | CMP Resources, strings/images/fonts, localization |
| `kotlin-multiplatform-mvi` | ✅ | Contract pattern, MviViewModel, Channel<Effect>, Turbine testing |

### UI System
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-design-system` | ✅ | Tokens, AppTheme, dark mode, 6 core components, no Material |
| `kotlin-multiplatform-design-system-extended` | ✅ | 27 components shipped |
| `kotlin-multiplatform-compose-slot-api` | ✅ | Slot patterns, scoped slots, CompositionLocal |
| `kotlin-multiplatform-compose-state-hoisting` | ✅ | Hoist-until-shared, controlled component, stateful wrapper |
| `kotlin-multiplatform-compose-state-container` | ✅ | remember/rememberSaveable/ViewModel survival matrix, custom Saver |

### Meta
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-expert` | ✅ | Dependency graph, build order, decision trees, anti-pattern checklist |
| `kotlin-multiplatform-audit` | ✅ | Architecture review, boundary check, skills repo hygiene, issue drafts |

### Cross-Cutting Patterns
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-dependency-injection` | ✅ | Koin manual + annotated modes, scope rules, test overrides |
| `kotlin-multiplatform-graphics-modifiers` | ✅ | graphicsLayer, Canvas, drawWithCache, workflow node pattern |

### Full-Stack / Backend
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-kotlin-rpc` | ✅ | Kotlin RPC vs REST vs gRPC decision, shared contract, scaffold script |
| `kotlin-multiplatform-ktor-auth-service` | ✅ | Bearer + JWT, sessions, Ktor RPC auth, scaffold script |
| `kotlin-multiplatform-mongodb-database` | ✅ | Coroutine driver, repository boundary, typed errors, change streams |

---

## Open Defects

### `kotlin-multiplatform-design-system-extended`

All known defects resolved. ✅

---

## Roadmap

### Batch 2 — Data & Storage

| Skill | Priority | Scope |
|---|---|---|
| `kotlin-multiplatform-datastore` | 📋 High | Multiplatform DataStore Preferences + Proto. `createDataStore {}` expect/actual, coroutines Flow reads, migration from SharedPreferences, Koin wiring |

### Batch 3 — Native Features

| Skill | Priority | Scope |
|---|---|---|
| `kotlin-multiplatform-biometric-auth` | 📋 Medium | BiometricPrompt (Android) + LocalAuthentication (iOS) via expect/actual. Shared `BiometricAuth` interface, result sealed type, Keychain/EncryptedSharedPrefs integration |
| `kotlin-multiplatform-push-notifications` | 📋 Medium | FCM token (Android) + APNs token (iOS). Shared `PushToken` domain type, `NotificationHandler` interface, deep-link routing from notification tap |

### Batch 4 — Observability & Quality

| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-unit-testing` | ✅ | runTest, Turbine, fake-over-mock, :core:testing fixtures, JVM ViewModel tests |
| `kotlin-multiplatform-preview-driven-development` | ✅ | Desktop-first @Preview, PreviewParameterProvider, PDD cycle, Roborazzi link |
| `kotlin-multiplatform-roborazzi` | ✅ | Screenshot tests from @Preview on JVM, golden images, CI diff job |
| `kotlin-multiplatform-code-quality` | ✅ | Ktlint (formatting) + Detekt (architecture rules), CI gates |
| `kotlin-multiplatform-logging` | ✅ | Kermit, log levels, pluggable writers, crash boundary, Koin wiring |
| `kotlin-multiplatform-analytics` | 📋 Medium | Shared `Analytics` interface, Firebase/Amplitude platform impls, event schema via sealed classes, automatic screen tracking |
| `kotlin-multiplatform-testing-robot` | 🚫 Retired | Replaced by `kotlin-multiplatform-roborazzi` + `kotlin-multiplatform-unit-testing` |

### Ideas (not yet scoped)

| Idea | Notes |
|---|---|
| `kotlin-multiplatform-paging` | Paging 3 in KMP — `PagingSource`, `Pager`, Compose `collectAsLazyPagingItems`, cursor vs offset strategies |
| `kotlin-multiplatform-workmanager` | Background sync — WorkManager (Android) + BGTaskScheduler (iOS) via expect/actual, retry policies, sync queue pattern |
| `kotlin-multiplatform-deep-linking` | Universal Links (iOS) + App Links (Android) setup, route parsing in KMP shared code, navigation integration |
| `kotlin-multiplatform-compose-animation` | CMP animation patterns — `AnimatedVisibility`, `animateContentSize`, shared element transitions, motion specs |

---

## Contribution Notes

- Every skill must follow the "real skill" principle: 80% patterns/decisions/pitfalls, ≤20% dependency setup
- Skill descriptions must be specific enough to trigger correctly — test against the keyword list before shipping
- Add cross-skill dependency references in "When to Use" sections where relevant
- Run `./gradlew :core:xxx:compileCommonMainKotlinMetadata` on any code snippet before committing

---

## Version Targets

| Tool | Current | Next target |
|---|---|---|
| AGP | 9.0.1 | Track AGP stable |
| Kotlin | 2.4.0 | Track K2 stable |
| Compose Multiplatform | 1.11.1 | Track CMP stable |
| Koin | 4.2.1 | — |
| Ktor | 3.1.3 | — |
| SQLDelight | 2.0.2 | — |
