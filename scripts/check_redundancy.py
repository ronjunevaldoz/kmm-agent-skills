#!/usr/bin/env python3
"""
check_redundancy.py — flag pairs of skills, or pairs of agents, whose scope
overlaps heavily enough that they might be redundant with each other.

This is NOT the same check as validate_keyword_routing.py, which only checks
that skills explicitly declared as "alternative to X" don't share a trigger
keyword. This script has no notion of declared alternatives — it scores every
pair by keyword/vocabulary overlap and flags the high-scoring ones for a human
to look at. It cannot tell you a pair IS redundant, only that they talk about
similar things; two skills can legitimately share heavy vocabulary (e.g.
kotlin-rpc / ktor-auth-service both mention "Ktor RPC") without either being
removable. Always non-blocking — never wired into the release gate sequence.

Skills are scored on their skills.json `keywords` list (Jaccard similarity).
Agents have no such list, so they're scored on a stopword-filtered token set
built from their title + first paragraph + "## When to use" bullets.

Usage:
    python3 scripts/check_redundancy.py
    python3 scripts/check_redundancy.py --threshold 0.5
    python3 scripts/check_redundancy.py --repo-root /path/to/repo
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_THRESHOLD = 0.4

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with",
    "this", "that", "is", "are", "it", "as", "by", "be", "when", "use",
    "using", "agent", "skill", "part", "kmm", "pipeline", "not", "own",
    "any", "its", "if", "at", "from", "into", "than", "then", "no", "does",
}

_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9-]{2,}")


def _tokenize(text: str) -> set[str]:
    return {
        w.lower() for w in _WORD_RE.findall(text)
        if w.lower() not in _STOPWORDS
    }


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_skill_keyword_sets(repo_root: Path) -> dict[str, set[str]]:
    skills_json = repo_root / "skills.json"
    data = json.loads(skills_json.read_text(encoding="utf-8"))
    result: dict[str, set[str]] = {}
    for skill in data["skills"]:
        keywords = {k.lower() for k in skill.get("keywords", [])}
        result[skill["name"]] = keywords
    return result


def load_agent_token_sets(repo_root: Path) -> dict[str, set[str]]:
    agents_dir = repo_root / "agents"
    result: dict[str, set[str]] = {}
    if not agents_dir.exists():
        return result

    when_to_use_re = re.compile(
        r"## When to use\s*\n(.*?)(?:\n##|\Z)", re.DOTALL | re.IGNORECASE
    )

    for agent_md in sorted(agents_dir.glob("*.md")):
        text = agent_md.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else ""

        # First non-empty paragraph after the title
        first_para = ""
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped or stripped == "---":
                if first_para:
                    break
                continue
            first_para += " " + stripped

        when_to_use = ""
        m = when_to_use_re.search(text)
        if m:
            when_to_use = m.group(1)

        combined = f"{title} {first_para} {when_to_use}"
        result[agent_md.stem] = _tokenize(combined)

    return result


def find_overlaps(sets_by_name: dict[str, set[str]], threshold: float) -> list[tuple[str, str, float]]:
    names = sorted(sets_by_name.keys())
    findings: list[tuple[str, str, float]] = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            score = jaccard(sets_by_name[a], sets_by_name[b])
            if score >= threshold:
                findings.append((a, b, score))
    findings.sort(key=lambda f: -f[2])
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flag skill pairs and agent pairs with heavily overlapping scope"
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD,
        help=f"Jaccard similarity threshold to flag a pair (default: {DEFAULT_THRESHOLD})",
    )
    args = parser.parse_args()

    skill_sets = load_skill_keyword_sets(args.repo_root)
    agent_sets = load_agent_token_sets(args.repo_root)

    skill_overlaps = find_overlaps(skill_sets, args.threshold)
    agent_overlaps = find_overlaps(agent_sets, args.threshold)

    if not skill_overlaps and not agent_overlaps:
        print(f"OK: no skill or agent pairs at or above {args.threshold:.2f} keyword overlap")
        return 0

    print(f"Heuristic overlap scan (threshold {args.threshold:.2f}) — review, don't auto-act:\n")

    if skill_overlaps:
        print(f"Skills ({len(skill_overlaps)} pair(s)):")
        for a, b, score in skill_overlaps:
            print(f"  {score:.2f}  {a}  <->  {b}")
        print()

    if agent_overlaps:
        print(f"Agents ({len(agent_overlaps)} pair(s)):")
        for a, b, score in agent_overlaps:
            print(f"  {score:.2f}  {a}  <->  {b}")
        print()

    print(
        "A high score means shared vocabulary, not confirmed redundancy — some pairs "
        "are legitimate companions (shared domain terms by design). Read both before "
        "merging, splitting, or narrowing scope."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
