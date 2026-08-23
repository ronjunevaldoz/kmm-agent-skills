---
name: kmp-resilience
description: >
  Resilience patterns for Kotlin Multiplatform — retry with exponential
  backoff and jitter, timeouts, circuit breakers, rate limiting, idempotency
  keys for safe mutation retries, and transient-vs-fatal error classification.
  Covers Ktor's built-in HttpRequestRetry (client) and RateLimit (server)
  plugins, kotlinx.coroutines' withTimeout, and why KMP has no
  cross-platform circuit-breaker library (Resilience4j is JVM-only) — a
  hand-rolled state machine is the honest default. Also covers auditing
  resilience parity across multiple platform-specific implementations of the
  same capability (multiple actuals, or multiple selectable backends) — a
  real, evidence-backed gap: one implementation handling recoverable failures
  while a sibling implementation doesn't is a parity bug, not a platform
  difference.
license: Apache-2.0
metadata:
  author: kmp-agent-skills
  last-updated: '2026-08-24'
  keywords:
    - resilience
    - retry
    - exponential backoff
    - jitter
    - circuit breaker
    - timeout
    - rate limiting
    - idempotency key
    - HttpRequestRetry
    - transient error
    - fatal error
    - device lost
    - connection lost
    - backend parity
---

## When to Use This Skill

Use when you need to:
- Decide how a failed network or native-resource call should be retried, if at all
- Protect a Ktor server route from being overwhelmed
- Make a mutation (checkout, payment, claiming a limited resource) safe to retry
  without double-executing it
- Classify an error as recoverable (retry, recreate the resource) vs fatal
  (surface to the caller, stop retrying)
- Audit whether resilience handling exists symmetrically across every
  platform-specific implementation of a capability, not just the one tested most

**Trigger keywords:** retry, exponential backoff, jitter, circuit breaker,
timeout, rate limiting, idempotency key, HttpRequestRetry, transient error,
fatal error, recoverable error, device lost, connection lost, resilience,
backend parity, platform parity.

**Freshness rule:** Ktor's `HttpRequestRetry` had a real bug where exponential
delay didn't work for delays ≤ 1 second (KTOR-7294), fixed in Ktor 3.0.0 —
recheck the installed Ktor version before relying on sub-second retry delays.

---

## Recommendation First

**Ktor's built-in plugins first** — `HttpRequestRetry` (client) and `RateLimit`
(server) ship in `ktor-client-core`/`ktor-server-core` with zero extra
dependencies and cover the two most common cases directly. **No
cross-platform circuit-breaker library exists for KMP** — Resilience4j is
JVM-only, breaking the multiplatform promise; a small hand-rolled state
machine (below) is the honest default, not a workaround. **Idempotency keys**
are what actually makes "just retry it" safe for a mutation — retry logic
alone is not a safety mechanism for anything that charges money or claims a
limited resource.

---

## Retry — Exponential Backoff and Jitter

```kotlin
val client = HttpClient(CIO) {
    install(HttpRequestRetry) {
        retryOnServerErrors(maxRetries = 5)
        exponentialDelay()   // (base^retryCount-1) * baseDelayMs + jitter — jitter is built in
    }
}
```

**Why jitter isn't optional**: a fixed-delay retry loop with no randomization
causes a thundering herd — if a dependency goes down, every caller's retry
lands at the same instant, re-crashing the dependency the moment it recovers.
`exponentialDelay()` includes jitter by default; never hand-roll
`delay(attempt * 1000L)` without adding randomization.

**For a non-HTTP suspend call** (a database driver, a native resource call),
the same shape without Ktor:

```kotlin
suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    initialDelayMs: Long = 200,
    block: suspend () -> T,
): T {
    var attempt = 0
    var delayMs = initialDelayMs
    while (true) {
        try {
            return block()
        } catch (e: RecoverableException) {
            attempt++
            if (attempt >= maxAttempts) throw e
            delay(delayMs + Random.nextLong(0, delayMs / 2))   // jitter
            delayMs *= 2
        }
    }
}
```

**Only retry idempotent operations without an idempotency key.** A read is
always safe to retry. A mutation is not — see Idempotency Keys below.

---

## Timeout

```kotlin
val result = withTimeoutOrNull(5_000) { fetchUpstreamData() }
    ?: return Result.failure(TimeoutException("upstream did not respond in 5s"))
```

