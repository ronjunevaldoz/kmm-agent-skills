from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

generate_release_notes_scripts = load_module(
    "generate_release_notes",
    REPO_ROOT / "scripts" / "generate_release_notes.py",
)

class GenerateReleaseNotesTests(unittest.TestCase):
    def test_read_skill_changelog_parses_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "## Changelog\n\n"
                "| Date | Change |\n"
                "|---|---|\n"
                "| 2026-06-21 | **Breaking** — Step 3 rewritten. |\n"
                "| 2026-06-18 | Initial release. |\n",
                encoding="utf-8",
            )
            entries = generate_release_notes_scripts.read_skill_changelog(skill_md)
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0]["date"], "2026-06-21")
            self.assertIn("Breaking", entries[0]["change"])
            self.assertEqual(entries[1]["date"], "2026-06-18")

    def test_read_skill_changelog_returns_empty_when_section_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text("## When to Use This Skill\n\nSome content.\n", encoding="utf-8")
            entries = generate_release_notes_scripts.read_skill_changelog(skill_md)
            self.assertEqual(entries, [])

    def test_read_unreleased_parses_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text(
                "# Changelog\n\n"
                "## [Unreleased]\n\n"
                "### Added\n- Some thing\n\n"
                "## [v1.0.0] — 2026-06-17\n\n"
                "### Added\n- Initial release\n",
                encoding="utf-8",
            )
            section = generate_release_notes_scripts.read_unreleased(changelog)
            self.assertIn("Some thing", section)
            self.assertNotIn("v1.0.0", section)

    def test_read_unreleased_returns_empty_when_section_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text("# Changelog\n\n## [v1.0.0] — 2026-06-17\n", encoding="utf-8")
            section = generate_release_notes_scripts.read_unreleased(changelog)
            self.assertEqual(section, "")

    def test_main_list_tags_exits_0(self) -> None:
        result = generate_release_notes_scripts.main(["--list-tags"])
        self.assertEqual(result, 0)

    def test_main_since_head_exits_0(self) -> None:
        result = generate_release_notes_scripts.main(["--since", "HEAD~1"])
        self.assertEqual(result, 0)

    def test_main_since_head_outputs_valid_json(self) -> None:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            generate_release_notes_scripts.main(["--since", "HEAD~1"])
        data = json.loads(buf.getvalue())
        self.assertIn("commits", data)
        self.assertIn("skill_changes", data)
        self.assertIn("unreleased_changelog", data)


if __name__ == "__main__":
    unittest.main()
