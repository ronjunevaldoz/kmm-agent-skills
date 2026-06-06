# kmm-agent-skills

A collection of AI agent skills for **Kotlin Multiplatform (KMP)** development,
targeting Android, iOS, Desktop (JVM), and Web (JS/Wasm).

Skills follow the [Agent Skills open standard](https://agentskills.io) — self-contained
`SKILL.md` files that ground AI agents with domain-specific knowledge and production-ready
templates. Each skill fills a gap where LLMs consistently underperform without explicit guidance.

---

## Available Skills

| Skill | Description |
|---|---|
| [`kotlin-multiplatform-feature-scaffold`](skills/kotlin-multiplatform-feature-scaffold/) | Scaffold a full KMP multi-module project or add a new feature module group (`:api/:domain/:data/:ui`). AGP 9+, build-logic convention plugins, version catalog, CMP, Koin 4. |
| [`kotlin-multiplatform-network-layer`](skills/kotlin-multiplatform-network-layer/) | Production-ready Ktor 3 network layer in `:core:network`. Bearer auth with automatic token refresh, `NetworkResult<T>`, `safeRequest {}`, platform engines for Android/iOS/Desktop/Web. |
| [`kotlin-multiplatform-ci-github-actions`](skills/kotlin-multiplatform-ci-github-actions/) | GitHub Actions CI: lint, Android tests (Ubuntu), iOS tests (macOS), Desktop/Web tests, Gradle cache. Release workflow: XCFramework build + GitHub Release. |

---

## Targets

All skills support the full KMP target matrix:

| Platform | Target | Entry Point |
|---|---|---|
| Android | `androidTarget()` | `:androidApp` |
| iOS | `iosArm64()`, `iosSimulatorArm64()` | `:iosApp` (Xcode) |
| Desktop | `jvm()` | `:desktopApp` |
| Web | `js { browser() }`, `wasmJs { browser() }` | `:webApp` |

---

## Installation

### Via skills CLI

```bash
npx skills add ronjunevaldoz/kmm-agent-skills
```

### Manual

Copy the desired skill folder into your agent's skills directory:

```bash
# Claude Code
cp -r skills/kotlin-multiplatform-feature-scaffold .claude/skills/

# All skills at once
cp -r skills/* .claude/skills/
```

---

## Versioning

| Tool | Version |
|---|---|
| AGP | 9.0.1 |
| Kotlin | 2.4.0 |
| Compose Multiplatform | 1.11.1 |
| Koin | 4.2.1 |
| Ktor | 3.1.3 |
| SQLDelight | 2.0.2 |
| BuildKonfig | 0.21.2 |
| Turbine | 1.2.1 |

---

## Skill Naming Convention

Skills in this repo follow `kotlin-multiplatform-<functional-name>`.

---

## Roadmap

- [ ] `kotlin-multiplatform-sqldelight-setup` — SQLDelight schema, migrations, type adapters
- [ ] `kotlin-multiplatform-navigation` — KMP navigation (Navigation 3 / Decompose)
- [ ] `kotlin-multiplatform-shared-resources` — Compose Resources (strings, fonts, images)
- [ ] `kotlin-multiplatform-flavor-environment` — Multi-environment BuildKonfig + flavors
- [ ] `kotlin-multiplatform-xcframework-spm` — XCFramework → Swift Package Manager

---

## References

- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills) — official Kotlin agent skills
- [android/skills](https://github.com/android/skills) — official Android agent skills
- [Kotlin/kmp-wizard](https://github.com/Kotlin/kmp-wizard) — AGP 9 KMP project templates
- [agentskills.io](https://agentskills.io) — Agent Skills open standard

---

## License

Apache-2.0
