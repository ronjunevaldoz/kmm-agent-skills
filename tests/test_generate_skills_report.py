from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

report_scripts = load_module(
    "generate_skills_report",
    REPO_ROOT / "scripts" / "generate_skills_report.py",
)


class GenerateSkillsReportTests(unittest.TestCase):
    """Real ask: a developer can't always review 64 SKILL.md files or raw
    scan_skill_issues.py JSON — this report is the at-a-glance summary.
    """

    def _make_skill(self, root: Path, name: str, body_lines: int, last_updated: str) -> None:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        padding = "\n".join(f"Line {i}." for i in range(body_lines))
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill.\nlast-updated: '{last_updated}'\n---\n\n"
            "## Recommendation First\n\nDo X.\n\n## Common Anti-Patterns\n\nNone.\n\n"
            "## Related Skills\n\nAll.\n\n## Output Style\n\nBe concise.\n\n"
            "## Testing\n\nSee runTest.\n\nFreshness rule: monthly\n\n" + padding,
            encoding="utf-8",
        )

    def test_report_lists_all_skills_sorted_by_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(root, "kotlin-multiplatform-small", 10, "2026-07-31")
            self._make_skill(root, "kotlin-multiplatform-big", 600, "2026-07-31")
            manifest = {
                "version": "0.0.0-test",
                "skills": [
                    {"name": "kotlin-multiplatform-small", "description": "d", "last_updated": "2026-07-31"},
                    {"name": "kotlin-multiplatform-big", "description": "d", "last_updated": "2026-07-31"},
                ],
            }
            (root / "skills.json").write_text(json.dumps(manifest), encoding="utf-8")

            with (
                mock.patch.object(report_scripts, "SKILLS_JSON", root / "skills.json"),
                mock.patch.object(report_scripts, "SKILLS_DIR", root / "skills"),
            ):
                text = report_scripts.build_report()

        self.assertIn("kotlin-multiplatform-small", text)
        self.assertIn("kotlin-multiplatform-big", text)
        # Larger skill (over 500 lines) must be listed before the smaller one —
        # same "biggest offenders first" ordering that surfaced KI-008.
        self.assertLess(text.index("kotlin-multiplatform-big"), text.index("kotlin-multiplatform-small"))

    def test_report_flags_status_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(root, "kotlin-multiplatform-oversized", 600, "2026-07-31")
            manifest = {
                "version": "0.0.0-test",
                "skills": [
                    {"name": "kotlin-multiplatform-oversized", "description": "d", "last_updated": "2026-07-31"},
                ],
            }
            (root / "skills.json").write_text(json.dumps(manifest), encoding="utf-8")

            with (
                mock.patch.object(report_scripts, "SKILLS_JSON", root / "skills.json"),
                mock.patch.object(report_scripts, "SKILLS_DIR", root / "skills"),
                mock.patch.object(report_scripts, "KNOWN_DEBT", set()),
            ):
                text = report_scripts.build_report()

        # Not in KNOWN_DEBT — a genuinely new violation must show as blocking, not debt.
        self.assertIn("🔴", text)


if __name__ == "__main__":
    unittest.main()
