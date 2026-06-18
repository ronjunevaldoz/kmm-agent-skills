---
name: kotlin-multiplatform-roborazzi
description: >
  Sets up Roborazzi screenshot tests for KMP: captures @Preview composables on JVM/Desktop,
  commits golden images, and wires a CI diff job that fails the build on visual regressions.
  Replaces kotlin-multiplatform-testing-robot for UI regression testing.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-18'
  keywords:
    - Roborazzi
    - screenshot test
    - golden image
    - '@Preview'
    - JVM screenshot
    - visual regression
    - CI diff
    - KMP
    - Kotlin Multiplatform
    - Desktop JVM
---

## When to Use This Skill

Use when you need to:
- Capture screenshot golden images from `@Preview` composables on JVM
- Detect visual regressions automatically in CI
- Replace manual UI review with automated screenshot diffs
- Wire Roborazzi into a KMP Desktop/JVM module

**Trigger keywords:** screenshot test, Roborazzi, golden image, visual regression, preview screenshot,
UI test JVM, screenshot diff, CI visual test.

**Freshness rule:** Roborazzi is actively developed — the Gradle plugin API and the
`captureRoboImage` / `captureRoboGif` API change between minor versions. Recheck the
GitHub releases page before pinning a version.

---

## Recommendation First

Default to **Roborazzi on the JVM/Desktop target, driven by existing `@Preview` functions,
with golden images committed to the repo**.

Why:
- `@Preview` composables are already stateless (Screen/Content split) — zero extra test code to write
- JVM execution means no emulator, no AVD, no Xcode — fast and CI-friendly
- committed goldens make diffs visible in PR reviews as image files
- the same test task (`jvmTest`) that runs unit tests runs screenshot tests — one CI step

Only use Roborazzi on Android (`roborazziAndroid`) when you need Android-specific resources
that cannot render on JVM.

---

## Gradle Setup

### `libs.versions.toml`

```toml
[versions]
roborazzi = "1.29.0"

[libraries]
roborazzi = { module = "io.github.takahirom.roborazzi:roborazzi", version.ref = "roborazzi" }
roborazzi-compose = { module = "io.github.takahirom.roborazzi:roborazzi-compose", version.ref = "roborazzi" }
roborazzi-junit-rule = { module = "io.github.takahirom.roborazzi:roborazzi-junit-rule", version.ref = "roborazzi" }

[plugins]
roborazzi = { id = "io.github.takahirom.roborazzi", version.ref = "roborazzi" }
```

### `build-logic/convention/build.gradle.kts`

```kotlin
dependencies {
    implementation(libs.plugins.roborazzi.get().let { "${it.pluginId}:${it.pluginId}.gradle.plugin:${it.version}" })
}
```

### Convention plugin: `GROUP_ID.feature.ui.gradle.kts` — add Roborazzi

```kotlin
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
    id("io.github.takahirom.roborazzi")
}

// ... existing kotlin {} block ...

roborazzi {
    outputDir = project.file("src/jvmTest/snapshots")
}
```

### Feature `:ui` module `build.gradle.kts`

```kotlin
plugins {
    id("GROUP_ID.feature.ui")
}

kotlin {
    androidLibrary {
        namespace = "GROUP_ID.feature.FEATURE_NAME.ui"
    }

    sourceSets {
        jvmTest.dependencies {
            implementation(libs.roborazzi)
            implementation(libs.roborazzi.compose)
            implementation(libs.roborazzi.junit.rule)
            implementation(libs.kotlin.test)
        }
    }
}
```

---

## Writing a Screenshot Test

```kotlin
// :feature:auth:ui/src/jvmTest/kotlin/.../AuthContentScreenshotTest.kt
class AuthContentScreenshotTest {

    @get:Rule
    val roborazziRule = RoborazziRule(
        captureRoot = captureRoboImage(),
    )

    @Test
    fun authContentLoading() {
        captureRoboImage("auth_content_loading.png") {
            AppTheme {
                AuthContent(state = AuthUiState.Loading, onIntent = {})
            }
        }
    }

    @Test
    fun authContentSuccess() {
        captureRoboImage("auth_content_success.png") {
            AppTheme {
                AuthContent(state = AuthUiState.Success(PreviewData.user), onIntent = {})
            }
        }
    }

    @Test
    fun authContentError() {
        captureRoboImage("auth_content_error.png") {
            AppTheme {
                AuthContent(state = AuthUiState.Error("Session expired"), onIntent = {})
            }
        }
    }
}
```

Each `captureRoboImage` call writes a PNG to `src/jvmTest/snapshots/`.

---

## Recording Golden Images

```bash
# Record (first run — write goldens)
./gradlew :feature:auth:ui:jvmTest -PrecordRoborazzi

# Verify (subsequent runs — diff against goldens)
./gradlew :feature:auth:ui:jvmTest

# Verify all feature UI modules at once
./gradlew jvmTest
```

Commit the `snapshots/` directory to git. PRs that change UI will produce image diffs in the PR review.

---

## CI Integration

Add a screenshot diff job to `.github/workflows/ci.yml`:

```yaml
test-screenshot:
  name: Screenshot Tests (JVM)
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

    - name: Run screenshot tests
      run: ./gradlew jvmTest

    - name: Upload screenshot diffs on failure
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: screenshot-diffs
        path: '**/src/jvmTest/snapshots/**/*_compare.png'
```

When a visual regression occurs, the CI job uploads diff images as artifacts — reviewers
see the before/after side-by-side without running the tests locally.

---

## Related Skills

- `kotlin-multiplatform-preview-driven-development` — the `@Preview` workflow that feeds into Roborazzi
- `kotlin-multiplatform-presenter-module` — the Screen/Content split that makes `Content` injectable with fixed state
- `kotlin-multiplatform-unit-testing` — Roborazzi covers `:ui`; unit tests cover `:presenter` and `:domain`
- `kotlin-multiplatform-ci-github-actions` — where the CI screenshot job is wired

---

## Common Anti-Patterns

- testing `Screen` composables (with a real ViewModel) — inject fixed `UiState` into `Content` instead
- not committing golden images — CI has nothing to diff against; diffs only work with committed goldens
- running Roborazzi on Android instead of JVM — slower, needs emulator; use `jvmTest` unless you need Android-specific resources
- one test class per state instead of one class per component — excessive boilerplate; group all states for a component in one test class
- forgetting to record new goldens after a planned UI change — run with `-PrecordRoborazzi` and commit the updated images

If a screenshot test fails unexpectedly after a dependency upgrade, re-record goldens and commit —
font rendering can shift between Compose versions.

---

## Output Style

When asked about screenshot testing or visual regression for KMP, respond in this order:
1. Gradle plugin + dependency setup (toml + build.gradle.kts)
2. test class with `captureRoboImage` calls
3. record vs verify commands
4. CI job snippet
5. golden image commit strategy
