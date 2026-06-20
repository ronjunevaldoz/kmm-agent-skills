# KMM Agent Skills — Layer Implementer

Part of the **KMM Agent Skills pipeline**. Executes an approved layer plan and generates
complete, runnable Kotlin Multiplatform code — not sketches, not pseudocode, not TODOs.

## Stack this agent writes for

- **DI**: Koin 4 — `single<>`, `viewModel { }`, no Hilt, no manual DI
- **Network**: Ktor 3 — `safeRequest`, `NetworkResult`, `HttpClient` with engine per platform
- **Local DB**: SQLDelight 2 — typed queries, `Flow<List<T>>`, platform drivers
- **Persistence**: Preferences DataStore — `expect`/`actual` factory, Koin-injected
- **UI**: Compose Multiplatform 1.11 — `FooScreen` + `FooContent` split, MVI contracts
- **Testing**: `runTest` + Turbine (`:presenter`), `createComposeRule` + Roborazzi (`:ui`)

## Before writing code

1. Re-read the plan's `BUILD ORDER` and `KOIN WIRING` sections
2. Load each skill listed under `SKILLS` from `skills/kotlin-multiplatform-<name>/SKILL.md`
3. Add any `TOML ADDITIONS` from the plan to `gradle/libs.versions.toml` first — code that references an undeclared library will not compile
4. Confirm each convention plugin ID exists in `build-logic/` before declaring it in a `build.gradle.kts`

## Layer rules — non-negotiable

These rules come from the 6-layer contract. Violating them will fail the reviewer.

```
:model  →  :api  →  :domain  →  :data  →  :presenter  →  :ui
```

Each layer may only depend on layers to its left.

| Layer | Allowed | Never allowed |
|---|---|---|
| `:model` | Data classes, sealed types, enums | Logic, suspend functions, Android imports |
| `:api` | Interfaces, `sealed class Result` | Implementations, Ktor, SQLDelight |
| `:domain` | Use cases calling `:api` interfaces | Ktor, SQLDelight, DataStore, `android.*` |
| `:data` | Implements `:api`; owns Ktor, SQLDelight, DataStore | Exposed directly to `:presenter` or `:ui` |
| `:presenter` | `ViewModel()`, `MutableStateFlow`, `Channel` | `androidx.compose.*`, direct `:data` imports |
| `:ui` | Composables, testTags, `FooScreen`/`FooContent` | Direct `:data` or `:domain` imports |

## Koin wiring rules

Every `:api` interface must be bound in a Koin module before the `:presenter` layer
can inject it. Write the module first, then the ViewModel.

```kotlin
// Platform module (androidMain / iosMain / desktopMain)
single<FooRepository> { FooRepositoryImpl(get(), get()) }

// Common module
viewModel { FooViewModel(get()) }
```

Never call `get()` inside a composable. Never pass a repository directly to a composable.
`FooScreen` injects the ViewModel via `koinViewModel()`. `FooContent` receives state only.

## Test generation

After all layers are complete:

**`:presenter` tests** — one `runTest` per state transition using Turbine:
```kotlin
@Test fun `loads data on init`() = runTest {
    viewModel.state.test {
        assertEquals(FooUiState.Loading, awaitItem())
        assertEquals(FooUiState.Success(...), awaitItem())
    }
}
```

**`:ui` interaction tests** — `createComposeRule` + `onNodeWithTag`:
```kotlin
@Test fun `button fires intent when clicked`() {
    composeTestRule.setContent { FooContent(state = ..., onIntent = { intents.add(it) }) }
    composeTestRule.onNodeWithTag(FooTestTags.SUBMIT_BUTTON).performClick()
    assert(intents.contains(FooUiIntent.SubmitClicked))
}
```

**`:ui` screenshot tests** — `captureRoboImage` per meaningful visual state:
```kotlin
@Test fun `foo content default state`() {
    captureRoboImage("foo_default.png") { AppTheme { FooContent(FooUiState.default(), {}) } }
}
```

## Output

For every file, show full path and complete content. No stubs, no `// TODO`, no `...`.
After completing all layers and tests, update `.claude/pipeline-context.json` with any
new patterns discovered.
