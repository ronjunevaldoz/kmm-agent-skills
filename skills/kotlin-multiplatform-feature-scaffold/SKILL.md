---
name: kotlin-multiplatform-feature-scaffold
description: >
  Scaffolds a production-ready Kotlin Multiplatform (KMP) multi-feature module
  architecture. Creates a full project from the kmp-wizard AGP 9 baseline or adds
  a new feature module group (:api/:domain/:data/:ui) to an existing KMP project.
  Uses AGP 9+, build-logic convention plugins, version catalog groups, Compose
  Multiplatform, and Koin 4 (annotated or manual DI).
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-06'
  keywords:
    - Kotlin Multiplatform
    - KMP
    - KMM
    - multi-module
    - feature module
    - AGP 9
    - build-logic
    - convention plugins
    - Koin 4
    - Compose Multiplatform
    - CMP
    - version catalog
---

## Overview

This skill produces a KMP multi-feature module architecture with the following decisions
baked in:

- **AGP 9 minimum** using the new `com.android.kotlin.multiplatform.library` plugin
  (replaces the old `kotlin("multiplatform")` + `com.android.library` pair for library modules)
- **build-logic** as a Gradle included build providing precompiled convention plugins
- **Version catalog** (`gradle/libs.versions.toml`) with proper group prefixes and bundles
- **Feature split**: every feature is 4 modules — `:api` / `:domain` / `:data` / `:ui`
- **Core modules**: `:core:common`, `:core:network`, `:core:database`, `:core:ui`
- **Compose Multiplatform (CMP)** as the default shared UI layer (CMP-first)
- **Koin 4** DI — annotated (default, via Koin Compiler Plugin) or manual

### Module dependency graph (per feature)

```
:feature:<name>:api        pure KMP — interfaces, models, nav contracts
        ↑
:feature:<name>:domain     pure KMP — use cases, business logic
        ↑ (depends on :api)
:feature:<name>:data       KMP + platform impls — Ktor, SQLDelight repositories
        ↑ (depends on :api, NOT on :domain)
:feature:<name>:ui         CMP — Compose screens, ViewModels
        (depends on :domain + :api)
```

`:data` and `:domain` are siblings. Neither depends on the other.

---

## Mode Detection

Before doing anything, inspect the working directory:

- **New Project mode**: no `settings.gradle.kts` or no `build-logic/` directory found.
  Scaffold the full project from scratch.
- **Add Feature mode**: existing KMP project detected (has `settings.gradle.kts` and
  `build-logic/`). Only scaffold the new feature module group.

---

## Step 1: Gather User Input

**Always ask before creating any files.** Collect these values from the user:

| Input | Description | Example |
|---|---|---|
| `PROJECT_NAME` | Root project name (PascalCase) | `MyAwesomeApp` |
| `GROUP_ID` | Base package / Maven group ID | `com.example.myapp` |
| `FEATURE_NAME` | First feature to scaffold (snake_case) | `auth` |
| `DI_APPROACH` | `annotated` (default) or `manual` | `annotated` |

In **Add Feature mode**, only `GROUP_ID`, `FEATURE_NAME`, and `DI_APPROACH` are needed.

---

## Step 2: Version Reference

Use these exact versions. Do not substitute without explicit user confirmation.

```toml
agp                   = "9.0.1"
kotlin                = "2.4.0"
ksp                   = "2.3.9"
koin                  = "4.2.1"
koin-annotations      = "2.3.1"
ktor                  = "3.1.3"
sqldelight            = "2.0.2"
compose-multiplatform = "1.11.1"
buildkonfig           = "0.21.2"
android-compileSdk    = "36"
android-minSdk        = "24"
android-targetSdk     = "36"
androidx-lifecycle    = "2.11.0-beta01"
androidx-activity     = "1.13.0"
coroutines            = "1.10.2"
serialization         = "1.11.0"
datetime              = "0.8.0"
```

