---
name: kotlin-multiplatform-audit
description: >
  KMP project audit skill for reviewing an existing Kotlin Multiplatform codebase.
  Use this skill to inspect architecture, module boundaries, state handling, repository
  and network layering, Compose patterns, expect/actual usage, shared resources,
  design system usage, test coverage, and platform readiness. Produces findings,
  risk levels, and a fix sequence instead of implementation code. Pair with
  kotlin-multiplatform-expert to route any follow-up work to the right domain skills.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-13'
  keywords:
    - KMP audit
    - project audit
    - architecture review
    - boundary review
    - architecture drift
    - clean architecture audit
    - module audit
    - state audit
    - repository audit
    - Compose audit
    - expect actual audit
    - KMP review
    - project health check
    - readiness review
---

## When to Use This Skill

Use this skill when you need to:
- Review an existing KMP repo for architecture drift or missing boundaries
- Check whether a feature or module is in the right place
- Validate MVI, repository, Compose, and `expect/actual` choices
- Produce a fix order before making code changes
- Compare the project against this collection's recommended KMP patterns

**Trigger keywords:** audit repo, review architecture, project health, boundary check,
module review, KMP audit, clean architecture review, readiness review, architecture drift,
what is wrong with this project, inspect this repo.

---

## Audit Flow

1. Read the project docs first: `AGENTS.md`, `README.md`, architecture notes, and any
   module-specific guidance.
2. Inspect the module graph and dependency direction.
3. Check data flow boundaries: UI, domain, data, network, database, platform code.
4. Check Compose patterns: MVI, state hoisting, slots, state containers, design system.
5. Check multiplatform choices: `expect/actual`, shared resources, platform targets.
6. Report findings with severity, evidence, and the recommended fix order.

This skill does **not** implement fixes by default. It is the review surface that tells
the user and the other skills what to do next.

---

## What to Inspect

### 1) Module boundaries
- UI must not import `:data`
- Domain must not know about DTOs or SQLDelight entities
- Repository interfaces should live in `:api`, implementations in `:data`
- Shared UI primitives should live in the design system, not feature modules

### 2) State and MVI
- Screen state should be immutable
- One-shot effects should not be replayed
- Prefer `Screen` / `Content` split for testability
- Check for the wrong state container in ephemeral UI state

### 3) Data layer
- DTOs and entities stay inside `:data`
- NetworkResult should not leak into UI state
- Repositories should own mapping and fetch strategy
- Offline support should be explicit, not accidental

### 4) Multiplatform code
- Prefer shared code in `commonMain`
- Use `expect/actual` only when platform behavior is genuinely different
- Check platform target coverage against the product goal

### 5) Design system
- Verify tokens, palette rules, and typography are consistent
- Check whether components use the right pattern for the repo's chosen UI system
- Flag hardcoded colors, sizes, and text styles

---

## Output Format

When auditing, return:
- `Findings` first, ordered by severity
- `Evidence` for each finding, with file paths when available
- `Recommended fix order`
- `Skills to use next`

Keep implementation advice short and actionable. If a finding maps cleanly to an existing skill,
name that skill so the follow-up path is obvious.

## Bundled Script

- `scripts/audit_project.py` — runs a lightweight scan for a few common KMP architecture
  smells such as effect replay bugs, state copy races, and obvious UI/data boundary leaks.
