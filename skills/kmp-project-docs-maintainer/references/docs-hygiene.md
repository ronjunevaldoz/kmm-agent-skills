# Docs Hygiene Reference

Full rules for classifying, cleaning, and keeping `docs/` thin.
Read this before any clean-up task on a consumer project's `docs/` directory.

---

## Doc Classification

Every file in `docs/` is one of three kinds. Classify before acting.

| Kind | Test question | Lifetime | Location |
|---|---|---|---|
| **Reference** | "How does this work?" | Permanent — update in place | `docs/` root or `docs/reference/` |
| **Task** | "What are we doing right now?" | Temporary — active while work runs | `docs/tasks/<parent>/` → `docs/tasks/<parent>/archive/` when done |
| **Non-doc** | "Is this a fixture, spec, or generated file?" | Belongs elsewhere entirely | `tests/fixtures/`, `api/`, `spec/`, project root |

### docs/ root vs docs/reference/

Both hold reference docs — the distinction is scope:

| Goes in `docs/` root | Goes in `docs/reference/` |
|---|---|
| Primary reference that the whole project relies on (`architecture.md`, `deployment.md`) | Supporting deep-dives that back up a primary doc |
| Entry-point docs linked from README | Technical audits, model setup notes, subsystem specifics |
| One per major concern — stays short and navigable | Can be numerous; readers come here by following a link, not browsing |

Rule of thumb: if you'd link to it from README, it belongs in `docs/` root. If you'd link to it from `architecture.md` or `deployment.md`, it belongs in `docs/reference/`.

### Active work lanes

Use these lanes when the project keeps planning or bug history in nested folders:

| Lane | Purpose | Example location |
|---|---|---|
| Tasks index | current work, cross-links, state summary | `docs/tasks.md` |
| MVP lane | structured MVP plan, phases, task notes | `docs/mvp/0-mvp/0-mvp.md` |
| Phase lane | one active phase under the MVP | `docs/mvp/0-mvp/0-phase/0-phase.md` |
| Task lane | individual task notes under a phase | `docs/mvp/0-mvp/0-phase/tasks/0-task.md` |
| Bug lane | active bug thread, one bug per file | `docs/bugs/0-bug.md` |

Keep these lanes short-lived and promote stable guidance out of them into
`docs/architecture.md`, `docs/deployment.md`, or `docs/reference/`.

### Classification examples

| File | Kind | Action |
|---|---|---|
| `architecture.md` | Reference (root) | Keep — primary, README-linked |
| `deployment.md` | Reference (root) | Keep — primary, README-linked |
| `stable-feature-rules.md` | Reference (root) | Keep — stable registry, updated in place |
| `MIRROR_MAP.md` (from `kmp-api-mimicry`) | Reference (root) | Keep at `docs/MIRROR_MAP.md`, not project root — a permanent, update-in-place registry of mimicked API primitives; split by Reference API into `docs/reference/mirror-map-<reference>.md` once past the 150-line limit below |
| `auth-flow-internals.md` | Reference (reference/) | Move to `docs/reference/` — subsystem deep-dive |
| `reference/*.md` | Reference (reference/) | Keep in `docs/reference/` |
| `known-blockers.md` | Task | Rename to `docs/tasks/<parent>/01-known-blockers-todo.md`; archive when resolved |
| `milestone-tracker.md` | Task | Rename + move to `docs/tasks/<parent>/01-milestone-tracker-doing.md` or `docs/mvp/`; archive when milestone ships |
| `q3-gap-plan.md` | Task | Rename + move to `docs/tasks/<parent>/01-q3-gap-plan-todo.md` or `docs/mvp/`; archive when plan completes |
| `0-bug.md` | Task lane | Keep active bug thread here; add a folder only if multiple bug files are needed |
| `0-mvp/` | Task lane | Keep active MVP plan here; archive or promote when stable |
| `tasks.md` | Task (entrypoint) | Keep at `docs/tasks.md` |
| `fixtures/*.json` | Non-doc | Move to `tests/fixtures/` or `src/test/resources/` |
| `openapi.json` | Non-doc | Move to `api/` or `spec/` at project root |

