# Versioning Policy

Canonical rules for how commits, changelogs, and releases are managed in this repo.
Agents and contributors must follow these rules exactly — no exceptions.

---

## Version Tiers

Every release falls into exactly one tier. The tier is determined by the git tag suffix, not by the commit message.

| Tier | Tag format | Example | GitHub Release | CHANGELOG entry |
|---|---|---|---|---|
| **dev** | no tag | — | no | no |
| **rc** | `vX.Y.Z-rc.N` | `v1.29.0-rc.1` | pre-release | auto-generated |
| **stable** | `vX.Y.Z` | `v1.29.0` | full release | auto-generated |

---

## Tier Rules

### dev — work in progress

- Any commit that does not create a tag is a dev commit.
- **CHANGELOG.md is never edited manually for dev commits.** The release script generates it from git log at release time.
- Commit messages must follow the Conventional Commit format (enforced by `commit-msg` hook).
- Dev commits accumulate on `main` freely. There is no limit on how many dev commits precede a release.

### rc — release candidate

- Used when a batch of dev work is ready for validation before shipping stable.
- Created with: `python3 scripts/release.py <bump> --rc`
- Tags as `vX.Y.Z-rc.N`. If `vX.Y.Z-rc.1` already exists, the next call creates `vX.Y.Z-rc.2`.
- CHANGELOG and skills.json are auto-updated by the release script.
- Creates a **pre-release** on GitHub — not visible as the latest release.
- After an RC, dev commits continue normally. The next stable release captures everything since the last stable tag.

### stable — production release

- Created with: `python3 scripts/release.py <bump>`
- Tags as `vX.Y.Z` with no suffix.
- CHANGELOG is auto-generated from git log since the previous stable tag.
- Creates a **full GitHub Release** — visible as the latest release.
- **Never create a stable tag manually.** Always use the release script.

---

## Commit Message Format

Every commit must use Conventional Commit format. This is enforced by the `commit-msg` git hook.

```
<type>[optional scope]: <description>
```

**Allowed types:**

| Type | When to use |
|---|---|
| `feat` | New skill, new audit pattern, new script, new command |
| `fix` | Bug fix in a skill, audit script, or tooling |
| `docs` | Documentation changes only |
| `chore` | Version bumps, dependency updates, housekeeping |
| `refactor` | Code restructuring with no behavior change |
| `test` | Adding or updating tests |
| `style` | Formatting, whitespace (no logic change) |
| `perf` | Performance improvement |
| `build` | Build system or CI changes |
| `ci` | CI/CD pipeline changes |

**Examples:**
```
feat(skills): add kotlin-multiplatform-layout-system skill
fix: correct KSP version scheme in feature-scaffold
chore(versions): bump ktor 3.1.3 → 3.5.0
docs: add dependency compatibility matrix
refactor(audit): extract jvm-api check into separate function
```

**Rejected commit messages (hook will block these):**
```
wip
fix stuff
update
misc changes
agent commit
```

---

## CHANGELOG Rules

| Action | Rule |
|---|---|
| Dev commit | Do NOT touch CHANGELOG.md |
| RC release | `release.py --rc` auto-generates the entry |
| Stable release | `release.py` auto-generates the entry |
| Manual edit | Only allowed to fix a typo in an existing released entry |

The CHANGELOG is generated from git log grouped by Conventional Commit type.
Good commit messages → meaningful CHANGELOG entries.
Vague commit messages → vague CHANGELOG entries — the commit author is responsible.

---

## Version Bump Decision

| What changed | Bump |
|---|---|
| Bug fix, typo, version update, freshness date, audit false-positive fix | `patch` |
| New skill, new audit pattern, new command, new reference doc | `minor` |
| Skill section headers renamed, skills.json schema changed, skill removed | `major` |

---

## Release Commands

```bash
# RC release (one or more before stable is optional)
python3 scripts/release.py patch --rc      # → v1.28.X-rc.1
python3 scripts/release.py patch --rc      # → v1.28.X-rc.2 (same base version)

# Stable release
python3 scripts/release.py patch           # → v1.28.X (full release)
python3 scripts/release.py minor           # → v1.29.0
python3 scripts/release.py major           # → v2.0.0

# Preview without writing anything
python3 scripts/release.py patch --dry-run
python3 scripts/release.py patch --rc --dry-run
```

---

## Hard Rules for Agents

1. **Never run `git tag` manually.** Always use `python3 scripts/release.py`.
2. **Never edit CHANGELOG.md manually** unless fixing a typo in an already-released entry.
3. **Every commit must use Conventional Commit format.** The `commit-msg` hook enforces this.
4. **Do not push tags or the release commit** without explicit user confirmation.
5. **RC tags do not require a user confirmation step before creation**, but the push to remote does.
6. **A stable release requires a clean working tree, passing audit, and passing tests.** The script enforces this — do not bypass it.

---

## Installing the Hooks

Run once per clone:

```bash
git config core.hooksPath .githooks
```

Or use the install script (for consumer projects):

```bash
bash scripts/install-hooks.sh
```

---

_Canonical source: `docs/reference/versioning-policy.md`_
_Referenced by: `AGENTS.md`, `scripts/release.py`_
