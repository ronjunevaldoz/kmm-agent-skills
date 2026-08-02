from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

check_compat_matrix = load_module(
    "check_compat_matrix",
    REPO_ROOT / "scripts" / "check_compat_matrix.py",
)


def _write(root: Path, rel_path: str, content: str) -> Path:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class ParseMatrixVersionsTests(unittest.TestCase):
    def test_parses_plain_and_bold_rows(self) -> None:
        text = (
            "| Library | Version |\n"
            "|---|---|\n"
            "| Kotlin | `2.4.0` |\n"
            "| **AGP** | `9.2.0` |\n"
        )
        versions = check_compat_matrix.parse_matrix_versions(text)
        self.assertEqual(versions["Kotlin"], "2.4.0")
        self.assertEqual(versions["AGP"], "9.2.0")

    def test_skips_placeholder_versions(self) -> None:
        text = "| KSP | `{kotlinVersion}-{kspPatch}` |\n"
        versions = check_compat_matrix.parse_matrix_versions(text)
        self.assertNotIn("KSP", versions)


class ParseTomlVersionsTests(unittest.TestCase):
    def test_extracts_key_value_pairs(self) -> None:
        text = '[versions]\nkotlin = "2.4.0"\nagp = "9.2.0"\n'
        versions = check_compat_matrix.parse_toml_versions(text)
        self.assertEqual(versions["kotlin"], "2.4.0")
        self.assertEqual(versions["agp"], "9.2.0")

    def test_keeps_first_occurrence_only(self) -> None:
        text = 'kotlin = "2.4.0"\nkotlin = "2.1.0"\n'
        versions = check_compat_matrix.parse_toml_versions(text)
        self.assertEqual(versions["kotlin"], "2.4.0")


class CheckDriftAcrossMultipleSkillsTests(unittest.TestCase):
    """Regression test for the fix that made LIBRARY_MAP support multiple
    (skill, key) pins per library — this is what would have caught the
    library-publishing vs feature-scaffold Kotlin version drift."""

    def _setup_repo(self, tmp: Path, feature_scaffold_kotlin: str, library_publishing_kotlin: str) -> None:
        _write(
            tmp, "docs/reference/compatibility-matrix.md",
            "| Library | Version |\n|---|---|\n| Kotlin | `2.4.0` |\n",
        )
        _write(
            tmp, "skills/kmp-feature-scaffold/SKILL.md",
            f'kotlin = "{feature_scaffold_kotlin}"\n',
        )
        _write(
            tmp, "skills/kmp-library-publishing/SKILL.md",
            f'kotlin = "{library_publishing_kotlin}"\n',
        )

    def _kotlin_only_map(self):
        return {
            "Kotlin": [
                ("kmp-feature-scaffold", "kotlin"),
                ("kmp-library-publishing", "kotlin"),
            ],
        }

    def test_no_drift_when_all_pins_agree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_repo(tmp, "2.4.0", "2.4.0")
            with mock.patch.object(check_compat_matrix, "LIBRARY_MAP", self._kotlin_only_map()):
                findings = check_compat_matrix.check(tmp)
            self.assertEqual(findings, [])

    def test_flags_drift_in_second_skill_even_when_first_agrees(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_repo(tmp, "2.4.0", "2.1.21")
            with mock.patch.object(check_compat_matrix, "LIBRARY_MAP", self._kotlin_only_map()):
                findings = check_compat_matrix.check(tmp)
            self.assertTrue(
                any("library-publishing" in f and "2.1.21" in f for f in findings),
                findings,
            )


if __name__ == "__main__":
    unittest.main()
