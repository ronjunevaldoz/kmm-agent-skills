# AI Collaboration

Canonical cross-agent policy for downstream repos using `kmp-agent-skills`.

This doc exists to stop policy drift across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, repo-local skills, and one-off notes in `docs/`.

## Source Of Truth

Use these boundaries:

- `docs/*` — stable project design, ownership, architecture, and human-facing guidance
- `skills/*` (project root) — **project-owned custom skills only**, never bundled
  `kmp-agent-skills` content: what to read, what to run, what to validate
- `agents/*` — role/persona overlays for project-specific agents
- `rules/*` — optional short assistant-facing overlays only; never the only copy of
  canonical policy
- `commands/*` — repo-local slash-command sources
- `hooks/*` — repo-local hook sources
- `.agents/skills/` — deployed skills, the cross-client target (bundled
  `kmp-agent-skills` + a mirror of any custom skill) — any agentskills.io-compliant
  client reads from here, not just Claude Code
- `.claude/*` — deployed Claude-specific runtime copy (mirrors `.agents/skills/`,
  plus Claude-only `AGENTS.md`/`commands/`/`settings.json`)

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
├── skills/            # source, custom skills only
│   └── <skill-name>/SKILL.md
├── AGENTS.md        # optional Codex/OpenAI-facing bootstrap
├── CLAUDE.md        # optional Claude-facing bootstrap
├── GEMINI.md        # optional Gemini-facing bootstrap
├── .agents/
│   ├── skills/                  # deployed, cross-client target
│   └── pipeline-context.json    # planner agent context
├── .claude/
│   ├── AGENTS.md
│   ├── commands/
│   ├── skills/                  # deployed, mirrors .agents/skills/
│   └── settings.json
├── .codex/
│   ├── agents/      # *.toml — subagents; Codex has no custom-commands mechanism
│   └── skills/       # global only (~/.codex/skills) as of this writing, not project-local
└── .gemini/
    ├── commands/    # *.toml — custom commands; no confirmed subagent mechanism
    └── skills/       # global only (~/.gemini/skills) as of this writing, not project-local
```

Codex/Gemini support a different, non-symmetric subset of commands/agents/skills, in
TOML rather than Markdown — see `docs/reference/provider-capability-matrix.md` for the
real, verified matrix and the translation rules before deploying to either.

## What To Commit Vs Gitignore Under `.claude/` And `.agents/`

Gitignore only `.claude/skills/` and `.agents/skills/` (reproducible mirrors); commit
`.claude/AGENTS.md`, `.claude/settings.json`, `.claude/commands/` (project-specific, and
for `AGENTS.md`, live system-prompt content). Rationale and `.gitignore` snippet:
`skills/kmp-expert/references/agents-md-templates.md`.

## Thin Entrypoints

`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` should stay thin — bootstrap flags, a short
"read these docs first" list, and a few startup-critical guardrails. They should never
become the only place architecture or repo policy lives.

## Duplication Rule

Keep the long-form explanation canonical in `docs/reference/ai-collaboration.md`,
`docs/reference/agent-catalog.md`, and other `docs/reference/*.md` domain rules.
Duplicate only short startup guardrails in entrypoint files, and only when: the agent
must reliably see it on startup, missing it would cause expensive/unsafe work, and the duplicated text stays short and points back to the canonical doc.

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
