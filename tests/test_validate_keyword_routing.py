from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

keyword_routing_scripts = load_module(
    "validate_keyword_routing",
    REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "scripts" / "validate_keyword_routing.py",
)

class ValidateKeywordRoutingTests(unittest.TestCase):
    EXPERT_HEADER = "## Skill Invocation Map\n"
    EXPERT_FOOTER = "\n---\n"

    def _make_repo(self, tmp: str, skill_names: list[str], map_rows: str) -> Path:
        root = Path(tmp)
        skills_dir = root / "skills"
        for name in skill_names:
            (skills_dir / name).mkdir(parents=True)
            (skills_dir / name / "SKILL.md").write_text("", encoding="utf-8")
        # expert SKILL.md with a Skill Invocation Map section
        expert_dir = skills_dir / "kotlin-multiplatform-expert"
        expert_dir.mkdir(parents=True, exist_ok=True)
        (expert_dir / "SKILL.md").write_text(
            self.EXPERT_HEADER + map_rows + self.EXPERT_FOOTER,
            encoding="utf-8",
        )
        return root

    def test_all_skills_present_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"],
                "| keyword-a | `kotlin-multiplatform-a` |\n"
                "| keyword-b | `kotlin-multiplatform-b` |\n",
            )
            self.assertEqual(keyword_routing_scripts.validate_keyword_routing(root), [])

    def test_missing_skill_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"],
                "| keyword-a | `kotlin-multiplatform-a` |\n",
            )
            errors = keyword_routing_scripts.validate_keyword_routing(root)
            self.assertTrue(any("kotlin-multiplatform-b" in e for e in errors))

    def test_meta_skills_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-audit", "kotlin-multiplatform-expert"],
                "",
            )
            # audit and expert are in SKIP_INVOCATION — no map rows needed
            self.assertEqual(keyword_routing_scripts.validate_keyword_routing(root), [])

    def test_missing_map_section_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expert_dir = root / "skills" / "kotlin-multiplatform-expert"
            expert_dir.mkdir(parents=True)
            (expert_dir / "SKILL.md").write_text("no section here", encoding="utf-8")
            errors = keyword_routing_scripts.validate_keyword_routing(root)
            self.assertTrue(any("not found" in e for e in errors))

    def test_main_exits_0_on_clean_repo(self) -> None:
        result = keyword_routing_scripts.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(result, 0)

    def _write_skill(self, root: Path, name: str, body: str) -> None:
        d = root / "skills" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(body, encoding="utf-8")

    def test_flags_keyword_shared_with_documented_alternative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"],
                "| keyword-a | `kotlin-multiplatform-a` |\n"
                "| keyword-b | `kotlin-multiplatform-b` |\n",
            )
            self._write_skill(
                root, "kotlin-multiplatform-a",
                "---\ndescription: >\n  Some skill.\n---\n\n"
                "**Trigger keywords:** widget, shared thing\n",
            )
            self._write_skill(
                root, "kotlin-multiplatform-b",
                "---\ndescription: >\n  Alternative to `kotlin-multiplatform-a` — not both in the same project.\n---\n\n"
                "**Trigger keywords:** gadget, shared thing\n",
            )
            errors = keyword_routing_scripts.validate_keyword_routing(root)
            self.assertTrue(any("shared thing" in e for e in errors))

    def test_ignores_shared_keyword_between_non_alternative_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"],
                "| keyword-a | `kotlin-multiplatform-a` |\n"
                "| keyword-b | `kotlin-multiplatform-b` |\n",
            )
            self._write_skill(
                root, "kotlin-multiplatform-a",
                "---\ndescription: >\n  Some skill, no alternative relationship.\n---\n\n"
                "**Trigger keywords:** widget, shared thing\n",
            )
            self._write_skill(
                root, "kotlin-multiplatform-b",
                "---\ndescription: >\n  A companion skill, complements kotlin-multiplatform-a.\n---\n\n"
                "**Trigger keywords:** gadget, shared thing\n",
            )
            errors = keyword_routing_scripts.validate_keyword_routing(root)
            self.assertFalse(any("collision" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
