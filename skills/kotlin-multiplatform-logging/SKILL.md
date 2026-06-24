---
name: kotlin-multiplatform-logging
description: >
  Sets up kotlin-logging or Kermit for KMP projects: log levels, logger factories per
  target, crash boundary integration (Firebase Crashlytics, Sentry), and Koin wiring so
  every layer gets a logger without constructing it directly.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-24'
  keywords:
    - Kermit
    - kotlin-logging
    - KotlinLogging
    - logging
    - KMP
    - Kotlin Multiplatform
    - log levels
    - crash reporting
    - Koin
    - logger factories
    - crash bridges
    - Crashlytics
    - Sentry
---

## When to Use This Skill

Use when you need to:
- Add structured logging to a KMP project
- Configure different log levels per build variant or environment
- Route breadcrumbs to Crashlytics or Sentry
- Wire a logger factory into Koin so feature modules do not construct loggers directly
- Keep test output quiet without disabling diagnostics in production

**Trigger keywords:** logging, kotlin-logging, Kermit, KMP logging, crash reporting,
logger setup, Crashlytics logging, Sentry logging, Koin logger, production logs.

**Freshness rule:** kotlin-logging modules and Kermit releases change between minor
versions. Recheck the [kotlin-logging repository](https://github.com/oshai/kotlin-logging)
and the [Kermit repository](https://github.com/touchlab/Kermit) before pinning a version.

---

## Recommendation First

Default to **one logging facade per project**.

Why:
- kotlin-logging is KMP-supported and gives you a consistent Kotlin-style facade across targets
- Kermit is also KMP-native and remains a good fit for existing projects already on it
- lazy lambda messages keep expensive strings out of hot paths
- a logger factory can be injected once and reused everywhere
- crash breadcrumbs stay separate from the logging facade, which keeps the architecture clean

Use `KotlinLogging.logger {}` when the project is on kotlin-logging. If the project already
uses Kermit, keep that path consistent instead of mixing both facades inside the same
module graph. In both cases, keep the logger behind a factory or small adapter.

---

## Gradle Setup

### `libs.versions.toml`

```toml
[versions]
kotlin-logging = "7.0.3"
kermit = "2.1.0"

[libraries]
kotlin-logging = { module = "io.github.oshai:kotlin-logging", version.ref = "kotlin-logging" }
kermit = { module = "co.touchlab:kermit", version.ref = "kermit" }
```

### `build-logic` - add to `GROUP_ID.core.gradle.kts`

```kotlin
sourceSets {
    commonMain.dependencies {
        implementation(libs.kotlin.logging) // swap to libs.kermit if the project already uses Kermit
    }
}
```

Feature modules receive the logger facade transitively via `:core:common`. Do not add
logging dependencies per feature. Pick one facade for the project and keep it uniform.
If the repository already standardizes on Kermit, keep that path and do not mix in
kotlin-logging in the same module graph.

---

## Logger Usage

### Shared code with kotlin-logging

```kotlin
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

fun loadUser(userId: String) {
    logger.debug { "Loading user $userId" }
}
```

### Shared code with Kermit

```kotlin
import co.touchlab.kermit.Logger

private val logger = Logger.withTag("AuthViewModel")

fun loadUser(userId: String) {
    logger.d { "Loading user $userId" }
}
```

### Log levels

| Level | Use for |
|---|---|
| `trace` | Highly detailed trace - only during development |
| `debug` | Flow control, variable values - development builds |
| `info` | Key lifecycle events - sign-in, app start |
| `warn` | Recoverable issues - retry triggered, fallback used |
| `error` | Unrecoverable errors - route to crash reporters |

Keep message formatting inside the lambda so expensive work is skipped when the level
is disabled.

---

## Koin Wiring

Inject a logger factory instead of scattering direct logger construction across the codebase:

```kotlin
// :core:common - CoreModule.kt
val coreModule = module {
    factory { (name: String) -> KotlinLogging.logger(name) }
}
```

### Consuming in a ViewModel

Choose the concrete logger type that matches the facade the project uses. If you need a
shared abstraction, keep it tiny and map it to the chosen logger in the infrastructure
layer.

---

## Crash Boundary

If you need breadcrumbs in crash reports, add a small bridge from your logger facade to
the crash reporter. Keep that bridge in infrastructure, not in feature modules.

```kotlin
interface BreadcrumbSink {
    fun breadcrumb(level: String, tag: String, message: String, throwable: Throwable? = null)
}

class CrashReporterBreadcrumbSink(
    private val reporter: CrashReporter,
) : BreadcrumbSink {
    override fun breadcrumb(level: String, tag: String, message: String, throwable: Throwable?) {
        reporter.addBreadcrumb("[$tag] $message", category = level)
        if (throwable != null) reporter.recordException(throwable, mapOf("tag" to tag))
    }
}
```

Route `warn` and `error` messages through the bridge when the project wants crash context.

---

## Silencing Logs in Tests

Keep tests quiet by injecting a no-op logger or by configuring the test backend to suppress
output. Do not use production logging configuration in commonTest.

---

## Related Skills

- `kotlin-multiplatform-feature-scaffold` - logger factory lives in `:core:common`
- `kotlin-multiplatform-unit-testing` - use a quiet test logger or no-op sink in `commonTest`
- `kotlin-multiplatform-dependency-injection` - Koin wiring for the logger factory
- `kotlin-multiplatform-crash-reporting` - breadcrumb bridge for crash reports

---

## Testing

Test your own logging adapter or crash bridge rather than the logging library itself:

```kotlin
class RecordingBreadcrumbSink : BreadcrumbSink {
    data class Entry(val level: String, val tag: String, val message: String)
    val entries = mutableListOf<Entry>()

    override fun breadcrumb(level: String, tag: String, message: String, throwable: Throwable?) {
        entries += Entry(level, tag, message)
    }
}
```

Verify that `warn` and `error` paths produce breadcrumbs, and that quiet-test configuration
does not leak production output into unit tests.

---

## Common Anti-Patterns

- constructing loggers inside tight loops - create them once and inject them
- using `println` or `System.out.println` for debug output - keep a real logger facade
- logging secrets or tokens - redact sensitive values before emitting them
- enabling verbose logging in release builds - it creates noise and hides signal
- coupling feature modules directly to crash SDK APIs - keep the bridge in infrastructure

If logs are not appearing where expected, check the selected kotlin-logging artifact for
that target and make sure the logger factory is wired before feature code executes.

---

## Output Style

When asked about logging in KMP, respond in this order:
1. Gradle dependency (toml + convention plugin)
2. logger creation in shared code
3. log level guidelines
4. Koin injection pattern (factory with tag/name)
5. crash breadcrumb bridge if the project needs crash context

---

## Changelog

| Date | Change |
|---|---|
| 2026-06-24 | Supported both kotlin-logging and Kermit, with a single-facade rule and shared breadcrumb bridge guidance. |
