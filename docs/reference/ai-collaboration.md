# AI Collaboration

Canonical cross-agent policy for downstream repos using `kmm-agent-skills`.

This doc exists to stop policy drift across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
repo-local skills, and one-off notes in `docs/`.

## Source Of Truth

Use these boundaries:

- `docs/*` — stable project design, ownership, architecture, and human-facing guidance
- `skills/*` — repo-local execution guidance for agents: what to read, what to run,
  what validations to perform, and project-specific workflow checklists
- `agents/*` — role/persona overlays for project-specific agents
- `rules/*` — optional short assistant-facing overlays only; never the only copy of
  canonical policy
- `commands/*` — repo-local slash-command sources
- `hooks/*` — repo-local hook sources
- `.claude/*` — deployed Claude runtime copy

Quick rule:

- if it answers "how is this project designed?" -> `docs/*`
- if it answers "how should an agent work in this repo?" -> `skills/*`

Do not let `skills/*` grow into duplicated architecture docs.

## Canonical Layout

```text
<project root>/
├── docs/
│   ├── architecture.md
│   └── reference/
│       ├── ai-collaboration.md
│       ├── agent-catalog.md
│       └── <domain-rule>.md
├── agents/
├── rules/
├── commands/
├── hooks/
├── skills/
│   └── <skill-name>/SKILL.md
├── AGENTS.md        # optional Codex/OpenAI-facing bootstrap
├── CLAUDE.md        # optional Claude-facing bootstrap
├── GEMINI.md        # optional Gemini-facing bootstrap
└── .claude/
    ├── AGENTS.md
    ├── commands/
    ├── skills/
    └── settings.json
```

## Thin Entrypoints

`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` should stay thin.

They may contain:

- bootstrap flags or tool-specific startup config
- a short "read these docs first" list
- a few critical guardrails that are important enough to repeat on startup

They should not become the only place that architecture or repo policy lives.

## Duplication Rule

Keep the long-form explanation canonical in:

- `docs/reference/ai-collaboration.md`
- `docs/reference/agent-catalog.md`
- other `docs/reference/*.md` domain rules

Duplicate only short startup guardrails in entrypoint files when all are true:

1. the agent must reliably see it on startup
2. missing it would cause expensive or unsafe work
3. the duplicated text stays short and points back to the canonical doc

## Docs Versus Skills

Good `docs/*` content:

- module boundaries
- ownership rules
- architecture diagrams
- domain-specific technical decisions
- release policy summaries

Good `skills/*` content:

- which repo docs to read first
- which scripts/tests/commands to run
- routing rules for local work
- project-specific implementation checklists
- repository-specific review expectations

## Starter Templates

Minimal `CLAUDE.md`:

```md
### Claude Code Project Profile

### Load skills context on initialization
--system-prompt-file=".claude/AGENTS.md"

### Read first
- docs/reference/ai-collaboration.md
- docs/reference/agent-catalog.md
```

Minimal `AGENTS.md`:

```md
# AGENTS.md

Read first:
- docs/reference/ai-collaboration.md
- docs/reference/agent-catalog.md

Critical guardrails:
- Keep entrypoints thin.
- Keep architecture policy in docs, not in runtime-only files.
```

Minimal `GEMINI.md`:

```md
# GEMINI.md

Read first:
- docs/reference/ai-collaboration.md
- docs/reference/agent-catalog.md
```

## Related Doc

- `docs/reference/agent-catalog.md` — provider-neutral model tiers and agent catalog
