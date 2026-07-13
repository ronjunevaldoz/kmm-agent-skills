from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

release_scripts = load_module(
    "release",
    REPO_ROOT / "scripts" / "release.py",
)

class ReleaseScriptTests(unittest.TestCase):
    def test_release_validation_invokes_all_gates_in_order(self) -> None:
        calls: list[str] = []

        def record(name: str):
            def inner() -> None:
                calls.append(name)
            return inner

        with (
            mock.patch.object(release_scripts, "run_audit", record("audit")),
            mock.patch.object(release_scripts, "run_scan_skill_issues", record("scan")),
            mock.patch.object(release_scripts, "run_skill_map_validation", record("skill_map")),
            mock.patch.object(release_scripts, "run_keyword_routing_validation", record("keyword_routing")),
            mock.patch.object(release_scripts, "run_tests", record("tests")),
        ):
            release_scripts.run_release_validation()

        self.assertEqual(calls, ["audit", "scan", "skill_map", "keyword_routing", "tests"])

    def test_release_validation_scripts_use_repo_root_flags(self) -> None:
        commands: list[list[str]] = []

        def fake_run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
            commands.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout="OK", stderr="")

        with mock.patch.object(release_scripts, "run", fake_run):
            release_scripts.run_skill_map_validation()
            release_scripts.run_keyword_routing_validation()

        self.assertIn(
            [
                "python3",
                str(release_scripts.VALIDATE_SKILL_MAP_SCRIPT),
                "--repo-root",
                str(release_scripts.REPO_ROOT),
            ],
            commands,
        )
        self.assertIn(
            [
                "python3",
                str(release_scripts.VALIDATE_KEYWORD_ROUTING_SCRIPT),
                "--repo-root",
                str(release_scripts.REPO_ROOT),
            ],
            commands,
        )


if __name__ == "__main__":
    unittest.main()
