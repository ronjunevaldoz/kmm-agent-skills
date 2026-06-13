#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_NAME_RE = re.compile(r"kotlin-multiplatform-[a-z0-9-]+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
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

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(skill_names)} skills indexed in README and expert map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
