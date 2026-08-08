# Development Plan

Tracks every skill's status and the roadmap for future work.
Update when skills are added, revised, or completed.

---

## Status Key

| Symbol | Meaning |
|---|---|
| ✅ | Shipped — skill is in `main`, production-ready |
| 🔧 | Known issues — skill exists but has open defects (see KNOWN_ISSUES.md) |
| 🚧 | In progress — actively being written |
| 📋 | Planned — scoped and ready to start |
| 💡 | Idea — not yet scoped |

---

## Shipped Skills

Full roster with what each skill owns, by layer: `skills/kmp-expert/SKILL.md`'s
"The N Skills and What They Own" section — the single source of truth, mechanically
checked against README.md and the planner routing table by
`skills/kmp-expert/scripts/validate_skill_map.py`. This file used to keep its own
copy of that same table; it silently drifted to 49 of 69 skills before anyone
noticed, because nothing checked it against the real count. Don't reintroduce a
second copy here — link to it instead.

Non-shipped work (🚧 in progress, 📋 planned, 💡 idea) is tracked below, under
Upcoming, since `kmp-expert`'s table only lists what's actually shipped.

---

## Open Defects

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for tracked open items — do not duplicate its
count or contents here; that duplication is what let this line go stale before.

---

## Upcoming — Platform Compatibility

Require coordination across multiple files or introduce breaking changes to existing skill guidance.

| Item | Priority | Description |
|---|---|---|
| Kotlin 2.x / K2 verification pass | HIGH | Audit every skill's code snippets against K2 — some `expect/actual` and annotation patterns changed. Update minimum Kotlin version across all TOML snippets. |
| AGP 10 migration | MEDIUM | AGP 10 changes module graph declaration API. Update `feature-scaffold` and `clean-architecture` skills when AGP 10 stable ships. |
| Compose Multiplatform 2.x readiness | MEDIUM | CMP 2.x expected to stabilize shared navigation and resources API. `navigation`, `shared-resources`, and `adaptive-layout` skills will need version bumps and pattern updates. |
| Skill freshness CI gate | LOW | `/kmp-setup-hooks Option C` describes a weekly cron. Add it to the repo's own `.github/workflows/` so freshness warnings surface without a local install — `kmp-audit.yml`/`repo-validation.yml` don't cover this yet. |

---

## Version Targets

| Tool | Current | Next target |
|---|---|---|
| AGP | 9.2.0 | AGP 10 stable |
| Kotlin | 2.4.0 | Track K2 stable |
| Compose Multiplatform | 1.11.1 | CMP 2.x stable |
| Koin | 4.2.1 | — |
| Ktor | 3.5.0 | — |
| SQLDelight | 2.0.2 | — |

---

## Contribution Notes

- Every skill must follow the "real skill" principle: 80% patterns/decisions/pitfalls, ≤20% dependency setup
- Skill descriptions must be specific enough to trigger correctly — test against the keyword list before shipping
- Use `/kmp-new-skill` to scaffold — it enforces all required sections at creation time
- Use `/kmp-modify-skill` to edit — it prevents accidental removal of required sections
- Run `python3 scripts/scan_skill_issues.py` after any SKILL.md change to verify zero HIGH findings
- Run `python3 skills/kmp-expert/scripts/validate_skill_map.py --repo-root .` after adding a skill to confirm README, expert, and planner are all updated
- Run `python3 skills/kmp-expert/scripts/validate_keyword_routing.py` after adding invocation map rows to confirm every skill has keyword routing coverage
- Run `/kmp-audit-screenshots` after recording Roborazzi goldens to verify design-system compliance visually
- Use `/kmp-new-project <description or samples/*.md>` to bootstrap a full KMP project from scratch
- To run E2E tests against a sample spec: clone a clean sandbox repo, then run `/kmp-new-project samples/todo-app.md`
