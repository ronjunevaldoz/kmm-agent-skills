---
name: kotlin-multiplatform-android-cli
description: >
  Wires Google's Android CLI (`android` binary, developer.android.com/tools/agents) into
  a KMP project's Android target — agent-first project scaffolding, emulator/device
  management, build + deploy, and SDK component installs from the terminal, without
  opening Android Studio. Covers `android init`/`android skills add` agent setup and the
  stable command surface; treats `android studio *` subcommands as Preview (require
  Android Studio Quail 2 Canary 1+) rather than a default dependency.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-07-19'
  keywords:
    - Android CLI
    - android-cli
    - android init
    - android skills
    - agent-first Android
    - emulator management
    - AVD
    - android run
    - android sdk
    - Android Studio agent tools
    - Journeys
    - Antigravity
---

## When to Use This Skill

Use when you need to:
- Set up a KMP project's Android target for agent-driven builds, deploys, and emulator
  management without a human opening Android Studio
- Create/start/stop an Android Virtual Device from the terminal
- Build and install a debug APK onto a device or emulator, or launch a specific activity
- Install SDK platforms/build-tools/system-images without the Android Studio SDK Manager UI
- Bootstrap `android init`/`android skills add` so this and other agents (Claude, Gemini,
  Codex) get Android-specific skills and a standardized entry point

**Requires:** `kotlin-multiplatform-feature-scaffold` project structure (or any Gradle
project with an `:androidApp`/Android target module) and the `android` CLI installed
(`https://developer.android.com/tools/agents`).

**Trigger keywords:** android cli, android-cli, android init, android skills add,
create android virtual device, AVD from terminal, start emulator cli, android run apk,
install apk cli, android sdk install, agent-first android, android studio quail,
render compose preview cli, journeys, google antigravity android.

**Freshness rule:** Android CLI is an actively evolving Google tool (own release notes,
separate cadence from AGP/Gradle). Re-check `android --version` output and
`developer.android.com/tools/agents` before relying on any command below in a new
project — flags and subcommands have moved between Preview and stable.

---

## Recommendation First

Default to **the stable command surface** (`create`, `describe`, `run`, `emulator`,
`sdk`) for anything scriptable/CI-safe. Treat `android studio *` (IDE-integration
subcommands — `analyze-file`, `find-declaration`, `render-compose-preview`) as
**Preview** — verified against Google's own docs: it explicitly requires Android Studio
Quail 2 Canary 1 or higher, and known issues include the Windows emulator command being
disabled and no PowerShell download support.

Why:
- the stable surface has no IDE dependency — it works in CI, in a headless dev
  container, or in any agent session that doesn't have Android Studio open
- gating on a Canary IDE build for anything beyond the Preview commands would make this
  skill unreliable outside that one environment
- `android init` + `android skills add` is the intended agent-onboarding path per
  Google's own docs (they explicitly name Claude/Gemini/Codex as supported agents) —
  wiring it once at project setup means every future agent session in this project gets
  Android-specific skills without re-discovering the tool

Reach for the Preview `android studio *` commands only when the project's IDE is
confirmed to be a qualifying Canary build — never assume it is.

---

## Installation & Verification

```bash
# Install: follow the platform-specific instructions at
# https://developer.android.com/tools/agents

# Verify installed and on PATH
which android
android --version

# Keep it current
android update
```

---

## Step 1: Bootstrap agent integration (once per project)

```bash
# From the KMP project root
android init            # sets up the project for agent workflows, installs the android-cli skill
android skills add --all   # installs all Android-specific skills for this and future agent sessions
android skills find 'performance'   # discover a narrower skill set instead of --all
```

`android init` is idempotent — safe to re-run after an `android update` to pick up new
agent-facing skills without touching project files that already exist.

---

## Step 2: Project & build

```bash
# Scaffold a new Android-only prototype (not for adding an Android target to an
# existing KMP module — use kotlin-multiplatform-feature-scaffold for that)
android create --template-name=<template> --output=<path>

# Inspect an existing project (module graph, target SDK, dependencies)
android describe --project_dir=/path/to/project
```

For a KMP project already scaffolded by `kotlin-multiplatform-feature-scaffold`, skip
`android create` — it targets a fresh Android-only project, not a multi-target KMP
module graph. Use `android describe` freely; it's read-only.

---

## Step 3: Emulator / device management

```bash
# Create a virtual device from a named profile
android emulator create --profile=medium_phone

# Start / stop
android emulator start medium_phone
android emulator stop emulator-5554
```

