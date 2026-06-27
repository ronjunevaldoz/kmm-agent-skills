# Versioning Policy

Canonical rules for commits, changelogs, and releases. Agents and contributors must follow exactly.

---

## Version Tiers

| Tier | Tag | Example | GitHub Release | CHANGELOG |
|---|---|---|---|---|
| **dev** | none | — | no | never touched manually |
| **rc** | `vX.Y.Z-rc.N` | `v1.29.0-rc.1` | pre-release | auto-generated |
| **stable** | `vX.Y.Z` | `v1.29.0` | full release | auto-generated |

**dev** — commit freely; CHANGELOG is never edited manually; hook enforces Conventional Commit format.

**rc** — `python3 scripts/release.py <bump> --rc`; tags `vX.Y.Z-rc.N` (N auto-increments); pre-release GitHub Release; dev commits continue normally after.

**stable** — `python3 scripts/release.py <bump>`; CHANGELOG auto-generated from git log since last stable tag; full GitHub Release. Never create this tag manually.

---

## Commit Format

Every commit must follow Conventional Commit format — enforced by `.githooks/commit-msg`:

```
<type>[optional scope]: <description>
```

| Type | When |
|---|---|
| `feat` | New skill, audit pattern, script, command |
| `fix` | Bug fix in skill, script, or tooling |
| `docs` | Documentation only |
| `chore` | Version bumps, housekeeping |
| `refactor` | Restructuring, no behavior change |
| `test` | Adding or updating tests |
| `build` / `ci` | Build system, CI/CD |

Examples: `feat(skills): add layout-system skill` · `fix: correct KSP version` · `chore(versions): bump ktor 3.5.0`

Rejected: `wip` · `fix stuff` · `update` · `agent commit`

---

## CHANGELOG Rules

| Action | Rule |
|---|---|
| Dev commit | Do NOT touch CHANGELOG.md |
| RC or stable release | `release.py` auto-generates from git log |
| Manual edit | Only to fix a typo in an already-released entry |

Good commit messages → meaningful CHANGELOG entries.

---

## Version Bump Decision

| What changed | Bump |
|---|---|
| Bug fix, typo, version update, freshness date | `patch` |
| New skill, new pattern, new reference doc | `minor` |
| Skill section renamed, schema changed, skill removed | `major` |

---

## Release Commands

```bash
python3 scripts/release.py patch --rc      # → vX.Y.Z-rc.1 (or rc.2, rc.3…)
python3 scripts/release.py patch           # → vX.Y.Z stable
python3 scripts/release.py minor           # → vX.(Y+1).0 stable
python3 scripts/release.py patch --dry-run # preview only
```

---

## Hard Rules for Agents

1. **Never `git tag` manually** — always use `scripts/release.py`.
2. **Never edit `CHANGELOG.md`** for dev commits.
3. **Every commit must use Conventional Commit format** — hook enforces this.
4. **Do not push** tags or release commits without explicit user confirmation.
5. Stable release requires clean tree + passing audit + passing tests — the script enforces this, do not bypass.

---

## Activating the Hook

```bash
git config core.hooksPath .githooks   # run once per clone
```
