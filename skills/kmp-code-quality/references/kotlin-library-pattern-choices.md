# Kotlin Library & Pattern Choices

Part of `kmp-code-quality`. Load this file when working on: kotlin library & pattern choices.

---

### `kotlin-reflect` — avoid in shared code

`kotlin-reflect` is a JVM-primary API — limited or absent on Kotlin/Native and Kotlin/JS,
and a real runtime/startup cost even on JVM. Never add it to `commonMain`'s dependencies;
if a `commonMain` file imports `kotlin.reflect.*` beyond the always-available `KClass`/
`::class` literal (full reflection: `memberProperties`, `KFunction.call`, etc.), that's a
signal the platform split was skipped, not a genuine cross-platform need.

- **Fine**: JVM-only modules (a Ktor server, a desktop-only feature) that already accept
  JVM as their sole target
- **Not fine**: reaching for reflection-based serialization or object inspection in
  shared code — use `kotlinx.serialization` instead, which code-generates via a compiler
  plugin and needs no runtime reflection on any platform
- `kmp-audit`'s `_detect_kotlin_reflect_in_common` catches full-reflection
  imports in `commonMain`

### Util/extension file organization

A single `Utils.kt`/`Helpers.kt`/`Extensions.kt` file accumulating unrelated top-level
functions across different domains (string formatting next to date math next to network
retry logic) is a real smell — the file has no single responsibility, and nothing about
its name tells a reader what's actually inside. Split by what the functions are *for*:
`StringExtensions.kt`, `DateExtensions.kt`, or move the function into the module that
owns the domain it touches. A file of extension functions all sharing the same receiver
type is fine and not what this flags — the smell is unrelated functions sharing only a
generic filename. `_detect_god_utils_file` flags a `*Utils.kt`/`*Helpers.kt` file with
10+ top-level functions spanning 3+ distinct (or no) receiver types.

### Regex readability

A regex used more than once, or complex enough to need explaining, must be bound to a
well-named constant — never inlined as a raw literal inside a function call:

```kotlin
// ❌ — unreadable inline, no name to signal intent, recompiled if hit in a hot path
if (Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$").matches(input)) { ... }

// ✓ — named, compiled once, self-documenting call site
private val EMAIL_RE = Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
if (EMAIL_RE.matches(input)) { ... }
```

For a pattern with 2+ capture groups, prefer named groups over positional ones — a caller
reading `match.groups["year"]` doesn't need to cross-reference the pattern to know what
`match.groupValues[2]` means. Add a one-line WHY comment above any pattern using
lookaheads/lookbehinds or non-obvious escaping — what it matches should not require
mentally executing the regex. `_detect_inline_unnamed_regex` flags a `Regex(...)`/
`toRegex()` call inlined directly as a function-call argument instead of bound to a
`val`.

### Performance killers — Detekt's Performance ruleset, plus two real gaps it doesn't cover

Verified against Detekt's own docs before writing this: enable its **Performance**
ruleset (8 real rules) in `detekt.yml` alongside the sections in Detekt Setup above —
`ArrayPrimitive`, `CouldBeSequence`, `ForEachOnRange`, `SpreadOperator`,
`UnnecessaryInitOnArray`, `UnnecessaryPartOfBinaryExpression`,
`UnnecessaryTemporaryInstantiation`, `UnnecessaryTypeCasting`. None of these cover an
object constructed inside a loop with no dependency on the loop variable — a real,
common killer Detekt's own ruleset doesn't check:

```kotlin
// ❌ — SimpleDateFormat rebuilt every iteration
for (item in items) {
    val fmt = SimpleDateFormat("yyyy-MM-dd")
    results.add(fmt.format(item))
}

// ✓ — built once, before the loop
val fmt = SimpleDateFormat("yyyy-MM-dd")
for (item in items) {
    results.add(fmt.format(item))
}
```

