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
    "kotlin-multiplatform-android-cli",          # CLI tool wrapper, no Kotlin API surface
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

# agentskills.io spec (verified against the real skills-ref validator, not guessed):
# name must be lowercase unicode alphanumeric + hyphens, no leading/trailing/double hyphen.
_AGENTSKILLS_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_AGENTSKILLS_MAX_RECOMMENDED_LINES = 500

# Known, tracked, deliberately-deferred debt (KI-008) — restructuring 22 skills'
# content into references/*.md is a large per-skill judgment call, not a mechanical
# fix, so these don't block a release the way a *new* violation would. Any skill or
# check not in this exact set still blocks — this is a snapshot, not a blanket
# exemption for the two checks. Update via `python3 scripts/scan_skill_issues.py`
# only after actually fixing the corresponding skill, never to silence a new one.
KNOWN_DEBT: set[tuple[str, str]] = {
    ("kotlin-multiplatform-clean-architecture", "oversized_skill_md"),
    ("kotlin-multiplatform-code-quality", "oversized_skill_md"),
    ("kotlin-multiplatform-compose-slot-api", "oversized_skill_md"),
    ("kotlin-multiplatform-compose-state-container", "oversized_skill_md"),
    ("kotlin-multiplatform-compose-state-hoisting", "oversized_skill_md"),
    ("kotlin-multiplatform-design-system", "description_approaching_limit"),
    ("kotlin-multiplatform-design-system", "oversized_skill_md"),
    ("kotlin-multiplatform-design-system-extended", "description_approaching_limit"),
    ("kotlin-multiplatform-design-system-extended", "oversized_skill_md"),
    ("kotlin-multiplatform-expect-actual", "oversized_skill_md"),
    ("kotlin-multiplatform-expert", "oversized_skill_md"),
    ("kotlin-multiplatform-feature-scaffold", "oversized_skill_md"),
    ("kotlin-multiplatform-layout-system", "description_approaching_limit"),
    ("kotlin-multiplatform-layout-system", "oversized_skill_md"),
    ("kotlin-multiplatform-legal-docs", "oversized_skill_md"),
    ("kotlin-multiplatform-library-publishing", "oversized_skill_md"),
    ("kotlin-multiplatform-mvi", "oversized_skill_md"),
    ("kotlin-multiplatform-navigation", "oversized_skill_md"),
    ("kotlin-multiplatform-network-layer", "oversized_skill_md"),
    ("kotlin-multiplatform-release", "oversized_skill_md"),
    ("kotlin-multiplatform-repository-pattern", "oversized_skill_md"),
    ("kotlin-multiplatform-roborazzi", "oversized_skill_md"),
    ("kotlin-multiplatform-shadcn-compose", "oversized_skill_md"),
    ("kotlin-multiplatform-shared-resources", "oversized_skill_md"),
    ("kotlin-multiplatform-sqldelight-setup", "oversized_skill_md"),
}

# Required quality sections (as headings or inline markers)
REQUIRED_SECTIONS = {
    "freshness_rule":    (r"Freshness rule:", "MEDIUM"),
    "anti_patterns":     (r"## Common Anti-Patterns", "MEDIUM"),
    "related_skills":    (r"## Related Skills", "LOW"),
    "output_style":      (r"## Output Style", "LOW"),
    "recommendation":    (r"## (?:Recommendation First|Stack contract)", "MEDIUM"),
}


