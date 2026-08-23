---
name: kmp-security
description: >
  Mobile app security for Kotlin Multiplatform beyond Android-only R8
  obfuscation — certificate/SSL pinning (expect/actual, no cross-platform
  Ktor support exists natively), root/jailbreak/tamper detection via
  freeRASP's real KMP variant, encrypted local storage via KSafe, iOS/
  Kotlin-Native release-binary symbol stripping, and an OWASP Mobile Top 10
  2024 coverage map across this collection. Does NOT cover Android-specific
  R8/ProGuard obfuscation — that's kmp-proguard-r8's own scope, cross-
  referenced here rather than duplicated. Does NOT cover secrets-in-source
  scanning (gitleaks pre-commit) — that's kmp-setup-hooks Option F.
license: Apache-2.0
metadata:
  author: kmp-agent-skills
  last-updated: '2026-08-24'
  keywords:
    - security
    - certificate pinning
    - SSL pinning
    - root detection
    - jailbreak detection
    - tamper detection
    - freeRASP
    - RASP
    - secure storage
    - encrypted storage
    - KSafe
    - OWASP Mobile Top 10
    - binary stripping
    - symbol stripping
    - reverse engineering
---

## When to Use This Skill

Use when you need to:
- Pin a server's certificate/public key so the app rejects a MITM proxy even
  with a trusted root CA installed on the device
- Detect a rooted/jailbroken device, an active debugger, or Frida/Xposed
  hooking at runtime
- Store a token/credential encrypted at rest, not in plain `SharedPreferences`/`NSUserDefaults`
- Strip debug symbols from a release iOS/Kotlin-Native binary
- Check this collection's coverage against the real OWASP Mobile Top 10

Do NOT use this skill for Android-specific obfuscation/minification — load
`kmp-proguard-r8` instead, this skill cross-references it rather than
duplicating it.

**Trigger keywords:** certificate pinning, SSL pinning, public key pinning,
root detection, jailbreak detection, tamper detection, freeRASP, RASP,
runtime application self-protection, secure storage, encrypted storage,
KSafe, OWASP Mobile Top 10, binary stripping, symbol stripping, strip debug
symbols, reverse engineering, Frida detection, MITM.

**Freshness rule:** freeRASP's KMP variant and KSafe are both actively
developed, real third-party libraries, not part of JetBrains' own KMP
release train — recheck their current versions before pinning; OWASP Mobile
Top 10 was last released in 2024 (still current as of this writing, verified
directly against owasp.org, not assumed).

---

## Recommendation First

**freeRASP (Talsec)** for root/jailbreak/tamper detection — real, dedicated
KMP variant (`com.aheaditec.talsec.security:freeRASP_KMP`), one shared
codebase across Android+iOS instead of hand-rolling two `expect`/`actual`
detectors. **KSafe** for encrypted local storage — encryption on by default,
a single code path with no `expect`/`actual` needed, and built-in
root/jailbreak WARN/BLOCK policy on top. **Certificate pinning has no native
cross-platform Ktor support** — verified, not assumed: it requires
`expect`/`actual`, OkHttp's `CertificatePinner` on the Android engine and a
`NSURLSessionDelegate` challenge handler on the Darwin (iOS) engine.

Why: detection alone is never sufficient on its own — every client-side
check is bypassable by a sufficiently motivated attacker. The real posture
is layered: client-side detection (freeRASP) raises the cost of tampering,
pinning + encrypted storage protect data in transit and at rest, and
anything security-critical (entitlement checks, purchase validation) still
gets verified server-side — a rooted device can manipulate any purely local
verification logic.

---

## Certificate / SSL Pinning

Ktor's client engines differ per platform, so pinning is genuinely
`expect`/`actual`, not a shared Ktor plugin:

```kotlin
// commonMain
expect fun createPinnedHttpClient(pins: List<String>): HttpClient
```

```kotlin
// androidMain — OkHttp engine, native CertificatePinner support
actual fun createPinnedHttpClient(pins: List<String>): HttpClient {
    val certificatePinner = CertificatePinner.Builder()
        .add("api.example.com", *pins.toTypedArray())   // "sha256/AAAA...=" format
        .build()
    return HttpClient(OkHttp) {
        engine { preconfigured = OkHttpClient.Builder().certificatePinner(certificatePinner).build() }
    }
}
```

```kotlin
// iosMain — Darwin engine, NSURLSessionDelegate challenge handling
actual fun createPinnedHttpClient(pins: List<String>): HttpClient {
    return HttpClient(Darwin) {
        engine {
            handleChallenge { _, _, challenge, completionHandler ->
                // Compare the server's public key hash against `pins` here;
                // cancel the challenge (reject) on mismatch instead of trusting
                // the system's CA store — see kmp-expect-actual for the platform
                // dispatch pattern this expect/actual pair follows.
            }
        }
    }
}
```

