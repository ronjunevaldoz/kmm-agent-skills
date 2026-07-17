# Provider Capability Matrix

Verified against each provider's own docs — **do not assume symmetry between providers**;
each supports a different subset, in a different file format.

## Matrix

| Capability | Claude Code | Codex CLI | Gemini CLI |
|---|---|---|---|
| Custom commands | ✅ `.claude/commands/*.md` (Markdown) | ❌ not supported — only built-in slash commands | ✅ `.gemini/commands/*.toml` (TOML, `prompt`/`description` fields) |
| Custom subagents | ✅ `.claude/agents/*.md` (Markdown frontmatter) | ✅ `.codex/agents/*.toml` (TOML — `name`/`description`/`developer_instructions` required) | ❌ not found in current docs |
| Skills | ✅ `.claude/skills/<name>/SKILL.md` | ✅ `~/.codex/skills` (global only, confirmed) | ✅ `~/.gemini/skills` (global only, confirmed) |
| Bootstrap file | `CLAUDE.md` | `AGENTS.md` | `GEMINI.md` |

## Translation, Not Copying

`agents/*.md` and `commands/*.md` at the project root stay the single canonical
source, authored once in Claude's format. Deploying to Codex/Gemini means
**translating**, not copying:

- An agent's Markdown frontmatter (`name`, `description`) + body becomes a
  `.codex/agents/<name>.toml` file (`developer_instructions` = the body).
- A command's Markdown becomes a `.gemini/commands/<name>.toml` file (`prompt` = the
  body, with `$ARGUMENTS` rewritten to Gemini's own `{{args}}` placeholder).

Translated content may reference Claude-specific tool names or conventions that don't
map cleanly — review the translated output, don't assume a verbatim dump works.

## Related Doc

- `docs/reference/ai-collaboration.md` — canonical layout and source-of-truth boundaries