`kmp-audit`'s `_detect_object_creation_in_loop` flags a known-expensive
constructor (`SimpleDateFormat`, `DateTimeFormatter`, `HttpClient`, `MessageDigest`,
`Gson`, `ObjectMapper`) built inside a `for`/`while` body whose arguments don't
reference the loop variable — a legitimate per-item construction (the constructor
genuinely uses the loop variable) is not flagged.

### Public mutable collection exposure

Distinct from the Compose-only unstable-collection-param check above — this is an
encapsulation concern, not a recomposition one. A public `MutableList`/`MutableMap`/
`MutableSet` property or return type lets any caller mutate your internal state through
the reference, regardless of whether Compose is involved at all:

```kotlin
// ❌ — a caller can add/remove/clear through this reference
class ItemStore {
    val items: MutableList<Item> = mutableListOf()
}

// ✓ — read-only surface, backed by a private mutable copy
class ItemStore {
    private val _items = mutableListOf<Item>()
    val items: List<Item> get() = _items
}
```

Especially relevant on an `explicitApi()` library's public surface, where this becomes
a permanent part of the contract. `_detect_public_mutable_collection` flags a
non-`private`/non-`internal` declaration exposing a `Mutable*` type directly.

### Android Context/Activity leak in a singleton

The classic Android memory leak: a `companion object` or singleton `object` caching a
`Context`/`Activity` reference. The singleton outlives the Activity, so the reference
prevents garbage collection for the process's whole lifetime — a real leak, not a style
nit. `applicationContext` (or an `Application` type) is the one safe exception — it
already lives for the process, so caching it long-term is fine:

```kotlin
// ❌ — leaks the Activity every time a new one is created
class SessionManager {
    companion object {
        var activity: Activity? = null
    }
}

// ✓ — application context is safe to hold long-term
class SessionManager {
    companion object {
        lateinit var appContext: Context  // set once, from Application.onCreate() with applicationContext
    }
}
```

Applies equally to a KMP library's Android `actual` implementation and an app —
`_detect_context_leak_in_singleton` scans both, no project-type gating.
`_detect_context_leak_in_singleton` flags a `Context`/`Activity`/`FragmentActivity`/
`AppCompatActivity`/`ComponentActivity`-typed property inside a `companion object`/
singleton scope.

### `TODO`/`FIXME` — already flagged, verify it's not silently off

Detekt's own `ForbiddenComment` rule (Style ruleset) flags `TODO:`/`FIXME:`/`STOPSHIP:`
comments **by default, active since Detekt 1.0.0** — verified against Detekt's own
docs, not assumed. Because this skill's `detekt.yml` uses `buildUponDefaultConfig =
true`, that default stays active automatically; nothing extra to enable. Worth stating
explicitly here since it was otherwise invisible — a project could have this running
the whole time with no one aware of it. Only touch it if you want to customize the
prefix list or add `allowedPatterns` exceptions.

### Patch-up fix instead of root-cause fix (hints)

"Is this a real fix or a band-aid" is a judgment call — but two specific, well-known
shapes of the pattern are mechanically detectable, as non-blocking hints (same tier as
the naming hints above):

- **Empty or log-only catch block** — silences the symptom without addressing why the
  exception was thrown. A deliberate best-effort no-op is sometimes genuinely correct
  (rare), so this stays a hint, not a blocker.
- **`@Suppress("Rule")` with no nearby comment** explaining why it's a false positive
  vs. silencing a real finding — legitimate suppressions are common, the missing
  justification is the actual signal, not the suppression itself.

```kotlin
// ❌ — hint fires: swallows the exception, no comment explaining why
try {
    risky()
} catch (e: Exception) {
}

// ✓ — real recovery, not flagged
try {
    risky()
} catch (e: IOException) {
    retryWithBackoff()
    logFailure(e)
}
```

A `TODO`/`FIXME` found in or near the flagged block is corroborating evidence, not a
requirement to fire — `_detect_empty_catch_block` and `_detect_unjustified_suppress`
both note it in the finding text when present, since a "TODO: fix properly" sitting
right next to the patch is a strong tell it's a known gap, not a considered decision.

---

