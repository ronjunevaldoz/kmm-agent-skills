#!/usr/bin/env python3
"""
Release script for kmm-agent-skills.

Usage:
    python3 scripts/release.py patch          # stable release — bug fixes, version bumps
    python3 scripts/release.py minor          # stable release — new skills, new features
    python3 scripts/release.py major          # stable release — breaking changes
    python3 scripts/release.py patch --rc     # release candidate — vX.Y.Z-rc.N tag
    python3 scripts/release.py patch --dry-run
    python3 scripts/release.py patch --rc --dry-run

Versioning tiers (see docs/reference/versioning-policy.md for the full policy):
    dev    — no tag; dev commits accumulate freely; CHANGELOG is never touched manually
    rc     — vX.Y.Z-rc.N tag; pre-release GitHub Release; CHANGELOG auto-generated
    stable — vX.Y.Z tag; full GitHub Release; CHANGELOG auto-generated

Versioning policy:
    patch — fixes only: audit false-positive corrections, typos, freshness date bumps,
            KNOWN_ISSUES updates, PLAN.md housekeeping, library version bumps
    minor — additive work: new skill, new audit pattern, new reviewer check, new command,
            new fixer rule, new agent, layout/theme enforcement additions
    major — breaking: skill section headers renamed (breaks external tooling that parses
            SKILL.md), skills.json schema changed, skill directories removed or renamed

What it does (in order):
    1.  Verify git working tree is clean
    2.  Run audit_skills_repo.py — must be zero findings
    3.  Run scan_skill_issues.py — must report zero issues
    4.  Run validate_skill_map.py — README, expert map, and planner must match
    5.  Run validate_keyword_routing.py — every skill must have routing coverage
    6.  Run pytest — must be 100% passing
    7.  Bump version in skills.json (semver base version, no pre-release suffix)
    8.  Regenerate all skill entries in skills.json from SKILL.md frontmatter
    9.  Update shipped skill count in PLAN.md
    10. Prepend new section to CHANGELOG.md (auto-generated from git log)
    11. Stage skills.json, PLAN.md, CHANGELOG.md
    12. Create a release commit: "Release vX.Y.Z" or "Release vX.Y.Z-rc.N"
    13. Create an annotated git tag vX.Y.Z or vX.Y.Z-rc.N
    14. --rc: create pre-release GitHub Release
        stable: create full GitHub Release
    15. Print push instructions — does NOT push automatically

Agents: run this script exactly as shown above. Do not push to remote
without explicit user confirmation. Never run `git tag` manually.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_JSON = REPO_ROOT / "skills.json"
PLAN_MD = REPO_ROOT / "PLAN.md"
CHANGELOG_MD = REPO_ROOT / "CHANGELOG.md"
SKILLS_DIR = REPO_ROOT / "skills"
AUDIT_SCRIPT = REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "audit_skills_repo.py"
SCAN_ISSUES_SCRIPT = REPO_ROOT / "scripts" / "scan_skill_issues.py"
VALIDATE_SKILL_MAP_SCRIPT = REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "scripts" / "validate_skill_map.py"
VALIDATE_KEYWORD_ROUTING_SCRIPT = REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "scripts" / "validate_keyword_routing.py"
TESTS_DIR = REPO_ROOT / "tests"


# ── helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, check=check)


def fail(msg: str) -> None:
    print(f"\n❌  {msg}", file=sys.stderr)
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"✅  {msg}")


def info(msg: str) -> None:
    print(f"    {msg}")


# ── step 1: clean working tree ────────────────────────────────────────────────

def check_clean_tree() -> None:
    result = run(["git", "status", "--porcelain"])
    if result.stdout.strip():
        fail(
            "Working tree is not clean. Commit or stash changes before releasing.\n"
            + result.stdout
        )
    ok("Working tree is clean")


# ── step 2: audit ─────────────────────────────────────────────────────────────

def run_audit() -> None:
    result = run(["python3", str(AUDIT_SCRIPT), str(REPO_ROOT)], check=False)
    if result.returncode != 0 or result.stdout.strip():
        fail(
            "audit_skills_repo.py found issues. Fix them before releasing.\n"
            + result.stdout
            + result.stderr
        )
    ok("Audit clean — zero findings")


def run_scan_skill_issues() -> None:
    result = run(["python3", str(SCAN_ISSUES_SCRIPT)], check=False)
    if result.returncode != 0:
        fail(
            "scan_skill_issues.py found issues. Fix them before releasing.\n"
            + result.stdout
            + result.stderr
        )
    ok("Skill issue scan clean — zero issues")


def run_skill_map_validation() -> None:
    result = run(
        ["python3", str(VALIDATE_SKILL_MAP_SCRIPT), "--repo-root", str(REPO_ROOT)],
        check=False,
    )
    if result.returncode != 0:
        fail(
            "validate_skill_map.py failed. Fix README/expert/planner routing before releasing.\n"
            + result.stdout
            + result.stderr
        )
    ok("Skill map validation passed")


def run_keyword_routing_validation() -> None:
    result = run(
        ["python3", str(VALIDATE_KEYWORD_ROUTING_SCRIPT), "--repo-root", str(REPO_ROOT)],
        check=False,
    )
    if result.returncode != 0:
        fail(
            "validate_keyword_routing.py failed. Fix invocation map coverage before releasing.\n"
            + result.stdout
            + result.stderr
        )
    ok("Keyword routing validation passed")


# ── step 3: tests ─────────────────────────────────────────────────────────────

def run_tests() -> None:
    result = run(["python3", "-m", "pytest", str(TESTS_DIR), "-v", "--tb=short"], check=False)
    if result.returncode != 0:
        fail("Tests are failing. Fix them before releasing.\n" + result.stdout + result.stderr)
    # Count passed
    match = re.search(r"(\d+) passed", result.stdout)
    count = match.group(1) if match else "?"
    ok(f"All tests pass ({count} passed)")


def run_release_validation() -> None:
    run_audit()
    run_scan_skill_issues()
    run_skill_map_validation()
    run_keyword_routing_validation()
    run_tests()


# ── step 4+5: bump version & regenerate skills.json ──────────────────────────

def bump_version(current: str, bump: str) -> str:
    parts = current.split(".")
    if len(parts) != 3:
        fail(f"Unexpected version format in skills.json: {current!r}")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def extract_skills() -> list[dict]:
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)

        name = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        license_ = re.search(r"^license:\s*(.+)$", fm, re.MULTILINE)
        last_updated = re.search(r"last-updated:\s*['\"]?(.+?)['\"]?\s*$", fm, re.MULTILINE)

        desc_match = re.search(r"^description:\s*>\n((?:  .+\n?)+)", fm, re.MULTILINE)
        if desc_match:
            desc = " ".join(line.strip() for line in desc_match.group(1).splitlines())
        else:
            dm2 = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
            desc = dm2.group(1).strip() if dm2 else ""

        kw_block = re.search(r"keywords:\n((?:    - .+\n?)+)", fm)
        keywords = []
        if kw_block:
            keywords = [re.sub(r"^\s*-\s*", "", l).strip()
                        for l in kw_block.group(1).splitlines() if l.strip()]

        trigger_match = re.search(r"\*\*Trigger keywords:\*\*\s*(.+?)(?=\n\n|\n\*\*)", text, re.DOTALL)
        triggers = []
        if trigger_match:
            raw = trigger_match.group(1).replace("\n", " ")
            triggers = [t.strip().strip(".") for t in raw.split(",") if t.strip()]

        scripts_dir = skill_dir / "scripts"
        scripts = [p.name for p in sorted(scripts_dir.glob("*.py"))] if scripts_dir.exists() else []

        skills.append({
            "name": name.group(1).strip() if name else skill_dir.name,
            "path": f"skills/{skill_dir.name}",
            "description": desc,
            "license": license_.group(1).strip() if license_ else "Apache-2.0",
            "last_updated": last_updated.group(1).strip() if last_updated else "",
            "keywords": keywords,
            "triggers": triggers,
            "scripts": scripts,
        })
    return skills


def update_skills_json(new_version: str) -> None:
    skills = extract_skills()
    manifest = {"version": new_version, "skills": skills}
    SKILLS_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    ok(f"skills.json updated — version {new_version}, {len(skills)} skills")


# ── step 6: update PLAN.md shipped count ─────────────────────────────────────

def update_plan_md(skill_count: int) -> None:
    text = PLAN_MD.read_text(encoding="utf-8")
    updated = re.sub(
        r"## Shipped Skills \(\d+\)",
        f"## Shipped Skills ({skill_count})",
        text,
    )
    if updated == text:
        info("PLAN.md shipped count already correct — no change needed")
        return
    PLAN_MD.write_text(updated, encoding="utf-8")
    ok(f"PLAN.md updated — Shipped Skills ({skill_count})")


# ── step 7–9: git commit + tag ────────────────────────────────────────────────

def get_previous_tag() -> str:
    result = run(["git", "describe", "--tags", "--abbrev=0", "HEAD"], check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def get_previous_stable_tag() -> str:
    """Return the most recent stable tag (no -rc suffix), or empty string."""
    result = run(["git", "tag", "--list", "v*", "--sort=-version:refname"], check=False)
    if result.returncode != 0:
        return ""
    for tag in result.stdout.strip().splitlines():
        if re.match(r"^v\d+\.\d+\.\d+$", tag.strip()):
            return tag.strip()
    return ""


def get_next_rc_number(base_version: str) -> int:
    """Return the next RC number for the given base version (1-based)."""
    result = run(["git", "tag", "--list", f"v{base_version}-rc.*"], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return 1
    nums = [
        int(m.group(1))
        for tag in result.stdout.strip().splitlines()
        if (m := re.search(r"-rc\.(\d+)$", tag.strip()))
    ]
    return max(nums) + 1 if nums else 1


def generate_changelog_section(new_version: str, prev_tag: str) -> str:
    """Build a CHANGELOG section from git log since prev_tag."""
    import datetime
    date = datetime.date.today().isoformat()
    tag = f"v{new_version}"

    if prev_tag:
        result = run(["git", "log", "--oneline", f"{prev_tag}..HEAD"])
    else:
        result = run(["git", "log", "--oneline"])

    lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]

    # Bucket by conventional commit prefix
    buckets: dict[str, list[str]] = {
        "feat": [], "fix": [], "docs": [], "chore": [], "other": []
    }
    for line in lines:
        sha, _, rest = line.partition(" ")
        prefix = rest.split("(")[0].split(":")[0].strip().lower()
        if prefix in buckets:
            buckets[prefix].append(f"- {rest}")
        else:
            buckets["other"].append(f"- {rest}")

    section = [f"## [{tag}] — {date}\n"]
    labels = [("feat", "Added"), ("fix", "Fixed"), ("docs", "Docs"), ("chore", "Chore"), ("other", "Other")]
    for key, heading in labels:
        if buckets[key]:
            section.append(f"### {heading}\n")
            section.extend(buckets[key])
            section.append("")

    return "\n".join(section)


def update_changelog(new_version: str, prev_tag: str, dry_run: bool) -> str:
    header = "# Changelog\n\nAll notable changes to kmm-agent-skills are documented here.\n\n"
    existing = CHANGELOG_MD.read_text(encoding="utf-8") if CHANGELOG_MD.exists() else header

    # Skip git log + prepend if a detailed entry was already written manually.
    if not dry_run and f"## [{new_version}]" in existing:
        ok(f"CHANGELOG.md already contains {new_version} entry — skipping prepend")
        return ""

    section = generate_changelog_section(new_version, prev_tag)

    if dry_run:
        info(f"[dry-run] CHANGELOG section preview:\n{section[:300]}…")
        return section

    # Strip the header so we can prepend the new section after it
    body = existing[len(header):] if existing.startswith(header) else existing
    CHANGELOG_MD.write_text(header + section + "\n---\n\n" + body, encoding="utf-8")
    ok(f"CHANGELOG.md updated — {new_version} section prepended")
    return section


def create_github_release(tag: str, changelog_section: str, dry_run: bool, prerelease: bool = False) -> None:
    result = run(["gh", "--version"], check=False)
    if result.returncode != 0:
        info("gh CLI not found — skipping GitHub Release creation")
        return

    if dry_run:
        kind = "pre-release" if prerelease else "release"
        info(f"[dry-run] would create GitHub {kind} {tag}")
        return

    cmd = ["gh", "release", "create", tag, "--title", tag, "--notes", changelog_section]
    if prerelease:
        cmd.append("--prerelease")

    result = run(cmd, check=False)
    if result.returncode == 0:
        ok(f"GitHub Release {tag} created")
    else:
        info(f"GitHub Release creation failed (non-fatal): {result.stderr.strip()}")


def git_commit_and_tag(
    new_version: str,
    tag: str,
    skill_count: int,
    changelog_section: str,
    dry_run: bool,
    prerelease: bool = False,
) -> None:
    msg = f"Release {tag}\n\n{skill_count} skills shipped. See CHANGELOG.md for details."

    if dry_run:
        info(f"[dry-run] would stage: skills.json PLAN.md CHANGELOG.md")
        info(f"[dry-run] would commit: {msg.splitlines()[0]}")
        info(f"[dry-run] would tag:    {tag}")
        return

    run(["git", "add", "skills.json", "PLAN.md", "CHANGELOG.md"])
    run(["git", "commit", "-m", msg])
    run(["git", "tag", "-a", tag, "-m", f"Release {tag} — {skill_count} skills"])
    ok(f"Committed and tagged {tag}")
    create_github_release(tag, changelog_section, dry_run=False, prerelease=prerelease)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Release kmm-agent-skills")
    parser.add_argument("bump", choices=["major", "minor", "patch"],
                        help="Version component to bump")
    parser.add_argument("--rc", action="store_true",
                        help="Create a release candidate tag (vX.Y.Z-rc.N) instead of a stable tag")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and preview without writing anything")
    args = parser.parse_args()

    tier = "RC" if args.rc else "STABLE"
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}kmm-agent-skills release — bump: {args.bump}, tier: {tier}\n")

    if not args.dry_run:
        check_clean_tree()

    run_release_validation()

    # Determine new base version
    manifest = json.loads(SKILLS_JSON.read_text())
    current_version = manifest["version"]
    new_base_version = bump_version(current_version, args.bump)

    # Build the full tag string
    if args.rc:
        rc_num = get_next_rc_number(new_base_version)
        full_version = f"{new_base_version}-rc.{rc_num}"
    else:
        full_version = new_base_version

    tag = f"v{full_version}"
    info(f"Version: {current_version} → {new_base_version}  |  Tag: {tag}")

    if args.dry_run:
        skills = extract_skills()
        info(f"Skills count: {len(skills)}")
        prev_tag = get_previous_tag()
        info(f"Previous tag: {prev_tag or '(none)'}")
        update_changelog(full_version, prev_tag, dry_run=True)
        git_commit_and_tag(new_base_version, tag, len(skills), "", dry_run=True, prerelease=args.rc)
        info("Dry run complete — nothing written")
        return 0

    prev_tag = get_previous_tag()
    info(f"Previous tag: {prev_tag or '(none)'}")

    # skills.json always stores the base semver (no -rc suffix)
    update_skills_json(new_base_version)
    skill_count = len(json.loads(SKILLS_JSON.read_text())["skills"])
    update_plan_md(skill_count)
    changelog_section = update_changelog(full_version, prev_tag, dry_run=False)
    git_commit_and_tag(new_base_version, tag, skill_count, changelog_section, dry_run=False, prerelease=args.rc)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {'Release candidate' if args.rc else 'Release'} {tag} ready.

  Push when confirmed:
    git push origin main
    git push origin {tag}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
