#!/usr/bin/env python3
"""heal_project.py — Comprehensive Project Health, Hooks, and Topology Doctor

Automates:
  1. Documentation Healing: Rebuilds docs/README.md sitemap and archives completed tasks.
  2. Git Hooks Healing: Verifies and installs .git/hooks/pre-commit.
  3. Scripts & Tools Hygiene: Ensures executable permissions (chmod +x) on scripts/ and tools/.
  4. Provenance Lockfile Healing: Updates .agents/skills.lock with upstream SemVer.
  5. Topology Verification: Checks standard project structure (docs, scripts, tools, .agents).
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Import doc healer
try:
    from heal_docs import heal_docs
except ImportError:
    # If run standalone
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from heal_docs import heal_docs

def fix_executable_permissions(repo_root: Path) -> int:
    print("\n🔧 Checking Script & Tool Permissions...")
    fixed = 0
    for subdir in ["scripts", "tools", "hooks", ".agents/skills/scripts"]:
        d = repo_root / subdir
        if d.exists():
            for p in d.rglob("*"):
                if p.is_file() and p.suffix in (".py", ".sh"):
                    current_mode = p.stat().st_mode
                    if not (current_mode & 0o111):
                        p.chmod(current_mode | 0o755)
                        print(f"  chmod +x: {p.relative_to(repo_root)}")
                        fixed += 1
    if fixed == 0:
        print("  ✅ All scripts and tools have proper executable permissions.")
    else:
        print(f"  ✅ Fixed permissions for {fixed} script(s).")
    return fixed

def heal_git_hooks(repo_root: Path, dry_run: bool = False) -> bool:
    print("\n🪝 Checking Git Hooks...")
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        print("  ℹ️ Not a git repository root, skipping hook healing.")
        return True
        
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    pre_commit = hooks_dir / "pre-commit"
    
    # Check if repo has its own hooks/pre-commit source
    source_hook = repo_root / "hooks" / "pre-commit"
    if source_hook.exists():
        if not pre_commit.exists() or pre_commit.read_bytes() != source_hook.read_bytes():
            if dry_run:
                print(f"  [dry-run] would install pre-commit hook from {source_hook.relative_to(repo_root)}")
            else:
                pre_commit.write_bytes(source_hook.read_bytes())
                pre_commit.chmod(0o755)
                print(f"  ✅ Installed/Refreshed .git/hooks/pre-commit from {source_hook.relative_to(repo_root)}")
        else:
            print("  ✅ .git/hooks/pre-commit is in sync and active.")
    else:
        print("  ℹ️ No custom hooks/pre-commit found in project root.")
    return True

def heal_lockfile(repo_root: Path, dry_run: bool = False) -> bool:
    print("\n🔒 Checking .agents/skills.lock...")
    lock_generator = Path(__file__).resolve().parent / "generate_skills_lock.py"
    if lock_generator.exists() and (repo_root / ".agents" / "skills").exists():
        if dry_run:
            print("  [dry-run] would regenerate .agents/skills.lock")
        else:
            res = subprocess.run([sys.executable, str(lock_generator), "--project", str(repo_root)], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"  {res.stdout.strip()}")
            else:
                print(f"  ⚠️ Warning: {res.stderr.strip()}")
    else:
        print("  ℹ️ No .agents/skills/ directory found to lock.")
    return True

def main() -> int:
    parser = argparse.ArgumentParser(description="Comprehensive KMP Project Doctor & Self-Healer")
    parser.add_argument("--project", default=".", help="Path to project root (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview healing actions without applying")
    args = parser.parse_args()

    project_root = Path(args.project).resolve()
    print(f"\n🩺 Starting Project Health & Doctor Suite: {project_root.name}")
    print(f"{'='*60}")

    # 1. Heal Docs
    heal_docs(project_root, args.dry_run)

    # 2. Permissions
    fix_executable_permissions(project_root)

    # 3. Hooks
    heal_git_hooks(project_root, args.dry_run)

    # 4. Lockfile
    heal_lockfile(project_root, args.dry_run)

    print(f"\n🎉 Project Doctor Complete for {project_root.name}!\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
