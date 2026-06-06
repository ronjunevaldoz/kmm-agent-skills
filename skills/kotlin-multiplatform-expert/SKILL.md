---
name: kotlin-multiplatform-expert
description: >
  KMP Expert Orchestrator — maps all 17 skills in this collection, their dependency
  order, and how to sequence them for any Kotlin Multiplatform project. Use this skill
  first to plan which other skills to invoke, in what order, for a given task. Covers:
  skill dependency graph, layer-by-layer build order, feature-slice assembly sequence,
  anti-pattern checklist, and decision trees for the most common "what do I use here?"
  questions in KMP. This is a meta-skill; it delegates to domain skills for implementation.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-06'
  keywords:
    - KMP expert
    - orchestrator
    - skill sequencing
    - dependency graph
    - project setup order
    - KMM architecture
    - Kotlin Multiplatform expert
    - what skill should I use
    - skill map
    - meta-skill
    - feature assembly
    - KMP decision tree
---

## When to Use This Skill

Use this skill when you need to:
- Start a new KMP project and don't know which skills to invoke or in what order
- Add a new full feature to an existing KMP project (network + DB + UI + navigation)
- Decide which skill answers a specific question ("where do I put this?", "which pattern fits?")
- Audit an existing KMP project against the full expert checklist
- Get a high-level roadmap before diving into implementation

**Trigger keywords:** where do I start KMP, full KMP setup, new KMP feature, which skill,
skill order, KMP architecture decision, KMM expert, KMP project plan, which pattern KMP,
KMP checklist, review my KMP project.

---

## The 17 Skills and What They Own

### Layer 0 — Project Foundation
| Skill | Owns |
|---|---|
| `kotlin-multiplatform-feature-scaffold` | Project structure, module graph, AGP 9, build-logic, version catalog, Koin 4 |
| `kotlin-multiplatform-flavor-environment` | Dev/staging/prod config, BuildKonfig, secrets, `AppConfig` facade |
| `kotlin-multiplatform-ci-github-actions` | GitHub Actions, test matrix, XCFramework release workflow |

### Layer 1 — Core Infrastructure
| Skill | Owns |
|---|---|
| `kotlin-multiplatform-network-layer` | Ktor 3 client, `NetworkResult<T>`, `safeRequest {}`, token refresh interceptor |
| `kotlin-multiplatform-sqldelight-setup` | SQLDelight 2, platform drivers, schema files, migrations, Flow queries |
| `kotlin-multiplatform-xcframework-spm` | XCFramework build, SPM binary target, Xcode integration |

### Layer 2 — Platform Patterns
| Skill | Owns |
|---|---|
| `kotlin-multiplatform-expect-actual` | `expect/actual` mechanism, interface-injection alternative, `@ObjCName`, Kotlin/Native memory |
| `kotlin-multiplatform-repository-pattern` | Data layer, single source of truth, fetch strategies, domain mapping, optimistic updates |

### Layer 3 — Feature Building Blocks
| Skill | Owns |
|---|---|
| `kotlin-multiplatform-navigation` | Type-safe routes, nested graphs, bottom nav, deep links |
| `kotlin-multiplatform-shared-resources` | Strings, images, fonts, plurals, localization |
| `kotlin-multiplatform-mvi` | MVI architecture, Contract pattern, `MviViewModel`, State/Intent/Effect, one-shot effects |

### Layer 4 — UI System
| Skill | Owns |
|---|---|
| `kotlin-multiplatform-design-system` | Tokens (colors, typography, shapes, spacing), dark mode, 6 core components, no Material dependency |
| `kotlin-multiplatform-design-system-extended` | 27 additional components: Dialog, Sheet, Toast, Tabs, TopAppBar, Checkbox, etc. |
| `kotlin-multiplatform-compose-slot-api` | `@Composable () -> Unit` slots, scoped slots, CompositionLocal, component API shape |
| `kotlin-multiplatform-compose-state-hoisting` | Hoist-until-shared rule, controlled components, stateless vs stateful composables |
| `kotlin-multiplatform-compose-state-container` | `remember` vs `rememberSaveable` vs `ViewModel` survival matrix, custom Saver |

---

## Dependency Graph

```
kotlin-multiplatform-feature-scaffold       ← start here
├── kotlin-multiplatform-flavor-environment (Layer 0, no deps)
├── kotlin-multiplatform-ci-github-actions  (Layer 0, no deps)
├── kotlin-multiplatform-network-layer      (depends on: scaffold)
├── kotlin-multiplatform-sqldelight-setup   (depends on: scaffold)
├── kotlin-multiplatform-xcframework-spm    (depends on: scaffold, ci)
├── kotlin-multiplatform-expect-actual      (depends on: scaffold)
├── kotlin-multiplatform-repository-pattern (depends on: network-layer, sqldelight-setup)
├── kotlin-multiplatform-navigation         (depends on: scaffold)
├── kotlin-multiplatform-shared-resources   (depends on: scaffold)
├── kotlin-multiplatform-mvi               (depends on: scaffold, navigation)
├── kotlin-multiplatform-design-system      (depends on: scaffold, shared-resources)
├── kotlin-multiplatform-design-system-extended (depends on: design-system)
├── kotlin-multiplatform-compose-slot-api   (depends on: design-system)
├── kotlin-multiplatform-compose-state-hoisting (depends on: mvi)
└── kotlin-multiplatform-compose-state-container (depends on: mvi, navigation)
```

