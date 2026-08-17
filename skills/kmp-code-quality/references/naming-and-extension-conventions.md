# Naming & Extension Conventions

Part of `kmp-code-quality`. Load this file when working on: naming & extension conventions.

---

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

A dedicated `*Extensions.kt` file is the right call for a **third-party or stdlib type**
you don't own the source of (`String`, `List<T>`) — there's no class file to put it in.
For a type **this project owns**, Kotlin's own coding conventions are more specific and
worth following exactly: an extension relevant to every caller of that class belongs in
the *same file as the class itself*, not a separate extensions file; an extension that
only makes sense for one specific caller belongs next to that caller's code instead.
"Avoid creating files just to hold all extensions of some class" (verified,
[kotlinlang.org/docs/coding-conventions.html](https://kotlinlang.org/docs/coding-conventions.html)).

### Extension functions — when to reach for one, and when not to

Verified against [kotlinlang.org/docs/extensions.html](https://kotlinlang.org/docs/extensions.html)
and [kotlinlang.org/docs/coding-conventions.html](https://kotlinlang.org/docs/coding-conventions.html).
An extension adds a callable function/property to a type you don't own, or don't want to
put a method directly on — dot-notation syntax, but resolved at compile time, not a real
member. Kotlin's own conventions endorse this liberally: "every time you have a function
that works primarily on an object, consider making it an extension function accepting
that object as a receiver" — but pair that with the visibility default below, or
"liberally" becomes public-API sprawl.

**Extensions are syntax. The receiver type and module dependency graph are the
architecture.** An extension only decides how a call *reads* — dot-notation sugar over
what's really a static top-level function. It grants no special access and enforces no
boundary by itself. Use extensions to build declarative, fluent vocabulary for a
domain — not just UI builders; a network-request DSL, a test-assertion DSL, a config
DSL are the same pattern. Use a narrow receiver type plus the module boundary
(`internal`, or simply which module declares the extension) to control what that
vocabulary is actually allowed to touch. A `public` extension on a broad receiver type
(`Any`, `String`) declared in a widely-depended-on module is unrestricted API surface no
matter how nicely it reads — the fix is always narrower receiver + narrower visibility,
never "write a better-named extension."

**Default to the narrowest visibility that works** — local (inside the function that uses
it) or `private` member/top-level, widening to `internal` or `public` only once a second,
real caller needs it. Kotlin's own conventions frame this explicitly as minimizing API
pollution, not just a style preference.

**Reach for an extension when:**
- Extending a type you can't modify — a third-party or stdlib type (`String`, `List<T>`,
  a platform SDK type)
- A pure utility that reads naturally as `receiver.doThing()` — check the stdlib first
  (`.map()`, `.filter()`, `.fold()`) before writing a new one
- A computed property with no backing state — `val User.displayName: String get() = ...`
- Building a DSL — see the DSL section below; scoped extension receivers are what make a
  type-safe builder's inner block feel like part of the type it's building

**Don't reach for an extension when:**
- **You need runtime polymorphism.** This is the pitfall that actually bites — extension
  functions are resolved **statically**, by the variable's *declared* type, not the
  object's *runtime* type. A member function overriding a base class dispatches
  correctly; an extension "overriding" one does not:

  ```kotlin
  fun Shape.describe() = "a shape"
  fun Rectangle.describe() = "a rectangle"   // NOT an override — a separate function

  fun printIt(s: Shape) = println(s.describe())

  printIt(Rectangle())   // prints "a shape" — resolved by the *declared* type Shape,
                          // not the real Rectangle instance. A member function would
                          // have printed "a rectangle".
  ```

  If a caller genuinely needs different behavior per subtype through a shared reference,
  that's a member function on the base type (or a `sealed class`/`when`), not an
  extension — no exception, this is the one case with a real correctness cost, not just
  a style preference.
- **The function needs private/protected access** to the type it's extending — extensions
  only see the public API, same as any other outside caller. Make it a member instead.
- **It's one of many `public` top-level extensions crowding a shared package** — the
  visibility default above is the fix; also prefer a narrower receiver type over a broad
  one (`fun JSONObject.toUserOrNull()` over a generic `fun Any.toUserOrNull()`).
- **State needs to be stored on the extended type.** Extension properties can't have a
  backing field or an initializer — `val Foo.cache: MutableMap<K, V> = mutableMapOf()`
  doesn't compile. Store the state elsewhere (an external map keyed by identity, or a
  real member on the type) if it's more than a computed read.

### God receiver — extension sprawl hides a type's real API

Mirror image of `_detect_god_utils_file` above: that one flags one *file* accumulating
unrelated receivers, this flags one *receiver* accumulating unrelated extensions across
many files. A type like `Context`, a shared `AppScope`, or any widely-injected class can
end up with dozens of `public` extensions scattered across the codebase — a networking
extension here, an analytics extension there, a navigation extension somewhere else. Each
individual extension looks clean; the type as a whole becomes a god object whose real
capability set is invisible from its own declaration — nothing in the class file tells a
reader what it can do, only a repo-wide grep does.

**The fix is membership over extensions**: if a function represents core, always-available
behavior of the type — every caller needs it, it's part of the type's essential
contract — make it a member, not an extension. Reserve extensions for what the earlier
"Reach for an extension when" list actually describes: types you don't own, optional
convenience, narrow-context sugar. A function that's core behavior but written as an
extension anyway doesn't gain anything from the dot-notation syntax — it just moves the
declaration somewhere the type's own file doesn't advertise, for no benefit.

This is a judgment call, not something mechanically flagged today — an extension count
alone doesn't distinguish "this type has genuinely broad, well-organized sugar" from "this
type is being used as a service locator via extensions." Watch for it during review: if
understanding what a type can do requires searching the whole codebase instead of reading
one file, that's the signal, regardless of how many extensions triggered it.

### Verb chaos — one verb per operation, dialects banned

The same semantic operation picks up multiple verb spellings as a codebase grows —
`emit`, `paint`, and `draw` all meaning "paint this primitive," or `release`, `clear`,
`reset`, and `free` all meaning "give this resource back" — each one added by a different
author who didn't know the others existed. A reader can no longer tell from the verb alone
whether two functions do the same thing or different things; they have to read both bodies
to find out.

**Pick one verb per operation, then ban the others** — a rename, not a synonym war:

- **A verb prefix reserved for one layer must never leak above it.** If `render*` is the
  real GPU/backend boundary, a widget-authoring function named `renderBadge()` blurs where
  rendering actually happens — reserve the prefix for the boundary it names, not for
  "anything that eventually causes pixels."
- **`with*` means lambda-scoped, nothing else.** A function that takes a trailing lambda
  and scopes some effect around it (`withTransaction { ... }`) can use `with*`. A
  value-returning transform with no lambda (`fun Dimension.orFallback(fallback: Dimension):
  Dimension`) needs a noun/participle name instead — `with*` on a non-lambda signature reads
  like the wrong shape at the call site.
- **Disjoint passes get disjoint verbs.** In a multi-pass pipeline (layout, resolution,
  allocation, state), each pass should own one verb that never appears in another pass —
  `measure*` (a pass touching layout state), `resolve*` (pure input → output, no side
  effects), `claim*` (slot/resource allocation), `remember*` (a cross-frame state hook).
  The verb is the reader's only signal for which pass they're in; sharing a verb across
  passes erases that signal.
- **A `PascalCase` function name is its own dialect violation.** `fun ProvideRequestId(...)`
  reads as a type/constructor at the call site even though it's a plain function —
  `provideRequestId` is the only correct shape for something that isn't a class.

```kotlin
// ❌ three dialects for "add work to the queue," scattered across unrelated files
fun WorkQueue.pushJob(job: Job)
internal fun submitJob(job: Job)
fun Scheduler.enqueueJobEntry(job: Job)

// ✓ one verb, one receiver, members not scattered extensions
interface WorkQueue {
    fun enqueue(job: Job)
    fun enqueueAll(jobs: List<Job>)
}
```

Once the dialect is named, enforce it mechanically — a regex-based architecture-fitness
check per module (same technique as `kmp-clean-architecture`'s Detekt rules), banning the
losing verb(s) directly rather than relying on review to keep catching new instances:
`\bfun\s+\w*Queue\.(push|submit)[A-Z]`.

### Twin Nouns — one canonical name per concept, no aliases

Two types describing the same concept under different names — a `Job` and a `Task` both
modeling one unit of scheduled work, or a bare `Money` kept alive as a `typealias` for
`Amount` — force every caller to learn which one is "the real one." Once both exist, they
tend to drift independently: one gains a convenience member the other doesn't, and now
they're not even interchangeable anymore. The fix is deletion, not documentation — keep
exactly one name, migrate every call site in the same change, and remove the alias. A
`typealias` or duplicate type kept "for compat" with no removal plan is exactly the kind of
unreviewable drift `@Deprecated` without a `ReplaceWith` already flags elsewhere in this
file — same failure, different mechanism.

The same pattern shows up one level down as a **same-concept, different-suffix twin**: a
second, `Async`-suffixed entry point duplicating a function's own name instead of the
function itself taking a `suspend` lambda (`submitJobAsync()` living next to `submitJob()`).
The "async" call should just be a call to the function's own suspending form — a second name
for the same capability is a Twin Noun with a verb-shaped disguise, not a real second
capability.

Distinct from god receiver above: god receiver is one receiver accumulating *unrelated*
concepts; Twin Nouns is *one* concept accumulating multiple names. Not mechanically
detected by name alone (two types can share a suffix and be genuinely different) — the
signal is overlapping property/method sets under different names, which needs a read, not
a regex.