Known issue (per Google's own docs, verified before shipping this skill): the emulator
command is disabled on Windows. On Windows, fall back to `emulator -avd <name>` from the
Android SDK's own `emulator/` tools directory, or drive a physical device instead.

---

## Step 4: Deploy & run

```bash
# Install and launch a built APK on a connected device or emulator
android run --apks=app-debug.apk --device=<serial> --activity=<fully.qualified.Name>

# Omit --device to target the only connected device/emulator
android run --apks=app-debug.apk
```

This replaces the `./gradlew installDebug && adb shell am start -n ...` two-step for
agent-driven runs — one command instead of chaining Gradle and `adb` manually.

---

## Step 5: SDK component management

```bash
android sdk list <pattern>
android sdk install platforms/android-34 build-tools/34.0.0
```

Prefer this over manually editing `local.properties`/SDK paths or scripting `sdkmanager`
calls directly — `android sdk` resolves the same components through one consistent
interface the rest of the CLI already uses.

---

## Preview: Android Studio IDE-integration commands

```bash
android studio check                        # verify a qualifying Studio install is present
android studio analyze-file <path>
android studio find-declaration <symbol>
android studio render-compose-preview <path> <composable>
```

**Gate these behind `android studio check` succeeding first** — do not assume Android
Studio Quail 2 Canary 1+ is installed just because the rest of the CLI works. If `check`
fails, fall back to the non-IDE equivalent (grep/read the source for `find-declaration`,
Roborazzi/`runComposeUiTest` for `render-compose-preview` — see
`kotlin-multiplatform-roborazzi`) rather than blocking on a Preview feature.

---

## Wiring into CI (stable surface only)

```yaml
# .github/workflows/android-cli-smoke.yml — stable commands only, no Studio dependency
name: Android CLI Smoke
on: [pull_request]
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Android CLI
        run: |
          # follow https://developer.android.com/tools/agents for the current install command
          android --version
      - name: Describe project
        run: android describe --project_dir=.
      - name: Create + start emulator, run instrumented smoke test
        run: |
          android emulator create --profile=medium_phone
          android emulator start medium_phone
          android sdk install platforms/android-34 build-tools/34.0.0
          ./gradlew connectedDebugAndroidTest
```

Do not add `android studio *` steps to CI — they require a Canary IDE install CI
runners don't have.

---

## Related Skills

- `kotlin-multiplatform-feature-scaffold` — the project structure this skill's Android
  target commands (`describe`, `run`) operate on; use that skill to add the Android
  target itself, not `android create`
- `kotlin-multiplatform-ci-github-actions` — where the CI smoke job above belongs
  alongside the existing Android/iOS/Desktop/Web test matrix
- `kotlin-multiplatform-roborazzi` — the non-Preview fallback for
  `android studio render-compose-preview` when a qualifying Studio install isn't present
- `kotlin-multiplatform-audit` — run after any Android CLI-driven scaffold change to
  confirm the 6-layer module contract still holds

---

## Common Anti-Patterns

- running `android studio *` commands in CI or a headless agent session without first
  checking `android studio check` — these require a Canary Android Studio install that
  CI runners and headless dev containers don't have
- using `android create` to add Android to an already-scaffolded KMP project — it
  targets a fresh Android-only project, not an existing multi-target module graph; use
  `kotlin-multiplatform-feature-scaffold` instead
- skipping `android init`/`android skills add` at project setup, then re-discovering the
  tool from scratch in every new agent session
- scripting raw `adb`/`sdkmanager`/`emulator` calls once `android run`/`android sdk`/
  `android emulator` already wrap the same operations through one consistent interface
- assuming the emulator command works identically on Windows — it's explicitly disabled
  there per Google's own docs; verify before scripting a cross-platform CI job around it

---

## Output Style

When asked about Android CLI setup or usage for a KMP project, respond in this order:
1. Whether `android` is installed and on PATH (`android --version`)
2. `android init` + `android skills add` bootstrap, if not already done
3. The specific stable command for the task (project, emulator, deploy, or SDK)
4. Whether the task actually needs a Preview `android studio *` command — if so, gate on
   `android studio check` first and name the non-Preview fallback
5. CI wiring, only if asked — stable surface only, never Preview

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-19 | Initial skill. Real gap found: the user asked for Android CLI (`developer.android.com/tools/agents`) as a mandatory skill; verified no official Claude Code skill exists for it and this repo had zero references. Covers the stable command surface (`init`/`skills add`, `create`/`describe`, `emulator`, `run`, `sdk`) as the default, and scopes `android studio *` IDE-integration commands as Preview (verified: requires Android Studio Quail 2 Canary 1+, known Windows emulator/PowerShell issues) rather than a default dependency. |
