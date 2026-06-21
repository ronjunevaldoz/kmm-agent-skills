# Development Plan

Tracks every skill's status and the roadmap for future work.
Update when skills are added, revised, or completed.

---

## Status Key

| Symbol | Meaning |
|---|---|
| ✅ | Shipped — skill is in `main`, production-ready |
| 🔧 | Known issues — skill exists but has open defects (see KNOWN_ISSUES.md) |
| 🚧 | In progress — actively being written |
| 📋 | Planned — scoped and ready to start |
| 💡 | Idea — not yet scoped |

---

## Shipped Skills (47) — v1.13.0

### Layer 0 — Architecture Contract
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-feature-scaffold` | ✅ | AGP 9, build-logic, version catalog, Koin 4, 6-layer model |
| `kotlin-multiplatform-clean-architecture` | ✅ | 6-layer contract, :model vs :api, internal visibility, Detekt rules |
| `kotlin-multiplatform-presenter-module` | ✅ | Pure Kotlin ViewModel, MVI contracts, no Compose dep, Koin wiring |

### Layer 1 — Project Foundation
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-dependency-injection` | ✅ | Koin manual + annotated modes, scope rules, test overrides |
| `kotlin-multiplatform-flavor-environment` | ✅ | BuildKonfig, AppConfig, Android product flavors |
| `kotlin-multiplatform-ci-github-actions` | ✅ | Android/iOS/Desktop/Web matrix, XCFramework release |
| `kotlin-multiplatform-audit` | ✅ | Architecture review, boundary check, skills repo hygiene, issue drafts |

### Layer 2 — Core Infrastructure
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-ktor-auth-service` | ✅ | Bearer + JWT, sessions, Ktor RPC auth, login/refresh/logout |
| `kotlin-multiplatform-mongodb-database` | ✅ | Coroutine driver, repository boundary, typed errors, change streams |
| `kotlin-multiplatform-kotlin-rpc` | ✅ | Kotlin RPC vs REST decision, shared contract, Ktor auth integration |
| `kotlin-multiplatform-network-layer` | ✅ | Ktor 3, NetworkResult<T>, safeRequest, token refresh interceptor |
| `kotlin-multiplatform-sqldelight-setup` | ✅ | SQLDelight 2, platform drivers, schema, migrations, Flow queries |
| `kotlin-multiplatform-datastore` | ✅ | Preferences + Proto DataStore, expect/actual factory, Koin wiring |
| `kotlin-multiplatform-xcframework-spm` | ✅ | XCFramework build, SPM binary target, CI release |
| `kotlin-multiplatform-logging` | ✅ | Kermit, log levels, pluggable writers, crash boundary, Koin wiring |

### Layer 3 — Platform Patterns
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-expect-actual` | ✅ | 4 categories, typealias actual, @ObjCName, Kotlin/Native memory |
| `kotlin-multiplatform-repository-pattern` | ✅ | Interface/:data impl, mapper pattern, 3 fetch strategies, optimistic updates |
| `jni-kotlin-pro` | ✅ | JNI bridge, @JvmStatic entry points, CPointer, memory-safe interop |

