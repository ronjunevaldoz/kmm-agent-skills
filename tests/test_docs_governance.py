from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module


def read_skill_with_references(skill_dir: Path) -> str:
    """SKILL.md text plus every references/*.md file concatenated — mirrors how
    scripts/check_compat_matrix.py and audit_skills_repo.py already read a skill
    after content was split out for the agentskills.io 500-line guideline (KI-008)."""
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        text += "\n" + "\n".join(
            ref.read_text(encoding="utf-8") for ref in sorted(references_dir.glob("*.md"))
        )
    return text


class DocsScopeBoundaryTests(unittest.TestCase):
    def test_repo_and_consumer_docs_boundary_is_explicit(self) -> None:
        normalize = lambda text: " ".join(text.lower().split())

        docs_maintainer = normalize((REPO_ROOT / "agents" / "docs-maintainer.md").read_text(encoding="utf-8"))
        planner = normalize((REPO_ROOT / "agents" / "planner.md").read_text(encoding="utf-8"))
        expert = normalize((REPO_ROOT / "skills" / "kmp-expert" / "SKILL.md").read_text(encoding="utf-8"))
        project_docs = normalize((REPO_ROOT / "skills" / "kmp-project-docs-maintainer" / "SKILL.md").read_text(encoding="utf-8"))
        readme = normalize((REPO_ROOT / "README.md").read_text(encoding="utf-8"))

        self.assertIn("repo-internal docs", docs_maintainer)
        self.assertIn("downstream consumer docs", docs_maintainer)
        self.assertIn("repo-internal docs -> `docs-maintainer`", planner)
        self.assertIn("downstream consumer docs -> `project-docs-maintainer`", planner)
        self.assertIn("docs scope guard", expert)
        self.assertIn("repo-internal docs", expert)
        self.assertIn("downstream consumer docs", expert)
        self.assertIn("downstream consumer-facing kmp project documentation only", project_docs)
        self.assertIn("if the target is this repository, route to `docs-maintainer` instead.", project_docs)
        self.assertIn("classify it as repo-internal or downstream consumer", readme)

    def test_local_assistant_sync_is_documented_separately(self) -> None:
        normalize = lambda text: " ".join(
            text.lower().replace("`", "").replace(":", "").replace(".", "").split()
        )

        readme = normalize((REPO_ROOT / "README.md").read_text(encoding="utf-8"))
        install = normalize((REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8"))
        command = normalize((REPO_ROOT / "commands" / "kmp-sync-local-skills.md").read_text(encoding="utf-8"))

        self.assertIn("kmp-sync-local-skills", readme)
        self.assertIn("local claude / codex / gemini installs on this mac", install)
        self.assertIn("sync the latest kmp-agent-skills release into the local assistant skill bundles", command)
        self.assertIn("does not copy commands/", command)

    def test_benchmark_tables_have_a_canonical_reference_home(self) -> None:
        docs = (REPO_ROOT / "skills" / "kmp-project-docs-maintainer" / "SKILL.md").read_text(encoding="utf-8").lower()

        self.assertIn("benchmark or performance comparison tables", docs)
        self.assertIn("docs/reference/benchmark-matrix.md", docs)

    def test_claude_scaffold_contract_is_documented_as_project_owned_plus_runtime(self) -> None:
        normalize = lambda text: " ".join(text.lower().replace("`", "").split())

        expert = normalize(read_skill_with_references(REPO_ROOT / "skills" / "kmp-expert"))
        setup_agents = normalize((REPO_ROOT / "commands" / "kmp-setup-agents.md").read_text(encoding="utf-8"))
        new_project = normalize((REPO_ROOT / "commands" / "kmp-new-project.md").read_text(encoding="utf-8"))

        for text in (expert, setup_agents, new_project):
            self.assertIn("rules/", text)
            self.assertIn("docs/reference/ai-collaboration.md", text)
            self.assertIn("claude.md", text)
            self.assertIn("project-owned", text)

    def test_cross_agent_reference_docs_cover_docs_vs_skills_and_model_tiers(self) -> None:
        ai = (REPO_ROOT / "docs" / "reference" / "ai-collaboration.md").read_text(encoding="utf-8").lower()
        catalog = (REPO_ROOT / "docs" / "reference" / "agent-catalog.md").read_text(encoding="utf-8").lower()

        self.assertIn("how is this project designed?", ai)
        self.assertIn("how should an agent work in this repo?", ai)
        self.assertIn("agents.md", ai)
        self.assertIn("claude.md", ai)
        self.assertIn("gemini.md", ai)

        self.assertIn("flagship-coding", catalog)
        self.assertIn("balanced-coding", catalog)
        self.assertIn("fast-utility", catalog)
        self.assertIn("precision-review", catalog)
        self.assertIn("provider-specific model mapping", catalog)


class AgentSetupSingleOwnerTests(unittest.TestCase):
    """`/kmp-setup-agents` is the single owner of the agent-scaffold templates.

    `/kmp-new-project` used to inline its own duplicate of them, and the two copies
    drifted in production: the `[Library]` AGENTS.md written by new-project had lost five
    skill-routing rows and used different placeholder names than the one setup-agents
    writes, so a library scaffolded through new-project silently got a worse AGENTS.md.
    Nothing checked for it, which is exactly why it drifted unnoticed.
    """

    def _read(self, rel: str) -> str:
        return (REPO_ROOT / rel).read_text(encoding="utf-8")

    def test_new_project_delegates_agent_setup_instead_of_inlining_it(self) -> None:
        new_project = self._read("commands/kmp-new-project.md")

        self.assertIn("/kmp-setup-agents", new_project)
        # The AGENTS.md body template must exist in exactly one command. These marker
        # lines are the template payload, not prose about it.
        for marker in ("# AGENTS.md — <PROJECT_NAME>", "## Published artifacts"):
            self.assertNotIn(
                marker, new_project,
                f"{marker!r} is back in kmp-new-project.md — the AGENTS.md template "
                f"belongs to /kmp-setup-agents alone, or the two copies will drift again",
            )

    def test_setup_agents_still_owns_the_agents_md_template(self) -> None:
        setup_agents = self._read("commands/kmp-setup-agents.md")
        self.assertIn("## Published artifacts", setup_agents)
        self.assertIn("## Skill routing", setup_agents)

    def test_new_project_still_owns_what_setup_agents_does_not_write(self) -> None:
        # setup-agents runs against existing projects that already have a README and
        # docs/, so it deliberately never writes them — new-project must keep those.
        new_project = self._read("commands/kmp-new-project.md")
        setup_agents = self._read("commands/kmp-setup-agents.md")

        self.assertIn("README.md", new_project)
        self.assertIn("docs/decisions/", new_project)
        self.assertNotIn("docs/decisions/", setup_agents)


class CommonFirstSharedCodeTests(unittest.TestCase):
    def test_common_first_formatting_rule_is_explicit(self) -> None:
        normalize = lambda text: " ".join(text.lower().replace("`", "").split())

        expert = normalize((REPO_ROOT / "skills" / "kmp-expert" / "SKILL.md").read_text(encoding="utf-8"))
        expect_actual = normalize((REPO_ROOT / "skills" / "kmp-expect-actual" / "SKILL.md").read_text(encoding="utf-8"))
        audit = normalize((REPO_ROOT / "skills" / "kmp-audit" / "SKILL.md").read_text(encoding="utf-8"))

        self.assertIn("string.format", expert)
        self.assertIn("shared formatter", expert)
        self.assertIn("implementing the behavior in commonmain first", expect_actual)
        self.assertIn("commonmain can express it cleanly and portably", expect_actual)
        self.assertIn("jvm-only utility in commonmain", expect_actual)
        self.assertIn("prefer a pure commonmain implementation before abstractions", audit)
        self.assertIn("jvm-only utilities in commonmain", audit)


if __name__ == "__main__":
    unittest.main()
