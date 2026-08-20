#!/usr/bin/env python3
"""Score recorded agent behavior against the skill-routing evaluation corpus.

The repository can validate routing metadata, but the host agent ultimately decides
which instructions it loads. Record a real run in JSON, then score the selected skills,
boundary statement, and evidence tokens against the versioned cases.

Usage:
    python3 skills/kmp-expert/scripts/evaluate_skill_behavior.py \
      --responses /path/to/agent-results.json
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CASES = Path(__file__).parents[1] / "fixtures" / "skill-behavior-cases.json"


@dataclass(frozen=True)
class Evaluation:
    case_id: str
    passed: bool
    mismatches: list[str]


def _load_list(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{path} must contain JSON objects")
    return data


def validate_cases(cases: list[dict[str, object]], skill_names: set[str]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    required_fields = {"id", "prompt", "expected_skills", "expected_boundary", "required_evidence"}
    for index, case in enumerate(cases, start=1):
        missing = required_fields - case.keys()
        if missing:
            errors.append(f"case {index} missing fields: {', '.join(sorted(missing))}")
            continue
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"case {index} has an invalid id")
            continue
        if case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        expected_skills = case["expected_skills"]
        if not isinstance(expected_skills, list) or not expected_skills:
            errors.append(f"case {case_id} must declare at least one expected skill")
            continue
        unknown = sorted(set(expected_skills) - skill_names)
        if unknown:
            errors.append(f"case {case_id} references unknown skills: {', '.join(unknown)}")
    return errors


def evaluate(cases: list[dict[str, object]], responses: list[dict[str, object]]) -> list[Evaluation]:
    responses_by_id = {response.get("id"): response for response in responses}
    evaluations: list[Evaluation] = []
    for case in cases:
        case_id = case["id"]
        response = responses_by_id.get(case_id)
        mismatches: list[str] = []
        if response is None:
            mismatches.append("missing response")
        else:
            selected_skills = sorted(response.get("selected_skills", []))
            if selected_skills != sorted(case["expected_skills"]):
                mismatches.append(
                    f"selected skills {selected_skills!r}; expected {sorted(case['expected_skills'])!r}"
                )
            if response.get("boundary") != case["expected_boundary"]:
                mismatches.append("boundary statement did not match")
            evidence = set(response.get("evidence", []))
            missing_evidence = sorted(set(case["required_evidence"]) - evidence)
            if missing_evidence:
                mismatches.append(f"missing evidence: {', '.join(missing_evidence)}")
        evaluations.append(Evaluation(case_id=case_id, passed=not mismatches, mismatches=mismatches))
    return evaluations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, required=True, help="JSON array of recorded agent results")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="JSON evaluation corpus")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[3])
    args = parser.parse_args(argv)

    cases = _load_list(args.cases)
    skill_names = {path.parent.name for path in (args.repo_root / "skills").glob("*/SKILL.md")}
    errors = validate_cases(cases, skill_names)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    evaluations = evaluate(cases, _load_list(args.responses))
    failed = [evaluation for evaluation in evaluations if not evaluation.passed]
    for evaluation in evaluations:
        status = "PASS" if evaluation.passed else "FAIL"
        detail = "" if evaluation.passed else f" — {'; '.join(evaluation.mismatches)}"
        print(f"{status}: {evaluation.case_id}{detail}")
    print(f"{len(evaluations) - len(failed)}/{len(evaluations)} behavior cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