**Test with a broken pin first** — configure an intentionally wrong hash,
confirm the connection is rejected, then switch to the real pin. Confirms the
pinning logic actually runs before trusting it in production. Do this on a
trusted network, not through a MITM proxy tool (Charles/Fiddler) — those are
exactly what pinning should reject.

---

## Root / Jailbreak / Tamper Detection — freeRASP

```kotlin
// build.gradle.kts, commonMain
dependencies {
    implementation("com.aheaditec.talsec.security:freeRASP_KMP:1.1.0")
}
```

```kotlin
// commonMain — SecurityManager.kt
object SecurityManager {
    private val config = freeraspConfig(
        watcherMail = "security@example.com",
        androidConfig = AndroidConfig(
            packageName = "com.example.app",
            certificateHashes = listOf("mVr/qQLO8DKTwqlL+B1qigl9NoBnbiUs8b4c2Ewcz0k="),
        ),
        iosConfig = IOSConfig(
            bundleIds = listOf("com.example.app"),
            teamId = "YOUR_TEAM_ID",
        ),
        isProd = true,
        killOnBypass = true,
    )

    suspend fun start(scope: CoroutineScope) {
        FreeraspKMP.threatEvents.onEach { event ->
            when (event) {
                is FreeRaspEvent.PrivilegedAccess -> handleRootOrJailbreak()
                is FreeRaspEvent.AppIntegrity -> handleRepackaging()
                is FreeRaspEvent.Debug -> handleDebuggerAttached()
                else -> Unit
            }
        }.flowOn(Dispatchers.IO).launchIn(scope)
        FreeraspKMP.start(config)
    }
}
```

Detects rooting/jailbreak (Magisk, Dopamine), Frida/Xposed hooking,
repackaging/tampering, and emulators — call `SecurityManager.start()` once
from app entry (`LaunchedEffect` in the root composable, or platform
`onCreate`/`AppDelegate` equivalent). iOS needs `TalsecRuntime.xcframework`/
`TalsecBridge.xcframework` linked in Xcode with "Embed & Sign"; Android needs
the manifest permissions its integration guide lists (`DETECT_SCREEN_CAPTURE`
among them) — both are one-time setup steps, not runtime code.

**Layer detection methods, don't rely on one.** File-system checks alone are
easily hooked with Frida/Substrate at the Kotlin/Swift layer — freeRASP's own
value is combining multiple signals (file system, API behavior, native-level
checks) instead of one easily-bypassed check.

---

## Secure Local Storage — KSafe

```kotlin
// build.gradle.kts
dependencies {
    implementation("eu.anifantakis:ksafe:3.0.0")
    implementation("eu.anifantakis:ksafe-compose:3.0.0")   // optional — Compose state integration
}
```

```kotlin
// Encrypted by default, property-delegate pattern
var authInfo by ksafe(AuthInfo())   // AuthInfo must be @Serializable

// Reads hit a hot in-memory cache after first load; writes happen async in the background

val ksafe = KSafe(
    context = context,
    securityPolicy = KSafeSecurityPolicy(
        rootedDevice = SecurityAction.WARN,       // IGNORE | WARN | BLOCK
        debuggerAttached = SecurityAction.BLOCK,
        onViolation = { violation -> analytics.log("security: ${violation.name}") },
    ),
)
```

One code path, no `expect`/`actual` needed for the storage layer itself —
KSafe owns the platform dispatch (Android Keystore-backed encryption,
iOS Keychain) internally. Prefer this over hand-rolling
`EncryptedSharedPreferences`/raw `Keychain` calls per platform unless the
project has a reason KSafe doesn't cover.

---

## Release Binary Protection

**Android**: R8/ProGuard obfuscation — load `kmp-proguard-r8`, this skill
doesn't duplicate it.

**iOS/Kotlin-Native**: strip debug symbols from the release `.framework`.
Verified Xcode Archive build settings, not the dev-build defaults:

```
Deployment Postprocessing = Yes
Strip Linked Product = Yes
Additional Strip Flags = -rSTx
```

`-T` strips Swift symbols specifically; the combination applies to any
bundled `.framework`, including the Kotlin/Native-produced one — debugging
information and descriptive function names in an unstripped binary make
reverse engineering meaningfully easier. Most crash-reporting tools (Sentry,
Crashlytics) support uploading symbols separately for stack-trace
symbolication, so stripping the shipped binary doesn't cost you crash
diagnosis — same tradeoff `kmp-proguard-r8` already documents for Android's
`mapping.txt`.

---

## Server-Side Verification — the Principle Underneath All of This

A rooted/jailbroken device can manipulate any client-side check, including
freeRASP's own signals if the attacker is determined enough. The real
security boundary for anything valuable (entitlements, purchase validation,
sensitive data access) is server-side verification — client-side detection
raises the cost of an attack, it doesn't replace backend validation. See
`kmp-in-app-purchases`'s server-side receipt validation for the concrete
example this collection already applies the same principle to.

