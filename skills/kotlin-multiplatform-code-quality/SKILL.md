---
name: kotlin-multiplatform-code-quality
description: >
  Sets up Ktlint (formatting) and Detekt (code smells + architecture rules) for a KMP project.
  Both run as CI gates. Ktlint is near-zero config. Detekt architecture rules enforce the
  6-layer module boundary contract from kotlin-multiplatform-clean-architecture.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-07-09'
  keywords:
    - Ktlint
    - Detekt
    - code quality
    - formatting
    - architecture rules
    - CI gate
    - KMP
    - Kotlin Multiplatform
    - lint
    - static analysis
    - KDoc
    - comments
    - comment style
    - documentation convention
    - kdoc vs comment
---

## When to Use This Skill

Use when you need to:
- Enforce consistent Kotlin formatting across a KMP project
- Detect architecture violations (`:ui` importing from `:data`) via static analysis
- Wire Ktlint and Detekt as CI gates on every PR
- Configure Detekt architecture rules for the 6-layer module model

**Trigger keywords:** Ktlint, Detekt, code quality, formatting, architecture rules, CI gate,
static analysis, lint, import check, layer violation, code style, KDoc, comment convention,
when to use comments, documentation comment, comment style, kdoc vs line comment,
how to comment kotlin.

**Freshness rule:** Ktlint and Detekt versions change frequently — recheck the latest releases
before pinning. Detekt architecture rule DSL changes between minor versions.

---

## Recommendation First

**Install both. They solve different problems.**

| Tool | Enforces | Config effort | When to run |
|---|---|---|---|
| Ktlint | Formatting — indentation, imports, line length | Near-zero | `ktlintFormat` before commit; `ktlintCheck` in CI |
| Detekt | Code smells + architecture rules | Medium | `detekt` in CI |

Ktlint is the easier win — add it first. Detekt's architecture rule set is the more powerful
tool for catching layer violations that Gradle dependency declarations miss (import-level coupling).

---

## Ktlint Setup

### `libs.versions.toml`

```toml
[versions]
ktlint = "12.1.1"

[plugins]
ktlint = { id = "org.jlleitschuh.gradle.ktlint", version.ref = "ktlint" }
```

### Root `build.gradle.kts`

```kotlin
plugins {
    alias(libs.plugins.ktlint) apply false
}
```

### `build-logic/convention/build.gradle.kts`

```kotlin
dependencies {
    implementation(libs.plugins.ktlint.get().let { "${it.pluginId}:${it.pluginId}.gradle.plugin:${it.version}" })
}
```

### Convention plugin — add to `GROUP_ID.core.gradle.kts` and feature plugins

```kotlin
plugins {
    // ... existing plugins ...
    id("org.jlleitschuh.gradle.ktlint")
}

ktlint {
    version = "1.3.1"         // Ktlint engine version (separate from Gradle plugin version)
    android = false           // KMP modules are not Android-only
    outputToConsole = true
    filter {
        exclude("**/generated/**")
        exclude("**/build/**")
    }
}
```

### `.editorconfig` (project root)

```ini
[*.{kt,kts}]
max_line_length = 120
ktlint_standard_no-wildcard-imports = disabled
ktlint_standard_import-ordering = disabled
```

### Usage

```bash
# Format all files
./gradlew ktlintFormat

# Check (CI — fails on violations)
./gradlew ktlintCheck
```

---

## Detekt Setup

### `libs.versions.toml`

```toml
[versions]
detekt = "1.23.7"

[libraries]
detekt-formatting = { module = "io.gitlab.arturbosch.detekt:detekt-formatting", version.ref = "detekt" }

[plugins]
detekt = { id = "io.gitlab.arturbosch.detekt", version.ref = "detekt" }
```

### Root `build.gradle.kts`

```kotlin
plugins {
    alias(libs.plugins.detekt) apply false
}
```

### Convention plugin — add to all feature plugins

```kotlin
plugins {
    // ... existing plugins ...
    id("io.gitlab.arturbosch.detekt")
}

detekt {
    config.setFrom(rootProject.file("detekt.yml"))
    buildUponDefaultConfig = true
    allRules = false
}

dependencies {
    detektPlugins(libs.detekt.formatting)
}
```

### Root `detekt.yml`