A suspend call with no timeout doesn't fail — it suspends indefinitely,
holding whatever resource it acquired (a connection, a coroutine, a native
handle) open forever. Every external call needs one; "it will eventually
throw" is not a timeout policy.

---

## Circuit Breaker — Hand-Rolled, KMP Has No Cross-Platform Library

```kotlin
class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val halfOpenAfterMs: Long = 10_000,
) {
    private enum class State { CLOSED, OPEN, HALF_OPEN }
    private var state = State.CLOSED
    private var consecutiveFailures = 0
    private var openedAtMs = 0L

    suspend fun <T> execute(block: suspend () -> T): T {
        if (state == State.OPEN) {
            if (currentTimeMs() - openedAtMs < halfOpenAfterMs) {
                throw CircuitOpenException()   // fail fast — no call attempted
            }
            state = State.HALF_OPEN
        }
        return try {
            val result = block()
            consecutiveFailures = 0
            state = State.CLOSED
            result
        } catch (e: RecoverableException) {
            consecutiveFailures++
            if (consecutiveFailures >= failureThreshold) {
                state = State.OPEN
                openedAtMs = currentTimeMs()
            }
            throw e
        }
    }
}
```

Compose with retry by wrapping, not nesting manually: `breaker.execute { retryWithBackoff { call() } }`.

---

## Rate Limiting — Ktor Server, Token Bucket

```kotlin
install(RateLimit) {
    register(RateLimitName("protected")) {
        rateLimiter(limit = 30, refillPeriod = 60.seconds)
    }
}

routing {
    rateLimit(RateLimitName("protected")) {
        get("/api/protected") { /* ... */ }
    }
}
```

Token bucket (Ktor's default) tolerates bursts; sliding window enforces
stricter, more even spacing — pick sliding window only when burst tolerance
is genuinely undesirable for that route.

---

## Idempotency Keys

```kotlin
suspend fun checkout(idempotencyKey: String, cart: Cart): CheckoutResult {
    processedKeys.get(idempotencyKey)?.let { return it }   // already processed — return cached result
    val result = paymentProvider.charge(cart)
    processedKeys.put(idempotencyKey, result)
    return result
}
```

Generate the key client-side (once, before the first attempt) and send it on
every retry of the same logical mutation — the server dedupes on the key, not
on request timing. Without this, a retried "charge the card" call after a
timeout (where the first attempt actually succeeded server-side, just the
response was lost) charges the card twice.

---

## Transient vs Fatal Error Classification

The real, general principle: not every failure is the same shape, and
treating them all as either "always retry" or "always crash" is wrong both
ways. Generic example — a database connection pool losing a stale connection
is exactly the same shape as a native device handle or a websocket dropping:

```kotlin
sealed class ConnectionException(message: String) : Exception(message) {
    class StaleConnection(message: String) : ConnectionException(message)   // recoverable — recreate and retry
    class AuthenticationFailed(message: String) : ConnectionException(message)  // fatal — credentials are wrong, retrying won't help
    class PoolExhausted(message: String) : ConnectionException(message)     // recoverable — backoff and retry
}

suspend fun withConnection(pool: ConnectionPool, block: suspend (Connection) -> Unit) {
    try {
        pool.acquire().use { block(it) }
    } catch (e: ConnectionException.StaleConnection) {
        pool.recreate()
        pool.acquire().use { block(it) }   // one retry after recreating
    }
    // AuthenticationFailed and PoolExhausted are NOT caught here — they propagate,
    // because "recoverable" and "fatal" need different handling, not the same catch-all
}
```

**Real evidence this distinction matters**: a KMP project with two
platform-specific backends for the same capability was found handling this
correctly on one platform (catching a specific recoverable native-result code
and recreating the resource) and not at all on the sibling platform (any
failure was an uncaught hard crash) — see Backend/Platform Parity below.

---

## Backend/Platform Parity Check

When a capability has **multiple platform-specific implementations** — more
than one `actual`, or a project that lets the caller select between several
backend strategies for the same job — resilience handling must be audited
**across every implementation**, not just the one exercised most during
development. Real, evidence-backed finding: one implementation had real
recovery logic for a recoverable resource-loss error; its sibling
implementation had no equivalent at all, not because the sibling's failure
mode doesn't exist, but because nobody had hit it yet in testing.

This is a parity bug, not a platform difference — "platform B doesn't need
retry logic" is a claim that needs evidence (does platform B's underlying
resource genuinely never fail transiently?), not an assumption because
platform A happened to get the resilience code written first.

