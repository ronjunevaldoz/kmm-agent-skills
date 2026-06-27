# Skills audit — 2026-06-18

Run against 23 skills using `skills/kotlin-multiplatform-audit/scripts/audit_skills_repo.py`
and a manual pass against the skill creation standards.

---

## Summary

| Metric | Count |
|---|---|
| Total skills | 23 |
| Missing freshness guidance | 14 |
| No scaffold script | 18 |
| Not tracked in PLAN.md | 6 |
| Missing `## Output Style` section | 21 |

---

## Critical — automated audit failures

### Missing freshness guidance (14 skills)

`audit_skills_repo.py` requires "latest", "freshness", or "recheck" when a skill
touches fast-moving APIs (Compose, Koin, Ktor, MVI, SQLDelight, Navigation, Graphics).

Affected:
- `kotlin-multiplatform-compose-slot-api`
- `kotlin-multiplatform-compose-state-container`
- `kotlin-multiplatform-compose-state-hoisting`
- `kotlin-multiplatform-dependency-injection`
- `kotlin-multiplatform-design-system`
- `kotlin-multiplatform-design-system-extended`
- `kotlin-multiplatform-expect-actual`
- `kotlin-multiplatform-feature-scaffold`
- `kotlin-multiplatform-flavor-environment`
- `kotlin-multiplatform-graphics-modifiers`
- `kotlin-multiplatform-ktor-auth-service`
- `kotlin-multiplatform-mongodb-database`
- `kotlin-multiplatform-mvi`
- `kotlin-multiplatform-repository-pattern`

Fix: add a `**Freshness rule:**` line near Prerequisites or the dependency catalog
in each skill.

---

## High — structural standards gaps

### Missing `## Output Style` section (21 skills)

Only `kotlin-multiplatform-audit` and `kotlin-multiplatform-dependency-injection`
define response ordering. Every skill should tell the agent how to structure output
(recommendation → structure → snippet → why → alternative). Without it, agents
ignore the format standard.

Affected: all skills except the two above.

### Skills not tracked in PLAN.md (6 skills)

These skills exist in the repo but are absent from PLAN.md. The file claims 17
shipped skills; the repo has 23.

Untracked:
- `kotlin-multiplatform-audit`
- `kotlin-multiplatform-dependency-injection`
- `kotlin-multiplatform-graphics-modifiers`
- `kotlin-multiplatform-kotlin-rpc`
- `kotlin-multiplatform-ktor-auth-service`
- `kotlin-multiplatform-mongodb-database`

---

## Medium — leverage gaps

### No skill leverages Claude Code hooks

Hooks in `.claude/settings.json` could auto-run `audit_skills_repo.py` on SKILL.md
edits, run `test_skill_scripts.py` on script changes, or enforce freshness checks.
Currently all automation is manual.

Fix: configure a `PostToolUse` hook on `Write`/`Edit` targeting `SKILL.md` files.

### No scaffold script (18 skills)

Only 5 skills have scripts: `audit`, `expert`, `feature-scaffold`, `ktor-auth-service`,
`kotlin-rpc`, `mongodb-database`. High-value candidates without scripts:

- `kotlin-multiplatform-navigation`
- `kotlin-multiplatform-mvi`
- `kotlin-multiplatform-repository-pattern`
- `kotlin-multiplatform-network-layer`
- `kotlin-multiplatform-design-system`
- `kotlin-multiplatform-dependency-injection`
- `kotlin-multiplatform-expect-actual`
- `kotlin-multiplatform-compose-slot-api`

### No visual references (22 skills)

Only `kotlin-multiplatform-graphics-modifiers` has a `references/` folder. Prime
candidates: `design-system`, `design-system-extended`, `mvi`, `navigation`,
`feature-scaffold`, `repository-pattern`.

---

## Low — completeness improvements

### Missing `## Recommendation First` section (18 skills)

Newer skills (kotlin-rpc, ktor-auth-service, mongodb-database, dependency-injection,
graphics-modifiers) have it. Older skills do not.

### Missing `## Common Anti-Patterns` section (19 skills)

Only `expect-actual`, `dependency-injection`, `graphics-modifiers`, `expert` include
anti-pattern guidance. This is high-signal for agents preventing pattern misuse.

### Sparse cross-skill references (8 skills)

These skills reference at most one other skill, missing routing guidance:
- `kotlin-multiplatform-compose-slot-api`
- `kotlin-multiplatform-dependency-injection`
- `kotlin-multiplatform-expect-actual`
- `kotlin-multiplatform-feature-scaffold`
- `kotlin-multiplatform-graphics-modifiers`
- `kotlin-multiplatform-kotlin-rpc`
- `kotlin-multiplatform-ktor-auth-service`
- `kotlin-multiplatform-mongodb-database`

---

## Info — roadmap awareness

### No memory guidance in any skill

Scaffolding skills (feature-scaffold, design-system, navigation) could instruct the
agent to write a project memory with chosen module names, package prefix, or flavor
strategy so future sessions don't re-derive it.

### PLAN.md Batch 2–4 items have no skill stubs

`datastore`, `biometric-auth`, `push-notifications`, `analytics`, `testing-robot` are
planned but no skill directories exist.

---

## Fix order

1. Configure hooks (one-time, prevents regressions)
2. Add freshness guidance to 14 skills (clears automated audit)
3. Add `## Output Style` to 21 skills
4. Sync PLAN.md with the 6 untracked skills
5. Add `## Recommendation First` and `## Common Anti-Patterns` to affected skills
6. Add cross-skill references where missing