### Layer 4 — Feature Building Blocks
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-navigation` | ✅ | JetBrains Nav Compose, type-safe routes, nested graphs, bottom nav |
| `kotlin-multiplatform-shared-resources` | ✅ | CMP Resources, strings/images/fonts, plurals, localization |
| `kotlin-multiplatform-mvi` | ✅ | Contract pattern, MviViewModel, Channel<Effect>, Turbine testing |
| `kotlin-multiplatform-paging` | ✅ | Paging 3, PagingSource, RemoteMediator, cursor/offset, load-state |
| `kotlin-multiplatform-analytics` | ✅ | Sealed AnalyticsEvent, Firebase/Amplitude impls, screen tracking, FakeAnalytics |
| `kotlin-multiplatform-form-validation` | ✅ | ValidationResult, FieldState, async debounce, ValidatedTextField, submit gate |
| `kotlin-multiplatform-image-loading` | ✅ | Coil 3, single ImageLoader, AsyncImage, AvatarImage, HeroImage |
| `kotlin-multiplatform-permissions` | ✅ | PermissionState, expect/actual PermissionController, Android + iOS |
| `kotlin-multiplatform-deep-linking` | ✅ | App Links + Universal Links, DeepLinkParser, NavHost navDeepLink, AASA |
| `kotlin-multiplatform-biometric-auth` | ✅ | BiometricResult, expect/actual BiometricAuthenticator, BiometricPrompt, LAContext |
| `kotlin-multiplatform-push-notifications` | ✅ | FCM + APNs, PushToken, FirebaseMessagingService, NotificationHandler expect/actual |
| `kotlin-multiplatform-workmanager` | ✅ | CoroutineWorker, BGTaskScheduler, expect/actual BackgroundScheduler, retry |
| `kotlin-multiplatform-feature-flags` | ✅ | FeatureFlag enum, Firebase Remote Config, A/B variants, kill switch |
| `kotlin-multiplatform-offline-first` | ✅ | SyncState, SyncManager, optimistic updates with rollback, conflict resolution |
| `kotlin-multiplatform-crash-reporting` | ✅ | CrashReporter interface, Firebase Crashlytics + Sentry, dSYM symbolication |

### Layer 5 — UI System
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-design-system` | ✅ | Tokens, AppTheme, dark mode, 6 core components, no Material dependency |
| `kotlin-multiplatform-design-system-extended` | ✅ | 27 additional components: Dialog, Sheet, Toast, Tabs, TopAppBar, etc. |
| `kotlin-multiplatform-adaptive-layout` | ✅ | WindowSizeClass, Compact/Medium/Expanded, list-detail split, migration mode |
| `kotlin-multiplatform-compose-animation` | ✅ | AnimatedVisibility, Crossfade, AnimatedContent, animateXAsState, shared elements |
| `kotlin-multiplatform-compose-slot-api` | ✅ | Slot patterns, scoped slots, CompositionLocal, component API shape |
| `kotlin-multiplatform-compose-state-hoisting` | ✅ | Hoist-until-shared rule, controlled components, stateless vs stateful |
| `kotlin-multiplatform-compose-state-container` | ✅ | remember/rememberSaveable/ViewModel survival matrix, custom Saver |
| `kotlin-multiplatform-graphics-modifiers` | ✅ | graphicsLayer, Canvas, drawBehind, drawWithCache, workflow node shells |
| `kotlin-multiplatform-preview-driven-development` | ✅ | Desktop-first @Preview, PreviewParameterProvider, PDD cycle |

### Layer 6 — Testing & Quality
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-unit-testing` | ✅ | runTest, Turbine, fake-over-mock, :core:testing fixtures, JVM ViewModel tests |
| `kotlin-multiplatform-roborazzi` | ✅ | Screenshot tests from @Preview on JVM, golden images, CI diff |
| `kotlin-multiplatform-code-quality` | ✅ | Ktlint + Detekt, CI gates, pre-commit hook |
| `kotlin-multiplatform-accessibility` | ✅ | Semantic roles, contentDescription, touch targets, Roborazzi a11y snapshots |

### Meta
| Skill | Status | Notes |
|---|---|---|
| `kotlin-multiplatform-expert` | ✅ | 47-skill routing map, dependency graph, invocation map, build order |

---

## Open Defects

None. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for tracked open items.

---

## Shipped — v1.15.0 (Consumer Changelogs, Release Notes & App Versioning)

| Item | Status | Description |
|---|---|---|
| `## Changelog` in all 47 skills | ✅ Shipped | Consumer-facing release note table in every SKILL.md; travels with the skill on install |
| `agents/changelog.md` | ✅ Shipped | Changelog agent: categorizes git + skill diff into Breaking/New/Improved/Fixed, writes consumer release notes |
| `commands/release-notes.md` | ✅ Shipped | `/release-notes` command: per-skill or collection release notes from git history |
| `scripts/generate_release_notes.py` | ✅ Shipped | Reads git log + per-skill `## Changelog` tables, outputs structured JSON for the changelog agent |
| App versioning pattern | ✅ Shipped | `gradle.properties` as single source of truth for `VERSION_NAME`/`VERSION_CODE`; `BuildKonfig` exposes `APP_VERSION` to `commonMain` |
| `CONTRIBUTING.md` | ✅ Shipped | Full contribution guide: skill authoring, commit format, PR checklist, release process |

