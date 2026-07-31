---
name: kotlin-multiplatform-library-publishing
description: >
  Publish a Kotlin Multiplatform library to Maven Central, GitHub Packages, or both.
  Covers: vanniktech maven-publish plugin setup, POM metadata, Sonatype OSSRH staging,
  multi-artifact BOM, kotlinx-binary-compatibility-validator API tracking, SNAPSHOT vs
  stable channels, and a release checklist. Pairs with kotlin-multiplatform-xcframework-spm
  for iOS/SPM distribution.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-07-31'
  keywords:
    - maven central
    - maven publish
    - library publishing
    - KMP library
    - vanniktech
    - mavenPublishing
    - OSSRH
    - Sonatype
    - GitHub Packages
    - BOM
    - bill of materials
    - binary compatibility
    - apiCheck
    - api dump
    - kotlinx-binary-compatibility-validator
    - SNAPSHOT
    - artifactId
    - groupId
    - POM metadata
    - publish artifact
    - distribute KMP
    - library versioning
    - staging repository
    - release candidate
    - library consumers
    - multiplatform library
    - publish to maven
    - open source library
    - license header
    - AbsentOrWrongFileLicense
    - file license
---

**Trigger keywords:** publish KMP library, Maven Central, publish library, maven-publish,
vanniktech, mavenPublishing, OSSRH, Sonatype, GitHub Packages library, BOM, bill of materials,
binary compatibility, apiCheck, apiDump, api dump, kotlinx-binary-compatibility-validator,
SNAPSHOT library, library release, distribute KMP, KMP library publishing, artifactId, groupId,
POM metadata, GPG signing library, library consumers, multiplatform library, open source KMP,
library versioning, staging repository, Central Portal, license header, file license header,
AbsentOrWrongFileLicense, per-file license.

