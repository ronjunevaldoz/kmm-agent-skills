#!/usr/bin/env python3
"""
Release script for kmm-agent-skills.

Usage:
    python3 scripts/release.py patch   # bug fixes, freshness updates
    python3 scripts/release.py minor   # new skills added
    python3 scripts/release.py major   # breaking structure changes
    python3 scripts/release.py --dry-run minor

What it does (in order):
    1. Verify git working tree is clean
    2. Run audit_skills_repo.py — must be zero findings
    3. Run pytest — must be 100% passing
    4. Bump version in skills.json (semver)
    5. Regenerate all skill entries in skills.json from SKILL.md frontmatter
    6. Update shipped skill count in PLAN.md
    7. Stage skills.json and PLAN.md
    8. Create a signed commit: "Release vX.Y.Z"
    9. Create an annotated git tag vX.Y.Z
   10. Print push instructions — does NOT push automatically

Agents: run this script exactly as shown above. Do not push to remote
without explicit user confirmation.
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
SKILLS_DIR = REPO_ROOT / "skills"
AUDIT_SCRIPT = REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "audit_skills_repo.py"
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


# ── step 3: tests ─────────────────────────────────────────────────────────────

def run_tests() -> None:
    result = run(["python3", "-m", "pytest", str(TESTS_DIR), "-v", "--tb=short"], check=False)
    if result.returncode != 0:
        fail("Tests are failing. Fix them before releasing.\n" + result.stdout + result.stderr)
    # Count passed
    match = re.search(r"(\d+) passed", result.stdout)
    count = match.group(1) if match else "?"
    ok(f"All tests pass ({count} passed)")


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

def git_commit_and_tag(new_version: str, skill_count: int, dry_run: bool) -> None:
    tag = f"v{new_version}"
    msg = f"Release {tag}\n\n{skill_count} skills shipped. See PLAN.md for details."

    if dry_run:
        info(f"[dry-run] would stage: skills.json PLAN.md")
        info(f"[dry-run] would commit: {msg.splitlines()[0]}")
        info(f"[dry-run] would tag:    {tag}")
        return

    run(["git", "add", "skills.json", "PLAN.md"])
    run(["git", "commit", "-m", msg])
    run(["git", "tag", "-a", tag, "-m", f"Release {tag} — {skill_count} skills"])
    ok(f"Committed and tagged {tag}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Release kmm-agent-skills")
    parser.add_argument("bump", choices=["major", "minor", "patch"],
                        help="Version component to bump")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and preview without writing anything")
    args = parser.parse_args()

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}kmm-agent-skills release — bump: {args.bump}\n")

    if not args.dry_run:
        check_clean_tree()

    run_audit()
    run_tests()

    # Determine new version
    manifest = json.loads(SKILLS_JSON.read_text())
    current_version = manifest["version"]
    new_version = bump_version(current_version, args.bump)
    info(f"Version: {current_version} → {new_version}")

    if args.dry_run:
        skills = extract_skills()
        info(f"Skills count: {len(skills)}")
        info("Dry run complete — nothing written")
        return 0

    update_skills_json(new_version)
    skill_count = len(json.loads(SKILLS_JSON.read_text())["skills"])
    update_plan_md(skill_count)
    git_commit_and_tag(new_version, skill_count, dry_run=False)

    tag = f"v{new_version}"
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Release {tag} ready.

  Push when confirmed:
    git push origin main
    git push origin {tag}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
