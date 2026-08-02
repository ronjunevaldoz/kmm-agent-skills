from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

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

        expert = normalize((REPO_ROOT / "skills" / "kmp-expert" / "SKILL.md").read_text(encoding="utf-8"))
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
