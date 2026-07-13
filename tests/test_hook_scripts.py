from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

HOOKS_DIR = REPO_ROOT / "hooks"

class HookScriptTests(unittest.TestCase):
    """KI-006 — hook shell script plumbing tests.

    Tests exit-code forwarding and argument handling for the two non-blocking
    hooks. The pre-commit hook is covered indirectly by the Python scripts it
    wraps; these tests cover the shell plumbing that the other tests do not.
    """

    # --- validate-architecture.sh ---

    def test_validate_arch_skips_non_kotlin_file(self) -> None:
        result = subprocess.run(
            ["bash", str(HOOKS_DIR / "validate-architecture.sh"), "readme.txt"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, (
            "validate-architecture.sh should exit 0 (skip) for non-.kt/.kts/.md files. "
            f"stderr: {result.stderr.decode()}"
        ))

    def test_validate_arch_runs_on_kotlin_file(self) -> None:
        # Pass a clean temp dir as $2 so the audit doesn't scan SKILL.md examples.
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "validate-architecture.sh"), "SomeFile.kt", tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "validate-architecture.sh should exit 0 on a clean project for a .kt file. "
            f"stdout: {result.stdout.decode()}  stderr: {result.stderr.decode()}"
        ))

    def test_validate_arch_runs_when_no_arg(self) -> None:
        # No file arg → audit runs; use a clean temp dir as $2 to avoid SKILL.md false positives.
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "validate-architecture.sh"), "", tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "validate-architecture.sh should exit 0 on a clean project when called with no file arg. "
            f"stderr: {result.stderr.decode()}"
        ))

    def test_validate_arch_skips_non_md_non_kt(self) -> None:
        for ext in (".json", ".sh", ".py", ".toml", ".xml"):
            with self.subTest(ext=ext):
                result = subprocess.run(
                    ["bash", str(HOOKS_DIR / "validate-architecture.sh"), f"file{ext}"],
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, (
                    f"validate-architecture.sh should skip and exit 0 for {ext} files."
                ))

    # --- check-skill-freshness.sh ---

    def _make_skill_dir(self, tmp: str, name: str, last_updated: str) -> Path:
        skills_dir = Path(tmp) / "skills"
        skill_dir = skills_dir / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\nmetadata:\n  last-updated: '{last_updated}'\n---\n",
            encoding="utf-8",
        )
        return skills_dir

    def test_freshness_exits_0_when_all_skills_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = self._make_skill_dir(tmp, "kotlin-multiplatform-foo", "2026-06-21")
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(skills_dir)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "check-skill-freshness.sh should exit 0 when all skills are fresh. "
            f"stdout: {result.stdout.decode()}"
        ))

    def test_freshness_exits_1_when_skill_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = self._make_skill_dir(tmp, "kotlin-multiplatform-old", "2020-01-01")
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(skills_dir)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 1, (
            "check-skill-freshness.sh should exit 1 when a skill is >90 days stale. "
            f"stdout: {result.stdout.decode()}"
        ))
        self.assertIn(b"STALE", result.stdout)

    def test_freshness_warns_on_missing_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            skill_dir = skills_dir / "kotlin-multiplatform-nodates"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: kotlin-multiplatform-nodates\n---\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(skills_dir)],
                capture_output=True,
            )
        # No stale count incremented — exits 0 but prints WARN
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"WARN", result.stdout)

    def test_freshness_exits_0_when_no_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            empty_skills = Path(tmp) / "skills"
            empty_skills.mkdir()
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(empty_skills)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "check-skill-freshness.sh should exit 0 when the skills directory is empty."
        ))


if __name__ == "__main__":
    unittest.main()
