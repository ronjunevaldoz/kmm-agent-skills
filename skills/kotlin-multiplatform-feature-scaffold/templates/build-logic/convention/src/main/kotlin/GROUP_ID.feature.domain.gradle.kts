import org.jetbrains.kotlin.gradle.dsl.JvmTarget

/**
 * Convention plugin for :feature:*:domain modules.
 *
 * Pure KMP — use cases and business logic.
 * No Compose, no network, no persistence.
 * Depends on :feature:*:api (declared per-module).
 *
 * Each module must add its own namespace:
 *   kotlin { androidLibrary { namespace = "com.example.feature.auth.domain" } }
 */
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
    id("org.jetbrains.kotlin.plugin.koin")
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    androidLibrary {
        compileSdk = libs.versions.android.compileSdk.get().toInt()
        minSdk = libs.versions.android.minSdk.get().toInt()

        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.koin.core)
            // :feature:*:api dependency declared per-module
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
