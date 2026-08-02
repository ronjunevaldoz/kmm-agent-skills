from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

derive_prefix_scripts = load_module(
    "derive_component_prefix",
    REPO_ROOT / "skills" / "kmp-design-system" / "scripts" / "derive_component_prefix.py",
)

class DeriveComponentPrefixTests(unittest.TestCase):
    def test_pascal_case_project_name(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name("GuildBase"), "GuildBase")

    def test_kebab_case_strips_noise_word(self) -> None:
        # "app" is a generic noise word — stripped when other words remain.
        self.assertEqual(derive_prefix_scripts.derive_from_name("acme-shop-app"), "AcmeShop")

    def test_space_separated_name(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name("Guild Base"), "GuildBase")

    def test_snake_case_name(self) -> None:
        # "admin" is part of the product identity, not generic noise — kept.
        self.assertEqual(derive_prefix_scripts.derive_from_name("lordnine_admin"), "LordnineAdmin")

    def test_pure_noise_word_falls_back_to_app(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name("app"), "App")

    def test_empty_name_falls_back_to_app(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name(""), "App")

    def test_settings_gradle_kts_takes_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text(
                'rootProject.name = "GuildBase"\n', encoding="utf-8"
            )
            (root / "build.gradle.kts").write_text(
                'group = "com.example.other"\n', encoding="utf-8"
            )
            raw_name, source = derive_prefix_scripts.resolve_source(root, None)
            self.assertEqual(raw_name, "GuildBase")
            self.assertIn("settings.gradle.kts", source)

    def test_falls_back_to_group_id_last_segment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle.kts").write_text(
                'group = "com.example.lordnine"\n', encoding="utf-8"
            )
            raw_name, source = derive_prefix_scripts.resolve_source(root, None)
            self.assertEqual(raw_name, "lordnine")
            self.assertIn("group ID", source)

    def test_explicit_name_overrides_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text(
                'rootProject.name = "Ignored"\n', encoding="utf-8"
            )
            raw_name, source = derive_prefix_scripts.resolve_source(root, "Explicit Name")
            self.assertEqual(raw_name, "Explicit Name")
            self.assertIn("--name", source)

    def test_falls_back_to_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "MyCoolApp"
            root.mkdir()
            raw_name, source = derive_prefix_scripts.resolve_source(root, None)
            self.assertEqual(raw_name, "MyCoolApp")
            self.assertIn("directory", source)

    def test_result_is_legal_kotlin_identifier_start(self) -> None:
        # A name that is purely numeric/symbolic must not produce an invalid prefix.
        self.assertEqual(derive_prefix_scripts.derive_from_name("123"), "App")


if __name__ == "__main__":
    unittest.main()