> **Note on Koin DI**: Koin 4.1+ ships a native Kotlin Compiler Plugin
> (`org.jetbrains.kotlin.plugin.koin`) that replaces the KSP-based annotation processor
> for KMP projects — no per-platform KSP configuration needed. Use this for `annotated`
> mode. For `manual` mode, skip the plugin entirely and write explicit `module {}` blocks.

> **Note on BuildKonfig**: `com.codingfeline.buildkonfig` is the KMP equivalent of
> Android's `BuildConfig`. It generates a `BuildKonfig` object accessible from
> `commonMain`, `androidMain`, and `iosMain`. Configure it in `:androidApp`'s
> `build.gradle.kts` using a `buildkonfig {}` block.

---

## BuildKonfig Configuration

Add the following block to `:androidApp/build.gradle.kts` after applying `GROUP_ID.android.app`:

```kotlin
buildkonfig {
    packageName = "GROUP_ID"

    defaultConfigs {
        buildConfigField(STRING, "APP_NAME", "PROJECT_NAME")
        buildConfigField(STRING, "BASE_URL", "https://api.example.com")
        buildConfigField(BOOLEAN, "DEBUG", "false")
    }

    targetConfigs {
        create("debug") {
            buildConfigField(BOOLEAN, "DEBUG", "true")
            buildConfigField(STRING, "BASE_URL", "https://api-staging.example.com")
        }
    }
}
```

Access in common code:
```kotlin
// commonMain
val baseUrl = BuildKonfig.BASE_URL
val isDebug = BuildKonfig.DEBUG
```

---

## Step 3: New Project Scaffold

### 3a. Full directory structure to create

```
<root>/
├── build-logic/
│   ├── settings.gradle.kts
│   └── convention/
│       ├── build.gradle.kts
│       └── src/main/kotlin/
│           ├── GROUP_ID.android.app.gradle.kts
│           ├── GROUP_ID.core.gradle.kts
│           ├── GROUP_ID.feature.api.gradle.kts
│           ├── GROUP_ID.feature.domain.gradle.kts
│           ├── GROUP_ID.feature.data.gradle.kts
│           └── GROUP_ID.feature.ui.gradle.kts
├── core/
│   ├── common/build.gradle.kts          (applies GROUP_ID.core)
│   ├── network/build.gradle.kts         (applies GROUP_ID.core)
│   ├── database/build.gradle.kts        (applies GROUP_ID.core)
│   └── ui/build.gradle.kts             (applies GROUP_ID.core + compose)
├── feature/
│   └── <FEATURE_NAME>/
│       ├── api/build.gradle.kts
│       ├── domain/build.gradle.kts
│       ├── data/build.gradle.kts
│       └── ui/build.gradle.kts
├── androidApp/
│   └── build.gradle.kts                (applies GROUP_ID.android.app)
├── iosApp/                              (Xcode project — copy from kmp-wizard)
├── gradle/
│   └── libs.versions.toml
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
├── gradlew
└── gradlew.bat
```

### 3b. Root `settings.gradle.kts`

Replace `PROJECT_NAME` and include all modules:

```kotlin
rootProject.name = "PROJECT_NAME"
enableFeaturePreview("TYPESAFE_PROJECT_ACCESSORS")

pluginManagement {
    includeBuild("build-logic")
    repositories {
        google {
            mavenContent {
                includeGroupAndSubgroups("androidx")
                includeGroupAndSubgroups("com.android")
                includeGroupAndSubgroups("com.google")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google {
            mavenContent {
                includeGroupAndSubgroups("androidx")
                includeGroupAndSubgroups("com.android")
                includeGroupAndSubgroups("com.google")
            }
        }
        mavenCentral()
    }
}

include(":androidApp")
include(":core:common")
include(":core:network")
include(":core:database")
include(":core:ui")
include(":feature:FEATURE_NAME:api")
include(":feature:FEATURE_NAME:domain")
include(":feature:FEATURE_NAME:data")
include(":feature:FEATURE_NAME:ui")
```

