from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT, load_module_registered

harvest_lessons = load_module_registered(
    "harvest_lessons",
    REPO_ROOT / "skills" / "kotlin-multiplatform-skill-harvester" / "scripts" / "harvest_lessons.py",
)


def _write_lesson(root: Path, name: str, frontmatter: dict, body: str) -> Path:
    lessons_dir = root / "docs" / "lessons"
    lessons_dir.mkdir(parents=True, exist_ok=True)
    fm_lines = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
    text = f"---\n{fm_lines}\n---\n{body}\n"
    path = lessons_dir / name
    path.write_text(text, encoding="utf-8")
    return path


class ParseFrontmatterTests(unittest.TestCase):
    def test_parses_valid_lesson(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            path = _write_lesson(
                tmp, "l1.md",
                {"skill": "kotlin-multiplatform-mvi", "date": "2026-01-01",
                 "severity": "high", "type": "correction"},
                "# Heading\n\nChannel effects were dropped on rotation.",
            )
            lesson = harvest_lessons.parse_lesson(path)
            self.assertEqual(lesson.skill, "kotlin-multiplatform-mvi")
            self.assertEqual(lesson.severity, "high")
            self.assertEqual(lesson.type, "correction")
            self.assertEqual(lesson.summary, "Channel effects were dropped on rotation.")
            self.assertEqual(lesson.errors, [])

    def test_unknown_skill_routes_to_unknown_with_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            path = _write_lesson(
                tmp, "l2.md",
                {"skill": "not-a-real-skill", "date": "2026-01-01",
                 "severity": "low", "type": "gap"},
                "Some body text.",
            )
            lesson = harvest_lessons.parse_lesson(path)
            self.assertEqual(lesson.skill, "unknown")
            self.assertTrue(any("unknown skill" in e for e in lesson.errors))

    def test_invalid_severity_falls_back_to_low(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            path = _write_lesson(
                tmp, "l3.md",
                {"skill": "unknown", "date": "2026-01-01",
                 "severity": "critical", "type": "gap"},
                "Body.",
            )
            lesson = harvest_lessons.parse_lesson(path)
            self.assertEqual(lesson.severity, "low")
            self.assertTrue(any("invalid severity" in e for e in lesson.errors))

    def test_missing_frontmatter_returns_empty_dict(self) -> None:
        fm, body = harvest_lessons._parse_frontmatter("no frontmatter here")
        self.assertEqual(fm, {})
        self.assertEqual(body, "no frontmatter here")


class CollectLessonsTests(unittest.TestCase):
    def test_min_severity_filters_out_lower_severity_lessons(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _write_lesson(
                tmp, "high.md",
                {"skill": "unknown", "date": "2026-01-01", "severity": "high", "type": "gap"},
                "High severity issue.",
            )
            _write_lesson(
                tmp, "low.md",
                {"skill": "unknown", "date": "2026-01-01", "severity": "low", "type": "gap"},
                "Low severity issue.",
            )
            lessons = harvest_lessons.collect_lessons([tmp], min_severity="high")
            self.assertEqual(len(lessons), 1)
            self.assertEqual(lessons[0].severity, "high")

    def test_missing_lessons_dir_is_skipped_silently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            lessons = harvest_lessons.collect_lessons([tmp], min_severity="low")
            self.assertEqual(lessons, [])


class GroupAndReportTests(unittest.TestCase):
    def test_group_by_skill_sorts_high_severity_first(self) -> None:
        lessons = [
            harvest_lessons.Lesson("a", "skill-a", "d", "low", "gap", "low issue"),
            harvest_lessons.Lesson("b", "skill-a", "d", "high", "correction", "high issue"),
        ]
        groups = harvest_lessons.group_by_skill(lessons)
        self.assertEqual(groups["skill-a"][0].severity, "high")

    def test_text_report_excludes_confirmations_from_amendment_count(self) -> None:
        lessons = [
            harvest_lessons.Lesson("a", "skill-a", "d", "low", "confirmation", "still works"),
        ]
        groups = harvest_lessons.group_by_skill(lessons)
        report = harvest_lessons.text_report(groups, total=1)
        self.assertIn("Proposed amendments: 0", report)


if __name__ == "__main__":
    unittest.main()