**Freshness rule:** vanniktech plugin releases frequently; check
[github.com/vanniktech/gradle-maven-publish-plugin/releases](https://github.com/vanniktech/gradle-maven-publish-plugin/releases)
and `SonatypeHost.CENTRAL_PORTAL` vs `SonatypeHost.S01` before wiring.
`binary-compatibility-validator` and `dokka` also track Kotlin releases closely —
verify versions in `libs.versions.toml` against the latest Kotlin version in the project.

---

## When to Use This Skill

Use when:
- You are building a KMP library for other developers to consume (not an end-user app)
- You need to publish to Maven Central or GitHub Packages
- You need to manage API surface across versions (`apiCheck`, binary dumps)
- You want a BOM so consumers can align versions across multiple artifacts
- You need SNAPSHOT builds for pre-release testing

**Pairs with:**
- `kotlin-multiplatform-xcframework-spm` — for iOS/SPM binary distribution alongside Maven
- `kotlin-multiplatform-ci-github-actions` — automate publishing in CI
- `kotlin-multiplatform-code-quality` — `detekt` and `ktlint` before publishing

---

## Recommendation First

Use **`com.vanniktech.maven.publish`** (vanniktech plugin). It is the de-facto standard for
KMP → Maven Central. It handles:
- Sonatype OSSRH staging (legacy + Central Portal)
- Javadoc/Dokka jar generation
- Sources jar
- POM generation from DSL
- Signing via GPG

Never wire `maven-publish` manually for Maven Central — POM requirements are strict and
the vanniktech plugin handles all the boilerplate correctly.

---

## Step 1 — Library project structure

A KMP library has **no** application plugin. The root module exposes multiplatform targets.

```
my-library/
├── build-logic/                  # Convention plugins (optional but recommended)
├── library/                      # Main library module
│   └── build.gradle.kts
├── library-testing/              # Test helpers for consumers (optional)
├── bom/                          # Bill of Materials (optional, for multi-artifact)
├── sample/                       # Sample app that consumes the library
│   └── build.gradle.kts          # Has com.android.application — only here
├── gradle/
│   └── libs.versions.toml
├── settings.gradle.kts
└── build.gradle.kts              # Root: coordinates + publishing config
```

`settings.gradle.kts` for a library:

```kotlin
rootProject.name = "my-library"

include(":library")
include(":library-testing")    // optional
include(":bom")                // optional
include(":sample:androidApp")  // sample only — no maven-publish applied here
```

For a library small enough to fit in one `:library` module, that's the whole structure.
Once `:library` itself grows past a handful of files covering genuinely separate
concerns, `kotlin-multiplatform-clean-architecture`'s 6-layer contract applies to a
library's own internals the same way it does to an app's — `:model`/`:api` split,
`internal` visibility between layers — the difference is only that the *outermost*
public surface is what `explicitApi()`/`apiCheck` above govern, not an app's UI layer.

---

## Step 2 — Dependencies

`gradle/libs.versions.toml`:

```toml
[versions]
kotlin = "2.1.21"
vanniktech-publish = "0.30.0"
binary-compat = "0.17.0"
dokka = "2.0.0"

[plugins]
vanniktech-publish = { id = "com.vanniktech.maven.publish", version.ref = "vanniktech-publish" }
binary-compat      = { id = "org.jetbrains.kotlinx.binary-compatibility-validator", version.ref = "binary-compat" }
dokka              = { id = "org.jetbrains.dokka", version.ref = "dokka" }
```

Root `build.gradle.kts`:

```kotlin
plugins {
    alias(libs.plugins.vanniktech.publish) apply false
    alias(libs.plugins.binary.compat)
    alias(libs.plugins.dokka) apply false
}

// Binary compatibility: track all public APIs
apiValidation {
    ignoredProjects += setOf("sample", "sample-androidApp", "bom")
    nonPublicMarkers += listOf("io.mylib.InternalApi")
}
```

---

## Step 3 — Library module `build.gradle.kts`

```kotlin
import com.vanniktech.maven.publish.SonatypeHost

plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.library)       // only if targeting Android
    alias(libs.plugins.vanniktech.publish)
    alias(libs.plugins.dokka)
}

kotlin {
    explicitApi()   // library-only — forces every public declaration to state its
                    // visibility and return type explicitly, see below

    androidTarget {
        publishLibraryVariants("release")
    }
    iosX64()
    iosArm64()
    iosSimulatorArm64()
    jvm()
    js(IR) { browser(); nodejs() }
    wasmJs { browser() }
    linuxX64()

    sourceSets {
        commonMain.dependencies {
            // shared dependencies
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}

mavenPublishing {
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)  // use OSSRH for legacy accounts

    signAllPublications()   // requires GPG key in env (see Step 6)

    coordinates(
        groupId    = "io.github.yourhandle",
        artifactId = "my-library",
        version    = version.toString(),   // read from gradle.properties
    )

    pom {
        name = "My Library"
        description = "A concise description of what the library does."
        url = "https://github.com/yourhandle/my-library"
        inceptionYear = "2024"

        licenses {
            license {
                name = "Apache-2.0"
                url  = "https://www.apache.org/licenses/LICENSE-2.0"
            }
        }

        developers {
            developer {
                id   = "yourhandle"
                name = "Your Name"
                url  = "https://github.com/yourhandle"
            }
        }

        scm {
            url                 = "https://github.com/yourhandle/my-library"
            connection          = "scm:git:git://github.com/yourhandle/my-library.git"
            developerConnection = "scm:git:ssh://git@github.com/yourhandle/my-library.git"
        }
    }
}
```

`gradle.properties` (version managed here, not in build script):

```properties
GROUP=io.github.yourhandle
POM_ARTIFACT_ID=my-library
VERSION_NAME=1.0.0-SNAPSHOT
```

### Per-file license headers (optional)

The POM `licenses { license { ... } }` block above is the legally required, project-level
license declaration for Maven Central — that's not optional. A per-file license header
comment repeated at the top of every `.kt` source file is a **separate, optional** choice,
worth it for a library specifically because each file may be vendored, copy-pasted, or
inspected independently of the repo it came from; a project-level `LICENSE` file alone
doesn't travel with an individual file once it's copied elsewhere. It's not needed for
app code (see `kotlin-multiplatform-code-quality`'s Comment & KDoc Conventions).

Enforce it with Detekt's `AbsentOrWrongFileLicense` rule (off by default):

```yaml
# detekt.yml
comments:
  AbsentOrWrongFileLicense:
    active: true
    licenseTemplateFile: 'license.template.txt'
```

```
# license.template.txt
/*
 * Copyright 2026 Your Name or Org
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 */
```

Keep the license identifier here consistent with the POM's `licenses { license { name = ... } }`
block — a per-file header claiming a different license than the POM declares is worse
than having no per-file header at all.

### `explicitApi()` — library-only, not for app code

Library code has a wider blast radius than app code: a `public` declaration nobody
intended to expose becomes part of the API surface the moment it ships, and removing it
later is a breaking change (exactly what `apiCheck`/binary-compatibility-validator in
Step 5 exists to catch after the fact). `explicitApi()` catches it *before* publishing
instead — it fails the build on any public declaration missing an explicit visibility
modifier or return type:

```kotlin
// ❌ fails to compile under explicitApi() — implicit public visibility, inferred return type
class UserRepository {
    fun getUser(id: String) = api.fetchUser(id)
}

// ✓ compiles — visibility and return type both explicit
public class UserRepository {
    public fun getUser(id: String): User = api.fetchUser(id)
}
```

**Don't add this to app code** — `kotlin-multiplatform-clean-architecture`'s 6-layer
contract already controls what's exposed between modules via `internal`, and an app has
no external consumers to protect from an accidental public leak the way a published
library does. `explicitApi()` on app code is pure ceremony with no corresponding benefit.

Two modes: `explicitApi()` fails the build (`ExplicitApiMode.Strict`), `explicitApiWarning()`
only warns. Use the strict form for a library that's already past its first stable
release — a warning is easy to ignore and defeats the point of catching this before
publishing.

### No forced framework coupling in library internals

`kotlin-multiplatform-dependency-injection` recommends Koin for **app code** — a
published library is a different situation. A consumer app might use Koin, Hilt, manual
DI, or nothing at all; a library that hard-imports `org.koin.*` inside its own public
classes forces that choice onto every consumer, or worse, silently requires Koin to be
on the consumer's classpath at all.

```kotlin
// ❌ forces Koin onto every consumer of this library
class UserRepository(scope: Scope) : KoinComponent {
    private val api: ApiClient by inject()
}

// ✓ plain constructor injection — the consumer wires it however they want
public class UserRepository(private val api: ApiClient) {
    // ...
}
```

If the library wants to *offer* Koin wiring as a convenience, ship it as a separate,
optional artifact (`my-library-koin`) with its own `module { }` — never bake the
dependency into the core artifact's own classes.

### KDoc coverage on the public API surface

`kotlin-multiplatform-code-quality`'s Comment & KDoc Conventions section covers KDoc
*style* — this is about *coverage*. Once `explicitApi()` forces every public declaration
to be deliberate, an undocumented one is a real gap: a consumer sees the declaration in
autocomplete with no explanation of what it does or when to use it.

```kotlin
// ❌ compiles under explicitApi(), but a consumer has no idea what this does
public class RetryPolicy(public val maxAttempts: Int, public val backoffMs: Long)

// ✓ the public contract is documented, not just the visibility
/**
 * Controls retry behavior for transient network failures.
 * @property maxAttempts stop retrying after this many attempts, including the first
 * @property backoffMs delay between attempts, doubled after each failure
 */
public class RetryPolicy(public val maxAttempts: Int, public val backoffMs: Long)
```

`kotlin-multiplatform-audit`'s `_detect_undocumented_public_api` flags a public
declaration with no preceding KDoc block, but only in a project that already uses
`explicitApi()` — without it, "public" isn't a deliberate signal worth checking.

---

## Step 4 — BOM (Bill of Materials) for multi-artifact libraries

Use a BOM when the library ships multiple artifacts that consumers should always
align (`my-library-core`, `my-library-testing`, `my-library-compose`).

`bom/build.gradle.kts`:

```kotlin
plugins {
    `java-platform`
    alias(libs.plugins.vanniktech.publish)
}

javaPlatform { allowDependencies() }

dependencies {
    constraints {
        api(project(":library"))
        api(project(":library-compose"))
        api(project(":library-testing"))
    }
}

mavenPublishing {
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)
    signAllPublications()
    coordinates("io.github.yourhandle", "my-library-bom", version.toString())
    // … same pom block
}
```

Consumer then uses:

```kotlin
// Consumer build.gradle.kts
dependencies {
    implementation(platform("io.github.yourhandle:my-library-bom:1.0.0"))
    implementation("io.github.yourhandle:my-library")           // no version needed
    testImplementation("io.github.yourhandle:my-library-testing") // no version needed
}
```

---

## Step 5 — Binary compatibility validator

The `binary-compatibility-validator` plugin generates `.api` dump files that track
every public symbol. A CI check (`apiCheck`) fails if a release PR accidentally removes
or changes a public API.

**One-time setup (after configuring the plugin in root build):**

```bash
./gradlew apiDump   # generates library/api/library.api
git add library/api/
git commit -m "chore: initial API dump"
```

**On every PR:**

```bash
./gradlew apiCheck  # fails if public API changed without a matching apiDump
```

**When intentionally changing the API:**

```bash
./gradlew apiDump   # regenerate the dump
git add library/api/
git commit -m "feat!: add Foo.bar() to public API"
```

**Marking internal APIs** (excluded from dump):

```kotlin
@RequiresOptIn(level = RequiresOptIn.Level.ERROR)
@Retention(AnnotationRetention.BINARY)
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION, AnnotationTarget.PROPERTY)
annotation class InternalApi
```

Add `InternalApi` to `nonPublicMarkers` in `apiValidation { }` (Step 2).

### `apiCheck` catches *that* the API changed, not *whether the version bump matches*

`apiCheck` fails on any `.api` diff, forcing a deliberate `apiDump` — but it has no
concept of semver. It passes identically whether the diff is a source-compatible
addition (minor-worthy) or a signature change/removal that breaks every consumer
(major-worthy). Nothing currently blocks tagging a *breaking* diff as a minor release.

This isn't mechanically enforceable from the `.api` file alone — the file lists symbols,
not which specific lines changed *how* between two dumps, and "is this actually
source/binary breaking" needs a real diff, not just a checksum mismatch. Treat it as a
review-time discipline instead: before tagging, `git diff` the previous `library.api`
against the new one and classify every change —

| Change | Semver bump |
|---|---|
| New public class/function/property added | Minor |
| Existing public signature changed or removed | Major |
| Internal-only change, `.api` file untouched | Patch |

Get this wrong once (a breaking change shipped as a minor) and every consumer pinned to
`^x.y` silently breaks on their next `./gradlew build` — there's no compiler error on
their side, just a runtime `NoSuchMethodError` or a build failure with no obvious cause.

---

## Step 6 — GPG signing and secrets

Maven Central requires every artifact to be signed with a GPG key.

**Generate a key (one-time):**

```bash
gpg --gen-key
gpg --list-secret-keys --keyid-format LONG   # note the KEY_ID
gpg --armor --export-secret-keys KEY_ID > signing.gpg
gpg --keyserver keyserver.ubuntu.com --send-keys KEY_ID
```

**GitHub Actions secrets** (Settings → Secrets):

| Secret | Value |
|---|---|
| `SIGNING_KEY_ID` | Last 8 chars of KEY_ID |
| `SIGNING_KEY` | Contents of `signing.gpg` (base64: `cat signing.gpg \| base64`) |
| `SIGNING_PASSWORD` | Your GPG passphrase |
| `OSSRH_USERNAME` | Sonatype / Central Portal username |
| `OSSRH_PASSWORD` | Sonatype / Central Portal token |

**`gradle.properties`** (never commit secrets here — only for local development):

```properties
signing.keyId=ABCDEF12
signing.password=your-passphrase
signing.secretKeyRingFile=/Users/you/.gnupg/secring.gpg
```

---

## Step 7 — GitHub Packages (simpler alternative / supplement)

GitHub Packages requires no Sonatype account and works with existing GitHub tokens.
Good for: internal libraries, pre-release testing, organisations on GitHub.

`library/build.gradle.kts` (add alongside or instead of Central):

```kotlin
publishing {
    repositories {
        maven {
            name = "GitHubPackages"
            url  = uri("https://maven.pkg.github.com/yourhandle/my-library")
            credentials {
                username = System.getenv("GITHUB_ACTOR")
                password = System.getenv("GITHUB_TOKEN")
            }
        }
    }
}
```

Consumers add the repository:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        maven {
            url = uri("https://maven.pkg.github.com/yourhandle/my-library")
            credentials {
                username = providers.gradleProperty("gpr.user").orNull ?: System.getenv("GITHUB_ACTOR")
                password = providers.gradleProperty("gpr.key").orNull  ?: System.getenv("GITHUB_TOKEN")
            }
        }
    }
}
```

---

## Step 8 — SNAPSHOT vs stable release channels

| Channel | `VERSION_NAME` | Publishes to | When |
|---|---|---|---|
| SNAPSHOT | `1.1.0-SNAPSHOT` | OSSRH snapshots / GitHub Packages | Every merge to `main` |
| RC | `1.1.0-rc.1` | Maven Central staging | Pre-release testing |
| Stable | `1.1.0` | Maven Central (released) | Tagged releases |

**SNAPSHOT publishing** in CI (`publish.yml`):

```yaml
- name: Publish snapshot
  if: github.ref == 'refs/heads/main'
  run: ./gradlew publishAllPublicationsToMavenCentralRepository --no-configuration-cache
  env:
    ORG_GRADLE_PROJECT_mavenCentralUsername: ${{ secrets.OSSRH_USERNAME }}
    ORG_GRADLE_PROJECT_mavenCentralPassword: ${{ secrets.OSSRH_PASSWORD }}
    ORG_GRADLE_PROJECT_signingInMemoryKeyId:       ${{ secrets.SIGNING_KEY_ID }}
    ORG_GRADLE_PROJECT_signingInMemoryKey:         ${{ secrets.SIGNING_KEY }}
    ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.SIGNING_PASSWORD }}
