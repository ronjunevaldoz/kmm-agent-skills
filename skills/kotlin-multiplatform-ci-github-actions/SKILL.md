---
name: kotlin-multiplatform-ci-github-actions
description: >
  Sets up GitHub Actions CI for a Kotlin Multiplatform (KMP) project.
  Produces two workflow files: ci.yml (lint, Android tests, iOS tests, Desktop JVM tests,
  Web JS + WasmJs tests, Gradle cache) and release.yml (XCFramework build + upload artifact).
  Covers Maven Central publishing via Doppler, changelog generation with git-cliff,
  and auto-bump patch versioning from gradle.properties.
  All target platforms are covered. Assumes AGP 9+ and the project structure from
  kotlin-multiplatform-feature-scaffold.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-23'
  keywords:
    - GitHub Actions
    - CI/CD
    - Kotlin Multiplatform
    - KMP
    - Android
    - iOS
    - Desktop
    - JVM
    - Web
    - JS
    - WasmJs
    - XCFramework
    - Gradle cache
    - Maven Central
    - Sonatype
    - publish
    - release notes
    - changelog
    - git-cliff
    - Doppler
    - semantic versioning
    - vanniktech
---

## When to Use This Skill

Use when you need to:
- Set up GitHub Actions CI for a new or existing KMP project
- Add automated Android, iOS, Desktop, or Web test jobs
- Configure a release workflow that builds and publishes an XCFramework
- Wire Gradle caching into CI for faster builds

**Requires:** `kotlin-multiplatform-feature-scaffold` project structure (or equivalent AGP 9+ KMP layout).

**Trigger keywords:** set up CI, GitHub Actions, CI pipeline, automated tests, build workflow,
release workflow, KMP CI, XCFramework release, Gradle cache CI, PR checks,
continuous integration, continuous delivery, CD pipeline, GitHub workflow YAML,
automate build, merge checks, branch protection, automated release, deploy workflow,
publish to Maven Central, Maven publish, release notes, changelog, git-cliff, Doppler secrets,
versioning, semantic versioning, bump version, vanniktech publish plugin.

**Freshness rule:** GitHub Actions runner images and `actions/setup-java` / `gradle/actions` versions
change frequently — recheck pinned versions and `runs-on` labels before using this skill in a new project.

---

## Recommendation First

Default to **two workflow files: `ci.yml` (PR matrix) + `release.yml` (tag-triggered XCFramework)**.

Why:
- per-target jobs (Android, iOS, Desktop, Web) run in parallel and give clear failure attribution
- a separate release workflow keeps tag-triggered publishing decoupled from PR validation
- Gradle cache restore/save steps are critical — without them, KMP CI is prohibitively slow

Set up Gradle caching and the `actions/setup-java` step before anything else.
Skip platform jobs only when the product explicitly excludes that target.

---

## Overview

Two workflow files:

| File | Trigger | Jobs |
|---|---|---|
| `.github/workflows/ci.yml` | push to `main`, all PRs | `lint`, `test-android`, `test-ios`, `test-desktop`, `test-web` |
| `.github/workflows/release.yml` | push tag `v*` | `build-xcframework` |

---

## Step 1: Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:

  # ─── Lint ───────────────────────────────────────────────────────────────────
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

      - name: Run lint
        run: ./gradlew lint --continue

      - name: Upload lint reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: lint-reports
          path: '**/build/reports/lint-results*.html'

  # ─── Android Tests ──────────────────────────────────────────────────────────
  test-android:
    name: Android Tests
    runs-on: ubuntu-latest
    needs: lint
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

      - name: Run Android unit tests
        run: ./gradlew testDebugUnitTest --continue

      - name: Run KMP common tests (JVM)
        run: ./gradlew allTests --continue

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: android-test-results
          path: '**/build/reports/tests/'

  # ─── iOS Tests ──────────────────────────────────────────────────────────────
  test-ios:
    name: iOS Tests
    runs-on: macos-latest
    needs: lint
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

      - name: Run iOS simulator tests (iosSimulatorArm64)
        run: ./gradlew iosSimulatorArm64Test --continue

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ios-test-results
          path: '**/build/reports/tests/'

  # ─── Desktop Tests ──────────────────────────────────────────────────────────
  test-desktop:
    name: Desktop (JVM) Tests
    runs-on: ubuntu-latest
    needs: lint
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

      - name: Run Desktop (JVM) tests
        run: ./gradlew jvmTest --continue

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: desktop-test-results
          path: '**/build/reports/tests/'

  # ─── Web Tests ──────────────────────────────────────────────────────────────
  test-web:
    name: Web (JS + WasmJs) Tests
    runs-on: ubuntu-latest
    needs: lint
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

      - name: Run JS tests
        run: ./gradlew jsTest --continue

      - name: Run WasmJs tests
        run: ./gradlew wasmJsTest --continue

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: web-test-results
          path: '**/build/reports/tests/'
