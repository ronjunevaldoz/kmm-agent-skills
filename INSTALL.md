# Installation Guide

This guide covers how to install and use the KMM agent skills with every major AI coding assistant.

## Quickest install — `npx skills add`

The [skills CLI](https://skills.sh) is the fastest way to install. It auto-detects your
agent and copies the right files to the right place:

```bash
# Install all skills (auto-detects Claude Code, Cursor, Codex, Copilot, etc.)
npx skills add ronjunevaldoz/kmm-agent-skills

# Install specific skills only
npx skills add ronjunevaldoz/kmm-agent-skills --skill kotlin-multiplatform-feature-scaffold

# Install to a specific agent
npx skills add ronjunevaldoz/kmm-agent-skills --agent claude-code

# List available skills without installing
npx skills add ronjunevaldoz/kmm-agent-skills --list
```

The CLI handles every agent's destination directory automatically. Use manual steps below
only if you prefer full control or are not using the CLI.

---

Each assistant also has its own mechanism for loading external context. The pattern is always the same:
**copy or reference the relevant `SKILL.md` file(s), then mention the skill by name or trigger keyword in your prompt.**

---

## Contents

- [Claude Code](#claude-code)
- [OpenAI Codex CLI](#openai-codex-cli)
- [GitHub Copilot](#github-copilot)
- [Cursor](#cursor)
- [Windsurf](#windsurf)
- [Gemini CLI](#gemini-cli)
- [Aider](#aider)
- [Continue](#continue)
- [Picking skills to install](#picking-skills-to-install)
- [Keeping skills up to date](#keeping-skills-up-to-date)

---

## Claude Code

Claude Code loads skills from the `.claude/skills/` directory in your project root. Each skill directory must contain a `SKILL.md` file. Trigger keywords in the frontmatter fire the skill automatically when Claude detects a matching intent.

### Install all skills

```bash
# Clone this repo alongside your project
git clone https://github.com/ronjunevaldoz/kmm-agent-skills

# Copy all skills into your project
cp -r kmm-agent-skills/skills/* your-kmp-project/.claude/skills/
```

### Install a single skill

```bash
cp -r kmm-agent-skills/skills/kotlin-multiplatform-feature-scaffold \
      your-kmp-project/.claude/skills/
```

### Directory layout after install

```
your-kmp-project/
└── .claude/
    └── skills/
        ├── kotlin-multiplatform-feature-scaffold/
        │   └── SKILL.md
        ├── kotlin-multiplatform-clean-architecture/
        │   └── SKILL.md
        └── ...
```

### Usage

Start any session with the expert skill to get routed to the right skill:

```
@kotlin-multiplatform-expert what should I do next?
```

Or trigger a skill directly via keyword:

```
scaffold a new feature module for auth
set up the presenter layer for the user profile screen
add Roborazzi screenshot tests
```

Claude Code matches the trigger keywords in each `SKILL.md` and loads the relevant skill automatically.

### Slash commands (Claude Code app)

If you use the Claude Code desktop or web app, you can invoke skills with `/use`:

```
/use kotlin-multiplatform-feature-scaffold
/use kotlin-multiplatform-presenter-module
```

---

## OpenAI Codex CLI

Codex CLI auto-reads `AGENTS.md` from the project root and any parent directories. Add skill content directly to `AGENTS.md`, or reference the skill files and let Codex load them.

### Option A — embed skills in `AGENTS.md`

```bash
# Append the skills you want Codex to always have in context
cat kmm-agent-skills/skills/kotlin-multiplatform-feature-scaffold/SKILL.md >> AGENTS.md
cat kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md >> AGENTS.md
```

### Option B — reference at session start

If your AGENTS.md is already large, reference skills on-demand in your prompt:

```
Read skills/kotlin-multiplatform-presenter-module/SKILL.md then set up the presenter layer.
```

### Usage

```bash
# Start Codex with your project context
codex

# In-session
> scaffold a new KMP feature module for auth
> set up the presenter layer — read SKILL.md for presenter first
```

---

## GitHub Copilot

GitHub Copilot reads `.github/copilot-instructions.md` as persistent project-level instructions.
Paste skill content here so Copilot follows your architecture decisions on every file.

### Install

```bash
mkdir -p .github

# Add a pointer and the core architecture skill
cat >> .github/copilot-instructions.md << 'EOF'

## KMP Architecture Skills

This project follows the KMM agent skills architecture. Key constraints:

EOF

# Append the skills you want enforced globally
cat kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md \
    >> .github/copilot-instructions.md
```

### Recommended skills for `copilot-instructions.md`

Include these three — they shape the most decisions:

- `kotlin-multiplatform-clean-architecture` — layer rules Copilot should never violate
- `kotlin-multiplatform-presenter-module` — ViewModel conventions
- `kotlin-multiplatform-feature-scaffold` — module naming and dependency graph

### Usage in Copilot Chat

Reference skills by name in the chat panel:

```
@workspace following the feature-scaffold skill, add a new :auth module group
```

Or paste the relevant `SKILL.md` section directly into the chat context when you need a specific skill that is not in `copilot-instructions.md`.

---

## Cursor

Cursor loads rules from `.cursor/rules/*.mdc` files (Cursor 0.45+). Each `.mdc` file has a frontmatter that controls when it applies.

### Install

```bash
mkdir -p .cursor/rules

# Convert a skill to a Cursor rule
# The SKILL.md content becomes the rule body
cp kmm-agent-skills/skills/kotlin-multiplatform-feature-scaffold/SKILL.md \
   .cursor/rules/kmm-feature-scaffold.mdc

cp kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md \
   .cursor/rules/kmm-clean-architecture.mdc

cp kmm-agent-skills/skills/kotlin-multiplatform-presenter-module/SKILL.md \
   .cursor/rules/kmm-presenter-module.mdc
```

### Add Cursor frontmatter

Cursor requires a frontmatter block so it knows when to apply each rule.
Prepend this to each `.mdc` file:

```
---
description: KMP feature scaffold — use when creating or adding KMP modules
globs: ["**/feature/**", "**/build.gradle.kts", "**/settings.gradle.kts"]
alwaysApply: false
---
```

Adjust `globs` and `description` per skill. Set `alwaysApply: true` for the architecture and
clean-architecture rules so they are always in context.

### Legacy `.cursorrules` (Cursor < 0.45)

```bash
# Concatenate the most important skills into .cursorrules
cat kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md \
    kmm-agent-skills/skills/kotlin-multiplatform-presenter-module/SKILL.md \
    > .cursorrules
```

### Usage

Reference skills in Cursor Chat with `@Rules` or by file:

```
@Rules scaffold a new auth feature module
@kmm-feature-scaffold add a presenter module for the dashboard feature
```

---

## Windsurf

Windsurf reads `.windsurfrules` (project-level) and `~/.windsurfrules` (global) for persistent instructions.

### Install

```bash
# Add architecture rules to your project
cat kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md \
    >> .windsurfrules

cat kmm-agent-skills/skills/kotlin-multiplatform-presenter-module/SKILL.md \
    >> .windsurfrules
```

### Recommended approach

Keep `.windsurfrules` focused on the rules that should always apply (architecture contract,
anti-patterns). For task-specific skills (Roborazzi, Logging), paste the `SKILL.md` content
into the chat context when you need it:

```
Here is the Roborazzi skill:
[paste skills/kotlin-multiplatform-roborazzi/SKILL.md]

Now add screenshot tests for the auth feature.
```

### Windsurf Memories

Windsurf also supports persistent Memories (set via the chat). Add a memory like:

```
This project uses the KMM 6-layer architecture: :model/:api/:domain/:data/:presenter/:ui.
:presenter has no Compose dependency. :ui depends only on :presenter.
Read .windsurfrules for the full contract.
```

---

## Gemini CLI

Gemini CLI (google-labs/gemini-cli) auto-loads `GEMINI.md` from the project root and parent
directories, following the same hierarchical pattern as Claude Code's `CLAUDE.md`.

### Install

```bash
# Create GEMINI.md with a pointer to the skills
cat > GEMINI.md << 'EOF'
# KMM Agent Skills

This project uses the KMM agent skills collection. The skills are in `skills/*/SKILL.md`.

Before making architecture decisions, read the relevant skill file. Start with:
- `skills/kotlin-multiplatform-expert/SKILL.md` — routing and build order
- `skills/kotlin-multiplatform-clean-architecture/SKILL.md` — layer contract
- `skills/kotlin-multiplatform-feature-scaffold/SKILL.md` — module structure

Key architecture rules:
- 6-layer feature model: :model / :api / :domain / :data / :presenter / :ui
- :presenter has NO Compose dependency (ViewModels testable on plain JVM)
- :ui depends ONLY on :presenter
EOF
```

### Usage

Gemini CLI reads `GEMINI.md` at session start. For skill-specific work, reference the file:

```
gemini
> Read skills/kotlin-multiplatform-roborazzi/SKILL.md then add screenshot tests for auth.
```

Or use `@` to include files directly:

```
> @skills/kotlin-multiplatform-presenter-module/SKILL.md set up the presenter for dashboard
```

---

## Aider

Aider supports `--read` to add read-only context files that the model can reference but not edit.

### Usage

```bash
# Pass skills as read-only context for a session
aider --read kmm-agent-skills/skills/kotlin-multiplatform-feature-scaffold/SKILL.md \
      --read kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md \
      feature/auth/presenter/build.gradle.kts

# Or add to your .aider.conf.yml
```

### `.aider.conf.yml`

```yaml
read:
  - kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md
  - kmm-agent-skills/skills/kotlin-multiplatform-presenter-module/SKILL.md
  - kmm-agent-skills/skills/kotlin-multiplatform-feature-scaffold/SKILL.md
```

### `CONVENTIONS.md` approach

For skills that apply project-wide:

```bash
# Create or append to CONVENTIONS.md
cat kmm-agent-skills/skills/kotlin-multiplatform-clean-architecture/SKILL.md \
    >> CONVENTIONS.md

# Use with --read on every session
aider --read CONVENTIONS.md
```

---

## Continue

Continue (the VS Code / JetBrains extension) supports `@file` context in its chat and custom
system prompts via `.continue/config.json`.

### `.continue/config.json`

```json
{
  "systemMessage": "This project uses the KMM 6-layer architecture. Before making decisions, read the relevant skill file in skills/*/SKILL.md. Key rules: :presenter has no Compose dependency; :ui depends only on :presenter.",
  "contextProviders": [
    {
      "name": "file",
      "params": {}
    }
  ]
}
```

### Usage in Continue Chat

```
@file skills/kotlin-multiplatform-presenter-module/SKILL.md
Set up the presenter layer for the profile feature.
```

---

## Picking skills to install

Not every project needs all 30 skills. Install by phase:

### Starting a new project

```
kotlin-multiplatform-expert
kotlin-multiplatform-feature-scaffold
kotlin-multiplatform-clean-architecture
kotlin-multiplatform-flavor-environment
kotlin-multiplatform-ci-github-actions
```

### Adding features

```
kotlin-multiplatform-presenter-module
kotlin-multiplatform-mvi
kotlin-multiplatform-navigation
kotlin-multiplatform-network-layer
kotlin-multiplatform-repository-pattern
kotlin-multiplatform-dependency-injection
```

### UI layer

```
kotlin-multiplatform-design-system
kotlin-multiplatform-preview-driven-development
kotlin-multiplatform-roborazzi
```

### Testing & quality

```
kotlin-multiplatform-unit-testing
kotlin-multiplatform-code-quality
kotlin-multiplatform-audit
```

### Infrastructure

```
kotlin-multiplatform-sqldelight-setup
kotlin-multiplatform-logging
kotlin-multiplatform-shared-resources
```

---

## Releasing a new version

See **[RELEASING.md](RELEASING.md)** for the full process. The short version:

```bash
python3 scripts/release.py --dry-run minor   # validate first
python3 scripts/release.py minor             # then execute
# then confirm and push:
# git push origin main && git push origin vX.Y.Z
```

---

## Keeping skills up to date

Skills reference library versions (`AGP`, `Kotlin`, `CMP`, etc.) in their frontmatter and
freshness rules. When you upgrade dependencies, pull the latest skills:

```bash
cd kmm-agent-skills
git pull

# Re-copy changed skills to your project
cp -r skills/kotlin-multiplatform-feature-scaffold .claude/skills/
```

Each `SKILL.md` has a `**Freshness rule:**` section that tells you exactly which version
targets to recheck. The version table in [`PLAN.md`](PLAN.md) shows current targets.
