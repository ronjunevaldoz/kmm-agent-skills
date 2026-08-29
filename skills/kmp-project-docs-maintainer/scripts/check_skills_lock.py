#!/usr/bin/env python3
"""check_skills_lock.py — Inspects .agents/skills.lock against upstream releases

Reports:
  1. Installed version in .agents/skills.lock
  2. Latest release on GitHub (or local upstream repo)
  3. New features, fixes, and improvements available
"""

import argparse
import json
import urllib.request
import sys
from pathlib import Path

def check_project_skills(project_root: Path) -> int:
    lock_file = project_root / ".agents" / "skills.lock"
    if not lock_file.exists():
        print(f"ℹ️ No .agents/skills.lock found in {project_root.name}.")
        return 0

    try:
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to parse .agents/skills.lock: {e}", file=sys.stderr)
        return 1

    installed_version = lock_data.get("version", "unknown").removeprefix("v")
    installed_commit = lock_data.get("commit", "unknown")[:8]
    skills_count = lock_data.get("installed_count", len(lock_data.get("installed_skills", [])))

    print(f"\n🔍 Skills Lockfile Inspection: {project_root.name}")
    print(f"{'='*60}")
    print(f"  • Installed Version : v{installed_version} ({installed_commit})")
    print(f"  • Tracked Skills    : {skills_count} skill(s)")

    # Query GitHub API for latest release
    latest_version = ""
    release_notes = ""
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/ronjunevaldoz/kmp-agent-skills/releases/latest",
            headers={"User-Agent": "kmp-agent-skills-checker"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                latest_version = data.get("tag_name", "").removeprefix("v")
                release_notes = data.get("body", "").strip()
    except Exception:
        pass

    if not latest_version:
        print("  • Upstream Status   : ⚠️ Could not reach GitHub (offline/rate-limited)")
        return 0

    print(f"  • Upstream Latest   : v{latest_version}")

    if installed_version == latest_version:
        print(f"  • Status            : 🟢 Up to date with latest release!")
        return 0
    else:
        print(f"  • Status            : 🔔 Update available: v{installed_version} → v{latest_version}")
        if release_notes:
            print("\n📋 Latest Release Improvements & Fixes:")
            for line in release_notes.splitlines()[:15]:
                print(f"    {line}")
        print("\n💡 Run `/kmp-update-skills` or `/kmp-doctor` to upgrade.")
        return 1

def main() -> int:
    parser = argparse.ArgumentParser(description="Check .agents/skills.lock freshness against upstream")
    parser.add_argument("--project", default=".", help="Project root (default: current directory)")
    args = parser.parse_args()
    return check_project_skills(Path(args.project).resolve())

if __name__ == "__main__":
    raise SystemExit(main())
