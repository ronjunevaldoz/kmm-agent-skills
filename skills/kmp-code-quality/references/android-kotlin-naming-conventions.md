# Naming Conventions (Android Kotlin Style Guide)

Part of `kmp-code-quality`. Load this file when working on: naming conventions.

---

Ktlint/Detekt above enforce *formatting* mechanically. They do not enforce naming
*semantics* — whether an acronym is cased right, whether a `val` actually qualifies as a
constant, whether a `@Composable` reads as a type or a verb. Verified against the real,
current [Android Kotlin style guide](https://developer.android.com/kotlin/style-guide)
(Google's official doc, last updated 2023-09-06), not assumed:

### File and package naming

- A file with one top-level class is named exactly after that class, case-sensitive —
  `AuthViewModel.kt`, never `authviewmodel.kt` or `AuthVM.kt`
- A file with multiple top-level declarations (extension functions, several small types)
  gets a descriptive PascalCase name — `StringExtensions.kt`, `NetworkResult.kt`
- Package names are all lowercase, words concatenated with no underscores —
  `GROUP_ID.feature.auth.presenter`, never `GROUP_ID.feature.auth_flow`

### Type, function, and constant names

| Kind | Case | Notes |
|---|---|---|
| Class / interface / object | `PascalCase` | Nouns or noun phrases (`AuthRepository`); interfaces may be adjectives too (`Readable`) |
| Test class | `PascalCase` + `Test` | `AuthViewModelTest`, `AuthRepositoryIntegrationTest` |
| Function | `camelCase` | Verb or verb phrase — `sendMessage`, `refreshToken` |
| Test function | `camelCase`, underscores allowed | `` `pop_emptyStack`` — underscores separate logical components, test names only |
| **`@Composable` function returning `Unit`** | **`PascalCase`, noun** | Read as a type, not a verb — `AppButton`, `ProductListScreen`. **Not** `appButton`/`renderProductList` |
| `@Composable` function returning a value | `camelCase` | A factory, not a UI node — `rememberScrollState()`, not `RememberScrollState()` |
| Constant (`const val`, or a `val` with no custom getter and deeply immutable contents) | `UPPER_SNAKE_CASE` | Only legal in an `object` or at top level — a `class`'s own property can't be a "constant" by this definition, even if it never changes; use `camelCase` there instead |
| Backing property | `_` + real property name | `private var _table: Map<...>?` backing `val table: Map<...>` |
| Type variable | Single capital + optional numeral, or `NameT` | `T`, `E`, `T2`, or `RequestT` |

The `@Composable` PascalCase rule is the one most relevant to this collection's own
generated code — every `App*`/`Shadcn*` component already follows it by convention; this
is the first place it's stated as an explicit, checkable naming rule rather than an
implicit pattern. `kmp-audit`'s `_detect_lowercase_unit_composable`
mechanically enforces it.

### Acronym casing

The style guide's camelCase conversion process lowercases an acronym's letters except
the first, same as any other word — never keep an acronym fully capitalized:

| Prose | Correct | Incorrect |
|---|---|---|
| "XML Http Request" | `XmlHttpRequest` | `XMLHTTPRequest` |
| "new customer ID" | `newCustomerId` | `newCustomerID` |
| "supports IPv6 on iOS" | `supportsIpv6OnIos` | `supportsIPv6OnIOS` |

### A known, deliberate deviation: line length

The Android guide sets a 100-character column limit. This repo's own
`.editorconfig` (see Ktlint Setup above) sets `max_line_length = 120`, matching
[kotlinlang.org's own Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html)
recommendation instead. This is a real, acknowledged conflict between the two official
sources, not an oversight — 120 stays the default here; a project that wants strict
Android-guide alignment should set `max_line_length = 100` in its own `.editorconfig`.