```yaml
build:
  maxIssues: 0

complexity:
  LongMethod:
    active: true
    threshold: 60
  LongParameterList:
    active: true
    functionThreshold: 6
    constructorThreshold: 7
  CyclomaticComplexMethod:
    active: true
    threshold: 15

naming:
  FunctionNaming:
    active: true
    excludes: ['**/test/**', '**/*Test.kt', '**/*Preview*']

libraries:
  rules:
    - name: 'NoComposeInPresenter'
      active: true
      includes: ['**/presenter/**']
      forbidden:
        - 'androidx.compose.*'
        - 'org.jetbrains.compose.*'

    - name: 'NoDataInUi'
      active: true
      includes: ['**/ui/**']
      forbidden:
        - '*.data.*'
        - 'io.ktor.*'
        - 'app.cash.sqldelight.*'

    - name: 'NoDomainInUi'
      active: true
      includes: ['**/ui/**']
      forbidden:
        - '*.domain.*'
```

### Usage

```bash
# Run Detekt (fails on violations)
./gradlew detekt

# Generate HTML report
./gradlew detekt --report html:build/reports/detekt/detekt.html

# Fix auto-fixable issues (formatting only)
./gradlew detektFormat
```

---

## Comment & KDoc Conventions

**The rule:** `/** ... */` (KDoc) documents the **public API surface** — what a public
class/function/property does, its contract, `@param`/`@return`/`@throws`/`@see`. `//` is
for **internal implementation notes** — the WHY behind a non-obvious piece of code, never
a restatement of WHAT the code does (well-named code already says that).

| Situation | Use | Notes |
|---|---|---|
| Public class/function/property contract | KDoc `/** ... */` | Picked up by Dokka and IDE quick-docs; `//` is invisible to both |
| Internal WHY note (a workaround, a non-obvious constraint) | `//` | Never document WHAT — that's what good naming is for |
| A private member needs a comment to explain what it does | Neither — **rename it** | If a private function's behavior isn't obvious from its name, the fix is a better name, not a comment. Detekt's `DocumentationOverPrivateFunction`/`DocumentationOverPrivateProperty` flag this directly |
| Nested comments | Block comments (`/* */`) nest in Kotlin, unlike Java/C | `/* outer /* inner */ still open */` is valid. KDoc (`/** */`) does **not** nest |

### Real bug this exact mistake caused

A `//` line comment placed inside a function call's argument list consumes everything
after it on that physical line — including a needed closing `)`/`{`. This shipped in
`kotlin-multiplatform-imagevector-generator`'s own codegen until a test caught it:

