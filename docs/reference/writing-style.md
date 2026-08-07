# Writing Style — procedural text

What this repo takes from Simplified Technical English, what it deliberately rejects, and
why. Read before authoring or editing a skill's Steps section or a slash command.

---

## The rule

**A numbered step holds one instruction and stays under 20 prose words.**

Mechanically checked by `scripts/scan_skill_issues.py`'s `long_procedural_step`. Inline
code spans don't count — `binary-compatibility-validator` is an identifier, not prose
complexity.

Alongside it, for procedural text only:

- Active voice. "Run the script", not "the script should be run".
- One topic per paragraph, six sentences at most.
- Put the explanation on its own line beneath the step, not inside it.

```markdown
<!-- over the limit: two instructions and a caveat in one line -->
1. Confirm shadcn-compose is already set up in the project (`ShadcnTheme` in real source) — if not, point to `kmp-shadcn-compose` first rather than proceeding

<!-- one instruction per line, explanation beneath -->
1. Confirm shadcn-compose is set up — look for `ShadcnTheme` in real source.
   If it is missing, point to `kmp-shadcn-compose` first.
```

---

## Where it applies

| Applies | Does not apply |
|---|---|
| Numbered steps in `commands/*.md` | Changelog entries — dense by design, a historical record |
| Numbered steps in a skill's Steps / Output Style sections | "Why this is a real gap" rationale blocks |
| Verification checklists | Reference `*.md` files holding code templates |

The exemptions are deliberate. A changelog entry earns its length by recording exactly
what changed and why; compressing it destroys the evidence. A rationale block is what
makes a finding credible rather than an assertion. Neither is something an agent executes
step by step, which is where ambiguity actually costs.

---

## What was rejected, and why

[ASD-STE100](https://www.asd-ste100.org/) is the aerospace controlled-language standard —
53 writing rules plus a ~900-word approved dictionary, free to use, current edition
January 2025. It was designed so maintenance staff who don't speak English natively can't
misread a safety-critical instruction.

This repo takes its **structural** rules and rejects its **vocabulary** rules.

**Rejected: the approved dictionary.** STE enforces one word per meaning ("start", never
"begin" or "commence"). Applied here it would strip terms doing real work — *delegate*,
*deduplicate*, *heuristic*, *residual*, *taxonomy*. STE does permit technical names
outside the dictionary, so `explicitApi()` and `@DslMarker` would survive; the ordinary
precise words would not.

**Rejected: applying the 20/25-word caps to all prose.** Measured before deciding —
`kmp-code-quality/SKILL.md` averages 30.6 words per sentence with 32% over 25 words, and
`commands/kmp-setup-agents.md` 30.3 with 39% over. Bringing every sentence under the cap
would mean rewriting most of the collection, and the length being cut is mostly rationale,
which is the part worth keeping.

**On the evidence.** There is no controlled study showing STE-formatted prompts improve
LLM instruction-following. It is practitioner consensus, now encoded in several agent
skills, not a measured result. One adjacent finding points the other way: Malik et al.
(2024) found GPT-4 complied *better* as CEFR specification detail **increased**, which
suggests precision matters more than simplicity. That asymmetry is exactly why the
structural rules were adopted for instructions — where ambiguity causes a wrong action —
and the vocabulary rules were not.

---

## Related

- `scripts/scan_skill_issues.py` — `long_procedural_step` check
- `docs/reference/agentskills-io-standards.md` — the 500-line progressive-disclosure rules
- `skills/kmp-code-quality/references/comment-kdoc-conventions.md` — comment and KDoc
  rules for Kotlin source, a separate surface from this repo's own markdown
