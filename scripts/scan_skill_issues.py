#!/usr/bin/env python3
"""
scan_skill_issues.py — scan all SKILL.md files for quality gaps and output
a structured JSON report consumed by the /summarize-issues command.

Exit codes:
  0 — no issues found
  1 — issues found (expected; not an error)
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
KNOWN_ISSUES_FILE = ROOT / "KNOWN_ISSUES.md"
TODAY = date.today()
STALE_MONTHS = 6

# Skills where a "Testing" section is not applicable
SKIP_TESTING = {
    "kotlin-multiplatform-clean-architecture",   # contract doc
    "kotlin-multiplatform-audit",                # meta review tool
    "kotlin-multiplatform-ci-github-actions",    # CI YAML config
    "kotlin-multiplatform-xcframework-spm",      # binary distribution
    "kotlin-multiplatform-library-publishing",   # Maven Central / GitHub Packages / BOM / binary-compat
    "kotlin-multiplatform-code-quality",         # linting/formatting config
    "kotlin-multiplatform-preview-driven-development",  # workflow guide
    "kotlin-multiplatform-expert",               # meta orchestrator
    "jni-kotlin-pro",                            # separate domain
}

# Patterns that indicate the skill already covers testing
TESTING_MARKERS = [
    r"## Testing",
    r"## Test",
    r"runTest",
    r"@Test\b",
    r"captureRoboImage",
    r"\bFake[A-Z]\w+\b",
    r"MockEngine",
    r"Flapdoodle",
    r"@Testcontainers",
    r"createComposeRule",
]
TESTING_RE = re.compile("|".join(TESTING_MARKERS))

# Required quality sections (as headings or inline markers)
REQUIRED_SECTIONS = {
    "freshness_rule":    (r"Freshness rule:", "MEDIUM"),
    "anti_patterns":     (r"## Common Anti-Patterns", "MEDIUM"),
    "related_skills":    (r"## Related Skills", "LOW"),
    "output_style":      (r"## Output Style", "LOW"),
    "recommendation":    (r"## (?:Recommendation First|Stack contract)", "MEDIUM"),
}


def parse_frontmatter(text: str) -> dict:
    """Extract simple key: value pairs from YAML frontmatter."""
    fm: dict = {}
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm and ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip("'\"")
    return fm


def months_since(date_str: str) -> float:
    try:
        d = datetime.fromisoformat(date_str.strip("'\"")).date()
        return (TODAY - d).days / 30.4
    except Exception:
        return 0.0


def scan_skill(skill_dir: Path) -> list[dict]:
    """Return a list of issue dicts for one skill directory."""
    md_file = skill_dir / "SKILL.md"
    if not md_file.exists():
        return []

    text = md_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    fm = parse_frontmatter(text)
    skill_name = fm.get("name") or skill_dir.name
    description = fm.get("description", "").replace("\n", " ").strip()
    last_updated = fm.get("last-updated", "")
    issues: list[dict] = []

    def add(severity: str, check: str, detail: str, prompt_hint: str) -> None:
        issues.append({
            "skill": skill_name,
            "skill_dir": skill_dir.name,
            "severity": severity,
            "check": check,
            "detail": detail,
            "prompt_hint": prompt_hint,
            "description": description,
            "last_updated": last_updated,
            "lines": len(lines),
        })

    # 1. Missing testing section
    if skill_dir.name not in SKIP_TESTING:
        if not TESTING_RE.search(text):
            add(
                severity="HIGH",
                check="missing_testing",
                detail="No testing section, runTest, @Test, or Fake* class found",
                prompt_hint=(
                    f'Add a comprehensive Testing section to the `{skill_name}` skill. '
                    f'Cover: a Fake implementation for unit tests, a ViewModel/use-case test '
                    f'using the fake, and any integration test pattern if the skill wraps '
                    f'platform APIs or a real driver.'
                ),
            )

    # 2. Stale last-updated
    if last_updated:
        age = months_since(last_updated)
        if age >= STALE_MONTHS:
            add(
                severity="MEDIUM",
                check="stale_skill",
                detail=f"last-updated: {last_updated} ({age:.0f} months ago)",
                prompt_hint=(
                    f'Review and refresh the `{skill_name}` skill — last updated {last_updated}. '
                    f'Check: library versions in TOML snippets, any deprecated APIs, '
                    f'and whether the Freshness rule reflects current upstream status.'
                ),
            )

    # 3. Required sections
    for key, (pattern, sev) in REQUIRED_SECTIONS.items():
        if not re.search(pattern, text):
            label = key.replace("_", " ").title()
            add(
                severity=sev,
                check=f"missing_{key}",
                detail=f'No `{pattern.strip("^## ")}` found',
                prompt_hint=(
                    f'Add a `{pattern.strip("^## ")}` section to the `{skill_name}` skill.'
                ),
            )

    # 4. Very thin skill (likely underdeveloped)
    if len(lines) < 80 and skill_dir.name not in SKIP_TESTING:
        add(
            severity="LOW",
            check="thin_skill",
            detail=f"Only {len(lines)} lines — may be underdeveloped",
            prompt_hint=(
                f'Expand the `{skill_name}` skill with more concrete patterns, '
                f'code snippets, and anti-patterns. Currently {len(lines)} lines.'
            ),
        )

    return issues


def read_open_known_issues() -> list[str]:
    """Return titles of issues marked as open in KNOWN_ISSUES.md."""
    if not KNOWN_ISSUES_FILE.exists():
        return []
    text = KNOWN_ISSUES_FILE.read_text(encoding="utf-8")
    open_issues = []
    in_open = False
    for line in text.splitlines():
        if line.strip() == "## Open":
            in_open = True
        elif line.startswith("## ") and in_open:
            break
        elif in_open and line.startswith("### "):
            open_issues.append(line.lstrip("# ").strip())
    return open_issues


def main() -> int:
    all_issues: list[dict] = []

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            all_issues.extend(scan_skill(skill_dir))

    open_known = read_open_known_issues()

    # Summary counts
    by_severity: dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    by_check: dict[str, int] = {}
    for issue in all_issues:
        by_severity[issue["severity"]] = by_severity.get(issue["severity"], 0) + 1
        by_check[issue["check"]] = by_check.get(issue["check"], 0) + 1

    report = {
        "generated": TODAY.isoformat(),
        "total_issues": len(all_issues),
        "by_severity": by_severity,
        "by_check": by_check,
        "open_known_issues": open_known,
        "issues": all_issues,
    }

    print(json.dumps(report, indent=2))
    return 0 if not all_issues else 1


if __name__ == "__main__":
    sys.exit(main())
