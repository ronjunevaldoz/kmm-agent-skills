from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT, load_module_registered


behavior_scripts = load_module_registered(
    "evaluate_skill_behavior",
    REPO_ROOT / "skills" / "kmp-expert" / "scripts" / "evaluate_skill_behavior.py",
)


class EvaluateSkillBehaviorTests(unittest.TestCase):
    def test_repository_corpus_is_valid(self) -> None:
        cases = json.loads(behavior_scripts.DEFAULT_CASES.read_text(encoding="utf-8"))
        skill_names = {path.parent.name for path in (REPO_ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(behavior_scripts.validate_cases(cases, skill_names), [])

    def test_validation_rejects_duplicate_and_unknown_skills(self) -> None:
        cases = [
            {
                "id": "duplicate",
                "prompt": "first",
                "expected_skills": ["kmp-real"],
                "expected_boundary": "boundary",
                "required_evidence": [],
            },
            {
                "id": "duplicate",
                "prompt": "second",
                "expected_skills": ["kmp-missing"],
                "expected_boundary": "boundary",
                "required_evidence": [],
            },
        ]
        errors = behavior_scripts.validate_cases(cases, {"kmp-real"})
        self.assertTrue(any("duplicate" in error for error in errors))
        self.assertTrue(any("kmp-missing" in error for error in errors))

    def test_evaluate_requires_exact_skills_boundary_and_evidence(self) -> None:
        cases = [
            {
                "id": "case",
                "prompt": "prompt",
                "expected_skills": ["kmp-a", "kmp-b"],
                "expected_boundary": "correct boundary",
                "required_evidence": ["first", "second"],
            }
        ]
        response = [{"id": "case", "selected_skills": ["kmp-a"], "boundary": "wrong", "evidence": ["first"]}]
        evaluation = behavior_scripts.evaluate(cases, response)[0]
        self.assertFalse(evaluation.passed)
        self.assertEqual(len(evaluation.mismatches), 3)

    def test_main_scores_passing_results(self) -> None:
        cases = [{
            "id": "case",
            "prompt": "prompt",
            "expected_skills": ["kmp-expert"],
            "expected_boundary": "boundary",
            "required_evidence": ["evidence"],
        }]
        responses = [{
            "id": "case",
            "selected_skills": ["kmp-expert"],
            "boundary": "boundary",
            "evidence": ["evidence"],
        }]
        with tempfile.TemporaryDirectory() as tmp:
            cases_path = Path(tmp) / "cases.json"
            responses_path = Path(tmp) / "responses.json"
            cases_path.write_text(json.dumps(cases), encoding="utf-8")
            responses_path.write_text(json.dumps(responses), encoding="utf-8")
            self.assertEqual(
                behavior_scripts.main([
                    "--cases", str(cases_path),
                    "--responses", str(responses_path),
                    "--repo-root", str(REPO_ROOT),
                ]),
                0,
            )


if __name__ == "__main__":
    unittest.main()
