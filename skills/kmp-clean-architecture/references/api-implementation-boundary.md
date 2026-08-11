# API/Implementation Boundary

Part of `kmp-clean-architecture`.

---

`internal` (Internal Visibility Rules, above) controls encapsulation *within* a module's
Kotlin source. This section controls the layer below that: which dependencies a module
declares with Gradle's `api` vs `implementation` configuration, and why getting it wrong
is a real compile-time correctness bug, not a style nit.

## The Rule

**Default to `implementation()`. Use `api()` only when this module's own public
declarations expose the dependency's types.**

Real Gradle semantics for the Kotlin/Java plugins' `api`/`implementation` configurations:

- **`implementation(dep)`** — `dep` is on this module's own compile and runtime
  classpath, but is **not** exposed to anything that depends on this module. A change to
  `dep`'s ABI only forces *this* module to recompile — not every consumer, transitively.
- **`api(dep)`** — `dep` is on this module's classpath **and** transitively exposed to
  every module that depends on this one. A change to `dep`'s ABI forces every consumer,
  all the way up the graph, to recompile too.

Decision rule: does any non-`internal` function or property signature in this module
return, accept, or extend a type from `dep`? Yes → `api(dep)` — a caller needs `dep`'s
type on *its own* classpath just to name the value it gets back; `implementation()`
would compile fine here locally but break the caller with a confusing "class X is not on
the classpath, though it is referenced" diagnostic. No → `implementation(dep)`, the
narrower default — same "narrowest that works" principle `kmp-code-quality`'s extension
visibility rule applies at the Kotlin level; this is the same discipline one layer down,
at the Gradle-configuration level.

## Real Example — Verified Against `kmp-feature-scaffold`'s Own Templates

The generated templates already get this right; nothing until now explained *why*, so a
later manual edit has no rule to check against:

```kotlin
// :feature:auth:api/build.gradle.kts — api(), correct
kotlin {
    sourceSets {
        commonMain.dependencies {
            api(projects.feature.auth.model)
            // AuthRepository's methods return/accept :model types (User, AuthError) —
            // a consumer calling repository.login() needs those types on its own
            // classpath to even hold the return value. implementation() here would
            // compile this module fine and break every real caller.
        }
    }
}
```

```kotlin
// :feature:auth:domain/build.gradle.kts — implementation(), correct
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(projects.feature.auth.api)
            // :domain calls AuthRepository, but :domain's OWN public surface (use
            // case classes) doesn't re-expose AuthRepository itself. The :model
            // types that DO flow through are already api()'d one layer down by
            // :api, so they stay transitively visible without :domain needing
            // api() too.
        }
    }
}
```

## ABI/Type Leakage — the Bug This Prevents

Get the choice backwards and the mistake is invisible at its own source: the module
using `implementation()` for a dependency it secretly needs to expose **compiles fine
locally**, because `implementation()` still puts the dependency on that module's own
classpath. The break only appears in a *consumer* module, often much later, in a
different part of the codebase, as a confusing missing-classpath error — not a clear
"you scoped this wrong" message pointing at the actual mistake. This is why the
decision rule above needs to be applied at the moment a dependency line is written, not
diagnosed after the fact from a downstream stack trace.

## Consumer Compile Fixtures

A structural way to catch a wrong `api()`/`implementation()` choice in CI, before a real
downstream team hits it: a small, dedicated fixture module that depends on the target
module exactly the way a real consumer would — nothing more — containing minimal,
realistic usage code that exercises the target's public surface.

```kotlin
// :feature:auth:consumer-fixture/build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(projects.feature.auth.api)  // exactly what a real
                                                          // consumer depends on,
                                                          // nothing extra
        }
    }
}
```

```kotlin
// :feature:auth:consumer-fixture/src/commonTest/kotlin/AuthApiConsumerFixtureTest.kt
// Exercises :feature:auth:api's public surface exactly as a real caller would.
// If this fails to compile, the api()/implementation() config on :feature:auth:api
// (or :model) is wrong — caught here, in CI, not by a real team hitting a
// classpath error weeks later.
class AuthApiConsumerFixtureTest {
    @Test
    fun repositoryContractIsFullyUsable() {
        val repo: AuthRepository = TODO()
        val user: User = TODO()          // only compiles if :model types are api()'d
                                           // transitively through :feature:auth:api
    }
}
```

This is the same discipline `kmp-library-publishing`'s "smoke-test a local consumer
resolves the published artifact" applies at the *publishing* boundary — a consumer
fixture applies it one level earlier, inside the same monorepo, at every internal
module boundary that matters, not only the final published one.

## Facade Scopes — Naming an Existing Pattern

The Internal Visibility Rules table's `:data` row above (only the DI module value is
public; every implementation class is `internal`) is already a facade scope: a narrow,
deliberately curated public surface hiding a wide, changeable set of internals.
Generalize it anywhere a layer's internals are volatile but its contract needs to stay
stable — the facade's own declarations get `api()`'d by whatever exposes them further
up, and everything it hides stays `internal` with its own dependencies scoped
`implementation()` so they can never leak through by accident. A facade scope is what
makes "default to `implementation()`" safe in practice: without one, a module
accumulates public surface by accident, because nothing forced a deliberate decision
about what was actually meant to be exposed.

## Dependency-Cycle Checks

Already covered by the Fitness Functions section above — `kmp-audit`'s
`_detect_module_layer_violation` is the mechanical check. A literal circular dependency
can't happen silently in the first place (Gradle refuses to build a real cycle); the
real, previously-uncaught gap that detector closes is a wrong-*direction* one-way
dependency, which Gradle allows fine and nothing else catches. Nothing new needed here
— cross-referenced, not duplicated.