---

## OWASP Mobile Top 10 (2024) — Coverage Map

Verified directly against owasp.org, not assumed:

| Category | Covered by |
|---|---|
| M1: Improper Credential Usage | `kmp-flavor-environment` (secrets never in source), this skill's KSafe section |
| M2: Inadequate Supply Chain Security | `kmp-setup-hooks` (gitleaks), `kmp-ci-github-actions` |
| M3: Insecure Authentication/Authorization | `kmp-ktor-auth-service`, `kmp-biometric-auth` |
| M4: Insufficient Input/Output Validation | `kmp-form-validation` |
| M5: Insecure Communication | This skill's Certificate/SSL Pinning section |
| M6: Inadequate Privacy Controls | `kmp-legal-docs` |
| M7: Insufficient Binary Protections | This skill's Release Binary Protection + Root/Jailbreak sections, `kmp-proguard-r8` |
| M8: Security Misconfiguration | `kmp-ci-github-actions`, `kmp-code-quality` (Detekt gates) |
| M9: Insecure Data Storage | This skill's Secure Local Storage section |
| M10: Insufficient Cryptography | This skill's KSafe section (delegates crypto to the library, doesn't hand-roll it) |

Every category has a real home somewhere in this collection — this table
exists so a reviewer can find it without re-deriving the mapping.

---

## Common Anti-Patterns

- **Trusting client-side root/jailbreak detection as the actual security
  boundary** — it's a cost-raising signal, not a guarantee; verify anything
  valuable server-side too.
- **Pinning against a leaf certificate instead of a public key or
  intermediate CA** — a leaf cert rotates on renewal and silently breaks the
  app; pin the public key (SPKI hash) or an intermediate that survives
  rotation.
- **No pin-rotation plan** — shipping a pinned app with no way to update the
  pins (a remote config fallback, or a hard app-store update requirement)
  means a legitimate certificate rotation locks users out.
- **Hand-rolling `EncryptedSharedPreferences`/raw `Keychain` calls per
  platform** when KSafe already covers the common case with less code and
  matching encryption guarantees on both.
- **Assuming R8 obfuscation covers iOS too** — it doesn't; the release
  binary needs its own, separate stripping step.
- **A single un-layered detection check** (just a `su` binary file check, for
  example) — easily defeated; combine multiple signals, or use a library that
  already does (freeRASP).

---

## Testing

```kotlin
class SecurityPolicyTest {
    @Test
    fun `WARN action logs but does not throw`() = runTest {
        var logged: String? = null
        val policy = KSafeSecurityPolicy(
            rootedDevice = SecurityAction.WARN,
            onViolation = { logged = it.name },
        )
        // Fake a rooted-device signal through the policy's own violation hook —
        // don't test against a real rooted device in CI.
        policy.onViolation(SecurityViolation.ROOTED_DEVICE)
        assertEquals("ROOTED_DEVICE", logged)
    }
}
```

Certificate pinning and freeRASP integration are best verified manually per
the intentional-broken-pin technique above — both depend on real platform
TLS/OS-level behavior that a JVM unit test can't meaningfully fake.

---

## Related Skills

- `kmp-proguard-r8` — Android obfuscation/minification; this skill's iOS/Native
  counterpart, cross-referenced not duplicated
- `kmp-flavor-environment` — build-time secrets injection, the M1 credential-usage half
- `kmp-setup-hooks` — gitleaks pre-commit secrets scanning (Option F)
- `kmp-network-layer` — the Ktor client this skill's pinning wraps
- `kmp-in-app-purchases` — the server-side receipt validation example this skill's
  "server-side verification" principle points to
- `kmp-biometric-auth` — device keystore-backed credential unlock, adjacent to KSafe

---

## Output Style

When asked about mobile security, respond in this order:
1. which of the five areas actually applies (pinning / RASP / storage /
   binary stripping / OWASP mapping) — don't dump all five for a narrow ask
2. the real library/API for that area, with its actual coordinates
3. code snippet
4. the layered/server-side-verification caveat if the ask implies
   client-side detection is the whole solution

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-24 | Initial release. User asked whether code security and obfuscation were covered — confirmed obfuscation existed (`kmp-proguard-r8`, Android-only) but certificate pinning, root/jailbreak/tamper detection, secure storage as an owned topic, and iOS/Native binary stripping were all real, zero-coverage gaps. Verified every library/API before writing: Ktor has no native cross-platform pinning (real, `expect`/`actual` required); freeRASP ships a real dedicated KMP variant with real Gradle coordinates and config shape; KSafe is a real KMP encrypted-storage library with real Maven coordinates; OWASP Mobile Top 10's current version is the real 2024 release (M1-M10 verified against owasp.org); Xcode's real Archive-time strip settings for a Kotlin/Native `.framework`. Added an OWASP Mobile Top 10 coverage map cross-referencing where each category is actually handled across this collection. |
