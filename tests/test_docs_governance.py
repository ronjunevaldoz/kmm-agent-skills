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
        expert = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "SKILL.md").read_text(encoding="utf-8"))
        project_docs = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-project-docs-maintainer" / "SKILL.md").read_text(encoding="utf-8"))
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
        command = normalize((REPO_ROOT / "commands" / "kmm-sync-local-skills.md").read_text(encoding="utf-8"))

        self.assertIn("kmm-sync-local-skills", readme)
        self.assertIn("local claude / codex / gemini installs on this mac", install)
        self.assertIn("sync the latest kmm-agent-skills release into the local assistant skill bundles", command)
        self.assertIn("does not copy commands/", command)

    def test_benchmark_tables_have_a_canonical_reference_home(self) -> None:
        docs = (REPO_ROOT / "skills" / "kotlin-multiplatform-project-docs-maintainer" / "SKILL.md").read_text(encoding="utf-8").lower()

        self.assertIn("benchmark or performance comparison tables", docs)
        self.assertIn("docs/reference/benchmark-matrix.md", docs)


class CommonFirstSharedCodeTests(unittest.TestCase):
    def test_common_first_formatting_rule_is_explicit(self) -> None:
        normalize = lambda text: " ".join(text.lower().replace("`", "").split())

        expert = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "SKILL.md").read_text(encoding="utf-8"))
        expect_actual = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-expect-actual" / "SKILL.md").read_text(encoding="utf-8"))
        audit = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "SKILL.md").read_text(encoding="utf-8"))

        self.assertIn("string.format", expert)
        self.assertIn("shared formatter", expert)
        self.assertIn("implementing the behavior in commonmain first", expect_actual)
        self.assertIn("commonmain can express it cleanly and portably", expect_actual)
        self.assertIn("jvm-only utility in commonmain", expect_actual)
        self.assertIn("prefer a pure commonmain implementation before abstractions", audit)
        self.assertIn("jvm-only utilities in commonmain", audit)


if __name__ == "__main__":
    unittest.main()