---

## Build Order for a New Project

### Phase 1: Foundation (do once per project)
1. **`feature-scaffold`** — create the project, establish module structure
2. **`flavor-environment`** — set up dev/staging/prod before writing any API code
3. **`network-layer`** — Ktor client, `NetworkResult`, auth interceptor
4. **`sqldelight-setup`** — local database, platform drivers, Koin wiring
5. **`ci-github-actions`** — CI before any feature merges

### Phase 2: iOS/Desktop Readiness (if shipping to those platforms)
6. **`xcframework-spm`** — SPM binary target for iOS team
7. **`expect-actual`** — platform-specific code (UUID, SecureStorage, dispatchers)

### Phase 3: First Feature (repeat for each feature)
8. **`design-system`** — tokens and core components (once per project, before first feature)
9. **`navigation`** — add the feature's routes to the nav graph
10. **`shared-resources`** — add strings/assets the feature needs
11. **`repository-pattern`** — wire `RemoteDataSource` + `LocalDataSource` → `FooRepository`
12. **`mvi`** — `FooContract` + `FooViewModel` + `FooScreen`/`FooContent` split

### Phase 4: Richer UI (as needed)
13. **`design-system-extended`** — pull in Dialog, Sheet, Toast etc. when the feature needs them
14. **`compose-slot-api`** — when designing reusable components for the design system
15. **`compose-state-hoisting`** — when a component hierarchy gets complex
16. **`compose-state-container`** — when debugging state survival across rotation/back-nav

---

## Feature Slice Checklist

For every new feature module group (`:feature:x:api/:domain/:data/:ui`), verify:

**`:feature:x:api` (interface + domain models)**
- [ ] `FooRepository` interface returns domain types and `Flow<T>` / `Result<T>` only
- [ ] Domain models are plain `data class` — no DTOs, no DB entities, no annotations
- [ ] `sealed interface FooError` defined for typed error cases

**`:feature:x:data` (implementation)**
- [ ] `FooRemoteDataSource` returns `NetworkResult<FooDto>`
- [ ] `FooLocalDataSource` returns `FooEntity` / `Flow<FooEntity?>`
- [ ] `FooRepositoryImpl` maps all types — no DTO or entity escapes to `:api`
- [ ] `FooDataModule` (Koin) wires both data sources and `FooRepository`

**`:feature:x:domain` (use cases, if complexity warrants)**
- [ ] Use cases have a single `invoke` operator
- [ ] Use cases depend only on `:api` — no `:data` imports

**`:feature:x:ui` (Compose + ViewModel)**
- [ ] `FooContract` — `State`, `Intent`, `Effect` all in one file
- [ ] `FooViewModel : MviViewModel<State, Intent, Effect>`
- [ ] `FooScreen` (wires ViewModel) — `FooContent` (pure function of state)
- [ ] Effects collected with `LaunchedEffect(viewModel)`, not `LaunchedEffect(Unit)`
- [ ] No `isLoading` forgotten in error branch — use `updateState { copy(isLoading = false) }`

---

## Decision Trees

### "Where does this code go?"

```
Is it platform-specific behavior?
├── YES: Does it wrap a platform SDK or require a platform type?
│   ├── YES → expect/actual (kotlin-multiplatform-expect-actual)
│   └── NO  → interface + Koin injection in platform sourcesets
└── NO:
    ├── Is it network communication?     → :core:network + network-layer skill
    ├── Is it local persistence?         → :core:database + sqldelight-setup skill
    ├── Is it domain logic?              → :feature:x:domain use cases
    ├── Is it data fetching + mapping?   → :feature:x:data repository-pattern skill
    ├── Is it screen state + intents?    → :feature:x:ui MVI skill
    ├── Is it a reusable UI component?   → :core:designsystem slot-api + state-hoisting skills
    └── Is it app-wide config?           → :core:common or flavor-environment skill
```

### "Which state container?"

```
Does the state involve async, IO, or repository calls?
├── YES → ViewModel (mvi skill)
└── NO:
    ├── Must survive rotation? YES
    │   ├── Bundle-safe type? → rememberSaveable {}
    │   └── Complex type?     → rememberSaveable(stateSaver = customSaver)
    └── Must survive rotation? NO → remember {}
    └── Shared with another screen? → ViewModel (graph-scoped)
```

Full survival matrix: see `kotlin-multiplatform-compose-state-container`.

### "expect/actual or interface?"

```
Is it a pure behavior difference (same API, different platform behavior)?
→ Interface + Koin injection

Does it require a platform-specific constructor argument (Context, UIViewController)?
→ expect class / typealias actual

Does it wrap a platform SDK with no clean interface abstraction?
→ expect class (Category 3 in expect-actual skill)

Is it a stateless primitive with no constructor (UUID, currentTimeMillis)?
→ expect fun (Category 4 in expect-actual skill)
```

