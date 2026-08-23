# Build Order for a New Project

Part of `kmp-expert`. Load this file when working on: build order for a new project.

---

### Phase 1: Foundation (do once per project)
1. **`clean-architecture`** — read the layer contract before writing any code
2. **`feature-scaffold`** — create the project from Kotlin/kmp-wizard, 6-layer module structure
3. **`flavor-environment`** — set up dev/staging/prod before writing any API code
4. **`network-layer`** — Ktor client, `NetworkResult`, auth interceptor
5. **`resilience`** — retry/backoff/jitter, timeout, idempotency keys on top of the network client
6. **`sqldelight-setup`** — local database, platform drivers, Koin wiring
7. **`logging`** — structured logging wrapper setup before any feature adds log calls
8. **`ci-github-actions`** — CI before any feature merges
9. **`code-quality`** — Ktlint + Detekt as CI gates from day one

### Phase 2: iOS/Desktop Readiness (if shipping to those platforms)
10. **`xcframework-spm`** — SPM binary target for iOS team
11. **`expect-actual`** — platform-specific code (UUID, SecureStorage, dispatchers)

### Phase 3: First Feature (repeat for each feature)
12. **`design-system`** — tokens and core components (once per project, before first feature)
13. **`navigation`** — add the feature's routes to the nav graph
14. **`shared-resources`** — add strings/assets the feature needs
15. **`repository-pattern`** — wire `RemoteDataSource` + `LocalDataSource` → `FooRepository`
16. **`presenter-module`** — `FooViewModel` (no Compose dep) + `FooUiState`/`FooUiIntent`
17. **`mvi`** — `FooScreen`/`FooContent` split consuming the presenter
18. **`preview-driven-development`** — Desktop `@Preview` for all states before wiring logic
19. **`unit-testing`** — `runTest` + Turbine tests for the ViewModel before shipping

### Phase 4: Richer UI & Quality (as needed)
20. **`design-system-extended`** — pull in Dialog, Sheet, Toast etc. when the feature needs them
21. **`compose-slot-api`** — when designing reusable components for the design system
22. **`compose-state-hoisting`** — when a component hierarchy gets complex
23. **`compose-state-container`** — when debugging state survival across rotation/back-nav
24. **`roborazzi`** — screenshot golden tests once the UI is stable

---

