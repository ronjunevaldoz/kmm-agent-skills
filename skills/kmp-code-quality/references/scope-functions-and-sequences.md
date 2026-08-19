# Scope Functions & Sequences

Part of `kmp-code-quality`. Load this file when working on: scope functions & sequences.

---

### Scope functions — `let`, `run`, `with`, `apply`, `also`

Verified against [kotlinlang.org/docs/scope-functions.html](https://kotlinlang.org/docs/scope-functions.html),
not assumed. Five functions, same basic job (execute a block on an object), differing
on exactly two axes:

| Function | Context object | Return value | Extension function? |
|---|---|---|---|
| `let` | `it` | Lambda result | Yes |
| `run` | `this` | Lambda result | Yes |
| `run` (no receiver) | — | Lambda result | No — called without a context object |
| `with` | `this` | Lambda result | No — takes the context object as an argument |
| `apply` | `this` | Context object | Yes |
| `also` | `it` | Context object | Yes |

**Pick by what the code needs, not by habit** — the two axes above map directly to a
real decision, not five interchangeable synonyms:

- **Executing a lambda on a non-null object, or introducing an expression as a local
  variable** → `let`. `it` reads better than `this` when the object is mostly passed
  as an argument, or when the block also touches other variables.
- **Configuring an object's own properties, no return value needed** → `apply`. Returns
  the context object itself, so it chains — the exact shape a builder-style
  configuration call wants.
- **Configuring an object AND computing a separate result** → `run`. Same `this` access
  as `apply`, but returns the lambda's result instead of the object.
- **Running a multi-statement block where an expression is required** (an `if`/`when`
  branch, a top-level initializer) → non-extension `run`, no context object at all.
- **A side effect that doesn't change the return chain** (logging, validating, a debug
  print) → `also`. Returns the context object unchanged, so it can sit mid-chain without
  altering what the next call receives.
- **Grouping several calls on one object when you don't need the result chained** →
  `with`. Not an extension function — reads as "with this object, do the following."

```kotlin
// ✓ let — non-null execution + local variable in one step
val length = customer.email?.let { sendConfirmation(it); it.length }

// ✓ apply — configures the object, returns the object itself (chains)
val intent = Intent(context, DetailActivity::class.java).apply {
    putExtra("id", itemId)
    putExtra("source", "list")
}

// ✓ run — configures AND computes a separate result
val distance = run {
    val dx = target.x - origin.x
    val dy = target.y - origin.y
    sqrt(dx * dx + dy * dy)
}

// ✓ also — side effect, chain unaffected
val items = fetchItems()
    .also { log.debug("fetched ${it.size} items") }
    .filter { it.isActive }

// ✓ with — grouped calls, no chaining needed
with(binding.headerView) {
    title.text = user.name
    subtitle.text = user.email
}
```

**Don't reach for one just because it's available.** A single `?.let { ... }` wrapping
one statement that doesn't need the non-null smart-cast benefit is often just a
plain `if (x != null)` with extra indirection — scope functions earn their keep when
the context-object/return-value shape actually matches what the code needs, not as a
default habit for "any block near an object."

### Sequences — lazy evaluation, not a default upgrade over `List`

Verified against [kotlinlang.org/docs/sequences.html](https://kotlinlang.org/docs/sequences.html).
The real difference: `Iterable`/`List` operations are **eager** — each `.filter{}`/`.map{}`
call runs to completion and allocates a full intermediate list before the next operation
starts. `Sequence` operations are **lazy** — each element runs through the whole chain
one at a time, and nothing downstream allocates an intermediate collection.

**Reach for `.asSequence()` when both are true:**
- The collection is large enough that intermediate-list allocation is real overhead
- The chain has 2+ operations, especially with an early-exit (`.take()`, `.first()`,
  `.any()`) that can stop before processing every element

```kotlin
// ✓ sequence pays off — large list, chained ops, early exit via take(4)
val lengths = words.asSequence()
    .filter { it.length > 3 }
    .map { it.length }
    .take(4)
    .toList()
```

**Don't reach for it on a small collection or a single operation.** Kotlin's own docs
state this directly: "the lazy nature of sequences adds some overhead which may be
significant when processing smaller collections or doing simpler computations." A
`.asSequence()` wrapping one `.filter{}` on a 20-item list is pure overhead — plain
`List` operations are both simpler to read and faster at that scale.

```kotlin
// ❌ sequence overhead with nothing to gain — small list, one operation, no early exit
val activeNames = users.asSequence().filter { it.isActive }.map { it.name }.toList()

// ✓ same result, no lazy-evaluation machinery needed
val activeNames = users.filter { it.isActive }.map { it.name }
```

The mechanical tell either way is the same: does the chain have an early-exit operator
and a collection large enough that skipping unnecessary work actually matters? If not,
`.asSequence()` is ceremony, not an optimization.
