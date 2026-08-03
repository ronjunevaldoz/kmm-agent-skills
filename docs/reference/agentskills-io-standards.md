# agentskills.io Standards Compliance

Verified against the real spec (`agentskills.io/specification`) and the real reference
validator (`github.com/agentskills/agentskills`, `skills-ref` package) — not assumed.
Agent Skills is the open format Anthropic originally developed; `SKILL.md` in this repo
already follows it. This doc records what was actually checked, how, and what's still open.

## How this was verified

```bash
git clone --depth 1 https://github.com/agentskills/agentskills.git /tmp/agentskills-check
cd /tmp/agentskills-check/skills-ref
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Run against every skill in this repo
cd /path/to/kmp-agent-skills
for d in skills/*/; do skills-ref validate "$d" || echo "FAIL: $d"; done
```

Result as of 2026-07-26: **64/64 pass.** Zero hard-spec violations.

## The spec, in full

### Frontmatter fields

| Field | Required | Constraint |
|---|---|---|
| `name` | Yes | 1-64 chars. Lowercase unicode alphanumeric + hyphens only. No leading/trailing/consecutive hyphen. **Must match the parent directory name.** |
| `description` | Yes | 1-1024 chars, non-empty. What the skill does *and* when to use it. |
| `license` | No | License name or pointer to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (product, system packages, network access). Most skills don't need it. |
| `metadata` | No | Arbitrary string→string map. |
| `allowed-tools` | No | Space-separated pre-approved tools. Experimental. |

### Directory structure

```
skill-name/
├── SKILL.md          # Required
├── scripts/           # Optional — executable code
├── references/        # Optional — docs loaded on demand
├── assets/             # Optional — templates, static resources
```

### Progressive disclosure (the load-time budget)

1. **Discovery** (~100 tokens): every skill's `name` + `description` loads at startup.
2. **Activation** (**recommended <5000 tokens / <500 lines**): the full `SKILL.md` body
   loads when a task matches.
3. **Execution** (as needed): `scripts/`/`references/`/`assets/` load only when the
   instructions tell the agent to.

This is the one guideline this repo doesn't fully meet yet — see Known Gaps below.

### Validation

`skills-ref validate ./my-skill` is the official reference check — install instructions
above. It only checks the hard spec (frontmatter), **not** the 500-line guideline; that's
a best-practice, not a validator rule.

## This repo's compliance script

`scripts/scan_skill_issues.py` now checks the full agentskills.io picture, not just this
repo's own internal quality bar:

| Check | Severity | What it catches |
|---|---|---|
| `name_too_long` | HIGH | `name` over 64 chars |
| `name_invalid_format` | HIGH | Uppercase, leading/trailing/double hyphen, non-alphanumeric |
| `name_dir_mismatch` | HIGH | Frontmatter `name` ≠ parent directory name |
| `description_too_long` | HIGH | `description` over the 1024-char hard limit |
| `description_approaching_limit` | LOW | `description` over 800 chars — not a violation, a heads-up |
| `oversized_skill_md` | MEDIUM | `SKILL.md` body over 500 lines — the progressive-disclosure guideline |

Run it: `python3 scripts/scan_skill_issues.py`

These run alongside this repo's own pre-existing quality checks (testing coverage, stale
dates, required sections) in the same report — agentskills.io compliance isn't a separate
gate, it's part of the same one.

## Known gaps

**22 of 64 skills exceed the 500-line guideline** — up to 6.2x over
(`kmp-compose-design-system-extended` at 3101 lines). Tracked as
[KI-008](../../KNOWN_ISSUES.md#ki-008--22-of-64-skillmd-files-exceed-agentskillsios-recommended-500-line-body).
Not a hard-spec failure (`skills-ref validate` still passes all 64) — but it means the
full body loads into context every time these skills activate, instead of the core
instructions loading with detail deferred to `references/*.md`. Fixing this is a
skill-by-skill content restructuring effort, not a mechanical script — each skill needs a
judgment call on what's core-on-every-load vs. reference-on-demand.

[`docs/reference/skills-report.md`](skills-report.md) is the live, per-skill view of this
gap — regenerated on every release by `scripts/generate_skills_report.py`, sourced from
the same `scan_skill_issues.py` data as the compliance script above.

## Best-practice guidance worth knowing (not enforced, but real)

From `agentskills.io/skill-creation/best-practices.md` and `optimizing-descriptions.md`:

- **Add what the agent lacks, omit what it knows.** Don't explain what a Compose function
  is; do explain this collection's own conventions (6-layer contract, Koin scope rules).
- **Gotchas sections are the highest-value content** — concrete corrections to mistakes
  an agent will make without being told, not generic advice.
- **Imperative descriptions**: "Use this skill when..." not "This skill does...". The
  agent is deciding whether to act.
- **Provide defaults, not menus** — this repo's own "Recommendation First" section in
  every skill already does exactly this.
- **File references stay one level deep** from `SKILL.md` — don't chain
  `references/a.md` pointing to `references/b.md` pointing to `references/c.md`.

## Related

- `kmp-audit`'s `_detect_project_skill_standards` already enforces a
  version of this 500-line rule (with a `references/` escape hatch) on *consumer
  projects'* own project-owned skills — this doc is this repo holding its own 68 skills
  to the same real standard, not inventing a new one.
