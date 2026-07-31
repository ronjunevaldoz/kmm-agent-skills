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

## The `.agents/skills/` cross-client convention

Verified against `agentskills.io/client-implementation/adding-skills-support` (the
official Agent Skills implementation guide, not assumed): `.agents/skills/` — at both
project level (`<project>/.agents/skills/`) and user level (`~/.agents/skills/`) — "has
emerged as a widely-adopted convention for cross-client skill sharing." A
skills-compliant client is expected to scan it *in addition to* its own native
directory, meaning skills placed there become visible to Cursor, Amp, Goose, OpenCode,
Letta, Roo Code, Kiro, VT Code, and any other compliant client — without a
client-specific sync step per tool.

`scripts/sync-local-assistant-skills.sh` syncs to `~/.agents/skills` alongside
`~/.claude/skills`/`~/.codex/skills`/`~/.gemini/skills` for exactly this reason. Name
collisions follow the spec's own documented precedence: project-level skills override
user-level skills; within the same scope, either first-found or last-found is
acceptable (client's choice) as long as it's consistent and logs a warning.

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
