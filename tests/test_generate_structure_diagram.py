from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT, load_module

diagram_scripts = load_module(
    "generate_structure_diagram",
    REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "generate_structure_diagram.py",
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


class StructureDiagramTests(unittest.TestCase):
    def test_app_project_detects_complete_and_missing_layers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for layer in ("model", "api", "domain", "presenter", "ui"):
                _touch(root / "feature" / "auth" / layer / "build.gradle.kts")
            _touch(root / "core" / "model" / "build.gradle.kts")

            state = diagram_scripts.gather(root)
            self.assertEqual(state["project_type"], "app")
            self.assertEqual(state["features"]["auth"], {"model", "api", "domain", "presenter", "ui"})

            text = diagram_scripts.build_diagram(state)
            self.assertIn(":data       MISSING", text)
            self.assertIn(":model      OK", text)
            self.assertIn("core/model", text)

    def test_library_project_detects_missing_sample(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _touch(root / "library" / "build.gradle.kts")
            _touch(root / "library-testing" / "build.gradle.kts")

            state = diagram_scripts.gather(root)
            self.assertEqual(state["project_type"], "library")

            text = diagram_scripts.build_diagram(state)
            self.assertIn("library/  OK", text)
            self.assertIn("sample/  MISSING", text)

    def test_mermaid_output_wraps_in_fence_and_marks_missing_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _touch(root / "feature" / "auth" / "model" / "build.gradle.kts")

            state = diagram_scripts.gather(root)
            mermaid = diagram_scripts.build_mermaid(state)
            self.assertTrue(mermaid.startswith("```mermaid"))
            self.assertTrue(mermaid.endswith("```"))
            self.assertIn("(missing)", mermaid)


if __name__ == "__main__":
    unittest.main()
