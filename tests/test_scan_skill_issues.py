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
                "kmp-foo",
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
                "kmp-bar",
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
                "kmp-baz",
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
                "kmp-expert",
                "---\nname: expert\ndescription: Orchestrator\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nLoad skills.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nNone.\n\n## Related Skills\n\nAll.\n\n"
                "## Output Style\n\nBe concise.\n",
            )
            report, _ = self._run_scan(root)

        testing_issues = [i for i in report["issues"] if i["check"] == "missing_testing"]
        self.assertEqual(len(testing_issues), 0)

    def test_android_cli_skipped_for_missing_testing(self) -> None:
        # CLI tool wrapper, no Kotlin API surface to unit test — same rationale as
        # kmp-ci-github-actions (CI YAML config).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kmp-android-cli",
                "---\nname: android-cli\ndescription: Android CLI wiring\nlast-updated: '2026-07-19'\n---\n\n"
                "## Recommendation First\n\nUse the stable command surface.\n\n"
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


class AgentSkillsSpecTests(unittest.TestCase):
    """Real rules from agentskills.io's specification, verified against the actual
    skills-ref reference validator (all 64 skills in this repo pass it today) rather
    than assumed. These checks are a regression guard for future skills.
    """

    def _make_skill(self, root: Path, dir_name: str, content: str) -> Path:
        skill_dir = root / "skills" / dir_name
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
                scan_skill_issues_scripts.main()
        finally:
            scan_skill_issues_scripts.SKILLS_DIR = old_root
            scan_skill_issues_scripts.KNOWN_ISSUES_FILE = old_ki
        return json.loads(buf.getvalue())

    def _minimal_skill_body(self, extra: str = "") -> str:
        return (
            "## Recommendation First\n\nDo X.\n\n"
            "## Common Anti-Patterns\n\nNone.\n\n## Related Skills\n\nAll.\n\n"
            "## Output Style\n\nBe concise.\n\nFreshness rule: check monthly\n"
            + extra
        )

    def test_name_over_64_chars_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            long_name = "a" * 70
            self._make_skill(
                root, long_name,
                f"---\nname: {long_name}\ndescription: Test\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(),
            )
            report = self._run_scan(root)
        self.assertTrue(any(i["check"] == "name_too_long" for i in report["issues"]))

    def test_name_uppercase_flagged_invalid_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root, "kmp-Foo",
                "---\nname: kmp-Foo\ndescription: Test\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(),
            )
            report = self._run_scan(root)
        self.assertTrue(any(i["check"] == "name_invalid_format" for i in report["issues"]))

    def test_name_dir_mismatch_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root, "kmp-foo",
                "---\nname: kmp-bar\ndescription: Test\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(),
            )
            report = self._run_scan(root)
        self.assertTrue(any(i["check"] == "name_dir_mismatch" for i in report["issues"]))

    def test_description_over_1024_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            long_desc = "x" * 1100
            self._make_skill(
                root, "kmp-foo",
                f"---\nname: kmp-foo\ndescription: {long_desc}\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(),
            )
            report = self._run_scan(root)
        self.assertTrue(any(i["check"] == "description_too_long" for i in report["issues"]))

    def test_description_folded_block_parsed_correctly(self) -> None:
        # A folded (>) description must be joined into real content, not read back
        # as the literal ">" block indicator — this was a real bug in parse_frontmatter.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root, "kmp-foo",
                "---\nname: kmp-foo\ndescription: >\n"
                "  This is a folded description that spans\n  multiple lines.\n"
                "last-updated: '2026-07-26'\n---\n\n" + self._minimal_skill_body(),
            )
            report = self._run_scan(root)
        matching = [i for i in report["issues"] if i["skill_dir"] == "kmp-foo"]
        for issue in matching:
            self.assertNotEqual(issue["description"], ">")

    def test_oversized_skill_md_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            padding = "\n".join(f"Line {i} of filler content." for i in range(600))
            self._make_skill(
                root, "kmp-foo",
                "---\nname: kmp-foo\ndescription: Test\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(padding),
            )
            report = self._run_scan(root)
        self.assertTrue(any(i["check"] == "oversized_skill_md" for i in report["issues"]))

    def test_oversized_reference_md_flagged(self) -> None:
        # Same 500-line guideline as SKILL.md itself, applied to references/*.md — a
        # single reference file that's still 500+ lines is a large one-shot load when
        # an agent does need it, and usually a sign it should split further.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = self._make_skill(
                root, "kmp-foo",
                "---\nname: kmp-foo\ndescription: Test\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(),
            )
            references_dir = skill_dir / "references"
            references_dir.mkdir()
            padding = "\n".join(f"Line {i} of filler content." for i in range(600))
            (references_dir / "big.md").write_text(f"# Big\n\n{padding}\n", encoding="utf-8")
            report = self._run_scan(root)
        self.assertTrue(any(i["check"] == "oversized_reference_md" for i in report["issues"]))

    def test_ignores_reference_md_under_the_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = self._make_skill(
                root, "kmp-foo",
                "---\nname: kmp-foo\ndescription: Test\nlast-updated: '2026-07-26'\n---\n\n"
                + self._minimal_skill_body(),
            )
            references_dir = skill_dir / "references"
            references_dir.mkdir()
            (references_dir / "small.md").write_text("# Small\n\nJust a short reference.\n", encoding="utf-8")
            report = self._run_scan(root)
        self.assertFalse(any(i["check"] == "oversized_reference_md" for i in report["issues"]))

    def test_oversized_command_md_flagged(self) -> None:
        # A slash command's whole body loads on invocation — the same cost
        # oversized_skill_md bounds for SKILL.md — but commands/ was covered by no size
        # check at all until this one.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            commands_dir = root / "commands"
            commands_dir.mkdir(parents=True)
            padding = "\n".join(f"Step {i}." for i in range(600))
            (commands_dir / "kmp-huge.md").write_text(f"# /kmp-huge\n\n{padding}\n", encoding="utf-8")
            (commands_dir / "kmp-small.md").write_text("# /kmp-small\n\nDo one thing.\n", encoding="utf-8")

            old = scan_skill_issues_scripts.COMMANDS_DIR
            scan_skill_issues_scripts.COMMANDS_DIR = commands_dir
            try:
                issues = scan_skill_issues_scripts.scan_commands()
            finally:
                scan_skill_issues_scripts.COMMANDS_DIR = old

        flagged = [i for i in issues if i["check"] == "oversized_command_md"]
        self.assertEqual([i["skill_dir"] for i in flagged], ["kmp-huge"])
        self.assertEqual(flagged[0]["skill"], "/kmp-huge")

    def test_known_debt_reported_but_does_not_block(self) -> None:
        # KI-008: a skill/check pair already in the KNOWN_DEBT baseline is real,
        # visible debt — it must still show up in the report, but must not fail
        # release.py's exit-code gate the way a brand-new violation would.
        # KI-008's oversized_skill_md entries were all fixed on 2026-08-04 (real
        # KNOWN_DEBT no longer has any), so this test monkeypatches a synthetic
        # entry rather than depending on a currently-debt-carrying real skill name.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            padding = "\n".join(f"Line {i} of filler content." for i in range(600))
            self._make_skill(
                root, "kmp-known-debt-fixture",
                "---\nname: kmp-known-debt-fixture\ndescription: Test\n"
                "last-updated: '2026-07-26'\n---\n\n" + self._minimal_skill_body(padding),
            )
            known_debt = {("kmp-known-debt-fixture", "oversized_skill_md")}
            with mock.patch.object(scan_skill_issues_scripts, "KNOWN_DEBT", known_debt):
                report = self._run_scan(root)
                self.assertTrue(any(i["check"] == "oversized_skill_md" for i in report["issues"]))
                # missing_testing still legitimately blocks this synthetic fixture
                # (unrelated to KNOWN_DEBT) — assert the oversized finding specifically
                # isn't counted as blocking, not that nothing blocks at all.
                blocking_checks = {
                    i["check"] for i in report["issues"]
                    if (i["skill_dir"], i["check"]) not in scan_skill_issues_scripts.KNOWN_DEBT
                }
        self.assertNotIn("oversized_skill_md", blocking_checks)

    def test_new_violation_still_blocks(self) -> None:
        # A skill NOT in the KNOWN_DEBT baseline must still block, even for the
        # exact same check — KNOWN_DEBT is a snapshot, not a blanket exemption.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            padding = "\n".join(f"Line {i} of filler content." for i in range(600))
            self._make_skill(
                root, "kmp-brand-new-skill",
                "---\nname: kmp-brand-new-skill\ndescription: Test\n"
                "last-updated: '2026-07-26'\n---\n\n" + self._minimal_skill_body(padding),
            )
            report = self._run_scan(root)
        self.assertGreater(report["blocking_issues"], 0)

    def test_small_valid_skill_has_no_agentskills_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root, "kmp-foo",
                "---\nname: kmp-foo\ndescription: A short valid description.\n"
                "last-updated: '2026-07-26'\n---\n\n" + self._minimal_skill_body(),
            )
            report = self._run_scan(root)
        agentskills_checks = {
            "name_too_long", "name_invalid_format", "name_dir_mismatch",
            "description_too_long", "description_approaching_limit", "oversized_skill_md",
        }
        found = {i["check"] for i in report["issues"]} & agentskills_checks
        self.assertEqual(found, set())


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
