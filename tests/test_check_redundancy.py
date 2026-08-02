from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _helpers import REPO_ROOT, load_module

check_redundancy = load_module(
    "check_redundancy",
    REPO_ROOT / "scripts" / "check_redundancy.py",
)


class JaccardTests(unittest.TestCase):
    def test_identical_sets_score_one(self) -> None:
        self.assertEqual(check_redundancy.jaccard({"a", "b"}, {"a", "b"}), 1.0)

    def test_disjoint_sets_score_zero(self) -> None:
        self.assertEqual(check_redundancy.jaccard({"a"}, {"b"}), 0.0)

    def test_empty_set_scores_zero(self) -> None:
        self.assertEqual(check_redundancy.jaccard(set(), {"a"}), 0.0)

    def test_partial_overlap(self) -> None:
        # {a,b} vs {b,c} -> intersection 1, union 3
        self.assertAlmostEqual(check_redundancy.jaccard({"a", "b"}, {"b", "c"}), 1 / 3)


class LoadSkillKeywordSetsTests(unittest.TestCase):
    def test_loads_from_skills_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            (tmp / "skills.json").write_text(
                json.dumps({
                    "skills": [
                        {"name": "skill-a", "keywords": ["Foo", "Bar"]},
                        {"name": "skill-b", "keywords": ["baz"]},
                    ]
                }),
                encoding="utf-8",
            )
            sets = check_redundancy.load_skill_keyword_sets(tmp)
            self.assertEqual(sets["skill-a"], {"foo", "bar"})
            self.assertEqual(sets["skill-b"], {"baz"})


class LoadAgentTokenSetsTests(unittest.TestCase):
    def _write_agent(self, root: Path, name: str, body: str) -> None:
        agents_dir = root / "agents"
        agents_dir.mkdir(exist_ok=True)
        (agents_dir / f"{name}.md").write_text(body, encoding="utf-8")

    def test_extracts_title_and_when_to_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._write_agent(
                tmp, "reviewer",
                "# Architecture Reviewer\n\nReviews implemented code against contracts.\n\n"
                "## When to use\n\nUse when checking layer boundaries and Koin wiring.\n\n"
                "## Other section\n\nirrelevant content here\n",
            )
            sets = check_redundancy.load_agent_token_sets(tmp)
            tokens = sets["reviewer"]
            self.assertIn("architecture", tokens)
            self.assertIn("boundaries", tokens)
            self.assertNotIn("irrelevant", tokens)

    def test_missing_agents_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            sets = check_redundancy.load_agent_token_sets(Path(tmp_str))
            self.assertEqual(sets, {})


class FindOverlapsTests(unittest.TestCase):
    def test_flags_pairs_at_or_above_threshold(self) -> None:
        sets = {
            "a": {"x", "y", "z"},
            "b": {"x", "y", "w"},
            "c": {"m", "n"},
        }
        findings = check_redundancy.find_overlaps(sets, threshold=0.4)
        pairs = {(f[0], f[1]) for f in findings}
        self.assertIn(("a", "b"), pairs)
        self.assertNotIn(("a", "c"), pairs)

    def test_sorted_descending_by_score(self) -> None:
        sets = {
            "a": {"x", "y"},
            "b": {"x", "y"},        # score 1.0
            "c": {"x", "y", "z", "w"},  # lower score vs a
        }
        findings = check_redundancy.find_overlaps(sets, threshold=0.1)
        scores = [f[2] for f in findings]
        self.assertEqual(scores, sorted(scores, reverse=True))


class RealRepoSmokeTest(unittest.TestCase):
    """Not a strict assertion on repo content — just proves the real skills.json
    and agents/ directory parse without error and produce a sane low-noise result
    at the shipped default threshold."""

    def test_runs_clean_against_real_repo(self) -> None:
        skill_sets = check_redundancy.load_skill_keyword_sets(REPO_ROOT)
        agent_sets = check_redundancy.load_agent_token_sets(REPO_ROOT)
        self.assertGreater(len(skill_sets), 0)
        self.assertGreater(len(agent_sets), 0)
        # Should not raise, and should return a list (possibly empty)
        findings = check_redundancy.find_overlaps(skill_sets, check_redundancy.DEFAULT_THRESHOLD)
        self.assertIsInstance(findings, list)


if __name__ == "__main__":
    unittest.main()
