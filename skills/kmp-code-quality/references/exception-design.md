# Exception Design — Custom Types vs `require`/`check` vs Generic `throw`

Part of `kmp-code-quality`. Load this file when working on: exception design.

---

Kotlin has **no checked exceptions** — nothing forces a caller to handle a
thrown exception the way Java's `throws` clause does. That single fact drives
every rule below: if a failure is a normal, expected outcome the caller
should handle, prefer a sealed return type over throwing at all, because
`when` exhaustiveness gives you the compile-time safety net Kotlin's
exceptions don't.

## Decision: sealed Result, `require`/`check`, or a custom exception type?

| Failure shape | Use | Why |
|---|---|---|
| Expected, recoverable outcome the caller should handle (network error, validation failure) | A sealed `Result`/`NetworkResult<T>`-style return type, not a thrown exception | `when` exhaustiveness forces every caller to handle every case; a thrown exception forces nothing |
| Precondition violation — caller passed a bad argument | `require`/`requireNotNull` | Throws `IllegalArgumentException`; this is an assertion, not meant to be caught |
| Invariant violation — the object's own internal state is wrong | `check`/`checkNotNull` | Throws `IllegalStateException`; same "should be impossible" contract, but about internal state, not the caller's input |
| Exceptional, and the caller genuinely needs to distinguish multiple recoverable-vs-fatal cases at a boundary where a sealed Result isn't practical (crossing a native/JNI boundary, deep in a call chain that can't easily be restructured to return a Result) | A custom sealed exception hierarchy | Gets the same `when`-exhaustiveness benefit as a sealed Result, at a call site where returning one isn't practical |
| Generic `throw Exception(...)`/`throw RuntimeException(...)` | **Avoid as a default** | A caller can't catch it selectively without also catching every other generic exception thrown nearby — it collapses "recoverable" and "fatal" into the same catchable type |

## `require` vs `check` — which one

- **`require(condition)` / `requireNotNull(value)`** — validates a **function
  argument**. Throws `IllegalArgumentException`. Use at the top of a function
  to validate what the caller passed in.
- **`check(condition)` / `checkNotNull(value)`** — validates **internal
  state**. Throws `IllegalStateException`. Use mid-function or in a property
  getter to assert an invariant about the receiver's own state, not about
  what the caller passed.
- Both are programmer-error assertions, appropriate for "this should be
  impossible if the code is correct" — not for an expected, recoverable
  failure path a real user can trigger (a network timeout is not a
  precondition violation; don't `require` it away).

## Custom exception type — when it earns its keep

```kotlin
sealed class SyncException(message: String) : Exception(message) {
    class NetworkUnavailable(message: String) : SyncException(message)          // caller should retry later
    class ConflictDetected(val serverVersion: Int, message: String) : SyncException(message)  // caller must resolve
    class SchemaOutOfDate(message: String) : SyncException(message)             // caller must force an app update — fatal
}

fun handleSyncFailure(e: SyncException) = when (e) {
    is SyncException.NetworkUnavailable -> scheduleRetry()
    is SyncException.ConflictDetected -> promptUserToResolve(e.serverVersion)
    is SyncException.SchemaOutOfDate -> forceAppUpdate()
}
```

A sealed exception hierarchy earns its keep specifically because the `when`
above is exhaustive — the compiler flags it the moment a fourth case is
added and this handler isn't updated. A generic `catch (e: Exception)` gives
none of that; every case gets the same handling by construction, whether
that's correct or not.

## The real cost of skipping this — evidence, not a hunch

A real KMP codebase's native-binding backend was found with exactly **one**
custom exception type in its entire render stack, used at 2 call sites — and
**61** `require`/`check` sites, 5 `error(...)` calls, and 4 bare
`throw Exception(...)` sites doing everything else. The one custom type
existed only because the code genuinely needed to distinguish one specific
recoverable native-result code from a fatal one — everywhere else, "should
this be retried or should this crash" had no answer encoded in the type
system at all, only in whichever developer happened to read that specific
`throw` site's message string. See `kmp-resilience`'s "Transient vs Fatal
Error Classification" for the general pattern this evidence backs.

## Common Anti-Patterns

- **`throw Exception("something went wrong")`** — no type information for a
  caller to branch on, no way to catch this specifically without catching
  every other generic exception nearby too.
- **Using `require`/`check` for an expected, user-triggerable failure** — a
  network timeout, a validation failure a real user can cause, is not a
  precondition/invariant violation; model it as a sealed Result instead.
- **A `catch (e: Exception)` around a call that can throw both recoverable
  and fatal errors** — treats "retry this" and "this can never succeed" as
  the same catchable event, guaranteeing the wrong response to at least one
  of them.
- **A custom exception hierarchy with only one subtype** — if there's
  nothing to distinguish yet, a sealed hierarchy is premature; a single
  exception type (or a sealed Result) covers it until a second real case
  shows up.