```

**Stable publishing** (triggered by version tag `v*`):

```yaml
- name: Publish release
  if: startsWith(github.ref, 'refs/tags/v')
  run: ./gradlew publishAllPublicationsToMavenCentralRepository --no-configuration-cache
  env:
    # same secrets as above
```

---

## Step 9 — Release checklist

Before tagging a stable release:

```
[ ] apiCheck passes — no accidental public API changes
[ ] All targets build: ./gradlew build
[ ] Tests pass on all targets: ./gradlew allTests
[ ] VERSION_NAME in gradle.properties has no -SNAPSHOT suffix
[ ] CHANGELOG updated
[ ] POM metadata complete (description, license, SCM, developers)
[ ] GPG key not expired: gpg --list-keys
[ ] ./gradlew publishToMavenLocal  → smoke-test consumer can resolve from mavenLocal()
[ ] Dry run: ./gradlew publishAllPublicationsToMavenCentralRepository --dry-run
[ ] Tag: git tag v1.1.0 && git push origin v1.1.0
[ ] Verify on search.maven.org (may take 15–30 min to appear)
```

---

## Step 10 — iOS distribution alongside Maven

KMP libraries targeting iOS consumers need two distribution channels in parallel:

| Consumer type | Distribution |
|---|---|
| Android / JVM / JS / Wasm | Maven Central (`implementation("io.github.you:lib:1.0.0")`) |
| iOS (Swift / Xcode) | XCFramework binary target in SPM Package.swift |

See `kotlin-multiplatform-xcframework-spm` for the full iOS distribution flow.
The release CI should run both publish tasks in the same workflow run when a tag is pushed.

---

## Step 11 — Ongoing maintenance (post-1.0)

Everything above covers shipping. A published library also needs a maintenance
practice — real gaps found repeatedly in libraries that only had a publish checklist:

### Deprecation cycle, not silent removal

Never delete a public symbol a consumer might already depend on. Mark it first:

```kotlin
@Deprecated(
    message = "Use fetchUserV2() — handles pagination correctly",
    replaceWith = ReplaceWith("fetchUserV2(id)"),
    level = DeprecationLevel.WARNING,
)
fun fetchUser(id: String): User
```

Cycle, tied to SemVer:
1. **This minor version** — add `@Deprecated(level = WARNING)`. `apiCheck` still passes;
   this is not a binary-breaking change.
2. **Next minor version** — bump to `level = ERROR`. Consumers must migrate to keep
   compiling, but the symbol still exists (source-compatible migration window).
3. **Next major version** — remove the symbol entirely. `apiDump` records the removal;
   `apiCheck` correctly fails until the API dump is regenerated for the major bump.

### Communicating a breaking change

A binary-incompatible change (an `apiCheck` failure you're accepting on purpose, not a
mistake to fix) needs three things before it ships, not just a version bump:
- A `CHANGELOG.md` entry naming the exact symbol and the replacement, not just "breaking changes"
- A migration note if the fix isn't mechanical (find/replace) — show the before/after
- The major version bump itself, per SemVer — a breaking change is never a minor/patch release

### Dependency upgrade cadence

A library's own dependency versions become every consumer's transitive minimum. Pin
conservatively and review on a cadence, not reactively:
- Renovate or Dependabot on the repo, scoped to `gradle/libs.versions.toml`
- Treat a transitive major-version bump (Compose Multiplatform, Kotlin itself) as its own
  reviewed change, never bundled silently into an unrelated feature release
- Keep `sample/`'s own dependency versions pinned to the library's own — a stale sample
  masks a real compatibility break until a real consumer hits it first

### Keep `sample/` from drifting

The sample app is the only thing that actually compiles against the library's *public*
API the way a real consumer would — an internal test suite compiles against internals
too and can miss a public-surface break. Run the sample's build as its own CI job on
every PR, not just at release time:

```bash
./gradlew :sample:compileKotlinX  # X = every registered target
```

A sample that still compiles against a symbol scheduled for removal is a signal the
deprecation cycle above hasn't actually reached consumers yet — don't remove the symbol
from the library until the sample itself has migrated off it.

---

## Output Style

When generating publishing configuration or release steps, output:
1. The complete `build.gradle.kts` block for the affected module (not diffs — consumers need the full context)
2. The `gradle.properties` fields to add/change
3. A copy-ready CI workflow snippet for the relevant trigger (push to main / tag push)
4. A numbered release checklist the developer can tick off before tagging

Never output partial Gradle snippets without the surrounding `mavenPublishing { }` block —
missing fields cause Maven Central validation failures that are hard to debug.

---

## Common Anti-Patterns

| Mistake | Fix |
|---|---|
| `VERSION_NAME` still has `-SNAPSHOT` on release | Remove the suffix in `gradle.properties` before tagging |
| Missing Javadoc jar | Dokka plugin must be applied; vanniktech plugin auto-configures it |
| `apiCheck` fails in CI but not locally | Run `./gradlew apiDump` locally and commit the `.api` file |
| GPG key expired | `gpg --edit-key KEY_ID` → `expire` → set new expiry → re-upload to keyserver |
| Consumer can't resolve SNAPSHOT | Must add OSSRH snapshot repo: `maven("https://s01.oss.sonatype.org/content/repositories/snapshots")` |
| `signAllPublications()` fails locally | Set `signing.*` properties in `~/.gradle/gradle.properties`, not in the project |
| Missing `scm` block in POM | Maven Central validation rejects POMs without SCM — always include it |
| Per-file license header names a different license than the POM's `licenses { license { name = ... } }` | Keep both in sync — a mismatched per-file header is worse than no per-file header at all |
| No `explicitApi()` | A public declaration nobody intended to expose ships as part of the API surface; `apiCheck` only catches the *next* accidental change, not the first one |
| Library's public classes `import org.koin.*` directly | Forces the consumer's DI choice; use plain constructor injection, ship Koin wiring as a separate optional artifact if wanted |
| Public class/fun with no KDoc under `explicitApi()` | The declaration is deliberate but undocumented — a consumer sees it in autocomplete with no explanation |
| Shipping a breaking `.api` diff as a minor version | `apiCheck` only confirms the diff was deliberate, not that the semver bump matches its severity — classify every diff (addition = minor, signature change/removal = major) before tagging |

---

## Related Skills

| Skill | When to use alongside this skill |
|---|---|
| `kotlin-multiplatform-xcframework-spm` | Distributing to iOS consumers via SPM binary target (runs in parallel with Maven publishing) |
| `kotlin-multiplatform-ci-github-actions` | Automating publish on tag push and SNAPSHOT on main merge |
| `kotlin-multiplatform-code-quality` | Detekt + ktlint checks to run before publishing |
| `kotlin-multiplatform-unit-testing` | All targets must pass tests before a stable release |
| `kotlin-multiplatform-expect-actual` | Platform-specific implementations inside the library |
| `kotlin-multiplatform-release` | App release pipeline (different from library publishing — covers Play Store / App Store) |
| `kotlin-multiplatform-project-docs-maintainer` | `docs/libraries.md` catalogs every published coordinate/version — point the release checklist there |
| `kotlin-multiplatform-docs-site` | Public GitHub Pages developer guide + Dokka HTML API reference; reuses this skill's Dokka setup for the separate HTML output, not the Javadoc jar |
| `kotlin-multiplatform-dependency-injection` | That skill's Koin recommendation is scoped to app code — see "No forced framework coupling in library internals" above for why a library's own classes shouldn't hard-depend on it |
| `kotlin-multiplatform-audit` | `_detect_undocumented_public_api` flags a public declaration with no KDoc, scoped to projects using `explicitApi()` |
| `kotlin-multiplatform-clean-architecture` | The 6-layer contract applies to a library's own `:library` internals too, once it outgrows a single module — see Step 1 |

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-31 | Added Step 11 — ongoing maintenance: real gap where this skill covered shipping (publish, apiCheck, signing) but nothing about maintaining a published library afterward. Covers the deprecation cycle (`@Deprecated(WARNING)` → `ERROR` → removal, tied to SemVer), breaking-change communication (CHANGELOG entry + migration note before a major bump, never bundled silently), dependency upgrade cadence (Renovate/Dependabot scoped to the version catalog, sample pinned to the library's own versions), and keeping `sample/` from drifting (its own CI compile job — the only thing that actually compiles against the real public surface the way a consumer would). |
| 2026-07-31 | Added "`apiCheck` catches that the API changed, not whether the version bump matches" — real gap: `apiCheck` has no concept of semver, so nothing blocks tagging a breaking `.api` diff as a minor release. Also cross-referenced `kotlin-multiplatform-clean-architecture`'s 6-layer contract for a library's own internal structure once `:library` outgrows a single module. 1 new anti-pattern, 1 new Related Skills row. |
| 2026-07-20 | Added "No forced framework coupling in library internals" (a library's own classes shouldn't hard-import Koin — ship it as a separate optional artifact instead) and "KDoc coverage on the public API surface", the second wired to `kotlin-multiplatform-audit`'s new `_detect_undocumented_public_api`. Real gaps from a library-vs-app rules discussion. 2 new anti-pattern rows, 2 new Related Skills. |
| 2026-07-20 | Added `explicitApi()` — real gap found in a library-vs-app rules survey: this skill covered binary compatibility, signing, and publishing channels but never the compiler mode that catches an accidental public API leak *before* it ships (as opposed to `apiCheck`, which only catches the *next* change to an already-public surface). Explicitly scoped to library code only — app code has no external consumers to protect and gains nothing from the ceremony. 1 new anti-pattern. |
| 2026-07-11 | Cross-referenced two new skills: `kotlin-multiplatform-project-docs-maintainer`'s new `docs/libraries.md` catalog page (release checklist should point there instead of nowhere), and `kotlin-multiplatform-docs-site` (public GitHub Pages developer guide, reuses this skill's Dokka setup for a separate HTML output, distinct from the Javadoc jar). |
| 2026-07-09 | Added a "Per-file license headers (optional)" section — Detekt's `AbsentOrWrongFileLicense` rule (off by default) with a license template, and why this is worth it for a library (files get vendored/copy-pasted independently of the repo) but not for app code. New anti-pattern: per-file header must stay consistent with the POM's declared license. |
| 2026-06-29 | Initial skill — vanniktech plugin, BOM, binary-compat-validator, SNAPSHOT/stable, GPG, GitHub Packages |
