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

For example, maintain a table like:

| Tier | OpenAI | Anthropic | Google |
|---|---|---|---|
| `flagship-coding` | current recommended flagship coding model | current recommended flagship coding model | current recommended flagship coding model |
| `balanced-coding` | current recommended balanced coding model | current recommended balanced coding model | current recommended balanced coding model |
| `fast-utility` | current recommended fast utility model | current recommended fast utility model | current recommended fast utility model |
| `precision-review` | current recommended review model | current recommended review model | current recommended review model |

Update the concrete names when provider guidance changes. The tier names stay stable.

## Agent File Rule

Repo-local agent files should:

- reference one of the canonical tiers
- describe why that tier fits the role
- avoid hardcoding a provider model unless the project truly depends on one runner

Example:

```yaml
model: balanced-coding
```

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