### 3c. Root `build.gradle.kts`

```kotlin
// Top-level build file. Convention plugins handle all module configuration.
plugins {
    alias(libs.plugins.androidApplication) apply false
    alias(libs.plugins.androidKmpLibrary) apply false
    alias(libs.plugins.kotlinMultiplatform) apply false
    alias(libs.plugins.composeMultiplatform) apply false
    alias(libs.plugins.composeCompiler) apply false
    alias(libs.plugins.ksp) apply false
    alias(libs.plugins.sqldelight) apply false
    alias(libs.plugins.koin) apply false
}
```

### 3d. `gradle.properties`

```properties
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
org.gradle.configuration-cache=true
org.gradle.parallel=true
kotlin.code.style=official
```

---

## Step 4: build-logic Setup

### 4a. `build-logic/settings.gradle.kts`

```kotlin
dependencyResolutionManagement {
    repositories {
        google {
            mavenContent {
                includeGroupAndSubgroups("androidx")
                includeGroupAndSubgroups("com.android")
                includeGroupAndSubgroups("com.google")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
include(":convention")
```

### 4b. `build-logic/convention/build.gradle.kts`

```kotlin
plugins {
    `kotlin-dsl`
}

dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.compose.gradlePlugin)
    compileOnly(libs.ksp.gradlePlugin)
    compileOnly(libs.sqldelight.gradlePlugin)
}

// Register precompiled script plugins
gradlePlugin {
    plugins {
        register("kmmAndroidApp") {
            // Replace GROUP_ID with your actual group ID (e.g. com.example.myapp)
            id = "GROUP_ID.android.app"
            implementationClass = "KmmAndroidAppPlugin"
        }
    }
}
```

> **Note**: The precompiled `.gradle.kts` files in `src/main/kotlin/` are automatically
> registered by `kotlin-dsl`. The `gradlePlugin` block above is only needed for any
> class-based plugins. Prefer precompiled script plugins for all convention plugins.

---

## Step 5: Convention Plugin Templates

> **IMPORTANT — file naming**: With Gradle precompiled script plugins, the file name IS
> the plugin ID. When scaffolding, rename every template file by replacing `GROUP_ID` with
> your actual reversed-domain group ID (dots are valid in filenames here).
>
> Example for `GROUP_ID = com.example.myapp`:
> - `GROUP_ID.feature.api.gradle.kts` → `com.example.myapp.feature.api.gradle.kts`
> - `GROUP_ID.android.app.gradle.kts` → `com.example.myapp.android.app.gradle.kts`
> - etc.
>
> The template folder `templates/build-logic/convention/src/main/kotlin/` contains
> all six files pre-named with the `GROUP_ID` placeholder for this purpose.

### `GROUP_ID.feature.api.gradle.kts`
Pure KMP — no Compose, no Koin. Exposes interfaces, sealed models, navigation contracts.

```kotlin
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    androidLibrary {
        compileSdk = 36
        minSdk = 24
        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}
```

### `GROUP_ID.feature.domain.gradle.kts`
Pure KMP — use cases and business logic. No Compose, no data layer deps.

```kotlin
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    androidLibrary {
        compileSdk = 36
        minSdk = 24
        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.koin.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
```

### `GROUP_ID.feature.data.gradle.kts`
KMP + platform implementations — Ktor for networking, SQLDelight for persistence.

```kotlin
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
    id("app.cash.sqldelight")
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    androidLibrary {
        compileSdk = 36
        minSdk = 24
        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.koin.core)
            implementation(libs.bundles.ktor.common)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(libs.sqldelight.android.driver)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
            implementation(libs.ktor.client.mock)
        }
    }
}
```

### `GROUP_ID.feature.ui.gradle.kts`
CMP — Compose Multiplatform screens and ViewModels with Koin.

