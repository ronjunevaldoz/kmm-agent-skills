from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

command_shell_portability_scripts = load_module(
    "scan_command_shell_portability",
    REPO_ROOT / "scripts" / "scan_command_shell_portability.py",
)

class CommandShellPortabilityTests(unittest.TestCase):
    """A find ... -not ... predicate in commands/kmp-audit-screenshots.md broke under
    a real user's RTK proxy hook (2026-07-10) — this scanner catches that pattern
    anywhere it recurs in commands/*.md.
    """

    def _write_command(self, root: Path, rel_path: str, content: str) -> None:
        d = (root / rel_path).parent
        d.mkdir(parents=True, exist_ok=True)
        (root / rel_path).write_text(content, encoding="utf-8")

    def test_flags_find_not_predicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_command(
                root, "commands/fake-command.md",
                "# /fake-command\n\n```bash\n"
                "find \"<dir>\" -name \"*.png\" \\\n"
                "  -not -name \"*_compare.png\" \\\n"
                "  | sort\n```\n",
            )
            findings = command_shell_portability_scripts.scan_command_file(
                root / "commands/fake-command.md"
            )
            self.assertTrue(any("find -not predicate" in f for f in findings))

    def test_ignores_grep_v_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_command(
                root, "commands/fake-command.md",
                "# /fake-command\n\n```bash\n"
                "find \"<dir>\" -name \"*.png\" | grep -v -e \"_compare\\.png$\" | sort\n```\n",
            )
            findings = command_shell_portability_scripts.scan_command_file(
                root / "commands/fake-command.md"
            )
            self.assertFalse(any("find -not predicate" in f for f in findings))

    def test_ignores_not_outside_a_bash_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_command(
                root, "commands/fake-command.md",
                "# /fake-command\n\nUse `find ... -not ...` only inside code, "
                "this prose mention should not be flagged.\n",
            )
            findings = command_shell_portability_scripts.scan_command_file(
                root / "commands/fake-command.md"
            )
            self.assertFalse(any("find -not predicate" in f for f in findings))

    def test_repo_commands_are_currently_clean(self) -> None:
        # Real regression check: the actual commands/*.md files in this repo.
        findings = []
        for path in sorted((REPO_ROOT / "commands").glob("*.md")):
            findings.extend(command_shell_portability_scripts.scan_command_file(path))
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
