from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

scaffold_scripts = load_module(
    "validate_module_graph",
    REPO_ROOT / "skills" / "kotlin-multiplatform-feature-scaffold" / "scripts" / "validate_module_graph.py",
)

class ValidateModuleGraphTests(unittest.TestCase):
    def test_validate_module_graph_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text("", encoding="utf-8")
            (root / "build-logic").mkdir()
            (root / "androidApp").mkdir()
            (root / "androidApp" / "build.gradle.kts").write_text(
                "implementation(projects.feature.auth.ui)",
                encoding="utf-8",
            )
            for module in ("model", "api", "domain", "data", "presenter", "ui"):
                module_dir = root / "feature" / "auth" / module
                module_dir.mkdir(parents=True)
                (module_dir / "build.gradle.kts").write_text("", encoding="utf-8")
            ui_src = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
            ui_src.mkdir(parents=True)
            (ui_src / "LoginContent.kt").write_text(
                "fun LoginContent() { Column { } }",
                encoding="utf-8",
            )
            (ui_src / "LoginContentPreview.kt").write_text(
                "fun LoginContentPreview() { LoginContent() }",
                encoding="utf-8",
            )

            self.assertEqual(scaffold_scripts.validate_module_graph(root, "auth"), [])

    def test_validate_module_graph_reports_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text("", encoding="utf-8")
            (root / "build-logic").mkdir()
            (root / "androidApp").mkdir()
            (root / "androidApp" / "build.gradle.kts").write_text("", encoding="utf-8")
            for module in ("model", "api", "domain", "data", "presenter", "ui"):
                module_dir = root / "feature" / "auth" / module
                module_dir.mkdir(parents=True)
                (module_dir / "build.gradle.kts").write_text("", encoding="utf-8")

            self.assertIn(
                "androidApp/build.gradle.kts does not reference projects.feature.auth.ui",
                scaffold_scripts.validate_module_graph(root, "auth"),
            )

    def test_validate_module_graph_reports_missing_preview_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text("", encoding="utf-8")
            (root / "build-logic").mkdir()
            (root / "androidApp").mkdir()
            (root / "androidApp" / "build.gradle.kts").write_text(
                "implementation(projects.feature.auth.ui)",
                encoding="utf-8",
            )
            for module in ("model", "api", "domain", "data", "presenter", "ui"):
                module_dir = root / "feature" / "auth" / module
                module_dir.mkdir(parents=True)
                (module_dir / "build.gradle.kts").write_text("", encoding="utf-8")
            ui_src = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
            ui_src.mkdir(parents=True)
            (ui_src / "LoginContent.kt").write_text(
                "fun LoginContent() { Column { } }",
                encoding="utf-8",
            )

            errors = scaffold_scripts.validate_module_graph(root, "auth")

            self.assertTrue(any("missing preview stub" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
