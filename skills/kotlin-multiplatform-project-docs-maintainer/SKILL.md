---
name: kotlin-multiplatform-project-docs-maintainer
description: >
  Maintains consumer-facing KMP project documentation: README, GETTING_STARTED, INSTALL,
  RELEASING, docs/reference pages, onboarding guides, and architecture notes. Use this
  skill when project docs need to match the actual code, commands, config, or folder
  layout. Does NOT cover consumer release-note generation, per-skill changelogs, or
  skills-repo documentation.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-24'
  keywords:
    - project docs
    - consumer docs
    - README
    - getting started
    - install guide
    - releasing guide
    - docs reference
    - onboarding docs
    - architecture docs
    - docs drift
    - documentation maintainer
    - project documentation
    - repo docs
    - docs sync
---

## When to Use This Skill

Use this skill when you need to:
- update a project README so it matches the current code, commands, or modules
- refresh onboarding docs such as GETTING_STARTED, INSTALL, or RELEASING
- keep `docs/` and `docs/reference*` content aligned with the project structure
- fix stale links, command names, screenshots, diagrams, or architecture notes
- reconcile docs after a code change, refactor, or release

Do NOT use this skill when:
- you are writing consumer release notes or per-skill changelog tables
- you are maintaining the skills repo's own README, agents, commands, or skill docs
- you are implementing product code instead of updating documentation

**Trigger keywords:** project docs, consumer docs, README, getting started, install,
releasing, docs reference, onboarding docs, architecture docs, docs drift,
documentation maintainer, project documentation, repo docs.

**Freshness rule:** project docs drift whenever code, commands, config, or folder names
change — re-read the live project README, the touched docs, and the relevant source files
before editing. Re-check docs that mention version numbers, command names, or module
paths after each code change.

---

## Recommendation First

Default to this sequence:
1. Read the live docs and the source files they describe.
2. Update the smallest docs surface that is now stale.
3. Keep terminology, command names, module names, and links consistent across all touched files.
4. Re-run any repo-specific validation or link checks before handing the docs back.

Why:
- project docs are only useful when they match the code people actually run
- stale onboarding or README guidance causes more confusion than missing guidance
- keeping one canonical phrasing across README, onboarding, and reference docs avoids drift

### Default Docs Topology

If a downstream project does not already have a clear docs layout, use this structure as
the default:

```text
docs/
├── tasks.md
├── tasks/
│   ├── YYYY-MM-DD-phase-1.md
│   ├── YYYY-MM-DD-phase-2.md
│   └── YYYY-MM-DD-task-log.md
├── roadmap.md
├── architecture.md
├── deployment.md
└── reference/
```

Use it like this:
- `docs/tasks.md` — single source of truth for current work, active decisions, and links
  into dated task/phasing notes
- `docs/tasks/` — dated task and phase records when work history gets too dense for one file
- `docs/roadmap.md` — consolidated planning, including integration and project planning
- `docs/architecture.md` — system design, kept as the stable long-form architecture doc
- `docs/deployment.md` — consolidated deployment and publishing flow
- `docs/reference/` — searchable technical audits, model setup notes, and deep references

Rules:
- make `docs/tasks.md` the primary entrypoint for day-to-day updates
- put detailed phase history, approvals, and dated execution notes in `docs/tasks/`
- consolidate overlapping planning or deployment docs instead of duplicating them
- keep `docs/reference/` out of the main flow; it supports the core docs, it does not replace them
- link from README or onboarding docs to `docs/tasks.md` if the project has a lot of moving parts
- if older task files exist at the root, consolidate them into `docs/tasks/` and leave a pointer
  from `docs/tasks.md` instead of keeping parallel task indexes

### Project Doc Change Checklist

| Change | Update |
|---|---|
| New module, command, or phase | README, onboarding docs, `docs/tasks.md`, and any `docs/reference*` page that mentions it |
| Renamed command or path | Every docs mention, code sample, and navigation link |
| Architecture shift | README plus the affected reference pages and diagrams |
| Release or setup change | RELEASING, INSTALL, and any onboarding checklist that relies on it |

## Project Doc Workflow

### 1) Read the current sources

Always inspect the live files first:
- the docs files you expect to change
- the code or config that those docs describe
- any linked reference docs that those files depend on

### 2) Edit the docs

Keep the docs narrow and accurate:
- prefer one canonical description over repeated paraphrases
- update examples to match the current repo shape
- remove references to deleted files, commands, or options

### 3) Validate

Use the project's own checks when the docs mention build steps, commands, or generated
output. For pure text edits, verify links and filenames by inspection.

If the docs live in this skills repo, also run:

```bash
python3 scripts/scan_skill_issues.py
python3 skills/kotlin-multiplatform-audit/scripts/audit_skills_repo.py .
```

## Testing

Use this validation matrix for project docs:

| Case | Expected |
|---|---|
| README mentions a module or command | The referenced file or command exists |
| `docs/tasks/` updates | `docs/tasks.md` links to the dated record and the dated record has a date-stamped filename |
| `docs/reference*` updates | Links resolve and match the code or configuration it documents |
| Onboarding docs change | The setup steps match the current project workflow |
| Release/setup docs change | Version numbers, paths, and commands reflect the current repo |

## Common Anti-Patterns

- Leaving a stale command name in README or onboarding docs after a rename.
- Updating one doc page and forgetting the linked reference page that explains it.
- Copying code snippets that no longer compile or run.
- Mixing consumer release-note content into general project docs.

## Related Skills

- `kotlin-multiplatform-audit` — catches doc drift when the docs repo or consumer project needs a health check.
- `kotlin-multiplatform-release` — use when project docs need to explain versioning or publishing flow.
- `kotlin-multiplatform-legal-docs` — use when the docs are specifically about privacy, terms, or compliance.

## Output Style

When asked to update project docs, respond in this order:
1. files changed
2. source-of-truth files consulted
3. validations run
4. follow-up docs that should be updated next

Keep the response focused on the project's docs surface and the source files it mirrors.

## Changelog

| Date | Change |
|---|---|
| 2026-06-24 | Expanded the default topology to include `docs/tasks/` for dated task and phase logs, with `docs/tasks.md` as the entrypoint. |
| 2026-06-24 | Added default docs topology: `docs/tasks.md`, `docs/roadmap.md`, `docs/architecture.md`, `docs/deployment.md`, and `docs/reference/` as the preferred organization for downstream projects. |
| 2026-06-24 | Initial release — consumer-facing project docs workflow, onboarding and reference-doc sync, link hygiene, and validation guidance. |
