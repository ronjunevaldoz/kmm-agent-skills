#!/usr/bin/env python3
"""
Generate structured release note inputs from git history and per-skill Changelog sections.

Usage:
  python3 scripts/generate_release_notes.py
  python3 scripts/generate_release_notes.py --since v1.14.0
  python3 scripts/generate_release_notes.py --since v1.13.0 --until v1.14.0
  python3 scripts/generate_release_notes.py --since v1.14.0 --skill kotlin-multiplatform-mvi
  python3 scripts/generate_release_notes.py --list-tags

Output: JSON on stdout with shape:
  {
    "since": "<ref>",
    "until": "<ref>",
    "skill_filter": "<name or null>",
    "commits": [{"sha": "...", "scope": "...", "subject": "...", "type": "..."}],
    "skill_changes": {
      "<skill-dir>": {
        "commits": [...],
        "changelog_entries": [{"date": "...", "change": "..."}]
      }
    },
    "unreleased_changelog": "<raw [Unreleased] section from CHANGELOG.md>"
  }
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


COMMIT_PATTERN = re.compile(
    r"^(?P<type>feat|fix|refine|enforce|docs|test|release|chore)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r":\s*(?P<subject>.+)$"
)

CHANGELOG_ROW_PATTERN = re.compile(
    r"^\|\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*(?P<change>.+?)\s*\|$"
)


def run(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"[generate_release_notes] warning: {' '.join(cmd)!r} exited {result.returncode}", file=sys.stderr)
        return ""
    return result.stdout.strip()


def latest_tag(repo: Path) -> str | None:
    out = run(["git", "describe", "--tags", "--abbrev=0"], cwd=repo)
    return out if out else None


def list_tags(repo: Path) -> list[str]:
    out = run(["git", "tag", "--sort=-version:refname"], cwd=repo)
    return [t for t in out.splitlines() if t]


def commits_in_range(repo: Path, since: str, until: str = "HEAD") -> list[dict]:
    fmt = "%H\x1f%s"
    out = run(["git", "log", f"{since}..{until}", f"--format={fmt}"], cwd=repo)
    commits = []
    for line in out.splitlines():
        if "\x1f" not in line:
            continue
        sha, subject = line.split("\x1f", 1)
        m = COMMIT_PATTERN.match(subject.strip())
        if m:
            commits.append({
                "sha": sha[:8],
                "type": m.group("type"),
                "scope": m.group("scope") or "",
                "subject": m.group("subject"),
            })
        else:
            commits.append({"sha": sha[:8], "type": "other", "scope": "", "subject": subject.strip()})
    return commits


def files_changed(repo: Path, since: str, until: str = "HEAD") -> list[str]:
    out = run(["git", "diff", "--name-only", f"{since}..{until}"], cwd=repo)
    return [f for f in out.splitlines() if f]


def skill_dir_for_scope(scope: str, skills_root: Path) -> str | None:
    """Map commit scope (e.g. 'audit', 'scaffold') to skill directory name."""
    if not scope:
        return None
    for d in skills_root.iterdir():
        if d.is_dir() and scope.replace("-", "") in d.name.replace("-", ""):
            return d.name
    # exact suffix match
    for d in skills_root.iterdir():
        if d.is_dir() and d.name.endswith(f"-{scope}"):
            return d.name
    return None


def read_skill_changelog(skill_md: Path) -> list[dict]:
    """Parse the ## Changelog table from a SKILL.md into [{date, change}]."""
    text = skill_md.read_text(encoding="utf-8")
    entries = []
    in_table = False
    for line in text.splitlines():
        if line.strip() == "## Changelog":
            in_table = True
            continue
        if in_table:
            if line.startswith("## ") and line.strip() != "## Changelog":
                break
            m = CHANGELOG_ROW_PATTERN.match(line.strip())
            if m:
                date = m.group("date")
                change = m.group("change")
                if date != "Date":  # skip header row
                    entries.append({"date": date, "change": change})
    return entries


def read_unreleased(changelog_md: Path) -> str:
    if not changelog_md.exists():
        return ""
    text = changelog_md.read_text(encoding="utf-8")
    m = re.search(r"## \[Unreleased\]\n(.*?)(?=\n## \[|$)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def build_report(
    repo: Path,
    since: str,
    until: str,
    skill_filter: str | None,
) -> dict:
    skills_root = repo / "skills"
    all_commits = commits_in_range(repo, since, until)
    changed_files = files_changed(repo, since, until)

    # Map each changed skill dir → its commits + changelog
    skill_changes: dict[str, dict] = {}

    # From commit scopes
    for c in all_commits:
        sd = skill_dir_for_scope(c["scope"], skills_root) if c["scope"] else None
        if sd:
            skill_changes.setdefault(sd, {"commits": [], "changelog_entries": []})
            skill_changes[sd]["commits"].append(c)

    # From file paths (catches direct SKILL.md edits with no scope in commit)
    for f in changed_files:
        parts = Path(f).parts
        if len(parts) >= 2 and parts[0] == "skills":
            sd = parts[1]
            skill_changes.setdefault(sd, {"commits": [], "changelog_entries": []})

    # Read per-skill changelog tables
    for sd in list(skill_changes.keys()):
        skill_md = skills_root / sd / "SKILL.md"
        if skill_md.exists():
            skill_changes[sd]["changelog_entries"] = read_skill_changelog(skill_md)

    # Apply skill filter
    if skill_filter:
        skill_changes = {k: v for k, v in skill_changes.items() if skill_filter in k}

    unreleased = read_unreleased(repo / "CHANGELOG.md")

    return {
        "since": since,
        "until": until,
        "skill_filter": skill_filter,
        "commits": all_commits,
        "skill_changes": skill_changes,
        "unreleased_changelog": unreleased,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default=None, help="Git ref to start from (default: latest tag)")
    parser.add_argument("--until", default="HEAD", help="Git ref to end at (default: HEAD)")
    parser.add_argument("--skill", default=None, help="Filter to a single skill name or partial match")
    parser.add_argument("--list-tags", action="store_true", help="List available git tags and exit")
    args = parser.parse_args(argv)

    repo = Path(__file__).resolve().parent.parent

    if args.list_tags:
        tags = list_tags(repo)
        print("\n".join(tags) if tags else "(no tags found)")
        return 0

    since = args.since
    if since is None:
        since = latest_tag(repo)
        if since is None:
            print('{"error": "No git tags found. Pass --since <ref> explicitly."}')
            return 1

    report = build_report(repo, since, args.until, args.skill)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