```kotlin
// ❌ WRONG — the // comments out the rest of the line, including `) {`
path(fill = SolidColor(Color.Black)  // color-agnostic — tint at the call site) {

// ✅ CORRECT — the call is syntactically complete before the comment starts
path(fill = SolidColor(Color.Black)) {  // color-agnostic — tint at the call site
```

### Code comment vs. development notes

A long WHY comment is a sign the explanation has two different audiences, and both are
being crammed into one place. Split them:

- **Inline code comment** — stays in the file, kept to whatever's needed to pass one
  test: **does this line answer a question someone would ask before deleting or
  "simplifying" this code?** If yes, it survives. If it's mechanism detail, alternatives
  you already rejected, or exact version numbers that only matter during a future
  upgrade, it doesn't pass that test — it's not preventing anyone from breaking anything
  today.
- **Development notes** — the exhaustive rationale that doesn't pass that test goes in
  `docs/reference/` (see `kotlin-multiplatform-project-docs-maintainer` — this is exactly
  the "searchable technical audits, deep references" lane it already defines), with a
  one-line pointer left in the code comment.

```kotlin
// ❌ Everything crammed inline — 9 lines to justify one includeBuild() call
// Not part of the stable module graph above: pinned to a pre-release Compose
// Multiplatform version (1.12.0-beta01) for androidx.compose.foundation.style's real
// Style/StyleScope/StyleState API (@ExperimentalFoundationStyleApi, not yet in the
// 1.11.1 stable line this project otherwise targets) -- see
// tailwind/style-experimental/build.gradle.kts. A regular `include()` subproject can't
// do this: the root's `apply false` on org.jetbrains.compose locks that plugin ID to
// 1.11.1 build-wide, and a subproject requesting a different version of the same
// plugin ID fails to resolve. `includeBuild` (a real composite build, its own
// settings.gradle.kts/plugin classpath) is the only way to get genuine version
// isolation while still consuming tailwind-core's source directly via dependency
// substitution.
includeBuild("tailwind/style-experimental")

// ✅ Inline comment answers "why not include()?" and "why a different version?" —
// the two questions that would make someone try to "clean this up." Everything else
// (exact API names, dependency-substitution mechanics) moves to docs/reference/.
// Composite build (not include()): root's apply false on org.jetbrains.compose locks
// that plugin ID to 1.11.1 build-wide. This module needs 1.12.0-beta01 for an
// experimental Compose Foundation Style API not available in the stable line.
// Full rationale: docs/reference/composite-build-style-experimental.md
includeBuild("tailwind/style-experimental")
```

### Detekt enforcement

Add to `detekt.yml`:

```yaml
comments:
  UndocumentedPublicClass:
    active: true
    excludes: ['**/test/**', '**/*Test.kt', '**/*Preview*']
  UndocumentedPublicFunction:
    active: true
    excludes: ['**/test/**', '**/*Test.kt', '**/*Preview*']
  DocumentationOverPrivateFunction:
    active: true
  DocumentationOverPrivateProperty:
    active: true
  OutdatedDocumentation:
    active: true
```

`UndocumentedPublic*` forces KDoc onto every public declaration; `DocumentationOverPrivate*`
forces the opposite — no KDoc on private members, since if one is needed the name is the
real problem. `OutdatedDocumentation` catches KDoc whose `@param`/signature no longer
matches the actual declaration after a refactor.

### KDoc tag reference

| Tag | On | Purpose |
|---|---|---|
| `@param` | function/constructor | Describes one parameter — required if the name alone doesn't make its role obvious |
| `@return` | function | What the return value represents (skip for `Unit`) |
| `@throws` / `@exception` | function | A checked failure mode the caller must handle — not every possible exception, just the ones that are part of the contract |
| `@see` | any | Cross-reference to a related declaration |
| `@sample` | function | Points at an actual, compiled function elsewhere as the usage example — see below |
| `@property` | class (constructor-declared properties) | Documents a primary-constructor `val`/`var` from the class-level KDoc |
| `@receiver` | extension function | Documents the receiver type's role in the extension |
| `@constructor` | class | Documents the primary constructor specifically, separate from the class-level summary |
| `@suppress` | any | Excludes a technically-public declaration from generated docs (e.g. an internal-use-only public API) |

### `@sample` — the correct way to attach an example, not a required one per function

**Don't require an example for every function or every file.** That contradicts the same
"why not what" principle as comments generally — an example only earns its place when a
public API's usage genuinely isn't obvious from its signature (a builder, a DSL, a
function with a non-obvious multi-step call pattern). A plain getter or a one-line
utility doesn't need one.

When an example is warranted, use `@sample` instead of a raw code block pasted into the
KDoc — `@sample` references an **actual, compiled function** elsewhere in the codebase
(typically under `src/*/kotlin/samples/`), so it's type-checked and breaks the build if
it goes stale. A hand-written code block in a comment can drift from the real API
silently; `@sample` can't.

```kotlin
/**
 * Builds a [Result] pipeline that retries on transient failures.
 *
 * @sample GROUP_ID.samples.retryPipelineSample
 */
fun <T> retryPipeline(times: Int, block: suspend () -> T): Flow<T> { ... }

// src/commonTest/kotlin/GROUP_ID/samples/RetrySamples.kt (or a dedicated samples source set)
private fun retryPipelineSample() {
    retryPipeline(times = 3) { fetchUser() }
}
```

Module- and package-level documentation (describing what an entire module or package is
for, not a single declaration) is a separate Dokka mechanism — a `Module.md`/`Package.md`
file referenced from the Dokka Gradle config — not a KDoc tag.

### License headers — situational, not a default

Per-file license header comments (an Apache-2.0 boilerplate block at the top of every
`.kt` file) were standard in the AOSP/Apache-Software-Foundation era and are still real
practice for **libraries redistributed externally** — Detekt even ships a rule for it,
`AbsentOrWrongFileLicense` (disabled by default). For a typical **app** codebase, skip
it: it's redundant with the root `LICENSE` file, and it's a maintenance burden (author/year
drift) with no legal upside for code that isn't independently redistributed per file.

Add it only when publishing a library — see
`kotlin-multiplatform-library-publishing`'s "Per-file license headers" for the Detekt
rule config and license-header template.

---

## CI Integration

Add to `.github/workflows/ci.yml` lint job:

```yaml
lint:
  name: Lint
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'zulu'

    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v4
      with:
        cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}

    - name: Ktlint check
      run: ./gradlew ktlintCheck

    - name: Detekt
      run: ./gradlew detekt

    - name: Upload Detekt report
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: detekt-report
        path: '**/build/reports/detekt/**'
```

---

## Related Skills

- `kotlin-multiplatform-clean-architecture` — defines the layer rules that Detekt enforces
- `kotlin-multiplatform-ci-github-actions` — the CI workflow where these gates run
- `kotlin-multiplatform-feature-scaffold` — convention plugins are where Ktlint/Detekt are applied
- `kotlin-multiplatform-project-docs-maintainer` — `docs/reference/` is where development notes go when a code comment's rationale outgrows what belongs inline
- `kotlin-multiplatform-library-publishing` — per-file license headers, a related but separate comment-placement decision

---

## Common Anti-Patterns

- applying Detekt only to the root project — violations in submodules go undetected; apply via convention plugins
- setting `maxIssues > 0` — a non-zero threshold lets violations accumulate silently
- using Ktlint without `.editorconfig` — line length defaults to 80; too short for Kotlin
- running `ktlintFormat` in CI instead of `ktlintCheck` — CI should fail, not silently reformat
- excluding the `:presenter` module from `NoComposeInPresenter` — the rule only matters if applied to presenter
- using `//` to document a public API's contract instead of KDoc — Dokka and IDE quick-docs never see a `//` comment
- adding KDoc to a private member to explain unclear behavior — rename the member instead; flagged by Detekt's `DocumentationOverPrivateFunction`/`DocumentationOverPrivateProperty`
- placing a `//` comment inside a function call's argument list before its closing `)`/`{` — silently comments out the rest of the line; this exact bug shipped in `kotlin-multiplatform-imagevector-generator`'s own codegen
- writing a multi-paragraph inline comment that mixes "why this code exists" with mechanism detail, rejected alternatives, and exact version numbers — split it: the short WHY stays inline, the exhaustive rationale goes in `docs/reference/` with a one-line pointer left in the comment

If Detekt reports false positives, use `@Suppress("RuleName")` at the call site, not a global exclude.

---

## Output Style

When asked about code quality, linting, or formatting for KMP, respond in this order:
1. Ktlint setup (plugin version, `.editorconfig`, `ktlintCheck` command)
2. Detekt setup (plugin, `detekt.yml`, architecture rules for the 6-layer model)
3. CI job snippet
4. which tool enforces what (table)
5. how to fix violations locally before pushing

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-09 | Added a "Code comment vs. development notes" split, from a real 9-line inline comment that crammed a build-topology explanation, rejected alternatives, and exact version numbers into one `includeBuild()` call site. Rule: an inline comment survives only if it answers a question that would make someone break the code by "simplifying" it; the exhaustive rationale moves to `docs/reference/` (per `kotlin-multiplatform-project-docs-maintainer`'s existing convention) with a one-line pointer left in the comment. Before/after example, 1 new anti-pattern, 2 new Related Skills cross-references. |
| 2026-07-09 | Extended the "Comment & KDoc Conventions" section: a full KDoc tag reference (`@param`/`@return`/`@throws`/`@see`/`@sample`/`@property`/`@receiver`/`@constructor`/`@suppress`), guidance that an example is warranted only for non-obvious public API (never required per function/file — same "why not what" principle), `@sample`'s advantage over a raw code block (references an actual compiled function, can't silently drift stale), and a "License headers" note (situational, not a default — cross-referenced to `kotlin-multiplatform-library-publishing`). |
| 2026-07-08 | Added a "Comment & KDoc Conventions" section — KDoc for public API contracts, `//` for internal WHY notes, private members should be renamed rather than commented (backed by Detekt's `DocumentationOverPrivateFunction`/`DocumentationOverPrivateProperty`), and a real bug example (a `//` comment inside a function call's argument list silently commenting out the rest of the line, which actually shipped in `kotlin-multiplatform-imagevector-generator`'s codegen). New `comments:` Detekt rule block and 3 anti-patterns. |
| 2026-06-18 | Initial release. |
