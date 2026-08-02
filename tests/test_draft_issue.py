from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

draft_issue_scripts = load_module(
    "draft_issue",
    REPO_ROOT / "skills" / "kmp-audit" / "scripts" / "draft_issue.py",
)

class DraftIssueTests(unittest.TestCase):
    def test_render_issue_includes_attribution_footer(self) -> None:
        content = draft_issue_scripts.render_issue(
            title="Missing freshness note",
            evidence="skills/foo/SKILL.md lacks a freshness rule.",
            recommendation="Add a freshness rule and re-run the audit.",
            skill="kmp-audit",
            kind="issue",
        )
        self.assertIn("# Missing freshness note", content)
        self.assertIn("Suggested by kmp-audit", content)

    def test_render_question_uses_question_heading(self) -> None:
        content = draft_issue_scripts.render_issue(
            title="Should X live in :model or :api?",
            evidence="Ambiguous placement.",
            recommendation="Confirm with the team.",
            skill="kmp-clean-architecture",
            kind="question",
        )
        self.assertIn("## Type\nQuestion", content)

    def test_build_gh_command_includes_repo_and_labels(self) -> None:
        cmd = draft_issue_scripts.build_gh_command(
            title="Test issue",
            body="body text",
            repo="owner/repo",
            labels=["skill-bug", "priority: high"],
        )
        self.assertIn("--repo", cmd)
        self.assertIn("owner/repo", cmd)
        self.assertEqual(cmd.count("--label"), 2)
        self.assertIn("skill-bug", cmd)
        self.assertIn("priority: high", cmd)

    def test_build_gh_command_no_labels(self) -> None:
        cmd = draft_issue_scripts.build_gh_command(
            title="T", body="B", repo="r/r", labels=[]
        )
        self.assertNotIn("--label", cmd)

    def test_submit_dry_run_prints_command_does_not_execute(self) -> None:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = draft_issue_scripts.submit_issue(
                title="T", body="B",
                repo="ronjunevaldoz/kmp-agent-skills",
                labels=["skill-bug"],
                dry_run=True,
            )
        output = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("DRY RUN", output)
        self.assertIn("gh issue create", output)
        self.assertIn("ronjunevaldoz/kmp-agent-skills", output)

    def test_default_repo_constant(self) -> None:
        self.assertEqual(
            draft_issue_scripts.DEFAULT_REPO,
            "ronjunevaldoz/kmp-agent-skills",
        )


if __name__ == "__main__":
    unittest.main()
