from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "bootstrap-consumer-skills.sh"


class BootstrapConsumerSkillsTests(unittest.TestCase):
    def _run(self, cwd: Path, target: str, env: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SCRIPT), target],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_noop_when_target_already_populated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            skills_dir = project / ".claude" / "skills" / "some-skill"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("---\nname: some-skill\n---\n", encoding="utf-8")

            result = self._run(project, ".claude/skills", os.environ.copy())

            self.assertEqual(result.returncode, 0, result.stderr)
            # No bootstrap attempted — no output at all.
            self.assertEqual(result.stdout.strip(), "")
            self.assertEqual(result.stderr.strip(), "")

    def test_bootstraps_from_local_source_when_target_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            # Deliberately no .claude/skills — the missing case.

            env = os.environ.copy()
            env["KMP_AGENT_SKILLS_SOURCE"] = str(REPO_ROOT)
            env.pop("KMM_AGENT_SKILLS_SOURCE", None)

            result = self._run(project, ".claude/skills", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Bootstrapped", result.stderr)
            deployed = project / ".claude" / "skills"
            self.assertTrue(deployed.is_dir())
            self.assertTrue((deployed / "kmp-expert" / "SKILL.md").is_file())
            self.assertTrue((deployed / ".kmp-agent-skills-version").is_file())

    def test_noop_when_target_is_empty_directory(self) -> None:
        # An empty (but existing) dir counts as "missing" for bootstrap purposes —
        # `ls -A` on an empty dir is empty, same as a dir that doesn't exist at all.
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".claude" / "skills").mkdir(parents=True)

            env = os.environ.copy()
            env.pop("KMP_AGENT_SKILLS_SOURCE", None)
            env.pop("KMM_AGENT_SKILLS_SOURCE", None)
            # No npx on a minimal PATH — forces the "nothing available" branch, not a
            # real network call in a test.
            env["PATH"] = "/usr/bin:/bin"

            result = self._run(project, ".claude/skills", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("bootstrap skipped", result.stderr)


if __name__ == "__main__":
    unittest.main()
