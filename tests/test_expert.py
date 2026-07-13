from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

expert_scripts = load_module(
    "validate_skill_map",
    REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "scripts" / "validate_skill_map.py",
)

class ValidateSkillMapTests(unittest.TestCase):
    def test_validate_skill_map_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                """
                kotlin-multiplatform-a
                kotlin-multiplatform-b
                kotlin-multiplatform-expert
                """.strip(),
                encoding="utf-8",
            )
            # planner.md must reference all non-meta skills (short names)
            (root / "agents").mkdir()
            (root / "agents" / "planner.md").write_text(
                "| feature a | `a`, `b` |\n",
                encoding="utf-8",
            )
            skills_dir = root / "skills"
            for name in ("kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"):
                (skills_dir / name).mkdir(parents=True)
                (skills_dir / name / "SKILL.md").write_text(
                    "## The 3 Skills and What They Own\n"
                    "kotlin-multiplatform-a\n"
                    "kotlin-multiplatform-b\n"
                    "kotlin-multiplatform-expert\n",
                    encoding="utf-8",
                )

            self.assertEqual(expert_scripts.validate_skill_map(root), [])

    def test_validate_skill_map_reports_missing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("kotlin-multiplatform-a", encoding="utf-8")
            skills_dir = root / "skills"
            (skills_dir / "kotlin-multiplatform-a").mkdir(parents=True)
            (skills_dir / "kotlin-multiplatform-a" / "SKILL.md").write_text(
                "## The 1 Skills and What They Own\nkotlin-multiplatform-a\n",
                encoding="utf-8",
            )
            (skills_dir / "kotlin-multiplatform-expert").mkdir(parents=True)
            (skills_dir / "kotlin-multiplatform-expert" / "SKILL.md").write_text(
                "## The 1 Skills and What They Own\nkotlin-multiplatform-a\n",
                encoding="utf-8",
            )
            errors = expert_scripts.validate_skill_map(root)
            self.assertTrue(any("declares 1 skills but repo has 2 skill folders" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
