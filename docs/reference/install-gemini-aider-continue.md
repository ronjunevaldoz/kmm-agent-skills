# Install — Gemini CLI, Aider, and Continue

Part of `INSTALL.md`'s per-assistant install guide. See `INSTALL.md` for Claude Code
(the primary target) and the quickest-install CLI.

---

## Gemini CLI

Gemini CLI (google-labs/gemini-cli) auto-loads `GEMINI.md` from the project root and parent
directories, following the same hierarchical pattern as Claude Code's `CLAUDE.md`.

### Install

First deploy skills to `.agents/skills/` (the cross-client target — see `INSTALL.md`'s
"Keeping local assistants in sync" section, or run `update-consumer-skills.sh`).
Project-root `skills/*/SKILL.md` is reserved for your own custom skills, never the bundled
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
