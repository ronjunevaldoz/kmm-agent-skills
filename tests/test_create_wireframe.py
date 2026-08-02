from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

create_wireframe_scripts = load_module(
    "create_wireframe",
    REPO_ROOT / "skills" / "kmp-layout-system" / "scripts" / "create_wireframe.py",
)

class CreateWireframeTests(unittest.TestCase):
    def _write(self, root: Path, screen: str, pattern: str = "A") -> Path:
        ls_dir = root / "docs" / "layout-system"
        ls_dir.mkdir(parents=True, exist_ok=True)
        components = ls_dir / "_components.md"
        if not components.exists():
            components.write_text(create_wireframe_scripts._COMPONENTS_TEMPLATE, encoding="utf-8")
        screen_file = ls_dir / f"{create_wireframe_scripts.slugify(screen)}.md"
        if screen_file.exists():
            return None
        screen_file.write_text(create_wireframe_scripts.render(screen, pattern), encoding="utf-8")
        return screen_file

    def test_each_screen_is_a_separate_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Inbox", "A")
            self._write(root, "Login", "D")
            screens = sorted((root / "docs" / "layout-system").glob("*.md"))
            names = {p.name for p in screens}
            self.assertIn("inbox.md", names)
            self.assertIn("login.md", names)
            self.assertIn("_components.md", names)

    def test_does_not_overwrite_existing_screen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Inbox", "A")
            again = self._write(root, "Inbox", "A")
            self.assertIsNone(again)  # refuses second create

    def test_screen_file_has_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self._write(root, "Inbox", "A")
            text = p.read_text()
            for token in ("# Inbox", "## Components", "## Interaction notes", "```"):
                self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
