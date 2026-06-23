# Getting Started with KMM Agent Skills

You have a Kotlin Multiplatform (KMP) project or want to start one. These agent skills guide you through architecture decisions, module structure, and implementation — end-to-end, one feature at a time.

**This is not a tutorial.** You don't read it. You use Claude Code (or your AI assistant) to invoke these skills directly in your project.

## 5-Minute Start

### 1. Open Claude Code in your KMP project

```bash
cd your-kmp-project
claude code
```

Or use the web app at [claude.ai/code](https://claude.ai/code).

### 2. Ask for help routing your next task

Type in the chat:
```
Use kotlin-multiplatform-expert — I need to add a login feature to my KMP app
```

Or simpler:
```
I need to add a login feature
```

The expert skill will:
- Map which skills you need and in what order
- Explain the 6-layer architecture (model → api → domain → data → presenter → ui)
- Hand off to the right domain skill (e.g., `ktor-auth-service` for the backend, `mvi` for the UI)

### 3. Follow the skill's guidance step-by-step

Each skill produces:
- Boilerplate code you copy/paste
- Architecture contracts you follow
- Anti-patterns to avoid
- Links to the full SKILL.md for deep dives

### 4. Audit your work

Before shipping:
```
Use kotlin-multiplatform-audit to review my changes
```

The audit catches:
- Layer boundary violations
- State handling mistakes
- Missing tests
- Design system inconsistencies

## Common Starting Points

| Goal | Use this skill first |
|---|---|
| **New KMP project from scratch** | `kotlin-multiplatform-feature-scaffold` (after reading `clean-architecture` for the rules) |
| **Add a new feature** | `kotlin-multiplatform-expert` (it will route you) |
| **Audit an existing project** | `kotlin-multiplatform-audit` |
| **Set up CI/CD** | `kotlin-multiplatform-ci-github-actions` |
| **Publish to Maven Central** | `kotlin-multiplatform-release` |
| **Debug architecture issues** | `kotlin-multiplatform-audit` (produces findings), then `kotlin-multiplatform-expert` (routes fixes) |

## How Skill Triggering Works

Skills auto-activate when you mention a trigger keyword. You don't need to say the skill name explicitly.

Say this:
```
How do I set up auth with JWT?
```

Claude will invoke `kotlin-multiplatform-ktor-auth-service` automatically because "JWT" and "auth" are trigger keywords.

See [README.md](README.md#trigger-keywords) for the full keyword list.

## Skill Collection Overview

**49 skills** organized into layers:

- **Foundation** (6 skills) — project setup, clean architecture rules, DI, CI
- **Infrastructure** (8 skills) — networking, databases, auth, logging
- **Patterns** (11 skills) — repositories, navigation, offline-first, paging
- **UI System** (9 skills) — design tokens, components, animations, state hoisting
- **Testing & Quality** (3 skills) — unit tests, screenshots, code quality
- **Meta** (2 skills) — expert routing, project audit
- **Plus:** JNI bridge, legal docs, push notifications, analytics, biometric auth, and more

See [README.md](README.md#skill-map) for the full map.

## Versioning & Stability

Install the latest collection:
```bash
npx skills add ronjunevaldoz/kmm-agent-skills
```

Or pin to a specific version in `.kmm-skills`:
```json
{
  "skills_repo": "ronjunevaldoz/kmm-agent-skills",
  "version": "1.25.2"
}
```

All skills are tested and versioned together. [CHANGELOG.md](CHANGELOG.md) tracks what changed each release.

## Governance: Enforce Skills in CI

Automatically fail builds that violate skill guidance:

**.kmm-skills** (project root)
```json
{
  "skills_repo": "ronjunevaldoz/kmm-agent-skills",
  "version": "1.25.2"
}
```

**.github/workflows/governance.yml**
```yaml
name: KMM Governance
on: [pull_request, push]

jobs:
  kmm-governance:
    uses: ronjunevaldoz/kmm-agent-skills/.github/workflows/kmm-audit.yml@main
    with:
      project_root: .
      fail_on: HIGH
      skills_ref: v1.25.2
```

Done. The workflow will catch architecture violations, hardcoded colors, Material theme usage, and layout inconsistencies before merge.

## File an Issue if Something's Wrong

<a name="when-to-file-here"></a>
**File here** if a skill gave you wrong guidance or missed a case.

**File in your own repo** if you applied the guidance correctly and something in your project broke (that's a project bug, not a skill bug).

Use `/report-skill-issue` from Claude Code to file with the right template.

## Next Steps

1. **Explore the skills:** Read [README.md](README.md#skill-map) to see what's available
2. **Ask the expert:** "What should I do next with my KMP project?" → `kotlin-multiplatform-expert` routes you
3. **Read one skill fully:** Pick a relevant SKILL.md and read it top-to-bottom to understand the contract
4. **Start a feature:** "Add a login screen" → skills guide you step-by-step
5. **Audit and ship:** `kotlin-multiplatform-audit` before merge, then release with `kotlin-multiplatform-release`

---

Questions? See [README.md](README.md) for installation, [CONTRIBUTING.md](CONTRIBUTING.md) for extending skills, or open an issue for bugs.
