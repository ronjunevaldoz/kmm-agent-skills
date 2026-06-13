#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_NAME_RE = re.compile(r"kotlin-multiplatform-[a-z0-9-]+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_skill_map(repo_root: Path) -> list[str]:
    skills_dir = repo_root / "skills"
    readme_path = repo_root / "README.md"
    expert_path = skills_dir / "kotlin-multiplatform-expert" / "SKILL.md"

    skill_dirs = sorted(
        p.parent for p in skills_dir.glob("*/SKILL.md") if p.is_file()
    )
    skill_names = {p.name for p in skill_dirs}

    readme_text = read_text(readme_path)
    expert_text = read_text(expert_path)

    readme_names = set(SKILL_NAME_RE.findall(readme_text))
    expert_names = set(SKILL_NAME_RE.findall(expert_text))

    errors: list[str] = []

    count_match = re.search(r"## The (\d+) Skills and What They Own", expert_text)
    if not count_match:
        errors.append("expert skill map header missing or malformed")
    else:
        declared_count = int(count_match.group(1))
        if declared_count != len(skill_names):
            errors.append(
                f"expert declares {declared_count} skills but repo has {len(skill_names)} skill folders"
            )

    missing_in_readme = sorted(skill_names - readme_names)
    missing_in_expert = sorted(skill_names - expert_names)

    if missing_in_readme:
        errors.append("missing from README: " + ", ".join(missing_in_readme))
    if missing_in_expert:
        errors.append("missing from expert: " + ", ".join(missing_in_expert))

    return errors


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate the skill map against README and expert docs.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to the repo root (defaults to the current repo)",
    )
    args = parser.parse_args(argv)

    errors = validate_skill_map(args.repo_root.resolve())

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    skill_count = len({p.parent for p in (args.repo_root / "skills").glob("*/SKILL.md") if p.is_file()})
    print(f"OK: {skill_count} skills indexed in README and expert map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
