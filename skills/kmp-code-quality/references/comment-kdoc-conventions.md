# Comment & KDoc Conventions

Part of `kmp-code-quality`. Load this file when working on: comment & kdoc conventions.

---

Kotlin-specific — for the C++/CPP side of a JNI or Kotlin/Native bridge (header
declaration vs `.cpp`/`.mm` implementation comments), see `kmp-native-authoring`'s
"Header vs implementation comments" section. Same underlying principle (declaration =
what a caller needs, implementation = what a maintainer needs), different syntax.

### Whether to write a comment at all

Ask in this order — stop at the first "yes":

1. **Does removing it lose zero information?** (the code/naming already says it) — don't
   write it. This is the single most common comment mistake: narrating WHAT instead of
   explaining WHY.
2. **Is it a public API contract another module or consumer relies on** (parameters,
   return value, thrown errors, a receiver precondition)? — KDoc `/** */`.
3. **Is it a non-obvious WHY** — a workaround, a constraint from outside this file, a
   reason simplifying this would break something? — single-line `//`.
4. Otherwise — don't write it. A comment that answers neither "what's the contract"
   nor "why is this not the obvious way" isn't pulling its weight.

**A single-line addition (one dependency declaration, one config value, one import)
almost never earns a comment**, even when the reasoning behind it is real and non-obvious.
Put that reasoning in the commit message — it's discoverable via `git blame` exactly when
someone needs it (touching that line), and doesn't sit in the file forever for every
reader who doesn't. The one exception: a gotcha a future maintainer will independently
re-trip on regardless of how they got there (a platform quirk, a version pin that looks
removable but isn't) — that earns a single terse line, not a paragraph.

**Watch for a WHY-shaped comment that's actually a leftover justification trail.** A
genuine WHY comment states a fact a future reader needs and stops — it doesn't defend the
choice. Tell: does it argue for the decision ("despite the name", "isn't just X", "to be
clear") the way you'd explain it to a reviewer mid-PR, rather than simply stating the
constraint to someone who already trusts the line works? That defensive tone is the
signal it's process narration that survived into the file, not documentation the codebase
needs. Cut it to the one sentence a maintainer actually needs, or drop it into the commit
message instead. `kmp-audit`'s `_detect_justification_comment_above_single_statement`
catches the mechanical shape of this (a 3+ line comment directly above one dependency
line in a Gradle build file) — but the tone test above is what to apply by hand, since it
generalizes past Gradle files.

**Write it the way you'd explain it to a teammate, not a textbook.** A comment that
translates the code into formal prose ("this function is responsible for validating
the user's email address in order to ensure it conforms to the expected format") reads
as robotic — a developer explaining the same thing out loud wouldn't reach for "is
responsible for" or "in order to." Plain words, or don't write it (per the WHAT test
above — that example says nothing the name doesn't already say):

```kotlin
// ❌ Robotic — textbook prose that says nothing the name doesn't
// This function is responsible for validating the user's email address
// in order to ensure it conforms to the expected format.
fun isValidEmail(email: String): Boolean = EMAIL_REGEX.matches(email)

// ✓ Name already says it — no comment needed
fun isValidEmail(email: String): Boolean = EMAIL_REGEX.matches(email)
```

`kmp-audit`'s `_detect_robotic_comment_phrase` catches a fixed list of formal openers
("is responsible for", "this class is used to", plus `kmp-project-docs-maintainer`'s
Writing Style hedge phrases — "in order to," "it should be noted that") in `//` and
KDoc comments — the same regex-safe, low-false-positive treatment as
`_detect_hedging_language`, applied to code comments instead of markdown docs.

**State the finding, not the investigation.** A comment walking through how a bug was
tracked down ("investigated: checked X first, ruled it out, turned out to be Y"), or
quoting an issue/bug-report's own prose verbatim, isn't what a reader needs — they need
the current fact the investigation ended on, not the path taken to find it. `TODO:`/
`FIXME:` are the one exception: readers already know that convention, and a linked
tracked issue for real deferred work is genuinely useful, not narration (see TODO/FIXME
below) — this rule is about prose that recounts the *process*, not a pointer to
follow-up work.

```kotlin
// ❌ narrates the investigation — a reader needs the fact, not the journey
// Investigated: first checked if it was a race condition, ruled that out. Then
// checked the retry logic, turned out the root cause was actually a stale cache
// entry. Bug report said: "app shows old data after reconnecting to wifi."
val cache = ExpiringCache(ttl = 30.seconds)

// ✓ states the fact the investigation ended on, nothing else
// 30s TTL — a longer cache silently served stale data across a network reconnect.
val cache = ExpiringCache(ttl = 30.seconds)
```

`kmp-audit`'s `_detect_investigation_narration_comment` catches a fixed list of
narration phrases ("investigated", "turned out to be", "root cause was", "steps to
reproduce") in `//` and KDoc comments — same regex-safe treatment as the robotic-phrase
and hedging checks above.

**Historical narration isn't a substitute for current purpose.** A comment describing
what code *used to be* or *how it got here* ("previously used LiveData", "migrated
from X in 2024", "this used to throw NPE") is git log's job, not the file's. A reader
needs what the line does and why it's shaped this way *now* — not its backstory,
which means nothing without context the comment doesn't provide either. If the current
shape has a real reason, state that reason directly, in one `//` line; drop the
"previously"/"migrated from" framing entirely.

```kotlin
// ❌ Narrates history — git log already has this
// Previously used LiveData, migrated to StateFlow in the 2024 refactor
val state: StateFlow<UiState> = ...

// ✓ States the current constraint, no history, one line
// Cold by default — a late collector sees nothing until the next update; call .value for the current snapshot.
val state: StateFlow<UiState> = ...
```

**Attribution comments need confirmation first — never added silently.** A comment
naming a *source* ("suggested by kmp-audit," a mode's own tag prefix, "per code
review") isn't the same as one stating a *fact*. It answers who said so, not why the
code is this way — a different failure than the justification trail above, and it
rots the same way a task reference does: the source stops mattering the moment context
changes.

Rule: before adding one, ask the user first (`AskUserQuestion`, or name the line and
get explicit go-ahead). No exceptions for a format built to carry real content, like a
tagged convention documenting a genuine limitation — the gate is on adding *this
instance*, not on whether the convention itself is legitimate.

```kotlin
// ❌ Attribution — cites a source, not a fact
// suggested by kmp-audit
val cache = mutableMapOf<String, User>()

// ❌ Still attribution, even in a tagged-convention format
// mode-tag: shortcut taken here
val cache = mutableMapOf<String, User>()

// ✓ Real WHY — states the fact, cites no source
// Global lock, not per-account — fine at current throughput; revisit if
// concurrent writes start queuing.
val cache = mutableMapOf<String, User>()
```

**A per-instance confirmation gate doesn't stop a mode from adding many, fast.** Real
case: a ponytail-mode session (its own `ponytail:` tag is legitimate WHY content by
design, not attribution — see above) added 40 of them across one work session, no
single instance wrong, but the total reads as noise. The per-instance gate is a
real-time behavioral rule an in-context mode can simply not apply; it isn't
mechanically enforceable after the fact. What *is* checkable after the fact is
density — `kmp-audit`'s `_detect_ponytail_comment_density` flags a project
accumulating 20+ `ponytail:` comments total (not per-file — the real case spread
thin, max 2 in any one file, so a per-file threshold would have caught none of it) as
a nudge to review the backlog, not a claim any individual tag is wrong.

**A process never gets one `//` per step — one line total, or zero.** This is broader
than the Inline blocks rule below: that one is scoped to loops/conditionals, this covers
*any* sequence of plain statements. Two shapes, same failure:

- **Interleaved**: a `//` naming each step sits above its own call, repeated down the
  function (`// 1. validate` / `validate()` / `// 2. log in` / `login()`). If the calls
  are already named for what they do, the numbering adds nothing top-to-bottom order
  doesn't already give a reader — delete every line.
- **Stacked, no code at all**: a function body that's *only* comments, each naming a step
  of an intended implementation, with nothing actually implemented. This isn't a
  documentation problem, it's an unimplemented stub wearing documentation as a disguise —
  collapse to one `TODO:` with a tracked issue (see TODO/FIXME below), not a checklist.

```kotlin
// ❌ interleaved — each call already says what it does; the steps add nothing
// 1. validate the form
validate()
// 2. then log in
login()

// ✓ names already say it
validate()
login()

// ❌ stacked, zero real code — a checklist standing in for an implementation
override fun recordCommand(encoder: CommandEncoder) {
    // Begin Shadow Render Pass
    // Bind basic shadow-casting pipeline
    // Render mesh positions only
    // End Render Pass
}

// ✓ one line, honest about being unimplemented, actually tracked
override fun recordCommand(encoder: CommandEncoder) {
    // TODO: github.com/org/repo/issues/123 - implement shadow pass
}
```

Distinct from a long stacked `//` block explaining one genuine WHY (the "Grows past
~4 lines" row in the table below, and `_detect_long_stacked_comment_block`'s WHY-signal
exemption) — that's one continuous explanation that happens to need several lines. This
is *N separate WHAT statements*, one per step; even two of them side by side is already
the anti-pattern, length isn't what makes it wrong.

Two comment types, two jobs — never mix them:

| | Single-line `//` | Multi-line `/** ... */` (KDoc) |
|---|---|---|
| Documents | Internal WHY — a workaround, a non-obvious constraint | Public API contract — `@param`/`@return`/`@throws`/`@sample` |
| Never used for | Restating WHAT the code does (good naming covers that) | Private members — rename instead (Detekt's `DocumentationOverPrivateFunction`/`Property` flags this) |
| Visible to | Nobody outside the source file | Dokka + IDE quick-docs |
| Grows past ~4 lines? | Split: keep the one-sentence WHY inline, move the rest to `docs/reference/` with a pointer comment (see below) — mechanically checked by `kmp-audit`'s `_detect_long_stacked_comment_block` (5+ consecutive `//` lines, no `docs/reference/` pointer, not a leading license header, not a block reading as genuine WHY — see that detector's own docs for the signal-word heuristic) | N/A — KDoc doesn't accumulate this way; if a class needs paragraphs, that's what `docs/reference/` is for too |
| Nests? | N/A | KDoc does **not** nest. Plain block comments (`/* */`) do, unlike Java/C |

### Formatting

Verified against Kotlin's own official coding conventions (kotlinlang.org), not invented:

- **`//`**: exactly one space after the slashes — `// like this`, not `//like this`.
- **KDoc, short**: a single line is fine when the whole comment fits — `/** This is a short documentation comment. */`. Don't force a one-sentence KDoc onto three lines for symmetry.
- **KDoc, long**: opening `/**` alone on its own line, every following line starts with a single space then `*`, closing `*/` alone on its own line:
  ```kotlin
  /**
   * This is a documentation comment
   * on multiple lines.
   */
  ```
- **`@param`/`@return`**: the official guidance is to *avoid* these tags generally —
  weave the parameter/return description into the main text instead, with `[paramName]`
  links wherever it's mentioned, and use `@param`/`@return` only when the description is
  long enough that it doesn't fit the flow of the prose. This repo's own tag table below
  lists them as available tags, not as the default shape every KDoc should take.
- **Coverage is all-or-nothing, never partial.** The choice above is about *form*
  (inline `[name]` vs an `@param` tag), never about which parameters get addressed at
  all. If a function has 3 parameters and the KDoc documents 1 of them, that's a real
  defect — either say something about all 3 (mixing inline mentions and `@param` tags on
  the same declaration is fine) or write a plain single-line summary with no parameter
  detail at all. A KDoc block that looks thorough but silently skips 2 of 3 parameters is
  worse than no KDoc — it reads as complete and isn't. `kmp-audit`'s
  `_detect_partial_param_documentation` catches this mechanically.
- **KDoc supports Markdown** — verified against kotlinlang.org, not assumed. Inline markup
  inside `/** */` is regular Markdown (bold/italic, lists, links), plus a KDoc-specific
  shorthand for linking to another declaration:
  ```kotlin
  /**
   * Wraps [HttpClient] with retry logic. Use [retryPipeline] instead of calling this
   * directly — see [this][GROUP_ID.core.network.NetworkResult] for the result shape.
   *
   * - Retries transient failures up to `times`
   * - Never retries a 4xx response
   */
  ```
  `[declaration]` resolves the same way a reference inside the documented element would —
  no full qualification needed if it's already imported in the file. A fenced code block
  (` ``` `) works too, for a short usage snippet that doesn't warrant a full `@sample`.
- **Never leave a referenced class, function, or property as raw text.** Wrap it in
  `[Brackets]` (or fully-qualified `[com.example.Client]` for a type outside the file)
  every time a KDoc mentions another declaration by name — the whole point of the
  Markdown support above is a Dokka-generated cross-link; plain text loses it silently,
  with no compiler warning to catch the omission.
- **Backtick a literal, value, or parameter name mentioned in prose** — `` `null` ``,
  `` `true` ``, `` `timeoutMillis` `` — same reasoning as code fences: it's a value, not
  English prose, and backticks are how Markdown (and this repo's own KDoc) already marks
  that distinction everywhere else.

### By architectural level

The table above sorts by comment *type*; this sorts by *where in the code* it lives —
use both together when reviewing or refactoring documentation.

| Level | Rule |
|---|---|
| Classes & interfaces | KDoc states the class's responsibility and architectural role only. Skip trivial openers ("Represents a X") — say what it owns and why it exists as a separate type, not what its name already tells you. |
| Functions & methods | KDoc only for complex public members, using the tag table below. Document inputs, outputs, and edge cases — never mechanics. `UndocumentedPublicFunction` requires *something*, so trivial one-liners (a getter, a pure delegate) get a single sentence, not a full `@param` breakdown. |
| Extension functions | State the receiver scope and calling context — *when* to reach for this extension, not just what it returns. Use `@receiver` for any precondition the receiver must satisfy (e.g. "must be called from inside an active `viewModelScope`"). This is the one KDoc case where "when to use it" outranks "what it does," because the same signature can exist as a member on an unrelated type. |
| Inline blocks (loops, conditionals) | No `//` that explains WHAT a block does — extract a named function or variable so the code reads as its own explanation. Keep `//` only for a non-obvious workaround or a business-logic WHY. |
| Sealed classes/interfaces & enums | KDoc the parent type for what the whole closed set represents, then a one-line KDoc per variant for what specifically distinguishes *that* case — never a blanket comment above the whole `when` a caller writes elsewhere. |

```kotlin
/**
 * Retries [block] with exponential backoff, but only while this scope's job is active.
 * @receiver Must be a scope tied to a UI lifecycle (e.g. `viewModelScope`) — cancels
 * in-flight retries when the receiver is cancelled instead of leaking a delay loop.
 */
suspend fun <T> CoroutineScope.retryWhileActive(times: Int, block: suspend () -> T): T { ... }
```

```kotlin
/** Outcome of a [retryWhileActive] call — exactly one of these per attempt. */
sealed interface RetryOutcome {
    /** [block] returned normally within the retry budget. */
    data class Success(val value: Any?) : RetryOutcome

    /** Every retry attempt failed; [cause] is the last exception thrown. */
    data class ExhaustedRetries(val cause: Throwable) : RetryOutcome

    /** The enclosing [CoroutineScope] was cancelled before [block] could complete. */
    data object Cancelled : RetryOutcome
}
```

### Two real mistakes this caught

**A `//` on the same line as code can swallow what follows it** — it runs to end-of-line,
including a needed closing `)`/`{`. Shipped in `kmp-imagevector-generator`'s
own codegen until a test caught it:

```kotlin
// ❌ WRONG — the // comments out the rest of the line, including `) {`
path(fill = SolidColor(Color.Black)  // tint at call site) {

// ✅ CORRECT — the call is syntactically complete before the comment starts
path(fill = SolidColor(Color.Black)) {  // tint at call site
```

**A `//` block that keeps growing is a sign two audiences got merged into one comment.**
Keep only the sentence that answers "why would someone break this by simplifying it?" —
one `//` line, not a paragraph — and move everything else (mechanism detail, rejected
alternatives, exact version numbers) to `docs/reference/` (the lane
`kmp-project-docs-maintainer` already defines for deep references), with a one-line
pointer left behind. Two lines total, not four — if the WHY sentence itself doesn't fit
one line, that's the signal the detail belongs in `docs/reference/` too, not a second or
third `//` line in the file:

```kotlin
// Composite build, not include() — needs 1.12.0-beta01, newer than root's 1.11.1 pin.
// Full rationale: docs/reference/composite-build-style-experimental.md
includeBuild("tailwind/style-experimental")
```

**Genuinely delicate code puts the pointer first, not last.** The ordering above is
right for the common case — the one-line summary already tells a reader enough, the
`docs/reference/` link is there if they want more. Reserve pointer-first for the rare
case where the risk is different in kind: correctness depends on a non-obvious
invariant that neither the type system nor a quick read of the function catches, and an
agent (or a person) confident enough to "simplify" it would silently reintroduce a real
bug — exact statement ordering for a hardware/driver timing reason, a workaround for a
specific upstream bug where the obvious fix brings it back. Putting the pointer first
means whoever's about to edit hits "read this before touching it" before they've formed
an opinion about the code, not after:

```kotlin
// Read docs/reference/retry-backoff-invariants.md before touching this function.
// Reordering these three lines reintroduces the double-fire bug from #482.
fun retryWithBackoff(attempt: Int): Duration { ... }
```

Don't reach for this ordering by default — it reads as an alarm, and an alarm that
fires on ordinary code stops meaning anything. It's for the specific case above, not a
substitute for a normal WHY comment on code that's merely a little subtle.

### KDoc: code definition, params, samples

| Tag | Purpose |
|---|---|
| `@param` | Official guidance: avoid — describe the parameter inline in the main text with a `[name]` link instead. Reach for `@param` only when that description is too long to weave into the flow |
| `@return` | Same as `@param` — inline by default, tag only for a lengthy description. Skip entirely for `Unit` |
| `@throws` | A failure mode that's part of the contract, not every possible exception |
| `@see` | Cross-reference to a related declaration |
| `@sample` | Points at an actual, compiled function elsewhere as the usage example |
| `@property` / `@receiver` / `@constructor` | Constructor property / extension receiver / primary constructor, documented separately from the class summary |
| `@suppress` | Hides a technically-public declaration from generated docs |

**There is no `@deprecated` KDoc tag** — verified against kotlinlang.org's KDoc
reference, which states this explicitly. Use the `@Deprecated` compiler annotation
instead; it's already the mechanism this repo's `deprecated` code-tier maps to (see
`kotlin-library-pattern-choices.md`'s Code categorization section), and unlike a doc
tag it actually produces a compiler warning at every call site, not just a
documentation note nobody sees until they open the generated docs.

**An example is warranted only when usage isn't obvious from the signature** (a builder, a
DSL) — never required per function or per file, same "why not what" rule as `//`. When one
is warranted, use `@sample`, not a pasted code block: it points at a real compiled
function, so it's type-checked and can't silently drift stale.

**When more than one tag is used on the same declaration, the required order is**
`@constructor`, `@receiver`, `@param`, `@property`, `@return`, `@throws`, `@see` — per the
[Android Kotlin style guide](https://developer.android.com/kotlin/style-guide)'s Block
tags rule. A tag never appears with an empty description; skip it entirely instead.

```kotlin
/**
 * Builds a [Result] pipeline that retries on transient failures.
 * @sample GROUP_ID.samples.retryPipelineSample
 */
fun <T> retryPipeline(times: Int, block: suspend () -> T): Flow<T> { ... }
```

Module/package-level docs (describing a whole module, not one declaration) are a separate
Dokka mechanism — `Module.md`/`Package.md` — not a KDoc tag.

### Detekt enforcement

```yaml
comments:
  UndocumentedPublicClass:
    active: true
    excludes: ['**/test/**', '**/*Test.kt', '**/*Preview*']
  UndocumentedPublicFunction:
    active: true
    excludes: ['**/test/**', '**/*Test.kt', '**/*Preview*']
  UndocumentedPublicProperty:
    active: true
    excludes: ['**/test/**', '**/*Test.kt', '**/*Preview*']
  DocumentationOverPrivateFunction:
    active: true
  DocumentationOverPrivateProperty:
    active: true
  OutdatedDocumentation:
    active: true
```

`UndocumentedPublic*` requires KDoc on every public declaration; `DocumentationOverPrivate*`
forbids it on private ones; `OutdatedDocumentation` catches KDoc whose `@param`/signature
no longer matches the declaration after a refactor.

**`UndocumentedPublicProperty` is easy to leave out and was** — this block enabled only
the `Class` and `Function` variants while the sentence above claimed "every public
declaration", and `kmp-audit`'s `_detect_undocumented_public_api` backstop matched only
`class`/`interface`/`object`/`fun` too. A public `val` on a library's API surface was
covered by neither. Both now include properties. It matters most under `explicitApi()`,
where a public property is a permanent part of the published surface that
`binary-compatibility-validator` will track whether or not anyone documented it.

### TODO / FIXME — deferred work, not a substitute for tracking it

Verified against Google's Java Style Guide §4.8.6.2 (the real, commonly-cited source for
this format, still applicable to Kotlin — kotlinlang.org's own conventions don't cover
it) and IntelliJ/Android Studio's built-in TODO tool window, which recognizes `TODO` and
`FIXME` case-insensitively by default:

```kotlin
// TODO: github.com/org/repo/issues/456 - remove once the upstream fix ships
// FIXME: github.com/org/repo/issues/789 - retry loop can spin forever on a 5xx
```

- Always a link to a tracked issue, never a bare name — Google's guide explicitly warns
  against using an individual's name as the only context; people leave, the comment
  outlives them.
- `TODO` = planned follow-up work; `FIXME` = known-broken code shipped anyway. Informal
  distinction — tooling treats both identically, so don't rely on the word alone to
  signal severity, say it in the note.
- **This is not where "known issues" documentation belongs.** A `TODO`/`FIXME` is a
  pointer to a tracked issue, not the issue's write-up — if there's no real issue behind
  it yet, that's the actual gap (file one, or use `kmp-project-docs-maintainer`'s
  `docs/bugs/` lane for an actively-worked one), not a long comment standing in for
  tracking.
- **Real gotcha, not a nice-to-have detail:** Detekt's `ForbiddenComment` rule (Style
  ruleset) is active by default and forbids the literal strings `TODO:`/`FIXME:`/
  `STOPSHIP:` outright — see `kotlin-library-pattern-choices.md`'s own section on this.
  It does not distinguish a linked, well-formed `TODO` from a bare one; both fail. A
  project that wants the format above to actually compile needs an `allowedPatterns`
  regex on that rule exempting lines that match it (e.g. a line containing an issue-
  tracker URL) — otherwise write the reasoning some other way (commit message, or the
  `docs/bugs/` lane) since the marker itself won't pass CI.

### License headers — situational, not a default

Per-file license headers were standard in the AOSP/Apache-Software-Foundation era and are
still worth it for **libraries redistributed externally** (Detekt ships
`AbsentOrWrongFileLicense`, off by default). Skip them for app code — redundant with the
root `LICENSE` file. See `kmp-library-publishing`'s "Per-file license
headers" for the rule config and template.

---

