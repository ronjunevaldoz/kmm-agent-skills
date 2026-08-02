from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module

fetch_component_signature_scripts = load_module(
    "fetch_component_signature",
    REPO_ROOT / "skills" / "kmp-shadcn-compose" / "scripts" / "fetch_component_signature.py",
)

class FetchComponentSignatureTests(unittest.TestCase):
    """fetch_component_signature.py exists so verifying a shadcn-compose component's
    real API costs one command instead of a manual GitHub lookup. Tests mock the
    network boundary (_fetch_raw/_list_component_files) and exercise the real parsing
    logic against the two tricky cases that broke a naive approach: nested parens in a
    default value (ShadcnCard's `header: (@Composable () -> Unit)? = null`), and a
    component living in a differently-named file (ShadcnTabsList inside ShadcnTabs.kt).
    """

    _CARD_KT = (
        "/**\n"
        " * Card with header/content/footer slots.\n"
        " */\n"
        "@Composable\n"
        "fun ShadcnCard(\n"
        "    modifier: Modifier = Modifier,\n"
        "    header: (@Composable () -> Unit)? = null,\n"
        "    footer: (@Composable () -> Unit)? = null,\n"
        "    content: @Composable ColumnScope.() -> Unit,\n"
        ") {\n"
        "    Box {}\n"
        "}\n"
    )

    _TABS_KT = (
        "/**\n"
        " * A segmented tab switcher.\n"
        " */\n"
        "fun ShadcnTabsList(\n"
        "    items: List<ShadcnTabItem>,\n"
        "    selected: String,\n"
        "    onSelectedChange: (String) -> Unit,\n"
        "    modifier: Modifier = Modifier,\n"
        ") {\n"
        "    Row {}\n"
        "}\n"
    )

    def test_extracts_signature_with_nested_parens_in_default_value(self) -> None:
        fun_start = fetch_component_signature_scripts._find_fun_start(self._CARD_KT, "ShadcnCard")
        self.assertIsNotNone(fun_start)
        signature = fetch_component_signature_scripts._extract_signature(self._CARD_KT, fun_start)
        self.assertIn("header: (@Composable () -> Unit)? = null", signature)
        self.assertIn("footer: (@Composable () -> Unit)? = null", signature)
        self.assertIn("content: @Composable ColumnScope.() -> Unit", signature)
        self.assertIn("Card with header/content/footer slots", signature)

    def test_finds_component_in_a_differently_named_file(self) -> None:
        def fake_fetch_raw(path: str) -> str:
            if path.endswith("ShadcnTabs.kt"):
                return self._TABS_KT
            raise fetch_component_signature_scripts.HTTPError(path, 404, "not found", None, None)

        with mock.patch.object(
            fetch_component_signature_scripts, "_fetch_raw", side_effect=fake_fetch_raw,
        ), mock.patch.object(
            fetch_component_signature_scripts, "_list_component_files",
            return_value=[
                "shadcn/core/src/commonMain/kotlin/io/github/ronjunevaldoz/shadcncompose/components/ShadcnTabs.kt",
            ],
        ):
            result = fetch_component_signature_scripts.find_signature("ShadcnTabsList")
        self.assertIsNotNone(result)
        path, signature = result
        self.assertTrue(path.endswith("ShadcnTabs.kt"))
        self.assertIn("fun ShadcnTabsList(", signature)
        self.assertIn("onSelectedChange: (String) -> Unit", signature)

    def test_returns_none_when_component_does_not_exist_anywhere(self) -> None:
        with mock.patch.object(
            fetch_component_signature_scripts, "_fetch_raw",
            side_effect=fetch_component_signature_scripts.HTTPError("x", 404, "not found", None, None),
        ), mock.patch.object(
            fetch_component_signature_scripts, "_list_component_files", return_value=[],
        ):
            result = fetch_component_signature_scripts.find_signature("ShadcnDoesNotExist")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