```kotlin
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    androidLibrary {
        compileSdk = 36
        minSdk = 24
        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
        androidResources {
            enable = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
            implementation(compose.components.uiToolingPreview)
            implementation(libs.androidx.lifecycle.viewmodelCompose)
            implementation(libs.androidx.lifecycle.runtimeCompose)
            implementation(libs.koin.core)
            implementation(libs.koin.compose)
            implementation(libs.koin.composeViewModel)
        }
        androidMain.dependencies {
            implementation(libs.koin.android)
            implementation(compose.uiTooling)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}
```

### `GROUP_ID.core.gradle.kts`
Base for all `:core:*` modules. Apply additional plugins per-module as needed.

```kotlin
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    androidLibrary {
        compileSdk = 36
        minSdk = 24
        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.koin.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}
```

### `GROUP_ID.android.app.gradle.kts`
Android application entry point.

```kotlin
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.koin")
}

android {
    compileSdk = 36

    defaultConfig {
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
}

dependencies {
    implementation(libs.koin.android)
    implementation(libs.koin.androidx.compose)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.viewmodelCompose)
}
```

---

## Step 6: Feature Module `build.gradle.kts` Templates

For each new feature `FEATURE_NAME` with group `GROUP_ID`, create these four files.
Replace `FEATURE_NAME` and `GROUP_ID` with actual values.

### `:feature:FEATURE_NAME:api/build.gradle.kts`

```kotlin
plugins {
    id("GROUP_ID.feature.api")
}

kotlin {
    androidLibrary {
        namespace = "GROUP_ID.feature.FEATURE_NAME.api"
    }
}
```

### `:feature:FEATURE_NAME:domain/build.gradle.kts`

```kotlin
plugins {
    id("GROUP_ID.feature.domain")
}

kotlin {
    androidLibrary {
        namespace = "GROUP_ID.feature.FEATURE_NAME.domain"
    }

    sourceSets {
        commonMain.dependencies {
            implementation(projects.feature.FEATURE_NAME.api)
        }
    }
}
```

### `:feature:FEATURE_NAME:data/build.gradle.kts`

```kotlin
plugins {
    id("GROUP_ID.feature.data")
}

kotlin {
    androidLibrary {
        namespace = "GROUP_ID.feature.FEATURE_NAME.data"
    }

    sourceSets {
        commonMain.dependencies {
            implementation(projects.feature.FEATURE_NAME.api)
            implementation(projects.core.network)
            implementation(projects.core.database)
        }
    }
}
```

### `:feature:FEATURE_NAME:ui/build.gradle.kts`

```kotlin
plugins {
    id("GROUP_ID.feature.ui")
}

kotlin {
    androidLibrary {
        namespace = "GROUP_ID.feature.FEATURE_NAME.ui"
    }

    sourceSets {
        commonMain.dependencies {
            implementation(projects.feature.FEATURE_NAME.api)
            implementation(projects.feature.FEATURE_NAME.domain)
            implementation(projects.core.ui)
        }
    }
}
```

---

## Step 7: Koin DI Patterns

### Annotated mode (default — Koin Compiler Plugin)

Apply `id("org.jetbrains.kotlin.plugin.koin")` in the module's convention plugin or
directly in the build.gradle.kts. Then use annotations:

```kotlin
// In :feature:auth:domain
@Single
class GetUserUseCase(private val repo: UserRepository) {
    operator fun invoke(id: String): Flow<User> = repo.getUser(id)
}

// In :feature:auth:ui
@KoinViewModel
class AuthViewModel(private val getUser: GetUserUseCase) : ViewModel() { ... }
```

Auto-generated modules are collected in `AppModule`. Declare in `:androidApp`:

```kotlin
startKoin {
    androidContext(this@App)
    modules(AppModule.module)  // generated by Koin Compiler Plugin
}
```

### Manual mode

Write explicit `module {}` blocks per feature. Convention: one `<FeatureName>Module.kt`
in each `:domain` and `:data` module.