---

## Shipped — v1.14.0 (E2E Testing & Project Bootstrap)

| Item | Status | Description |
|---|---|---|
| `/new-project` command | ✅ Shipped | Natural language → full KMP project scaffold. Drives full pipeline: feature-scaffold → clean-arch → infrastructure → design system → features → verify |
| `samples/todo-app.md` | ✅ Shipped | E2E test spec: 12 skills, local persistence, form validation, MVI, Roborazzi. Pass/fail is objective (audit + jvmTest + screenshot audit) |
| More sample specs | 📋 Planned | `samples/social-feed.md` (paging, image loading, kRPC), `samples/settings-app.md` (DataStore, biometric auth) |

---

## Upcoming — v1.x (Quality & Hardening)

Targeted improvements that don't require new skills.

| Item | Priority | Description |
|---|---|---|
| CI gate: block PR without Testing section | LOW | `scan_skill_issues.py` runs at release time, but a skill directory could be merged without a Testing section if the author doesn't cut a release. Add a GitHub Actions step to run the scanner on every PR. |
| Wire `validate_keyword_routing.py` into release script | LOW | `release.py` calls `validate_skill_map.py` but not `validate_keyword_routing.py`. Run both so a release is blocked if a new skill has no invocation map row. |

---

## Upcoming — v2.0 (Platform Milestone)

Require coordination across multiple files or introduce breaking changes to existing skill guidance.

| Item | Priority | Description |
|---|---|---|
| Kotlin 2.x / K2 verification pass | HIGH | Audit every skill's code snippets against K2 — some `expect/actual` and annotation patterns changed. Update minimum Kotlin version across all TOML snippets. |
| AGP 10 migration | MEDIUM | AGP 10 changes module graph declaration API. Update `feature-scaffold` and `clean-architecture` skills when AGP 10 stable ships. |
| Compose Multiplatform 2.x readiness | MEDIUM | CMP 2.x expected to stabilize shared navigation and resources API. `navigation`, `shared-resources`, and `adaptive-layout` skills will need version bumps and pattern updates. |
| Skill freshness CI gate | LOW | `/setup-hooks Option C` describes a weekly cron. Post-v2.0 add it to the repo's own `.github/workflows/` so freshness warnings surface without a local install. |
| `kotlin-multiplatform-testing-robot` | 💡 Deferred | UI test robot pattern (Page Object Model for Compose). Deferred until Roborazzi + compose-test-rule coverage feels insufficient in practice. |

---

## Version Targets

| Tool | Current | Next target |
|---|---|---|
| AGP | 9.0.1 | AGP 10 stable |
| Kotlin | 2.4.0 | Track K2 stable |
| Compose Multiplatform | 1.11.1 | CMP 2.x stable |
| Koin | 4.2.1 | — |
| Ktor | 3.1.3 | — |
| SQLDelight | 2.0.2 | — |

---

## Contribution Notes

- Every skill must follow the "real skill" principle: 80% patterns/decisions/pitfalls, ≤20% dependency setup
- Skill descriptions must be specific enough to trigger correctly — test against the keyword list before shipping
- Use `/new-skill` to scaffold — it enforces all required sections at creation time
- Use `/modify-skill` to edit — it prevents accidental removal of required sections
- Run `python3 scripts/scan_skill_issues.py` after any SKILL.md change to verify zero HIGH findings
- Run `python3 skills/kotlin-multiplatform-expert/scripts/validate_skill_map.py` after adding a skill to confirm README, expert, and planner are all updated
- Run `python3 skills/kotlin-multiplatform-expert/scripts/validate_keyword_routing.py` after adding invocation map rows to confirm every skill has keyword routing coverage
- Run `/audit-screenshots` after recording Roborazzi goldens to verify design-system compliance visually
- Use `/new-project <description or samples/*.md>` to bootstrap a full KMP project from scratch
- To run E2E tests against a sample spec: clone a clean sandbox repo, then run `/new-project samples/todo-app.md`