### Ambiguity test

**Will this still be useful and accurate six months from now without edits?**
- Yes → Reference.
- No → Task. Archive when done.
- Neither → Non-doc. Move it out of `docs/`.

---

## Clean-up Sequence

When cleaning a messy `docs/`, always follow this order to avoid breaking references:

1. **Classify every file** — apply the three-kind test to each file before touching anything.
2. **Grep for internal references** — before moving any file, find every doc that links to it:
   ```bash
   grep -r "filename-without-extension" docs/ README.md
   ```
3. **Update references first** — rewrite all links to point at the new location before moving the file.
4. **Move or archive** — rename to `<NN>-<slug>-<status>.md` under its parent folder if needed, then move to the correct location.
5. **Consolidate task content** — if a task-kind file exists outside `docs/tasks/`, extract its active content into `docs/tasks.md` or a numbered task note, then archive the original.
6. **Move non-docs out** — relocate fixtures, specs, and generated files to their proper homes outside `docs/`.
7. **Validate** — run the hygiene check and verify no links are broken.

---

## Consolidation Rule

If a task-kind file (blockers, gap plan, milestone tracker) exists at the `docs/` root:

1. Open `docs/tasks.md` and add a summary entry for the work it tracks.
2. Move detailed content into a numbered file under its parent:
   `docs/tasks/<parent>/01-slug-todo.md` (numbering starts at `01` and resets per parent
   folder; the date goes inside the file content, not the filename — see Naming
   Convention below).
3. Archive the original file once done: `docs/tasks/<parent>/archive/01-slug-done.md`.
4. Leave a backlink in `docs/tasks.md` pointing to the archived entry.

For completed task-kind files, archive rather than delete. The history is evidence.

If the project uses `docs/mvp/` or `docs/bugs/`, keep those lanes as the active
working surface and use `docs/tasks.md` as the index that links into them.

---

## Delete vs Archive

Git history already preserves every version of every file — archiving isn't what makes a
file recoverable, `git log`/`git show` does that regardless. Archiving is for one specific
case: a human should be able to stumble on the old content again *without* going to git
history. Ask which case applies:

| Case | Action | Why |
|---|---|---|
| Task-kind file, work is done (bug fixed, milestone shipped, plan completed) | Rename its status suffix to `-done` and archive (`docs/tasks/<parent>/archive/`, `docs/lessons/archive/`) | Future readers browsing `docs/` may want the resolution history without digging through git log |
| Reference doc now fully superseded, zero unique information left | Delete | Nothing left to browse to — keeping it around just recreates the clutter this checklist exists to prevent; git history covers "what did this used to say" |
| Non-doc file after it's been moved to its real home (`tests/fixtures/`, `api/`, project root) | Delete the `docs/` copy | The file lives on at its new path; leaving a stale copy in `docs/` is drift, not history |
| File superseded by a rename (old path, content unchanged) | Delete old path | `git mv`/rename already carries the history forward; a leftover old-named file is a duplicate, not an archive |

If in doubt whether a reference doc still has unique information, don't guess — grep for
inbound links (see Clean-up Sequence step 2) and check whether anything still points at it
before deleting.

---

## Naming Convention

All `docs/` files use **kebab-case**. Snake_case is a violation.

| Wrong | Correct |
|---|---|
| `auth_flow_internals.md` | `auth-flow-internals.md` |
| `milestone_tracker.md` | `docs/tasks/<parent>/01-milestone-tracker-doing.md` (task) or `milestone-tracker.md` (reference) |
| `q3_gap_plan.md` | `docs/tasks/<parent>/01-q3-gap-plan-todo.md` |

The audit script (`audit_skills_repo.py --docs-hygiene-only`) flags snake_case filenames automatically.

### Task filenames: `<NN>-<slug>-<status>.md`

Task files live under a parent grouping folder, never loose directly in `docs/tasks/`:

```
docs/tasks/<parent-slug>/<NN>-<task-slug>-<status>.md
```