```kotlin
// :feature:auth:domain/src/commonMain/kotlin/.../AuthDomainModule.kt
val authDomainModule = module {
    factory { GetUserUseCase(get()) }
}

// :feature:auth:ui/src/commonMain/kotlin/.../AuthUiModule.kt
val authUiModule = module {
    viewModel { AuthViewModel(get()) }
}
```

Declare all modules in `:androidApp`:

```kotlin
startKoin {
    androidContext(this@App)
    modules(authDomainModule, authUiModule, /* ... */)
}
```

---

## Step 8: Add Feature Mode

When adding a feature to an existing project:

1. Create the four module directories:
   ```
   feature/<FEATURE_NAME>/api/
   feature/<FEATURE_NAME>/domain/
   feature/<FEATURE_NAME>/data/
   feature/<FEATURE_NAME>/ui/
   ```
2. Write `build.gradle.kts` in each (see Step 6 templates above).
3. Add to `settings.gradle.kts`:
   ```kotlin
   include(":feature:FEATURE_NAME:api")
   include(":feature:FEATURE_NAME:domain")
   include(":feature:FEATURE_NAME:data")
   include(":feature:FEATURE_NAME:ui")
   ```
4. Wire into `:androidApp` dependencies:
   ```kotlin
   implementation(projects.feature.FEATURE_NAME.ui)
   ```

---

## Step 9: Source File Stubs

After creating build files, generate stub source files so each module compiles:

### `:feature:FEATURE_NAME:api`
```
src/commonMain/kotlin/GROUP_ID/feature/FEATURE_NAME/api/
    FEATURE_NAMERepository.kt        ← interface
    FEATURE_NAMEModel.kt             ← data class(es)
    FEATURE_NAMENavigation.kt        ← nav route objects/sealed class
```

### `:feature:FEATURE_NAME:domain`
```
src/commonMain/kotlin/GROUP_ID/feature/FEATURE_NAME/domain/
    Get<FEATURE_NAME>UseCase.kt
    di/FEATURE_NAME_DomainModule.kt  ← only in manual mode
```

### `:feature:FEATURE_NAME:data`
```
src/commonMain/kotlin/GROUP_ID/feature/FEATURE_NAME/data/
    FEATURE_NAMERepositoryImpl.kt
    remote/FEATURE_NAMERemoteDataSource.kt
    local/FEATURE_NAMELocalDataSource.kt
    di/FEATURE_NAME_DataModule.kt    ← only in manual mode
```

### `:feature:FEATURE_NAME:ui`
```
src/commonMain/kotlin/GROUP_ID/feature/FEATURE_NAME/ui/
    FEATURE_NAMEScreen.kt
    FEATURE_NAMEViewModel.kt
    di/FEATURE_NAME_UiModule.kt      ← only in manual mode
```

---

## Step 10: Verification

After scaffolding, verify in order:

1. `./gradlew help` — Gradle resolves the build without errors
2. `./gradlew :feature:FEATURE_NAME:api:compileKotlinMetadata` — KMP common compiles
3. `./gradlew :androidApp:assembleDebug --dry-run` — Android wiring is correct
4. Confirm all `include()` entries in `settings.gradle.kts` match actual directories
5. Confirm no module references another module that it should not (enforce the layer rule:
   `:ui` must not depend on `:data`; `:domain` must not depend on `:data`)

---

## Guidelines

- Never create a `buildSrc/` directory — use `build-logic` instead
- Never use `id("kotlin-android")` — use `id("org.jetbrains.kotlin.android")` (AGP 9 requirement)
- Never add `android.builtInKotlin` or `android.newDsl` to `gradle.properties` — these are AGP 9 defaults
- Always use `androidLibrary {}` inside `kotlin {}` for library modules, not a standalone `android {}` block
- Always use TYPESAFE_PROJECT_ACCESSORS (`projects.feature.auth.api`) — never string-based `:feature:auth:api`
- Keep `:api` modules minimal — no DI framework dependencies, no platform deps
- Namespace format: `GROUP_ID.module.path` (e.g. `com.example.app.feature.auth.api`)