def parse_frontmatter(text: str) -> dict:
    """Extract key: value pairs from YAML frontmatter — including multi-line
    folded (`>`) or literal (`|`) block scalars, which most skills use for
    `description`. Without this, a folded description reads back as the
    single-character block indicator instead of its real content.

    Deliberately permissive about indentation for plain `key: value` lines (matches
    the previous implementation) so nested fields like `metadata: / last-updated:`
    still get picked up — only the block-scalar case needs indentation-aware parsing,
    to consume its continuation lines instead of misreading each as its own key.
    """
    fm: dict = {}
    lines = text.splitlines()
    in_fm = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                i += 1
                continue
            else:
                break
        if in_fm and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val in (">", "|", ">-", "|-"):
                indent = len(line) - len(line.lstrip())
                block_lines: list[str] = []
                i += 1
                while i < len(lines) and (
                    not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip())) > indent
                ):
                    block_lines.append(lines[i].strip())
                    i += 1
                fm[key] = " ".join(l for l in block_lines if l)
                continue
            fm[key] = val.strip("'\"")
        i += 1
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

    # 5. agentskills.io spec: name field (verified against the real skills-ref
    # validator — all 64 skills pass today, kept as a regression guard for new ones)
    name_val = fm.get("name", "")
    if len(name_val) > 64:
        add(
            severity="HIGH",
            check="name_too_long",
            detail=f"name is {len(name_val)} chars — spec limit is 64",
            prompt_hint=f'Shorten the `name` field in `{skill_name}`\'s frontmatter to 64 characters or fewer.',
        )
    if name_val and not _AGENTSKILLS_NAME_RE.match(name_val):
        add(
            severity="HIGH",
            check="name_invalid_format",
            detail=f"name '{name_val}' fails agentskills.io's charset/hyphen rules",
            prompt_hint=(
                f'Fix the `name` field in `{skill_name}`\'s frontmatter — must be lowercase '
                f'alphanumeric + hyphens only, no leading/trailing/consecutive hyphens.'
            ),
        )
    if name_val and name_val != skill_dir.name:
        add(
            severity="HIGH",
            check="name_dir_mismatch",
            detail=f"frontmatter name '{name_val}' != directory name '{skill_dir.name}'",
            prompt_hint=f'Make the `name` field in `{skill_name}`\'s frontmatter match its parent directory name — required by the agentskills.io spec.',
        )

    # 6. agentskills.io spec: description length (hard limit 1024; soft warning
    # above 800 since "keep it concise" is an explicit best-practice)
    if len(description) > 1024:
        add(
            severity="HIGH",
            check="description_too_long",
            detail=f"description is {len(description)} chars — spec hard limit is 1024",
            prompt_hint=f'Shorten `{skill_name}`\'s `description` field to 1024 characters or fewer.',
        )
    elif len(description) > 800:
        add(
            severity="LOW",
            check="description_approaching_limit",
            detail=f"description is {len(description)} chars — {1024 - len(description)} under the 1024 hard limit",
            prompt_hint=f'Consider trimming `{skill_name}`\'s `description` — approaching the 1024-char spec limit, and agentskills.io\'s own guidance says to keep it concise.',
        )

    # 7. agentskills.io best-practice: SKILL.md body under 500 lines, with detail
    # pushed to references/ (progressive disclosure) — soft guideline, not part of
    # the hard spec (skills-ref validate doesn't check it), but real and verified:
    # this collection's own consumer-project skill-standards detector already
    # enforces this exact 500-line number on OTHER people's skills without holding
    # itself to it.
    if len(lines) > _AGENTSKILLS_MAX_RECOMMENDED_LINES:
        add(
            severity="MEDIUM",
            check="oversized_skill_md",
            detail=f"{len(lines)} lines — agentskills.io recommends under 500, with detail moved to references/",
            prompt_hint=(
                f'`{skill_name}` is {len(lines)} lines. Per agentskills.io\'s progressive-'
                f'disclosure guidance, split detailed reference material into `references/'
                f'*.md` files, telling the agent exactly when to load each one, and keep '
                f'`SKILL.md` itself under 500 lines / ~5000 tokens.'
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

    blocking_issues = [
        i for i in all_issues if (i["skill_dir"], i["check"]) not in KNOWN_DEBT
    ]

    report = {
        "generated": TODAY.isoformat(),
        "total_issues": len(all_issues),
        "blocking_issues": len(blocking_issues),
        "by_severity": by_severity,
        "by_check": by_check,
        "open_known_issues": open_known,
        "issues": all_issues,
    }

    print(json.dumps(report, indent=2))
    return 0 if not blocking_issues else 1


if __name__ == "__main__":
    sys.exit(main())
