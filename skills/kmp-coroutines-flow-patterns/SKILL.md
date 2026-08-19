---
name: kmp-coroutines-flow-patterns
description: >
  General-purpose Kotlin coroutines and Flow patterns for Kotlin Multiplatform — structured
  concurrency and scope hierarchy, parallel decomposition, cold Flow vs StateFlow vs
  SharedFlow selection, exception transparency (the catch operator vs try/catch around a
  collector), cancellation-safe cleanup, and coroutine/Flow testing with runTest and
  Turbine. Does NOT cover screen-level state/effect wiring (see kmp-mvi) or repository
  Flow exposure conventions (see kmp-repository-pattern) — this is the shared foundation
  both build on.
license: Apache-2.0
metadata:
  author: kmp-agent-skills
  last-updated: '2026-08-19'
  keywords:
    - coroutines
    - kotlinx.coroutines
    - structured concurrency
    - coroutine scope
    - Flow
    - StateFlow
    - SharedFlow
    - cold flow
    - hot flow
    - flatMapLatest
    - flatMapMerge
    - retry backoff
    - catch operator
    - exception transparency
    - cancellation
    - runTest
    - Turbine
    - GlobalScope
    - async awaitAll
    - Mutex
---

## When to Use This Skill

Use this skill when you need to:
- Choose the right coroutine scope or Flow type for a given piece of code
- Run work in parallel and combine the results
- Handle retries, backoff, or exceptions inside a Flow correctly
- Write cancellation-safe cleanup for a coroutine or a long-running collector
- Test coroutines or Flow-emitting code

Do NOT use this skill when:
- The question is about a ViewModel's `State`/`Intent`/`Effect` wiring — see `kmp-mvi`
- The question is about how a repository exposes data as a `Flow` — see `kmp-repository-pattern`
- The question is about injecting a `CoroutineScope` via Koin — see `kmp-dependency-injection`

**Trigger keywords:** coroutine, kotlinx.coroutines, coroutine scope, structured
concurrency, GlobalScope, Flow, StateFlow, SharedFlow, cold flow, hot flow,
flatMapLatest, flatMapMerge, flatMapConcat, retry backoff, catch operator, exception
transparency, cancellation, runTest, Turbine, async awaitAll, parallel decomposition,
Mutex, coroutine testing.