Full guide: see `kotlin-multiplatform-expect-actual`.

### "What layer does this DTO/entity/model belong to?"

```
NetworkDto (from Ktor JSON)      → stays inside :feature:x:data/remote/dto/
DatabaseEntity (from SQLDelight) → stays inside :feature:x:data/local/
DomainModel                      → lives in :feature:x:api/model/
UiState                          → lives in :feature:x:ui/FooContract.kt
```

The rule: data flows **inward** through mappers. Neither the DTO nor the entity ever
crosses the `:data` module boundary. The domain model is the lingua franca.

---

## Common Architecture Violations (Anti-Pattern Checklist)

Review each of these before shipping a feature:

- [ ] **DTO leaking to ViewModel**: `state.userDto.name` in a Screen composable
- [ ] **NetworkResult in MVI State**: `State(result: NetworkResult<User>)` — map to domain first
- [ ] **Direct DB query in ViewModel**: `db.userQueries.select()` in `handleIntent()` — use Repository
- [ ] **`GlobalScope` coroutine**: anywhere in the codebase — use `viewModelScope` or `CoroutineScope(SupervisorJob())`
- [ ] **Mutable `LaunchedEffect` key**: `LaunchedEffect(state.someFlag)` — restarts the effect on every change; use `Channel<Effect>` instead
- [ ] **`isLoading = true` without reset on error**: every `updateState { copy(isLoading = true) }` must have a matching `false` in the error branch
- [ ] **State in `remember` that must survive rotation**: registration form, search query, scroll offset with meaning
- [ ] **ViewModel state for dropdown/tooltip open state**: pure ephemeral UI → `remember`
- [ ] **`@Preview` impossible because state is buried**: composable has internal `remember` that can't be injected — hoist it
- [ ] **`actual everywhere` for pure Kotlin logic**: identical actuals on all platforms → move to `commonMain`
- [ ] **No local cache — pass-through repository**: `override suspend fun getUser() = remote.getUser().toDomain()` — no resilience, no offline support
- [ ] **`observeProducts()` triggers a network call**: the Flow should be reactive (SQLDelight); refresh is a separate `suspend fun`

---

## Skill Invocation Map

When the user asks about one of these topics, invoke the corresponding skill:

| User asks about | Invoke skill |
|---|---|
| "set up a new KMP project", "create feature module" | `kotlin-multiplatform-feature-scaffold` |
| "add Ktor", "network layer", "API calls", "token refresh" | `kotlin-multiplatform-network-layer` |
| "local database", "SQLite", "SQLDelight", "offline storage" | `kotlin-multiplatform-sqldelight-setup` |
| "CI", "GitHub Actions", "run KMP tests" | `kotlin-multiplatform-ci-github-actions` |
| "dev/staging/prod", "BuildKonfig", "environment config" | `kotlin-multiplatform-flavor-environment` |
| "XCFramework", "Swift Package Manager", "SPM", "iOS binary" | `kotlin-multiplatform-xcframework-spm` |
| "expect actual", "platform-specific", "@ObjCName", "iOS interop" | `kotlin-multiplatform-expect-actual` |
| "repository", "data layer", "offline-first", "cache", "single source of truth" | `kotlin-multiplatform-repository-pattern` |
| "navigation", "screen routing", "NavHost", "deep links" | `kotlin-multiplatform-navigation` |
| "shared strings", "localization", "image assets", "fonts" | `kotlin-multiplatform-shared-resources` |
| "MVI", "ViewModel state", "one-shot effects", "Screen/Content split" | `kotlin-multiplatform-mvi` |
| "design system", "AppTheme", "design tokens", "dark mode" | `kotlin-multiplatform-design-system` |
| "dialog", "bottom sheet", "toast", "tabs", "TopAppBar", "Checkbox" | `kotlin-multiplatform-design-system-extended` |
| "slot API", "content lambda", "composable parameter", "scoped slot" | `kotlin-multiplatform-compose-slot-api` |
| "state hoisting", "hoist state", "controlled component", "where does state go" | `kotlin-multiplatform-compose-state-hoisting` |
| "remember vs ViewModel", "rememberSaveable", "state survival", "config change" | `kotlin-multiplatform-compose-state-container` |

---

## Quick Health Check for Existing Projects

Run through these 5 questions for any KMP project audit:

1. **Dependency direction**: do `:ui` or `:domain` modules ever import from `:data`?
   If yes → architectural violation; data layer details are leaking.

2. **Network/DB types at the boundary**: does any ViewModel `State` contain a `Dto`, `Entity`,
   or `NetworkResult`? If yes → mapping is missing at the repository boundary.

3. **Effect delivery**: are effects `SharedFlow` or `StateFlow`? They should be `Channel<Effect>`.
   `SharedFlow` can replay effects (double navigation, double toast).

4. **State atomicity**: are there any `_state.value = _state.value.copy(...)` calls?
   They should be `_state.update { it.copy(...) }` to be thread-safe under concurrent intents.

5. **Expect/actual ratio**: what fraction of platform files have identical implementations?
   High ratio → probable over-use of expect/actual; move shared logic to `commonMain`.
