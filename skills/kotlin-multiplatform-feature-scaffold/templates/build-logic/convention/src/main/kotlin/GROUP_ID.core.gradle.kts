import org.jetbrains.kotlin.gradle.dsl.JvmTarget

/**
 * Convention plugin for :core:* modules.
 *
 * Base KMP library — utilities, shared abstractions, base classes.
 * Apply additional plugins per-module as needed (e.g. sqldelight for :core:database).
 *
 * Each module must add its own namespace:
 *   kotlin { androidLibrary { namespace = "com.example.core.common" } }
 */
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
    id("org.jetbrains.kotlin.plugin.serialization")
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
            implementation(libs.kotlinx.serialization)
            implementation(libs.kotlinx.datetime)
            implementation(libs.koin.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