---

## Testing

`runTest` gives virtual time — `delay()` calls inside retry/backoff logic
resolve instantly in tests, no real waiting, no flaky sleep-based tests:

```kotlin
class RetryWithBackoffTest {
    @Test
    fun `retries until success within maxAttempts`() = runTest {
        var callCount = 0
        val result = retryWithBackoff(maxAttempts = 3) {
            callCount++
            if (callCount < 3) throw RecoverableException("transient")
            "success"
        }
        assertEquals("success", result)
        assertEquals(3, callCount)
    }

    @Test
    fun `gives up after maxAttempts and rethrows`() = runTest {
        var callCount = 0
        assertFailsWith<RecoverableException> {
            retryWithBackoff(maxAttempts = 2) {
                callCount++
                throw RecoverableException("always fails")
            }
        }
        assertEquals(2, callCount)
    }
}

class CircuitBreakerTest {
    @Test
    fun `opens after threshold consecutive failures and fails fast`() = runTest {
        val breaker = CircuitBreaker(failureThreshold = 2)
        repeat(2) {
            assertFailsWith<RecoverableException> {
                breaker.execute { throw RecoverableException("down") }
            }
        }
        // Third call: circuit is open, fails immediately without calling block()
        var blockCalled = false
        assertFailsWith<CircuitOpenException> {
            breaker.execute { blockCalled = true }
        }
        assertFalse(blockCalled)
    }
}
```

For the transient-vs-fatal distinction, a fake that throws each `ConnectionException`
subtype in turn is enough to verify the caller branches correctly — no real
connection pool or native resource needed. See `kmp-unit-testing`'s
fake-over-mock rule for the same reasoning applied here.

---

## Common Anti-Patterns

- **`delay(attempt * 1000L)` with no jitter** — a thundering herd waiting to happen the
  moment the dependency it's calling recovers from an outage.
- **Retrying a mutation with no idempotency key** — "just retry it" doubles the
  side effect (double charge, double booking) when the first attempt actually
  succeeded and only the response was lost.
- **A single generic `catch (e: Exception)` around retry logic** — retries a fatal
  error (bad credentials, malformed request) exactly as many times as a
  transient one, wasting the retry budget on something retrying can never fix.
- **A call with no timeout** — "it'll eventually throw" isn't a policy; it holds
  the resource it acquired open indefinitely.
- **Assuming a JVM-only resilience library works in commonMain** — Resilience4j,
  and most Java resilience tooling, is JVM-only; verify multiplatform support
  before adding a dependency to shared code.
- **Resilience logic written for one platform's implementation and never ported
  to its siblings** — see Backend/Platform Parity above; audit every `actual`
  or selectable backend, not just the one tested most.

---

## Related Skills

- `kmp-network-layer` — the Ktor client this skill's retry/timeout patterns wire into
- `kmp-mvi` — surfacing a fatal (non-retried) error as a UI `Effect`
- `kmp-expect-actual` — the `actual` boundary where Backend/Platform Parity applies
- `kmp-jni-pro` — native resource lifecycle (acquire/release) that transient-vs-fatal classification often wraps

---

## Output Style

When asked about resilience, respond in this order:
1. is the operation idempotent, or does it need an idempotency key first
2. retry policy (Ktor plugin or hand-rolled), with jitter
3. timeout
4. transient-vs-fatal classification if the failure has more than one real shape
5. circuit breaker only if repeated failures against the same dependency are a real, observed problem — not by default

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-24 | Initial release. Real, evidence-backed gap: ts-agent-skills already had a full `ts-resilience` skill (retry/circuit-breaker/timeout/rate-limiting/idempotency), kmp-agent-skills had nothing equivalent. Confirmed while investigating a real KMP native-binding project's graphics backend — one platform implementation had real recovery logic for a recoverable resource-loss error, its sibling implementation had none at all, and device/resource init failures were hard, unretried throws in both. Verified Ktor's real plugins before citing them: `HttpRequestRetry` (client, built-in exponential backoff with jitter, real KTOR-7294 bug fixed in 3.0.0) and `RateLimit` (server, built-in token bucket). Confirmed no cross-platform circuit-breaker library exists for KMP (Resilience4j is JVM-only) before presenting a hand-rolled one as the default, not a fallback. Added "Backend/Platform Parity Check" as a named principle, generalized from the real finding — examples throughout use a generic connection-pool scenario, not the domain the gap was found in. |
