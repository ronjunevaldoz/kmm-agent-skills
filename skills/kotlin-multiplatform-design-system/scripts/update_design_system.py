#!/usr/bin/env python3
"""
update_design_system.py — compare a project's :core:designsystem/components against
the reference implementations embedded in the design-system SKILL.md.

Usage:
  python3 update_design_system.py <project_root>
  python3 update_design_system.py <project_root> --diff AppButton
  python3 update_design_system.py <project_root> --skill-root /path/to/kmm-agent-skills

Exit codes:
  0 — all components CURRENT or MODIFIED (project exists, agent can review)
  1 — one or more components MISSING in project
  2 — SKILL.md not found
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import sys
from pathlib import Path


# Matches ### `components/AppXxx.kt` followed by a ```kotlin … ``` block in SKILL.md.
_COMPONENT_BLOCK_RE = re.compile(
    r"###\s+`components/(\w+\.kt)`\s*\n+```kotlin\n(.*?)```",
    re.DOTALL,
)

# Directories that are project-owned and must never be touched by this script.
_OWNED_DIRS = ("tokens", "theme")


def extract_reference_components(skill_md: Path) -> dict[str, str]:
    """Return {filename: code_body} for every `components/AppXxx.kt` block in SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in _COMPONENT_BLOCK_RE.finditer(text)}


def find_component_dir(project_root: Path) -> Path | None:
    """Locate the components directory inside the project's :core:designsystem."""
    candidates = [
        project_root / "core" / "designsystem" / "src" / "commonMain" / "kotlin",
        project_root / "core" / "designsystem" / "components",
        project_root / "core" / "designsystem",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _md5(text: str) -> str:
    return hashlib.md5(text.strip().encode()).hexdigest()


def compare(project_root: Path, skill_md: Path) -> list[dict]:
    """Return a list of comparison results, one per reference component."""
    reference = extract_reference_components(skill_md)
    comp_dir = find_component_dir(project_root)

    results = []
    for filename, ref_code in sorted(reference.items()):
        project_file: Path | None = None
        if comp_dir:
            matches = list(comp_dir.rglob(filename))
            project_file = matches[0] if matches else None

        if project_file is None:
            results.append({
                "file": filename,
                "status": "MISSING",
                "ref": ref_code,
                "project": None,
                "path": None,
            })
        else:
            project_code = project_file.read_text(encoding="utf-8")
            status = "CURRENT" if _md5(ref_code) == _md5(project_code) else "MODIFIED"
            results.append({
                "file": filename,
                "status": status,
                "ref": ref_code,
                "project": project_code,
                "path": project_file,
            })

    return results


def _resolve_filename(name: str) -> str:
    """Normalise 'AppButton' / 'AppButton.kt' → 'AppButton.kt'."""
    if not name.endswith(".kt"):
        name = name if name.startswith("App") else f"App{name}"
        name = f"{name}.kt"
    return name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare project design system components against the skill reference."
    )
    parser.add_argument("project_root", type=Path, help="Root of the KMP project to inspect")
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=None,
        help="Path to kmm-agent-skills repo (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--diff",
        metavar="COMPONENT",
        help="Show unified diff for one component, e.g. --diff AppButton",
    )
    args = parser.parse_args()

    skill_root = args.skill_root or Path(__file__).resolve().parents[3]
    skill_md = (
        skill_root / "skills" / "kotlin-multiplatform-design-system" / "SKILL.md"
    )
    if not skill_md.exists():
        print(f"error: SKILL.md not found at {skill_md}", file=sys.stderr)
        return 2

    results = compare(args.project_root.resolve(), skill_md)

    if args.diff:
        target = _resolve_filename(args.diff)
        match = next((r for r in results if r["file"] == target), None)
        if not match:
            print(f"error: {target} not found in reference", file=sys.stderr)
            return 1
        if match["status"] == "MISSING":
            print(f"# {target} — MISSING in project\n# Reference implementation:\n")
            print(match["ref"])
        elif match["status"] == "CURRENT":
            print(f"# {target} — CURRENT (project matches skill reference)")
        else:
            diff = list(difflib.unified_diff(
                match["ref"].splitlines(keepends=True),
                match["project"].splitlines(keepends=True),
                fromfile=f"skill/{target}",
                tofile=f"project/{target}",
            ))
            print(f"# {target} — MODIFIED (skill → project diff below)\n")
            sys.stdout.writelines(diff)
        return 0

    # Default: summary report
    current  = [r for r in results if r["status"] == "CURRENT"]
    modified = [r for r in results if r["status"] == "MODIFIED"]
    missing  = [r for r in results if r["status"] == "MISSING"]

    print(f"Design system components — {len(results)} reference component(s)\n")
    print(f"  ✅  CURRENT   {len(current):>2}  (matches skill reference)")
    print(f"  ⚠️   MODIFIED  {len(modified):>2}  (project has customisations — review before updating)")
    print(f"  ❌  MISSING   {len(missing):>2}  (not yet generated in project)")
    print()

    if modified:
        print("MODIFIED — review with --diff <name> before deciding to update:")
        for r in modified:
            print(f"  {r['file']}  ({r['path']})")
        print()

    if missing:
        print("MISSING — generate with the design-system skill:")
        for r in missing:
            print(f"  {r['file']}")
        print()

    print("Reminder: tokens/ and theme/ are project-owned — this script never touches them.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
