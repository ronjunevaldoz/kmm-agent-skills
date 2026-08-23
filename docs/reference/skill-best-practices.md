# Skill Best-Practice Guidance (not enforced, but real)

Re-verified directly against the live `agentskills.io/skill-creation/best-practices.md`
and `optimizing-descriptions.md` on 2026-08-24. `kmp-refine-skill` uses this page as its
qualitative checklist for consumer project-owned skills — distinct from
`agentskills-io-standards.md`'s mechanical spec compliance (frontmatter, line caps).

- **Add what the agent lacks, omit what it knows.** Don't explain what a Compose function
  is; do explain this collection's own conventions (6-layer contract, Koin scope rules).
- **Design coherent units.** Scoped too narrowly forces multiple skills to load for one
  task; scoped too broadly becomes hard to activate precisely — the real test is "does
  this compose well with other skills," the same judgment call as sizing a function.
- **Aim for moderate detail.** An overly comprehensive skill hurts more than it helps —
  the agent struggles to extract what's relevant. Concise stepwise guidance with a
  working example beats exhaustive documentation covering every edge case.
- **Match specificity to fragility.** Give the agent freedom (with the *why*, not just
  the *what*) when multiple approaches are valid and the task tolerates variation; be
  prescriptive — an exact command sequence, "do not modify this" — only when operations
  are genuinely fragile or a specific order must be followed. Most skills are a mix;
  calibrate each section independently, don't apply one register to the whole file.
- **Provide defaults, not menus** — this repo's own "Recommendation First" section in
  every skill already does exactly this.
- **Favor procedures over declarations.** Teach the agent *how to approach* a class of
  problem, not *what to produce* for one specific instance — a reusable method
  generalizes to the next task, a specific answer only covers this one.
- **Gotchas sections are the highest-value content** — concrete corrections to mistakes
  an agent will make without being told ("the `users` table uses soft deletes, queries
  need `WHERE deleted_at IS NULL`"), not generic advice ("handle errors appropriately").
- **Templates for structured output** beat prose descriptions of a format — agents
  pattern-match well against a concrete template, worse against "format it nicely."
- **Progressive disclosure pointers must say *when*, not just *where*.** "Read
  `references/api-errors.md` if the API returns non-200" beats a bare "see references/
  for details" — the agent needs the trigger condition, not just the file's existence.
- **File references stay one level deep** from `SKILL.md` — don't chain
  `references/a.md` pointing to `references/b.md` pointing to `references/c.md`.
- **Imperative descriptions**: "Use this skill when..." not "This skill does...". Err on
  the side of being explicit about when it applies, including cases where the user
  doesn't name the domain directly ("even if they don't explicitly mention CSV").
- **Trigger accuracy is testable, not just guessable** — the real methodology: a labeled
  `eval_queries.json` (8-10 should-trigger, 8-10 should-not-trigger, weighted toward
  *near-miss* negatives that share vocabulary but need something else), run each query
  3× since model behavior is nondeterministic, compute a trigger rate, split train/
  validation so you don't overfit the description to your own test set. The official
  [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
  skill automates this whole loop — defer to it rather than hand-rolling an eval runner.