- `<parent-slug>` — kebab-case grouping for the feature/project the task belongs to
  (e.g. `todo-app`). Every task file lives under one.
- `<NN>` — two-digit sequence number, zero-padded, **resets to `01` within each parent
  folder** — it is not a global counter across `docs/tasks/`.
- `<task-slug>` — kebab-case, short, action-first.
- `<status>` — exactly one of `todo`, `doing`, `blocked`, `done`. This is the whole
  point of the convention: status is readable from the filename alone, no need to open
  the file or grep its content.

Example: `docs/tasks/todo-app/01-add-auth-doing.md`.

**The date moves inside the file content, not the filename.** Put it right after the
title, as the file's own record of when it started:

```markdown
# Add auth

**Date:** 2026-08-22

...
```

**Rename the file when status changes** — `01-add-auth-doing.md` becomes
`01-add-auth-blocked.md` if it stalls, then `01-add-auth-done.md` when finished. A
`-done` file still sitting in the active (non-archive) parent folder is a hygiene
violation — move it to `docs/tasks/<parent>/archive/` in the same rename.

The audit script (`audit_skills_repo.py --docs-hygiene-only`) validates the
`<NN>-<slug>-<status>.md` shape, flags a `-done` file still outside `archive/`, flags a
task file with no `**Date:**` line in its content, and flags an active task file with
no matching row in `docs/tasks.md`'s Task Log table — the index has to name every
active file, or a reader can't trust it as a substitute for opening each one.

---

## Hygiene Limits (enforced by audit script)

| Rule | Limit | Action |
|---|---|---|
| Any `docs/` file (outside `archive/`) | 150 lines | Split or archive completed sections |
| Root-level named doc (`README.md`, `KNOWN_ISSUES.md`, etc. — see `_ROOT_DOCS_WITH_SIZE_LIMIT` in `audit_skills_repo.py`; `CHANGELOG.md` is exempt, it's auto-generated and append-only) | 500 lines | Split least-central sections into `docs/reference/*.md`, leave a pointer — same pattern as an oversized `SKILL.md` |
| Unprocessed lessons in `docs/lessons/` | 20 files | Harvest via `kmp-skill-harvester` |
| Lesson file age without harvest | 30 days | Harvest or archive |
| Task file with a `-done` filename suffix still in active `docs/tasks/<parent>/` | 0 | Move to `docs/tasks/<parent>/archive/` immediately |
| Task filename not matching `<NN>-<slug>-<status>.md` (status: todo/doing/blocked/done) | 0 | Rename to match the task naming convention |
| Task file missing a `**Date:**` line in its content | 0 | Add the date line — filenames no longer carry a date prefix |
| Active task file not mentioned in `docs/tasks.md` | 0 | Add a Task Log row — the index must name every active task so status is readable without opening each file |
| Non-doc file (`.json`, `.yaml`, etc.) directly in `docs/` | 0 | Move to purpose-specific directory |
| Snake_case filename in `docs/` | 0 | Rename to kebab-case |
| Reference doc (`docs/` root or `docs/reference/`) with no inbound links anywhere in the repo | 0 | Review — link it from wherever introduces the topic, or delete per Delete vs Archive above if it's genuinely stale |

### Lesson lifecycle

```
docs/lessons/YYYY-MM-DD-slug.md
    ↓  harvested + skill amended
docs/lessons/archive/YYYY-MM-DD-slug.md
```

### Running the hygiene check

```bash
# Docs hygiene only (fast)
python3 skills/kmp-audit/scripts/audit_skills_repo.py . --docs-hygiene-only

# Full audit including docs hygiene
python3 skills/kmp-audit/scripts/audit_skills_repo.py .
```

Despite the name, `--docs-hygiene-only` works standalone against **any** project's `docs/`
root, not just this skills repo — it ships inside `kmp-audit`'s own `scripts/` directory, so
every consumer project that installs `kmp-audit` already has it locally. `audit_project.py`
(the other script in the same directory) is a separate tool for Kotlin/Compose code smells
and does not implement these hygiene checks — don't reach for it here.
