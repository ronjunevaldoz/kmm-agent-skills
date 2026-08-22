# Goal gap analysis — 2026-06-18

**Date:** 2026-06-18

---

## Coverage

| Goal | Status | Skill |
|---|---|---|
| Multi-module feature split (`api/domain/data/ui`) | covered | `kmp-feature-scaffold` |
| `:model` module — pure domain types separate from `:api` | **missing** | — |
| `:presenter` module — ViewModels isolated from Compose | **missing** | — |
| Design system — custom tokens, no Material UI | covered | `kmp-compose-design-system` + extended |
| Environment config | covered | `kmp-flavor-environment` |
| Preview-driven development | **missing** | — |
| Unit testing patterns | **missing** | — |
| Roborazzi UI screenshot testing | **missing** | — |
| Code quality gates — Detekt + Ktlint | **missing** | — |
| Logging — Kermit | **missing** | — |
| Cross-layer error handling strategy | **missing** | — |
| `internal` visibility enforcement | **missing** | — |

---

## Key gaps

### Layer model — add `:model` and `:presenter`

Current scaffold: `api / domain / data / ui`
Proposed: `model / api / domain / data / presenter / ui`

```
:model     — data classes, sealed types, enums (no deps)
:api       — repository interfaces, nav contracts (depends on :model)
:domain    — use cases (depends on :api)
:data      — DTOs, mappers, repo impls (depends on :api)
:presenter — ViewModels, MVI contracts (depends on :domain, no Compose)
:ui        — Compose screens + previews (depends on :presenter only)
```

`:presenter` with no Compose dependency = ViewModels testable in plain JVM.
That is the prerequisite for both unit testing and Roborazzi.

### Preview-driven development

**Use Desktop previews — they compile to JVM, no AGP, no emulator, fastest possible cycle.**

Desktop target compiles 3–5× faster than Android. The Compose desktop preview runner in
IntelliJ/Android Studio renders `@Preview` composables instantly on JVM. This is the same
JVM target Roborazzi runs on, so preview → screenshot test is a single coherent workflow.

PDD cycle:
1. Write `Content` composable that accepts state as a parameter (Screen/Content split from MVI skill)
2. Write `@Preview` on Desktop target — covers loading, error, empty, populated states via `@PreviewParameterProvider`
3. Verify visually in the IDE without running a build
4. Roborazzi captures the same previews as golden screenshots — no extra test code
5. CI runs `./gradlew :desktopApp:jvmTest` — screenshot diffs fail the build

Why Desktop over Android previews:
- JVM compilation only — no `processDebugResources`, no D8, no manifest merge
- Works without a connected device or running emulator
- Same target as Roborazzi screenshot tests, so golden images are stable across machines
- `./gradlew :desktopApp:run` gives a live interactive preview during development

The MVI Screen/Content split is the technical enabler. This skill codifies it as a workflow.

### Roborazzi

Runs `@Preview` composables on JVM, captures bitmaps, diffs them in CI. Requires:
- `:presenter` / `:ui` split (inject fixed state without a ViewModel)
- Paparazzi or Roborazzi Gradle plugin wired per feature UI module
- Golden images committed to the repo or stored in CI artifacts
- CI job that fails on visual diff

Zero coverage today. Not in roadmap. Should replace `kmp-testing-robot`.

### Unit testing

No dedicated skill. Scattered notes in MVI (Turbine) and repository-pattern (fakes). Needs:
- `:core:testing` module — shared fakes, builders, coroutine test utilities
- `runTest` + `TestCoroutineScheduler` patterns
- Turbine for Flow assertions
- Fake-over-mock rule: `FakeAuthRepository implements AuthRepository`, no Mockito/MockK
- ViewModel tests that run on JVM via `:presenter` module (no Android dependency)

### Code quality — Ktlint + Detekt

**Install both.** They solve different problems:

| Tool | What it enforces | Config effort |
|---|---|---|
| Ktlint | Formatting — indentation, imports, line length | Near-zero. Add plugin, run `ktlintFormat`. |
| Detekt | Code smells + architecture rules — no `:ui` importing `:data`, complexity limits | Medium. Worth it for architecture violation detection. |

Ktlint is the easier win. Add it today. Detekt's architecture rule set is the more powerful tool for enforcing the layer model above.

### Other gaps

- **Logging (Kermit)** — KMP-native logging, pluggable writers, crash boundary. Without it every dev picks a different logger.
- **Error handling** — no guidance on propagating typed errors from `:data` → `:domain` → `:presenter` → `:ui`. The network skill covers `NetworkResult`; nothing covers the full arc.
- **`internal` visibility** — Gradle dependency rules are the first boundary; `internal` is the second. No guidance today.

---

## Suggested skills — priority order

| # | Skill | Unlocks |
|---|---|---|
| 1 | `kmp-clean-architecture` | Layer contract, `:model` split, `internal` rules |
| 2 | `kmp-presenter-module` | `:presenter` isolated from Compose; scaffold update |
| 3 | `kmp-unit-testing` | `runTest`, Turbine, fakes, `:core:testing` module |
| 4 | `kmp-compose-preview-driven-development` | `@Preview` workflow, `PreviewParameterProvider`, PDD cycle |
| 5 | `kmp-roborazzi` | Screenshot tests from previews, CI diff job |
| 6 | `kmp-code-quality` | Ktlint + Detekt, architecture rule set, CI gates |
| 7 | `kmp-logging` | Kermit, log levels, crash boundary |

Roadmap reprioritization: retire `kmp-testing-robot`, replace with skills 3–5 above.
