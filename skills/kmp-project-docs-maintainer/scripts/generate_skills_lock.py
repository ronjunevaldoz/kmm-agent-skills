#!/usr/bin/env python3
"""generate_skills_lock.py — Generates a .agents/skills.lock file in a consumer project

Records the exact upstream version, source repository, commit SHA, and installed skills.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def detect_source(project_root: Path) -> Path:
    """Find the kmp-agent-skills clone. This script deploys into consumer projects
    under skills/kmp-project-docs-maintainer/scripts/, so its own parent tree is
    never the source repo there — mirrors update-consumer-skills.sh's detection order."""
    env_path = os.environ.get("KMP_AGENT_SKILLS_SOURCE") or os.environ.get("KMM_AGENT_SKILLS_SOURCE")
    candidates = [Path(env_path)] if env_path else []
    candidates += [
        project_root / "skills",
        project_root.parent / "kmp-agent-skills",
        Path.home() / "dev" / "kmp-agent-skills",
        Path.home() / "Documents" / "kmp-agent-skills",
    ]
    for candidate in candidates:
        if (candidate / "skills.json").exists():
            return candidate.resolve()
    return project_root / "skills"  # falls through to the "not found" error below

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate .agents/skills.lock for a consumer project")
    parser.add_argument("--project", default=".", help="Path to consumer project root (default: current directory)")
    parser.add_argument("--source", default=None, help="Path to kmp-agent-skills source repo (auto-detected if omitted)")
    args = parser.parse_args()

    project_root = Path(args.project).resolve()
    source_root = Path(args.source).resolve() if args.source else detect_source(project_root)

    skills_json_path = source_root / "skills.json"
    if not skills_json_path.exists():
        print(f"❌ skills.json not found in {source_root}", file=sys.stderr)
        print("   Pass --source PATH, or set $KMP_AGENT_SKILLS_SOURCE to the kmp-agent-skills clone.", file=sys.stderr)
        return 1

    manifest = json.loads(skills_json_path.read_text(encoding="utf-8"))
    version = manifest.get("version", "unknown")

    commit_sha = ""
    try:
        commit_sha = run(["git", "-C", str(source_root), "rev-parse", "HEAD"])
    except Exception:
        commit_sha = "unknown"

    agents_skills_dir = project_root / ".agents" / "skills"
    installed_skills = []
    if agents_skills_dir.exists():
        for p in sorted(agents_skills_dir.iterdir()):
            if p.is_dir() and (p / "SKILL.md").exists():
                installed_skills.append(p.name)

    lock_data = {
        "$schema": "https://agentskills.io/schema/lockfile-v1.json",
        "source": "https://github.com/ronjunevaldoz/kmp-agent-skills",
        "version": f"v{version}",
        "commit": commit_sha,
        "installed_count": len(installed_skills),
        "installed_skills": installed_skills
    }

    lock_file = project_root / ".agents" / "skills.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(lock_data, indent=2) + "\n", encoding="utf-8")

    print(f"✅ Generated {lock_file.relative_to(project_root) if lock_file.is_relative_to(project_root) else lock_file}")
    print(f"   Upstream version : v{version} ({commit_sha[:8]})")
    print(f"   Skills tracked   : {len(installed_skills)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
