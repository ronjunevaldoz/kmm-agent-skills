from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

scan_skill_issues_scripts = load_module(
    "scan_skill_issues",
    REPO_ROOT / "scripts" / "scan_skill_issues.py",
)

class ScanSkillIssuesTests(unittest.TestCase):
    def _make_skill(self, root: Path, name: str, content: str) -> Path:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        return skill_dir

    def _run_scan(self, root: Path) -> dict:
        import json, io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        old_root = scan_skill_issues_scripts.SKILLS_DIR
        old_ki = scan_skill_issues_scripts.KNOWN_ISSUES_FILE
        scan_skill_issues_scripts.SKILLS_DIR = root / "skills"
        scan_skill_issues_scripts.KNOWN_ISSUES_FILE = root / "KNOWN_ISSUES.md"
        try:
            with redirect_stdout(buf):
                rc = scan_skill_issues_scripts.main()
        finally:
            scan_skill_issues_scripts.SKILLS_DIR = old_root
            scan_skill_issues_scripts.KNOWN_ISSUES_FILE = old_ki
        return json.loads(buf.getvalue()), rc

    def test_missing_testing_section_reported_as_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-foo",
                "---\nname: foo\ndescription: Foo skill\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nUse Foo.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nDont do X.\n\n## Related Skills\n\nBar.\n\n"
                "## Output Style\n\nBe concise.\n",
            )
            report, rc = self._run_scan(root)

        self.assertEqual(rc, 1)
        high_issues = [i for i in report["issues"] if i["severity"] == "HIGH"]
        self.assertTrue(len(high_issues) >= 1)
        self.assertTrue(any(i["check"] == "missing_testing" for i in high_issues))

    def test_skill_with_testing_markers_no_high_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-bar",
                "---\nname: bar\ndescription: Bar skill\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nUse Bar.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nDont do X.\n\n## Related Skills\n\nFoo.\n\n"
                "## Output Style\n\nBe concise.\n\n## Testing\n\n```kotlin\n@Test fun fakeBar() {}\n```\n",
            )
            report, rc = self._run_scan(root)

        high_issues = [i for i in report["issues"] if i["check"] == "missing_testing"]
        self.assertEqual(len(high_issues), 0)

    def test_missing_required_sections_reported_as_medium(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-baz",
                # missing: anti_patterns, freshness_rule, recommendation
                "---\nname: baz\ndescription: Baz\nlast-updated: '2026-06-21'\n---\n\n"
                "## Related Skills\n\nFoo.\n\n## Output Style\n\nBe concise.\n\n"
                "## Testing\n\nFakeBaz\n",
            )
            report, _ = self._run_scan(root)

        checks = [i["check"] for i in report["issues"]]
        self.assertIn("missing_anti_patterns", checks)
        self.assertIn("missing_recommendation", checks)

    def test_skipped_skill_not_flagged_for_missing_testing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-expert",
                "---\nname: expert\ndescription: Orchestrator\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nLoad skills.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nNone.\n\n## Related Skills\n\nAll.\n\n"
                "## Output Style\n\nBe concise.\n",
            )
            report, _ = self._run_scan(root)

        testing_issues = [i for i in report["issues"] if i["check"] == "missing_testing"]
        self.assertEqual(len(testing_issues), 0)

    def test_report_structure_has_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            report, _ = self._run_scan(root)

        for key in ("generated", "total_issues", "by_severity", "by_check", "open_known_issues", "issues"):
            self.assertIn(key, report)

    def test_clean_scan_returns_exit_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            _, rc = self._run_scan(root)

        self.assertEqual(rc, 0)


class ReadOpenKnownIssuesTests(unittest.TestCase):
    """read_open_known_issues() looked for the literal heading '## Open Issues', but
    KNOWN_ISSUES.md's real heading is '## Open' — the mismatch meant this function
    silently returned [] regardless of what was actually under that section, for as
    long as the mismatch existed. No prior test caught it because none exercised a
    real '## Open' heading with actual entries under it.
    """

    def _run(self, root: Path, content: str) -> list[str]:
        (root / "KNOWN_ISSUES.md").write_text(content, encoding="utf-8")
        old_ki = scan_skill_issues_scripts.KNOWN_ISSUES_FILE
        scan_skill_issues_scripts.KNOWN_ISSUES_FILE = root / "KNOWN_ISSUES.md"
        try:
            return scan_skill_issues_scripts.read_open_known_issues()
        finally:
            scan_skill_issues_scripts.KNOWN_ISSUES_FILE = old_ki

    def test_finds_entry_under_real_open_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self._run(
                root,
                "## Open\n\n### KI-007 — Something genuinely open\n\n"
                "**Status:** Open\n\n---\n\n## Resolved\n\n### KI-R01 — Fixed thing\n",
            )
        self.assertEqual(result, ["KI-007 — Something genuinely open"])

    def test_stops_at_the_next_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self._run(
                root,
                "## Open\n\n### KI-001 — Open one\n\n---\n\n"
                "## Resolved\n\n### KI-R99 — Should not be counted as open\n",
            )
        self.assertEqual(result, ["KI-001 — Open one"])

    def test_empty_when_open_section_has_no_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self._run(root, "## Open\n\nNothing currently open.\n\n## Resolved\n")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
