from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT, load_module

classify_scripts = load_module(
    "classify_declarations",
    REPO_ROOT / "skills" / "kmp-audit" / "scripts" / "classify_declarations.py",
)


class ClassifyDeclarationsTests(unittest.TestCase):
    """Classifier for kmp-code-quality's core/sugar/helper/sample-local/deprecated
    taxonomy. Distinct from `_detect_god_utils_file`, which asks a filename question —
    this asks, per declaration, what role it plays in the API surface.
    """

    def _classify(self, files: dict[str, str]) -> dict[str, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, content in files.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            rows = classify_scripts.classify(root)
        return {r["name"]: r for r in rows}

    # ── the three exactly-decidable categories ──────────────────────────────────

    def test_internal_and_private_are_helpers(self) -> None:
        rows = self._classify({"lib/A.kt":
            "internal fun a() = 1\nprivate fun b() = 2\n"})
        self.assertEqual(rows["a"]["classification"], "helper")
        self.assertEqual(rows["b"]["classification"], "helper")
        self.assertEqual(rows["a"]["confidence"], "high")

    def test_deprecated_annotation_wins_over_visibility(self) -> None:
        rows = self._classify({"lib/A.kt":
            '@Deprecated("x", ReplaceWith("y()"))\npublic fun old() = y()\n'})
        self.assertEqual(rows["old"]["classification"], "deprecated")
        self.assertEqual(rows["old"]["problem"], "")

    def test_deprecated_without_replacewith_is_a_problem(self) -> None:
        # The taxonomy says deprecated means "has a real migration path" — without one
        # it's dead code, which is a different category needing different handling.
        rows = self._classify({"lib/A.kt": '@Deprecated("gone")\npublic fun old() = 1\n'})
        self.assertEqual(rows["old"]["classification"], "deprecated")
        self.assertIn("ReplaceWith", rows["old"]["problem"])

    def test_sample_path_classifies_as_sample_local(self) -> None:
        rows = self._classify({"samples/Demo.kt": "public fun runDemo() { p() }\n"})
        self.assertEqual(rows["runDemo"]["classification"], "sample-local")
        self.assertIn("sample module", rows["runDemo"]["problem"])

    # ── sugar: the one heuristic ────────────────────────────────────────────────

    def test_delegating_expression_body_is_high_confidence_sugar(self) -> None:
        rows = self._classify({"lib/A.kt":
            "public fun send(r: R) = dispatch(r)\ninternal fun dispatch(r: R) = 1\n"})
        self.assertEqual(rows["send"]["classification"], "sugar")
        self.assertEqual(rows["send"]["confidence"], "high")

    def test_overload_delegating_to_itself_is_high_confidence_sugar(self) -> None:
        rows = self._classify({"lib/A.kt":
            "public fun req(u: String, t: Long) = engine(u, t)\n"
            "public fun req(u: String) = req(u, 30)\n"
            "public fun engine(u: String, t: Long) = 1\n"})
        self.assertEqual(rows["req"]["classification"], "sugar")
        self.assertEqual(rows["req"]["confidence"], "high")

    def test_unresolved_callee_is_only_medium_confidence(self) -> None:
        # Could be delegating to another module, or could be a genuine one-line impl —
        # the classifier can't tell without cross-module resolution, so it says so.
        rows = self._classify({"lib/A.kt": "public fun go() = SomeOtherModule.run()\n"})
        self.assertEqual(rows["go"]["classification"], "sugar")
        self.assertEqual(rows["go"]["confidence"], "medium")

    # ── core: the residual ──────────────────────────────────────────────────────

    def test_public_non_delegating_declaration_is_core(self) -> None:
        rows = self._classify({"lib/A.kt": "public class Engine(private val t: Long)\n"})
        self.assertEqual(rows["Engine"]["classification"], "core")

    def test_visibility_defaults_to_public_when_omitted(self) -> None:
        # Kotlin's default is public; without explicitApi() the keyword is usually absent,
        # so treating "no modifier" as helper would misclassify most app code.
        rows = self._classify({"lib/A.kt": "class Engine(val t: Long)\n"})
        self.assertEqual(rows["Engine"]["classification"], "core")

    # ── scope ───────────────────────────────────────────────────────────────────

    def test_test_sources_are_skipped(self) -> None:
        rows = self._classify({"lib/src/commonTest/kotlin/ATest.kt": "public fun t() = 1\n"})
        self.assertEqual(rows, {})

    def test_comment_lines_are_not_parsed_as_declarations(self) -> None:
        rows = self._classify({"lib/A.kt": "// public fun ghost() = 1\npublic fun real() = 1\n"})
        self.assertIn("real", rows)
        self.assertNotIn("ghost", rows)


if __name__ == "__main__":
    unittest.main()
