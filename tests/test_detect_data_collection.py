from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import REPO_ROOT, load_module
from _helpers import load_module_registered

detect_data_collection_scripts = load_module_registered(
    "detect_data_collection",
    REPO_ROOT / "skills" / "kmp-legal-docs" / "scripts" / "detect_data_collection.py",
)

class DetectDataCollectionTests(unittest.TestCase):
    def _make_project(self, files: dict[str, str]) -> Path:
        tmp = tempfile.mkdtemp()
        root = Path(tmp)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return root

    def test_detects_firebase_analytics(self) -> None:
        root = self._make_project({
            "feature/analytics/src/commonMain/Analytics.kt":
                "import com.google.firebase.analytics.FirebaseAnalytics\n"
                "fun track() = FirebaseAnalytics.getInstance(ctx).logEvent(\"screen_view\", null)\n"
        })
        detections = detect_data_collection_scripts.scan_project(root)
        types = [d.data_type for d in detections]
        self.assertIn("analytics", types)

    def test_detects_location_permission(self) -> None:
        root = self._make_project({
            "androidApp/src/main/AndroidManifest.xml":
                '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>\n'
        })
        detections = detect_data_collection_scripts.scan_project(root)
        types = [d.data_type for d in detections]
        self.assertIn("location_precise", types)

    def test_no_detections_on_empty_project(self) -> None:
        root = self._make_project({"build.gradle.kts": "plugins { }\n"})
        detections = detect_data_collection_scripts.scan_project(root)
        self.assertEqual(detections, [])

    def test_finds_gap_when_analytics_not_in_policy(self) -> None:
        detections = [detect_data_collection_scripts.Detection(data_type="analytics", evidence=["Analytics.kt:1"])]
        gaps = detect_data_collection_scripts.find_gaps(detections, policy_text="we collect your email.")
        self.assertIn("analytics", gaps)

    def test_no_gap_when_analytics_disclosed_in_policy(self) -> None:
        detections = [detect_data_collection_scripts.Detection(data_type="analytics", evidence=["Analytics.kt:1"])]
        gaps = detect_data_collection_scripts.find_gaps(detections, policy_text="usage analytics via firebase analytics sdk.")
        self.assertNotIn("analytics", gaps)

    def test_finds_conflict_when_policy_mentions_location_but_code_does_not(self) -> None:
        policy_text = "we collect your precise location via gps."
        conflicts = detect_data_collection_scripts.find_conflicts(detections=[], policy_text=policy_text)
        self.assertIn("location_precise", conflicts)

    def test_main_exits_0_on_no_gaps(self) -> None:
        root = self._make_project({"build.gradle.kts": "plugins { }\n"})
        result = detect_data_collection_scripts.main([str(root)])
        self.assertEqual(result, 0)

    def test_main_exits_1_on_gaps(self) -> None:
        root = self._make_project({
            "Analytics.kt": "val x = FirebaseAnalytics.getInstance(ctx)\n"
        })
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Privacy Policy\n\nWe collect your email.\n")
            policy_path = f.name
        result = detect_data_collection_scripts.main([str(root), "--policy", policy_path])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
