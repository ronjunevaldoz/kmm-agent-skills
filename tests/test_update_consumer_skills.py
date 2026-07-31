from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT


class UpdateConsumerSkillsScriptTests(unittest.TestCase):
    def _write(self, root: Path, rel_path: str, content: str) -> None:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_setup_agents_scaffolds_root_sources_and_syncs_project_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            source = tmp_root / "source"
            project = tmp_root / "project"
            source.mkdir()
            project.mkdir()

            self._write(source, "skills.json", '{"version":"0.0.1"}\n')
            self._write(
                source,
                "skills/shared-skill/SKILL.md",
                "---\nname: shared-skill\ndescription: Shared bundle skill.\n---\n",
            )
            self._write(source, "CHANGELOG.md", "## [v0.0.1]\n- init\n---\n")

            self._write(project, "settings.gradle.kts", 'rootProject.name = "DemoApp"\n')
            (project / ".claude" / "skills").mkdir(parents=True)
            self._write(
                project,
                "skills/demo-skill/SKILL.md",
                "---\nname: demo-skill\ndescription: Project-owned skill.\n---\n\n## Rules\n- Demo\n",
            )

            result = subprocess.run(
                [
                    "bash",
                    str(REPO_ROOT / "scripts" / "update-consumer-skills.sh"),
                    "--source",
                    str(source),
                    "--agent-dir",
                    ".claude/skills",
                    "--setup-agents",
                ],
                cwd=project,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue((project / ".claude" / "skills" / "shared-skill" / "SKILL.md").is_file())
            self.assertTrue((project / ".claude" / "skills" / "demo-skill" / "SKILL.md").is_file())
            self.assertTrue((project / ".claude" / "AGENTS.md").is_file())
            self.assertTrue((project / ".claude" / "settings.json").is_file())
            self.assertTrue((project / "CLAUDE.md").is_file())
            self.assertTrue((project / "docs" / "reference" / "ai-collaboration.md").is_file())
            self.assertTrue((project / "docs" / "reference" / "agent-catalog.md").is_file())
            self.assertTrue((project / "agents" / "README.md").is_file())
            self.assertTrue((project / "rules" / "README.md").is_file())
            self.assertTrue((project / "hooks" / "README.md").is_file())
            self.assertTrue((project / "commands" / "README.md").is_file())
            self.assertTrue((project / "skills" / "README.md").is_file())

            # Real gaps fixed: .agents/skills cross-client mirror, pipeline-context.json
            # seeding, and the mandatory-baseline rows in the fallback AGENTS.md template.
            self.assertTrue((project / ".agents" / "skills" / "shared-skill" / "SKILL.md").is_file())
            self.assertTrue((project / ".agents" / "pipeline-context.json").is_file())
            agents_md = (project / ".claude" / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("kotlin-multiplatform-code-quality", agents_md)
            self.assertIn("kotlin-multiplatform-unit-testing", agents_md)
            self.assertIn("kotlin-multiplatform-android-cli", agents_md)
            self.assertIn("kotlin-multiplatform-project-docs-maintainer", agents_md)
            self.assertIn("/kmm-setup-hooks", result.stdout)

    def test_agents_skills_mirror_skipped_when_agent_dir_is_already_agents_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            source = tmp_root / "source"
            project = tmp_root / "project"
            source.mkdir()
            project.mkdir()

            self._write(source, "skills.json", '{"version":"0.0.1"}\n')
            self._write(
                source, "skills/shared-skill/SKILL.md",
                "---\nname: shared-skill\ndescription: Shared bundle skill.\n---\n",
            )
            self._write(source, "CHANGELOG.md", "## [v0.0.1]\n- init\n---\n")
            (project / ".agents" / "skills").mkdir(parents=True)

            result = subprocess.run(
                [
                    "bash", str(REPO_ROOT / "scripts" / "update-consumer-skills.sh"),
                    "--source", str(source), "--agent-dir", ".agents/skills",
                ],
                cwd=project, capture_output=True, text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            # Only one deploy message, not a redundant self-mirror.
            self.assertNotIn("cross-client convention", result.stdout)


if __name__ == "__main__":
    unittest.main()