**Freshness rule:** `kotlinx.coroutines` releases new operators and testing APIs
between minor versions — recheck [github.com/Kotlin/kotlinx.coroutines/releases](https://github.com/Kotlin/kotlinx.coroutines/releases)
before pinning. Minimum version: `kotlinx-coroutines-core = "1.11.0"` in
`gradle/libs.versions.toml`.

---

## Recommendation First

Default to structured concurrency everywhere: every coroutine has a parent scope tied
to a real lifecycle (`viewModelScope`, a test's `TestScope`, or a scope you own and
`cancel()` yourself) — never `GlobalScope`. For Flow, default to `StateFlow` when
exposing state a UI reads (conflated, always has a current value) and reserve
`SharedFlow`/`Channel` for one-shot events (see `kmp-mvi`'s Contract pattern for the
exact effect-delivery shape).

```kotlin
class SyncCoordinator(
    private val scope: CoroutineScope,
    private val repository: ItemRepository,
) {
    private val _status = MutableStateFlow<SyncStatus>(SyncStatus.Idle)
    val status: StateFlow<SyncStatus> = _status.asStateFlow()

    fun start() {
        scope.launch {
            _status.value = SyncStatus.Syncing
            runCatching { repository.syncAll() }
                .onSuccess { _status.value = SyncStatus.Idle }
                .onFailure { _status.value = SyncStatus.Failed(it.message) }
        }
    }
}
```

---

## Structured Concurrency & Scope Hierarchy

**Never `GlobalScope`.** A coroutine launched on `GlobalScope` outlives every lifecycle
it should be tied to — nothing cancels it when the screen closes, the test ends, or the
app backgrounds. Every coroutine needs a parent scope that gets cancelled when its owner
goes away:

```kotlin
// ❌ outlives the ViewModel, screen, or test that started it
GlobalScope.launch { fetchData() }

// ✓ cancelled automatically when the ViewModel is cleared
viewModelScope.launch { fetchData() }

// ✓ cancelled automatically when the composable leaves composition
LaunchedEffect(key) { fetchData() }
```

### Parallel decomposition

Use `coroutineScope` + `async` when two or more independent suspend calls can run
concurrently — `coroutineScope` propagates a failure in any child to the others and
waits for all children before returning:

```kotlin
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val items = async { itemRepository.getRecent() }
    val stats = async { statsRepository.getToday() }
    val profile = async { userRepository.getCurrent() }
    Dashboard(items = items.await(), stats = stats.await(), profile = profile.await())
}
```

Sequential `await()`s called one after another without `async` first defeat the whole
point — each `await()` blocks the next call from even starting:

```kotlin
// ❌ sequential — profile fetch doesn't start until items finishes
suspend fun loadDashboardSlow(): Dashboard {
    val items = itemRepository.getRecent()
    val stats = statsRepository.getToday()
    val profile = userRepository.getCurrent()
    return Dashboard(items, stats, profile)
}
```

---

## Flow Type Selection: Cold, StateFlow, SharedFlow

| Type | Shape | Reach for it when |
|---|---|---|
| `Flow` (cold) | Starts fresh per collector, no memory of past emissions | A one-shot or per-request stream — a network call wrapped as a `Flow`, a database query result |
| `StateFlow` | Hot, always has a current value, conflated (a slow collector skips intermediate values, sees only the latest) | UI state a screen reads — the collector always wants "the current state," never a full history |
| `SharedFlow` | Hot, configurable replay/buffer, no default current value | Broadcasting an event to 0+ collectors, or replaying the last N values to a *late* subscriber — not a single "current value" the way `StateFlow` is |
| `Channel` | Hot, single-consumer, exactly-once delivery per element | One-shot side effects (navigation, a toast) — see `kmp-mvi`'s Contract pattern for why `Channel` beats `SharedFlow` here |

**The conflation distinction is the one that actually bites**: a `StateFlow` collector
that's slow (recomposition backpressure, a paused screen) never sees every intermediate
value — only the latest when it catches up. If a caller genuinely needs every emitted
value in order (an audit log, a sequence of discrete events), `StateFlow` silently drops
data that a `SharedFlow` with `replay = 0` and unbounded buffer would preserve.

---

## Exception Transparency — `catch`, Not `try`/`catch` Around `collect`

A `Flow`'s exception-handling contract is that exceptions propagate downstream through
collection — wrapping the `collect {}` call in `try`/`catch` catches exceptions from the
collector's own body too, not just the upstream Flow, and it's easy to mask a bug this
way. Use the `catch` operator, placed exactly where it should intercept:

```kotlin
// ❌ catches bugs in the collector body too, not just upstream failures
try {
    repository.observeItems().collect { items -> render(items) }
} catch (e: Exception) {
    showError(e)
}

// ✓ catch operates only on the upstream Flow, before collect ever runs
repository.observeItems()
    .catch { e -> showError(e) }
    .collect { items -> render(items) }
```

`catch` only intercepts exceptions from operators *above* it in the chain — it can't
catch something thrown inside `collect {}` itself, which is the intended behavior, not
a limitation.

### Retry with backoff

`retry`/`retryWhen` re-subscribe to the upstream Flow on a predicate — pair with a real
backoff delay, not a tight retry loop:

```kotlin
fun observeWithRetry(): Flow<List<Item>> = repository.observeItems()
    .retryWhen { cause, attempt ->
        if (cause !is IOException || attempt >= 3) return@retryWhen false
        delay(1000L * (1 shl attempt.toInt()))
        true
    }
```

---

## Choosing an Operator: `flatMapLatest` vs `flatMapMerge` vs `flatMapConcat`

All three flatten a `Flow<Flow<T>>` into a `Flow<T>` — they differ in what happens when
a new upstream value arrives before the previous inner `Flow` finishes:

- **`flatMapLatest`** — cancels the previous inner `Flow` and switches to the new one.
  Reach for this on a search-as-you-type box: a new keystroke should cancel the
  in-flight request for the old query, not race it.
- **`flatMapConcat`** — runs inner Flows one at a time, in order, never overlapping.
  Reach for this when order matters and concurrent execution would corrupt state (a
  sequence of writes that must apply in order).
- **`flatMapMerge`** — runs inner Flows concurrently, interleaving their emissions.
  Reach for this when the inner Flows are independent and order doesn't matter — most
  "fetch N things in parallel and emit as each completes" cases.

```kotlin
// ✓ flatMapLatest — a new query cancels the previous in-flight search
searchQueryFlow
    .debounce(300)
    .flatMapLatest { query -> repository.search(query) }
    .collect { results -> render(results) }
```

---

## Cancellation-Safe Cleanup

A `finally` block runs even on cancellation, but a **suspending call inside `finally`**
throws immediately once the coroutine is already cancelled — wrap cleanup that must
itself suspend in `withContext(NonCancellable)`:

```kotlin
suspend fun withConnection(block: suspend (Connection) -> Unit) {
    val connection = pool.acquire()
    try {
        block(connection)
    } finally {
        // ✓ closeSuspending() still runs even though the coroutine is cancelled —
        // without NonCancellable, this suspend call would throw immediately instead
        withContext(NonCancellable) { connection.closeSuspending() }
    }
}
```

For a `Flow`, `onCompletion {}` is the equivalent hook — runs whether the Flow finished
normally, threw, or was cancelled, and receives the cause (`null` on normal completion):

```kotlin
repository.observeItems()
    .onCompletion { cause -> if (cause != null) log.warn("collection stopped: $cause") }
    .collect { items -> render(items) }
```

---

## Suspend-Safe Critical Sections: `Mutex`, Not a Plain Lock

`synchronized`/`ReentrantLock` block the underlying thread while held — inside a
suspend function, that can block a shared dispatcher thread for the duration, starving
other coroutines. `kotlinx.coroutines.sync.Mutex` suspends the coroutine instead of
blocking the thread:

```kotlin
class Cache {
    private val mutex = Mutex()
    private val map = mutableMapOf<String, User>()

    suspend fun getOrPut(id: String, load: suspend () -> User): User =
        mutex.withLock { map.getOrPut(id) { load() } }
}
```

---

## Testing

`kotlinx-coroutines-test`'s `runTest` runs suspending test bodies on a virtual-time test
dispatcher — `delay()` calls skip forward instantly instead of actually waiting:

```kotlin
class SyncCoordinatorTest {

    @Test
    fun `start transitions Idle to Syncing to Idle on success`() = runTest {
        val coordinator = SyncCoordinator(scope = this, repository = FakeItemRepository())

        coordinator.status.test {
            assertEquals(SyncStatus.Idle, awaitItem())
            coordinator.start()
            assertEquals(SyncStatus.Syncing, awaitItem())
            assertEquals(SyncStatus.Idle, awaitItem())
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `retryWhen backs off and gives up after 3 attempts`() = runTest {
        var attempts = 0
        val flow = flow<Unit> {
            attempts++
            throw IOException("boom")
        }.retryWhen { cause, attempt -> cause is IOException && attempt < 3 }

        assertFailsWith<IOException> { flow.collect() }
        assertEquals(4, attempts) // initial attempt + 3 retries
    }
}
```

Use Turbine's `.test {}` (already a dependency once `kmp-mvi` is set up) to assert on a
sequence of Flow emissions instead of manually collecting into a list — `awaitItem()`
fails loudly if an expected emission never arrives, instead of a test that passes
because it stopped collecting too early.

---

## Common Anti-Patterns

- **`GlobalScope.launch { ... }`** — outlives every real lifecycle it should be tied to.
  Use a scope owned by something that gets torn down (`viewModelScope`, a scope you
  `cancel()` yourself in `onDestroy`/equivalent).
- **`try`/`catch` wrapped around `flow.collect { }`** — catches bugs in the collector's
  own body along with genuine upstream failures, masking the difference. Use the
  `catch` operator placed precisely where it should intercept.
- **A blocking call inside a coroutine with no `withContext(Dispatchers.IO)`** — a
  synchronous file/network/DB call on `Dispatchers.Main` or `Dispatchers.Default`
  starves every other coroutine sharing that dispatcher.
- **`SharedFlow` used where `StateFlow`'s conflation is what's actually needed** (or the
  reverse) — a late collector on `SharedFlow(replay = 0)` misses everything that
  happened before it subscribed; a `StateFlow` consumer that needs every discrete event
  in order silently loses intermediate values it was never designed to keep.
- **A plain `synchronized`/`ReentrantLock` inside a suspend function** — blocks the
  underlying dispatcher thread instead of suspending; use `Mutex.withLock` instead.

---

## Related Skills

- `kmp-mvi` — builds `Channel<Effect>` one-shot delivery and `StateFlow` screen state
  directly on the patterns here
- `kmp-repository-pattern` — Flow-returning data sources follow the cold-Flow and
  exception-transparency rules from this skill
- `kmp-dependency-injection` — how a `CoroutineScope` gets constructed and injected
  rather than created ad hoc
- `kmp-unit-testing` — general test conventions this skill's `runTest`/Turbine examples
  follow

---

## Output Style

When asked about coroutines or Flow in KMP, respond in this order:
1. recommendation (scope choice or Flow type, stated directly)
2. code snippet (minimal working example)
3. why this approach fits
4. main alternative and when it would apply instead

Keep responses focused — this skill covers general coroutine/Flow patterns, not
screen-level state wiring (`kmp-mvi`) or repository conventions (`kmp-repository-pattern`).

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-19 | Initial release. Gap found comparing coverage against a third-party skill collection: no skill in this repo covered general coroutine/Flow patterns as their own topic — scattered implicitly across `kmp-mvi`/`kmp-repository-pattern`, which both assumed the reader already knew structured concurrency, Flow type selection, and exception transparency. Covers: scope hierarchy (never `GlobalScope`), parallel decomposition, `Flow`/`StateFlow`/`SharedFlow`/`Channel` selection, `catch` vs `try`/`catch` around `collect`, `flatMapLatest`/`flatMapMerge`/`flatMapConcat` selection, `NonCancellable` cleanup, `Mutex` over blocking locks, and `runTest`/Turbine testing. |