```

---

## Step 2: Create `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:

  # ─── Build XCFramework ──────────────────────────────────────────────────────
  build-xcframework:
    name: Build XCFramework
    runs-on: macos-latest
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

      - name: Build XCFramework
        run: ./gradlew :shared:assembleReleaseXCFramework

      - name: Upload XCFramework artifact
        uses: actions/upload-artifact@v4
        with:
          name: XCFramework-${{ github.ref_name }}
          path: shared/build/XCFrameworks/release/
          retention-days: 30

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: shared/build/XCFrameworks/release/**
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Step 3: Gradle configuration for CI

Add to `gradle.properties`:

```properties
# CI performance
org.gradle.configuration-cache=true
org.gradle.parallel=true
org.gradle.caching=true

# Kotlin daemon — reduce memory on CI
kotlin.daemon.jvm.options=-Xmx2g
```

Add to root `build.gradle.kts` — ensures all modules report test results in a CI-friendly format:

```kotlin
subprojects {
    tasks.withType<AbstractTestTask>().configureEach {
        testLogging {
            events("passed", "skipped", "failed")
            showStandardStreams = false
        }
    }
}
```

---

## Step 4: Required GitHub secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Purpose |
|---|---|
| `GRADLE_ENCRYPTION_KEY` | Encrypts the Gradle build cache. Generate with: `openssl rand -base64 16` |

No other secrets are required for a public repo. For private repos, `GITHUB_TOKEN` is auto-provided.

---

## Step 5: Enable Gradle build cache on CI

The `gradle/actions/setup-gradle@v4` action automatically:
- Caches `~/.gradle/caches` between runs keyed on dependency hash
- Uploads/restores the Gradle configuration cache
- Reports cache hit/miss in the Actions summary

No extra `actions/cache` step is needed.

---

## Step 6: XCFramework Gradle config (shared module)

Ensure `:shared` (or your main shared KMP module) configures the XCFramework in its `build.gradle.kts`:

```kotlin
kotlin {
    listOf(
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "Shared"
            isStatic = true
        }
    }
}
```

The `assembleReleaseXCFramework` task is auto-generated by the KMP plugin.

---

---

## Maven Central Publishing

### Version source of truth

Keep `VERSION` in `gradle.properties` as the single source of truth:

```properties
# gradle.properties
#Library version — bump here before publishing
VERSION=0.2.0
```

Each publishable module reads it:

```kotlin
// build.gradle.kts
val libraryVersion = (project.findProperty("VERSION") as? String) ?: "0.2.0"

mavenPublishing {
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)
    if (project.hasProperty("signing.keyId") || project.hasProperty("signingKey")) signAllPublications()
    coordinates("io.github.yourhandle", "your-artifact", libraryVersion)
}
```

Keep the fallback `?: "x.y.z"` in sync with `gradle.properties` — a stale fallback silently publishes the wrong version when `-PVERSION` is omitted.

**Gradle automatically maps `ORG_GRADLE_PROJECT_*` env vars to project properties.** Store Maven credentials as:
- `ORG_GRADLE_PROJECT_mavenCentralUsername`
- `ORG_GRADLE_PROJECT_mavenCentralPassword`
- `ORG_GRADLE_PROJECT_signingKey` (ASCII-armored GPG key, optional)
- `ORG_GRADLE_PROJECT_signingPassword` (optional)

No `-P` flags needed in the publish command when these env vars are set.

---

### Doppler integration (local publish script)

Store secrets in Doppler instead of `~/.gradle/gradle.properties` or shell exports.

**`.doppler.yaml`** (project root, committed):
```yaml
setup:
  project: your-project
  config: prd
```

**`.env`** (project root, gitignored — for local use):
```
DOPPLER_TOKEN=dp.st.xxxxxxxxxxxxxxxxxxxx
```

**`scripts/publish-maven.sh`** — full publish script pattern:

```bash
#!/usr/bin/env bash
# Publishes to Maven Central using Doppler for credentials.
# Reads VERSION from gradle.properties, then auto-bumps patch after success.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PROPS="$ROOT_DIR/gradle.properties"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

VERSION="$(grep -E '^VERSION=' "$PROPS" | cut -d= -f2 | tr -d '[:space:]')"
TAG="v${VERSION}"

# Load .env if DOPPLER_TOKEN not already in env
if [[ -z "${DOPPLER_TOKEN:-}" && -f "$ROOT_DIR/.env" ]]; then
  set -o allexport; source "$ROOT_DIR/.env"; set +o allexport
fi

DOPPLER_ARGS=("run")
[[ -n "${DOPPLER_TOKEN:-}" ]] && DOPPLER_ARGS+=(--token "$DOPPLER_TOKEN")
DOPPLER_ARGS+=(--)

# Generate changelog, tag, publish, create GitHub release, then bump patch
RELEASE_NOTES="$(git-cliff --tag "$TAG" --unreleased --strip all 2>/dev/null)"
$DRY_RUN && { echo "$RELEASE_NOTES"; exit 0; }

git-cliff --tag "$TAG" --output "$ROOT_DIR/CHANGELOG.md"
git add CHANGELOG.md && git commit -m "chore(release): ${TAG}" || true
git tag -a "$TAG" -m "Release ${TAG}"
git push origin main --tags

doppler "${DOPPLER_ARGS[@]}" \
  "$ROOT_DIR/gradlew" -p "$ROOT_DIR" \
  publishAllPublicationsToMavenCentralRepository \
  -PVERSION="$VERSION" --no-daemon

gh release create "$TAG" --title "Graphyn ${VERSION}" --notes "$RELEASE_NOTES"

# Auto-bump patch
IFS='.' read -r major minor patch <<< "$VERSION"
NEXT="${major}.${minor}.$((patch + 1))"
sed -i '' "s/^VERSION=.*/VERSION=${NEXT}/" "$PROPS"
git add gradle.properties && git commit -m "chore: bump version to ${NEXT}"
git push origin main
```

**Versioning workflow:**
- Patch releases: just run `./scripts/publish-maven.sh` — reads current VERSION, publishes, auto-bumps patch
- Minor/major milestone: manually edit `gradle.properties` (`VERSION=0.3.0`), then run the script
- Dry run (preview changelog only): `./scripts/publish-maven.sh --dry-run`

**Note:** Maven Central (Sonatype Central Portal) does not accept `-SNAPSHOT` versions. For pre-release
artifacts, use GitHub Packages or JitPack.

---

## Changelog with git-cliff

**Install:** `brew install git-cliff`

**`cliff.toml`** (project root, committed):

```toml
[changelog]
header = """
# Changelog\n
All notable changes are documented here.\n
"""
body = """
{% if version %}\
## [{{ version | trim_start_matches(pat="v") }}] — {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group }}
{% for commit in commits %}
- {% if commit.scope %}**{{ commit.scope }}:** {% endif %}{{ commit.message | upper_first }}\
  {% if commit.breaking %} ⚠ BREAKING{% endif %}
{%- endfor %}
{% endfor %}\n
"""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
  { message = "^feat",     group = "Features" },
  { message = "^fix",      group = "Bug Fixes" },
  { message = "^refactor", group = "Refactoring" },
  { message = "^perf",     group = "Performance" },
  { message = "^test",     group = "Testing" },
  { message = "^docs",     group = "Documentation" },
  { message = "^build",    group = "Build" },
  { message = "^ci",       group = "CI" },
  { message = "^chore",    skip = true },
]
filter_commits = true
tag_pattern = "v[0-9].*"
sort_commits = "oldest"
```

**Commands:**
```bash
git-cliff --output CHANGELOG.md                        # full history
git-cliff --tag v0.2.0 --unreleased --strip all        # release notes for next tag
git-cliff --tag v0.2.0 --output CHANGELOG.md           # update file and tag it
```

Requires [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `refactor:`, etc.

---

## Step 7: Required secrets for publishing

Add these in **Settings → Secrets and variables → Actions** when running publish from CI:

| Secret | Purpose |
|---|---|
| `GRADLE_ENCRYPTION_KEY` | Encrypts the Gradle build cache. Generate: `openssl rand -base64 16` |
| `DOPPLER_TOKEN` | Doppler service token — injects Maven + signing credentials at runtime |

Store `ORG_GRADLE_PROJECT_mavenCentralUsername`, `ORG_GRADLE_PROJECT_mavenCentralPassword`,
`ORG_GRADLE_PROJECT_signingKey`, and `ORG_GRADLE_PROJECT_signingPassword` **in Doppler**, not
directly as GitHub secrets. The publish script fetches them via `doppler run --token $DOPPLER_TOKEN`.

---

## Guidelines

- Always use `concurrency` with `cancel-in-progress: true` on CI to cancel stale PR runs
- Run `lint` as a gate before tests — fail fast on obvious issues
- Use `macos-latest` only for iOS jobs (billable minutes ~10× more than Ubuntu)
- Android, Desktop, and Web tests all run on `ubuntu-latest` — fast and cheap
- Use `gradle/actions/setup-gradle@v4` — it supersedes the older `gradle/gradle-build-action`
- Never store secrets in `gradle.properties` — use GitHub secrets and inject via `env:`
- Set `retention-days` on artifacts to avoid storage accumulation

## Verification

1. Open a draft PR — confirm `lint`, `test-android`, `test-ios`, `test-desktop`, `test-web` all trigger
2. Push a `v0.0.1` tag — confirm `build-xcframework` triggers and artifact appears in release
3. Check Actions summary for Gradle cache hit rates after the second run

---

## Common Anti-Patterns

- running all targets in one job — a single iOS failure blocks Android feedback; use per-target jobs
- skipping Gradle cache setup — KMP builds take 10–20 min cold; caching brings it under 5 min
- storing secrets in `gradle.properties` — use GitHub Secrets or Doppler; never commit credentials
- using `actions/upload-artifact` without `retention-days` — storage accumulates quickly
- triggering the release job on every push instead of on version tags — publishes pre-release builds
- stale fallback version in `build.gradle.kts` (`?: "0.1.0"`) — when `VERSION` property is missing,
  Gradle silently publishes the wrong version; keep the fallback in sync with `gradle.properties`
- publishing `-SNAPSHOT` to Maven Central — Sonatype Central Portal rejects snapshot versions;
  use GitHub Packages or JitPack for pre-release artifacts
- storing Maven credentials as plain GitHub secrets mapped via `-P` flags — use
  `ORG_GRADLE_PROJECT_*` env vars instead (Gradle maps them automatically, no `-P` needed)
- mixing version bumping into CI — version is the publisher's decision; keep auto-bump in the
  local publish script, not in GitHub Actions

If CI is slow, check the Gradle cache hit rate in the Actions summary before making other changes.

---

## Related Skills

- `kotlin-multiplatform-feature-scaffold` — the project structure CI builds and tests
- `kotlin-multiplatform-code-quality` — Ktlint and Detekt checks run as CI gates
- `kotlin-multiplatform-xcframework-spm` — XCFramework release job assembled and published from CI
- `kotlin-multiplatform-roborazzi` — screenshot diff CI job that runs on pull requests

## External tools referenced

- [vanniktech/gradle-maven-publish-plugin](https://github.com/vanniktech/gradle-maven-publish-plugin) — `com.vanniktech.maven.publish` plugin for Sonatype Central Portal
- [git-cliff](https://git-cliff.org) — changelog generator from Conventional Commits
- [Doppler](https://www.doppler.com) — secrets manager; CLI: `brew install dopplerhq/cli/doppler`
- [Sonatype Central Portal](https://central.sonatype.com) — Maven Central publishing dashboard

---

## Output Style

When asked about CI setup or GitHub Actions for KMP, respond in this order:
1. recommendation (matrix workflow: Android/iOS/Desktop/Web + XCFramework release job)
2. workflow structure (jobs and trigger events)
3. YAML snippet (one job block)
4. why that CI shape fits KMP targets
5. main alternative (single job, different CI provider)

Keep the YAML snippet to one job. Map to the user's actual module names and signing secrets when provided.

---

## Changelog

| Date | Change |
|---|---|
| 2026-06-06 | Initial release. |
