# Install — Cursor and Windsurf

Part of `INSTALL.md`'s per-assistant install guide. See `INSTALL.md` for Claude Code
(the primary target) and the quickest-install CLI.

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
