from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT, load_module

compliance_scripts = load_module(
    "scan_mimicry_compliance",
    REPO_ROOT / "skills" / "kmp-api-mimicry" / "scripts" / "scan_mimicry_compliance.py",
)


class NamespaceViolationTests(unittest.TestCase):
    def test_flags_reference_namespace_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kt = root / "src" / "Foo.kt"
            kt.parent.mkdir(parents=True)
            kt.write_text("import androidx.compose.ui.Modifier\n", encoding="utf-8")

            findings = compliance_scripts.scan_namespace_violations(root, ("androidx.compose.",))
            self.assertTrue(any("androidx.compose.ui.Modifier" in f for f in findings))

    def test_does_not_flag_own_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kt = root / "src" / "Foo.kt"
            kt.parent.mkdir(parents=True)
            kt.write_text("package com.myengine.ui\n\nimport com.myengine.ui.Modifier\n", encoding="utf-8")

            findings = compliance_scripts.scan_namespace_violations(root, ("androidx.compose.",))
            self.assertFalse(findings)

    def test_no_findings_when_no_prefixes_given(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kt = root / "src" / "Foo.kt"
            kt.parent.mkdir(parents=True)
            kt.write_text("import androidx.compose.ui.Modifier\n", encoding="utf-8")

            findings = compliance_scripts.scan_namespace_violations(root, ())
            self.assertFalse(findings)


class FontLicenseTests(unittest.TestCase):
    def test_flags_font_with_no_license_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fonts_dir = root / "assets" / "fonts"
            fonts_dir.mkdir(parents=True)
            (fonts_dir / "Inter-Regular.ttf").write_bytes(b"\x00")

            findings = compliance_scripts.scan_font_licenses(root)
            self.assertTrue(any("Inter-Regular.ttf" in f for f in findings))

    def test_does_not_flag_font_with_ofl_alongside(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fonts_dir = root / "assets" / "fonts"
            fonts_dir.mkdir(parents=True)
            (fonts_dir / "Inter-Regular.ttf").write_bytes(b"\x00")
            (fonts_dir / "OFL.txt").write_text("SIL Open Font License\n", encoding="utf-8")

            findings = compliance_scripts.scan_font_licenses(root)
            self.assertFalse(findings)


class DependencyRelinkingTests(unittest.TestCase):
    def test_flags_real_reference_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle.kts").write_text(
                'implementation("androidx.compose.ui:ui:1.7.0")\n', encoding="utf-8"
            )

            findings = compliance_scripts.scan_dependency_relinking(root, ("androidx.compose.ui:",))
            self.assertTrue(any("build.gradle.kts" in f for f in findings))

    def test_no_findings_when_no_coordinates_given(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle.kts").write_text(
                'implementation("androidx.compose.ui:ui:1.7.0")\n', encoding="utf-8"
            )

            findings = compliance_scripts.scan_dependency_relinking(root, ())
            self.assertFalse(findings)


if __name__ == "__main__":
    unittest.main()
