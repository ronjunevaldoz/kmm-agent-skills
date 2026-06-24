---
name: kotlin-multiplatform-skill-docs-maintainer
description: >
  Maintains the KMM skills collection documentation: each skill's SKILL.md frontmatter
  and body, the expert routing map, trigger keywords, freshness notes, related skills,
  and the repo guidance that keeps skill discovery in sync. Use this skill when adding,
  renaming, or updating skills, or when validation finds stale or missing skill-doc
  guidance. Does NOT cover consumer release notes or general repo docs.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-24'
  keywords:
    - skill docs
    - SKILL.md
    - skill maintainer
    - docs maintainer
    - routing map
    - skill map
    - trigger keywords
    - freshness rule
    - last-updated
    - skill hygiene
    - skills repo
    - modify skill
    - new skill
    - docs drift
---

## When to Use This Skill

Use this skill when you need to:
- add a new skill to the collection
- rename or retire an existing skill
- update a skill's `SKILL.md` frontmatter, trigger keywords, freshness note, related skills,
  or output style
- reconcile the expert routing map, planner routing table, or README skill list with the
  actual `skills/` directory
- fix `scan_skill_issues.py` or `audit_skills_repo.py` findings tied to skill metadata

Do NOT use this skill when:
- you are writing consumer release notes or per-skill changelog tables
- you are updating the repo's general docs, README, command docs, or agent docs
- you are implementing product code instead of maintaining skill metadata

**Trigger keywords:** skill docs, SKILL.md, skill maintainer, docs maintainer, skill map,
routing map, trigger keywords, freshness rule, last-updated, new skill, modify skill,
skill hygiene, docs drift, skill audit.

**Freshness rule:** the skills collection changes whenever a skill is added, renamed,
or edited — recheck `skills/kotlin-multiplatform-expert/SKILL.md`, `agents/planner.md`,
and `README.md` before editing any skill doc. Run the validation scripts after any
routing or metadata change.

---

## Recommendation First

Default to this sequence:
1. Read the target skill, the expert routing map, the planner table, and the README skill list.
2. Update the target skill's own `SKILL.md` first.
3. Update the expert routing map and dependency graph if the skill is new, renamed, or retired.
4. Update the planner row and README skill list so discovery stays consistent.
5. Run validation before committing.

Why:
- the skill file is the source of truth for user-facing routing and behavior
- the expert map and planner are the two places where stale names usually linger
- validation catches missing sections, stale dates, and mismatched keyword routing

### Skill Doc Change Checklist

| Change | Update |
|---|---|
| New skill | `SKILL.md`, expert map, dependency graph, planner row, README skill list |
| Renamed skill | Same as new skill, plus keep the folder name and `name:` field aligned |
| Trigger keyword change | Frontmatter keywords, README trigger wording, validation output |
| Freshness refresh | `last-updated` and the `Freshness rule:` text if it references a version |
| Retired skill | Remove routing references everywhere and confirm the map no longer points to it |

## Skill Doc Workflow

### 1) Read the current sources

Always inspect the live files first:
- the target `skills/*/SKILL.md`
- `skills/kotlin-multiplatform-expert/SKILL.md`
- `agents/planner.md`
- `README.md`
- `scripts/scan_skill_issues.py`

### 2) Edit the skill doc

Keep the skill file specific and compact:
- frontmatter should describe what the skill does and does not cover
- `## When to Use This Skill` should contain concrete trigger phrases
- `## Recommendation First` should state the canonical approach
- `## Common Anti-Patterns` should capture the mistakes this skill prevents
- `## Related Skills` should point to the skills most likely to follow this one
- `## Output Style` should tell Codex how to answer when the skill is used

### 3) Update routing surfaces

When the skill is new or renamed, update:
- the expert skill map and dependency graph
- the planner routing table if the user-facing "what skill should I use?" guidance changes
- the README skill list so humans and agents see the same inventory

### 4) Validate

Run these after skill-doc changes:

```bash
python3 scripts/scan_skill_issues.py
python3 skills/kotlin-multiplatform-audit/scripts/audit_skills_repo.py .
python3 skills/kotlin-multiplatform-expert/scripts/validate_skill_map.py --repo-root .
python3 skills/kotlin-multiplatform-expert/scripts/validate_keyword_routing.py --repo-root .
```

If scripts or validation guidance changed, add or update tests for the changed script in
the same commit.

## Testing

Use these checks as the skill's validation matrix:

| Case | Expected |
|---|---|
| New skill added | The new folder exists, the expert map names it, the planner lists it, and README links it |
| Existing skill edited | `last-updated` is refreshed and `scan_skill_issues.py` reports no missing sections |
| Skill renamed or retired | Old references disappear from the expert map, planner, and README |
| Trigger words changed | Keyword routing still resolves to the right skill after `validate_keyword_routing.py` |

## Common Anti-Patterns

- Updating only the skill file and forgetting the expert map or README. That leaves the
  collection with two different skill inventories.
- Rewording trigger keywords without rerunning validation. That can silently break routing.
- Changing a skill's behavior without bumping `last-updated`. Freshness checks will drift.
- Folding consumer release-note work into this skill. Release notes belong to the changelog flow.

## Related Skills

- `kotlin-multiplatform-expert` — owns the collection-wide skill map and dependency graph.
- `kotlin-multiplatform-audit` — flags missing sections, stale metadata, and other skill repo gaps.
- `kotlin-multiplatform-release` — use when a skill change also needs versioned release notes.

## Output Style

When asked to update skill docs, respond in this order:
1. skill files changed
2. routing files changed
3. validation commands run
4. any follow-up doc drift that still needs attention

Keep the answer focused on skill metadata and routing. Do not drift into consumer release
notes or general repo docs.

## Changelog

| Date | Change |
|---|---|
| 2026-06-24 | Initial release — skill-docs maintenance workflow, routing map sync, validation matrix, and repo discovery guidance. |
