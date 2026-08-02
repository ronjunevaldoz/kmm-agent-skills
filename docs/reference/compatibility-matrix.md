# KMP Dependency Compatibility Matrix

Tracks the pinned versions used across all skills and documents known hard constraints between them.
Update this table whenever a version is bumped in any skill.

---

## Pinned Versions

| Library | Version | Artifact / Plugin ID |
|---|---|---|
| Kotlin | `2.4.0` | `org.jetbrains.kotlin.*` |
| AGP | `9.2.0` | `com.android.application` / `com.android.kotlin.multiplatform.library` |
| Gradle Wrapper | `8.14` | `gradle/wrapper/gradle-wrapper.properties` |
| KSP | `2.4.0-2.0.0` | `com.google.devtools.ksp` |
| Compose Multiplatform | `1.11.1` | `org.jetbrains.compose` |
| Coroutines | `1.11.0` | `org.jetbrains.kotlinx:kotlinx-coroutines-core` |
| AndroidX Lifecycle | `2.11.0` | `org.jetbrains.androidx.lifecycle:lifecycle-viewmodel` |
| Navigation Compose (KMP) | `2.9.2` | `org.jetbrains.androidx.navigation:navigation-compose` |
| Koin | `4.2.2` | `io.insert-koin:koin-core` |
| Ktor | `3.5.0` | `io.ktor:ktor-client-core` |
| SQLDelight | `2.3.2` | `app.cash.sqldelight` |
| Decompose | `3.5.0` | `com.arkivanov.decompose:decompose` |
| BuildKonfig | `0.22.0` | `com.codingfeline.buildkonfig` |
| Roborazzi | `1.64.0` | `io.github.takahirom.roborazzi` |

---

## Hard Constraints

These pairings have strict version coupling — getting them wrong causes build or runtime failures.

| Constraint | Rule | Example |
|---|---|---|
| **KSP ↔ Kotlin** | KSP version must start with the Kotlin version: `{kotlinVersion}-{kspPatch}` | Kotlin `2.4.0` → KSP `2.4.0-2.0.0` |
| **CMP ↔ Kotlin floor** | Each Compose Multiplatform release requires a minimum Kotlin version | CMP `1.11.x` requires Kotlin ≥ `2.1.0` |
| **AGP ↔ Gradle min** | Each AGP major requires a minimum Gradle version | AGP `9.x` requires Gradle ≥ `8.11.1` |
| **SQLDelight ↔ Kotlin** | SQLDelight `2.x` requires Kotlin ≥ `1.9.0`; use the matching Gradle plugin | SQLDelight `2.3.x` + Kotlin `2.4.0` ✓ |
| **Koin compiler plugin ↔ Kotlin** | `org.jetbrains.kotlin.plugin.koin` version must match the project Kotlin version | Kotlin `2.4.0` → plugin `2.4.0` |
| **Roborazzi ↔ Robolectric** | Roborazzi screenshot tests require Robolectric on the test classpath | Add `robolectric` to `testImplementation` alongside Roborazzi |
| **Navigation Compose ↔ CMP** | JetBrains navigation-compose tracks the JetBrains Compose Multiplatform release train | Use versions from the same CMP release cycle |

---

## Known Conflict Zones

Areas where upgrades frequently break each other — check all entries in the zone before bumping any single one.

### Zone 1 — Kotlin core stack
Bumping Kotlin requires bumping all of these together:

- Kotlin (`org.jetbrains.kotlin.*`)
- KSP (`2.4.0-2.0.0` prefix must match)
- Compose Multiplatform (check minimum Kotlin requirement)
- Koin compiler plugin (version must equal Kotlin version)
- Coroutines (follow Kotlin release notes for minimum coroutines version)

### Zone 2 — Android build toolchain
Bumping AGP often requires bumping Gradle wrapper:

- AGP (`com.android.application` / `com.android.kotlin.multiplatform.library`)
- Gradle Wrapper (`gradle-wrapper.properties`)
- AndroidX Lifecycle (follows AGP's supported lifecycle-viewmodel releases)

### Zone 3 — Navigation
Navigation Compose (JetBrains fork) tracks the CMP release train:

- Navigation Compose (`org.jetbrains.androidx.navigation`)
- Compose Multiplatform
- AndroidX Lifecycle ViewModel (navigation depends on `lifecycle-viewmodel-compose`)

### Zone 4 — SQLDelight
SQLDelight has its own Gradle plugin that must stay in sync:

- SQLDelight version (`app.cash.sqldelight`)
- SQLDelight Gradle plugin (`sqldelight-gradlePlugin`)
- KSP (SQLDelight uses KSP for code generation in `2.x`)

---

## How to Update

1. Bump the version in the relevant `SKILL.md` (`libs.versions.toml` block).
2. Update the **Pinned Versions** table above.
3. Check the **Hard Constraints** and **Conflict Zones** tables — bump all coupled entries.
4. Run the audit: `python3 skills/kmp-audit/scripts/audit_skills_repo.py .`
5. Update `CHANGELOG.md` and tag a new release.

---

## Checking for Conflicts

The audit script scans skills for JVM-only APIs in `commonMain`. For version conflicts, cross-reference:

- [Maven Central](https://central.sonatype.com/) — latest stable for `io.insert-koin`, `io.ktor`, `app.cash.sqldelight`
- [JetBrains Compose releases](https://github.com/JetBrains/compose-multiplatform/releases) — CMP ↔ Kotlin compatibility table
- [KSP releases](https://github.com/google/ksp/releases) — `{kotlinVersion}-{patch}` tags
- [AGP release notes](https://developer.android.com/build/releases/gradle-plugin) — Gradle minimum version per AGP release

---

_Last updated: 2026-06-27_
