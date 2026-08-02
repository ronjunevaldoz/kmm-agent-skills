# Installation Guide

This guide covers how to install and use the KMP agent skills with every major AI coding assistant.

## Quickest install — `npx skills add`

The [skills CLI](https://skills.sh) is the fastest way to install. It auto-detects your
agent and copies the right files to the right place:

```bash
# Install all skills (auto-detects Claude Code, Cursor, Codex, Copilot, etc.)
npx skills add ronjunevaldoz/kmp-agent-skills

# Install specific skills only
npx skills add ronjunevaldoz/kmp-agent-skills --skill kmp-feature-scaffold

# Install to a specific agent
npx skills add ronjunevaldoz/kmp-agent-skills --agent claude-code

# List available skills without installing
npx skills add ronjunevaldoz/kmp-agent-skills --list
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

Also copy the same skills to `.agents/skills/` — the
[agentskills.io](https://agentskills.io/client-implementation/adding-skills-support)
cross-client convention. `.agents/skills/` is the primary, client-neutral target; the
`.claude/skills/` copy is Claude Code's own mirror of it. If you only run Claude Code in
this project, the `.agents/skills/` copy costs nothing and future-proofs the project for
any other agentskills.io-compliant client (Cursor, Amp, Goose, and others) added later.

### Install all skills

```bash
# Clone this repo alongside your project
git clone https://github.com/ronjunevaldoz/kmp-agent-skills

# Copy all skills into your project — both the cross-client target and Claude's mirror
cp -r kmp-agent-skills/skills/* your-kmp-project/.agents/skills/
cp -r kmp-agent-skills/skills/* your-kmp-project/.claude/skills/
```

### Install a single skill

```bash
cp -r kmp-agent-skills/skills/kmp-feature-scaffold \
      your-kmp-project/.agents/skills/
cp -r kmp-agent-skills/skills/kmp-feature-scaffold \
      your-kmp-project/.claude/skills/
```

### Directory layout after install

```
your-kmp-project/
├── .agents/
│   └── skills/                  # cross-client target — primary
│       ├── kmp-feature-scaffold/
│       │   └── SKILL.md
│       ├── kmp-clean-architecture/
│       │   └── SKILL.md
│       └── ...
└── .claude/
    └── skills/                  # Claude Code's own mirror of .agents/skills/
        └── ... (same contents)
```

### Usage

Start any session with the expert skill to get routed to the right skill:

```
@kmp-expert what should I do next?
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
/use kmp-feature-scaffold
/use kmp-presenter-module
```

### Installing slash commands

> **Required review before install** — files in `commands/` define agent slash commands that can
> run shell operations on your machine. Auto-copying them is a supply chain risk: a command that
> looks like docs is actually an executable agent instruction.
>
> Do NOT copy `commands/` as part of a bulk install. Review each file first, then install only
> the ones you want.

**Step 1 — Read each command file before installing it.**

```bash
# List available commands
ls kmp-agent-skills/commands/

# Read one before approving
cat kmp-agent-skills/commands/kmp-new-skill.md
cat kmp-agent-skills/commands/kmp-run-audit.md
```

**Step 2 — Install only the commands you have reviewed.**

```bash
mkdir -p your-kmp-project/.claude/commands/

# Install individually — one at a time, after reading each
cp kmp-agent-skills/commands/kmp-new-skill.md your-kmp-project/.claude/commands/
cp kmp-agent-skills/commands/kmp-run-audit.md      your-kmp-project/.claude/commands/
```

**Or use the guided installer** (prompts you per command):

```bash
bash kmp-agent-skills/scripts/update-consumer-skills.sh \
  --source kmp-agent-skills \
  --agent-dir your-kmp-project/.claude/skills \
  --install-commands
```

Unlike the manual `cp` commands above, this script mirrors to `.agents/skills/`
automatically — no separate step needed.

The `--install-commands` flag lists each command with its header line and asks `[y/N]` before
copying it. You can review the source file in another terminal before answering.

**Consumer commands** (install these in your project):

| Command | What it does |
|---|---|
| `/kmp-new-project <description>` | Scaffold a full KMP project from natural language |
| `/kmp-setup-agents [path]` | Initialize `.claude/` agent setup in an existing KMP project |
| `/kmp-implement-feature <name>` | Plan → Implement → Validate → Review a new feature |
| `/kmp-execute-ticket <id>` | Implement a GitHub issue end-to-end |
| `/kmp-run-audit [path]` | Run architecture audit with per-finding remediation |
| `/kmp-verify [path]` | Full validation pipeline: tests, audit, screenshots |
| `/kmp-review-changes` | Review git diff against 6-layer rules |
| `/kmp-fix-design [path]` | Scan and fix design system violations |
| `/kmp-update-design-system [path]` | Pull latest design system components |
| `/kmp-record-design-baselines` | Record Roborazzi golden PNGs |
| `/kmp-audit-screenshots [path]` | Vision audit of Roborazzi goldens |
| `/kmp-audit-design-visual [path]` | Cross-screen visual consistency check |
| `/kmp-update-skills` | Pull latest skills and re-deploy |
| `/kmp-check-updates` | Check whether a newer version is available |
| `/kmp-report-skill-issue` | File a structured skill bug report |

**Or use the guided installer** to set up the full `.claude/` in one step:

```bash
# New project — scaffolds code + generates .claude/ at the end
/kmp-new-project "build a todo app with offline sync"

# Existing project — generates .claude/AGENTS.md, installs commands, deploys skills
/kmp-setup-agents .
```

Or run the shell script manually with the `--setup-agents` flag:

```bash
bash kmp-agent-skills/scripts/update-consumer-skills.sh \
  --source kmp-agent-skills \
  --agent-dir your-kmp-project/.claude/skills \
  --install-commands \
  --setup-agents
```

### Keeping local assistants in sync on this Mac

If you use Claude, Codex, or Gemini on this Mac and want all three to read the same
released skill set, run:

```bash
bash kmp-agent-skills/scripts/sync-local-assistant-skills.sh
```

This updates:

- `~/.claude/skills`
- `~/.codex/skills`
- `~/.gemini/skills`
- `~/.agents/skills` — the cross-client convention from
  [agentskills.io](https://agentskills.io/client-implementation/adding-skills-support) —
  syncing here makes these skills visible to any agentskills.io-compliant client
  (Cursor, Amp, Goose, OpenCode, Letta, Roo Code, Kiro, and others) without a
  client-specific sync step per tool

It does not copy slash commands.

If you also want to refresh the local Claude / Codex / Gemini installs on this Mac,
run the repo-maintenance command `/kmp-sync-local-skills` from the kmp-agent-skills repo.

---

## OpenAI Codex CLI

Codex CLI auto-reads `AGENTS.md` from the project root and any parent directories. Add skill content directly to `AGENTS.md`, or reference the skill files and let Codex load them.

### Option A — embed skills in `AGENTS.md`

```bash
# Append the skills you want Codex to always have in context
cat kmp-agent-skills/skills/kmp-feature-scaffold/SKILL.md >> AGENTS.md
cat kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md >> AGENTS.md
```

### Option B — reference at session start

If your AGENTS.md is already large, reference skills on-demand in your prompt:

```
Read skills/kmp-presenter-module/SKILL.md then set up the presenter layer.
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

This project follows the KMP agent skills architecture. Key constraints:

EOF

# Append the skills you want enforced globally
cat kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md \
    >> .github/copilot-instructions.md
```

### Recommended skills for `copilot-instructions.md`

Include these three — they shape the most decisions:

- `kmp-clean-architecture` — layer rules Copilot should never violate
- `kmp-presenter-module` — ViewModel conventions
- `kmp-feature-scaffold` — module naming and dependency graph

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
cp kmp-agent-skills/skills/kmp-feature-scaffold/SKILL.md \
   .cursor/rules/kmp-feature-scaffold.mdc

cp kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md \
   .cursor/rules/kmp-clean-architecture.mdc

cp kmp-agent-skills/skills/kmp-presenter-module/SKILL.md \
   .cursor/rules/kmp-presenter-module.mdc
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
cat kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md \
    kmp-agent-skills/skills/kmp-presenter-module/SKILL.md \
    > .cursorrules
```

### Usage

Reference skills in Cursor Chat with `@Rules` or by file:

```
@Rules scaffold a new auth feature module
@kmp-feature-scaffold add a presenter module for the dashboard feature
```

---

## Windsurf

Windsurf reads `.windsurfrules` (project-level) and `~/.windsurfrules` (global) for persistent instructions.

### Install

```bash
# Add architecture rules to your project
cat kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md \
    >> .windsurfrules

cat kmp-agent-skills/skills/kmp-presenter-module/SKILL.md \
    >> .windsurfrules
```

### Recommended approach

Keep `.windsurfrules` focused on the rules that should always apply (architecture contract,
anti-patterns). For task-specific skills (Roborazzi, Logging), paste the `SKILL.md` content
into the chat context when you need it:

```
Here is the Roborazzi skill:
[paste skills/kmp-roborazzi/SKILL.md]

Now add screenshot tests for the auth feature.
```

### Windsurf Memories

Windsurf also supports persistent Memories (set via the chat). Add a memory like:

```
This project uses the KMP 6-layer architecture: :model/:api/:domain/:data/:presenter/:ui.
:presenter has no Compose dependency. :ui depends only on :presenter.
Read .windsurfrules for the full contract.
```

---

## Gemini CLI

Gemini CLI (google-labs/gemini-cli) auto-loads `GEMINI.md` from the project root and parent
directories, following the same hierarchical pattern as Claude Code's `CLAUDE.md`.

### Install

First deploy skills to `.agents/skills/` (the cross-client target — see the "Keeping
local assistants in sync" section, or run `update-consumer-skills.sh`). Project-root
`skills/*/SKILL.md` is reserved for your own custom skills, never the bundled
kmp-agent-skills collection — point `GEMINI.md` at the deployed copy instead:

```bash
# Create GEMINI.md with a pointer to the deployed skills
cat > GEMINI.md << 'EOF'
# KMP Agent Skills

This project uses the KMP agent skills collection, deployed at `.agents/skills/*/SKILL.md`.

Before making architecture decisions, read the relevant skill file. Start with:
- `.agents/skills/kmp-expert/SKILL.md` — routing and build order
- `.agents/skills/kmp-clean-architecture/SKILL.md` — layer contract
- `.agents/skills/kmp-feature-scaffold/SKILL.md` — module structure

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
> Read .agents/skills/kmp-roborazzi/SKILL.md then add screenshot tests for auth.
```

Or use `@` to include files directly:

```
> @.agents/skills/kmp-presenter-module/SKILL.md set up the presenter for dashboard
```

---

## Aider

Aider supports `--read` to add read-only context files that the model can reference but not edit.

### Usage

```bash
# Pass skills as read-only context for a session
aider --read kmp-agent-skills/skills/kmp-feature-scaffold/SKILL.md \
      --read kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md \
      feature/auth/presenter/build.gradle.kts

# Or add to your .aider.conf.yml
```

### `.aider.conf.yml`

```yaml
read:
  - kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md
  - kmp-agent-skills/skills/kmp-presenter-module/SKILL.md
  - kmp-agent-skills/skills/kmp-feature-scaffold/SKILL.md
```

### `CONVENTIONS.md` approach

For skills that apply project-wide:

```bash
# Create or append to CONVENTIONS.md
cat kmp-agent-skills/skills/kmp-clean-architecture/SKILL.md \
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
  "systemMessage": "This project uses the KMP 6-layer architecture. Before making decisions, read the relevant skill file in skills/*/SKILL.md. Key rules: :presenter has no Compose dependency; :ui depends only on :presenter.",
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
@file skills/kmp-presenter-module/SKILL.md
Set up the presenter layer for the profile feature.
```

---

## Picking skills to install

Not every project needs all 30 skills. Install by phase:

### Starting a new project

```
kmp-expert
kmp-feature-scaffold
kmp-clean-architecture
kmp-flavor-environment
kmp-ci-github-actions
```

### Adding features

```
kmp-presenter-module
kmp-mvi
kmp-navigation
kmp-network-layer
kmp-repository-pattern
kmp-dependency-injection
```

### UI layer

```
kmp-design-system
kmp-preview-driven-development
kmp-roborazzi
```

### Testing & quality

```
kmp-unit-testing
kmp-code-quality
kmp-audit
```

### Infrastructure

```
kmp-sqldelight-setup
kmp-logging
kmp-shared-resources
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
# Quick update — pulls latest and redeploys skills/
bash kmp-agent-skills/scripts/update-consumer-skills.sh

# Dry-run first to see what would change
bash kmp-agent-skills/scripts/update-consumer-skills.sh --dry-run
```

> **Commands are not updated automatically.** The update script only redeploys `skills/`.
> If a command file changes between releases, the script will print a reminder. Review the
> diff manually and re-install the command if you want the update:
> ```bash
> bash kmp-agent-skills/scripts/update-consumer-skills.sh --install-commands
> ```

Each `SKILL.md` has a `**Freshness rule:**` section that tells you exactly which version
targets to recheck. The version table in [`PLAN.md`](PLAN.md) shows current targets.
