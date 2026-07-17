# Agent Catalog

Canonical model-routing and agent-catalog guidance for downstream repos.

Keep provider-specific model mapping here, not scattered across every agent file.

## Model Tiers

Treat `model:` as a capability tier, not a provider lock-in.

Recommended tier names:

- `flagship-coding` — hardest architecture, debugging, and high-stakes implementation work
- `balanced-coding` — default implementation and general project work
- `fast-utility` — lightweight transforms, summaries, mechanical edits, and low-risk chores
- `precision-review` — validation, final review, and high-cost correctness checks

These names are intentionally provider-neutral.

## Mapping Rule

Keep the mapping from capability tier -> concrete provider model in one canonical doc,
not in every agent file.

Anthropic column below is filled with real, currently-valid values — this repo's own
agent files (and `awaken`'s) use exactly these short aliases in `model:`, verified, not
guessed. OpenAI and Google columns are deliberately left for you to fill in yourself,
checked directly against each provider's own current docs immediately before use — an
attempt to verify them here returned model names that didn't match either provider's
real naming convention (almost certainly a stale or fabricated summary), so this doc
does not propagate an unverified guess into something you'd copy into a real config.

| Tier | OpenAI (verify before filling) | Anthropic | Google (verify before filling) |
|---|---|---|---|
| `flagship-coding` | — | `opus` | — |
| `balanced-coding` | — | `sonnet` | — |
| `fast-utility` | — | `haiku` | — |
| `precision-review` | — | `opus` | — |

Update the concrete names when provider guidance changes. The tier names stay stable.
Never fill a `—` with a guess — check https://platform.openai.com/docs/models and
https://ai.google.dev/gemini-api/docs/models directly, since model names change often
enough that anything written here today could already be stale.

## Agent File Rule

**A real agent file's `model:` frontmatter field must be a real, resolvable model id
(e.g. `sonnet`, `opus`) — never a tier name literally.** Claude Code (and other
providers) has no concept of `balanced-coding`; writing it into a real
`.claude/agents/*.md` file leaves that agent with an unresolvable model and it will
fail to load or fall back unpredictably.

Tier names exist for *this catalog document* — reasoning about and discussing agent
roles at a provider-neutral level, and for the mapping table above that resolves a tier
to the real id per provider. When you actually write or generate a repo-local agent
file:

1. Decide the tier the role needs (using this catalog's descriptions)
2. Look up that tier's real model id for the target provider in the Mapping Rule table
3. Write the **real id** into the agent file's `model:` field — not the tier name

```yaml
# ❌ WRONG — Claude Code doesn't resolve tier names
model: balanced-coding

# ✅ CORRECT — real id, looked up from the tier via the Mapping Rule table
model: sonnet
```

Repo-local agent files should still document *which tier* they map to — as a comment
or in the catalog entry (see Suggested Catalog Fields below) — so the mapping stays
traceable when provider guidance changes, but the frontmatter itself is always the
real id.

## Suggested Catalog Fields

For each repo-local agent, capture:

- `name`
- `purpose`
- `default_tier`
- `escalate_to`
- `reads_first`
- `validations_required`

## Example Agent Catalog Entry

```md
## UI Refiner

- default_tier: `balanced-coding`
- escalate_to: `flagship-coding` for deep architecture or performance work
- reads_first:
  - docs/reference/ai-collaboration.md
  - docs/reference/ui-ownership.md
  - skills/ui-refiner/SKILL.md
```

## Relationship To Other Files

- `docs/reference/ai-collaboration.md` explains where agent policy belongs
- `skills/*` define repo-local execution behavior
- `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` stay thin and point back here
