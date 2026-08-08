# Install — OpenAI Codex CLI and GitHub Copilot

Part of `INSTALL.md`'s per-assistant install guide. See `INSTALL.md` for Claude Code
(the primary target) and the quickest-install CLI.

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
