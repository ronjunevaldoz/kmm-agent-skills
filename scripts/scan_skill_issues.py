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
COMMANDS_DIR = ROOT / "commands"
KNOWN_ISSUES_FILE = ROOT / "KNOWN_ISSUES.md"
TODAY = date.today()
STALE_MONTHS = 6

# Skills where a "Testing" section is not applicable
SKIP_TESTING = {
    "kmp-clean-architecture",   # contract doc
    "kmp-audit",                # meta review tool
    "kmp-ci-github-actions",    # CI YAML config
    "kmp-android-cli",          # CLI tool wrapper, no Kotlin API surface
    "kmp-xcframework-spm",      # binary distribution
    "kmp-library-publishing",   # Maven Central / GitHub Packages / BOM / binary-compat
    "kmp-code-quality",         # linting/formatting config
    "kmp-compose-preview-driven-development",  # workflow guide
    "kmp-expert",               # meta orchestrator
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
#
# KI-008 (oversized_skill_md) is fully resolved as of 2026-08-04 — all 22 skills that
# exceeded the 500-line guideline were split into references/*.md. Only the unrelated
# description_approaching_limit debt (a different check, description field length, not
# body length) remains.
KNOWN_DEBT: set[tuple[str, str]] = {
    ("kmp-compose-design-system", "description_approaching_limit"),
    ("kmp-layout-system", "description_approaching_limit"),
    # KI-009 (oversized_command_md) is fully resolved as of 2026-08-07 — both offending
    # commands are under the guideline. Only description-length debt remains, which is a
    # different check on a different field.
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

    # 8. Same 500-line guideline, applied to references/*.md — a reference file is only
    # loaded on demand (not on every activation like SKILL.md), but a single reference
    # that itself runs past 500 lines is still a large one-shot load when an agent does
    # need it, and often a sign it should split further (e.g. by component/step).
    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        for ref_file in sorted(references_dir.glob("*.md")):
            ref_lines = ref_file.read_text(encoding="utf-8").splitlines()
            if len(ref_lines) > _AGENTSKILLS_MAX_RECOMMENDED_LINES:
                add(
                    severity="MEDIUM",
                    check="oversized_reference_md",
                    detail=(
                        f"references/{ref_file.name} is {len(ref_lines)} lines — "
                        f"same 500-line guideline as SKILL.md itself"
                    ),
                    prompt_hint=(
                        f'`{skill_name}`\'s `references/{ref_file.name}` is {len(ref_lines)} '
                        f'lines. Split it further — by component, step, or concern — into '
                        f'more than one `references/*.md` file, same reasoning as the '
                        f'`oversized_skill_md` check applied to SKILL.md itself.'
                    ),
                )

    return issues


# ASD-STE100 (the aerospace controlled-language standard, free at asd-ste100.org) caps a
# procedural sentence at 20 words and requires one instruction per sentence. This repo
# adopts that structural rule for *procedural* text only — numbered steps — and
# deliberately not STE's ~900-word approved dictionary, which would strip precise terms
# this collection depends on ("delegate", "heuristic", "residual"). Rationale and the
# rejected alternatives live in docs/reference/writing-style.md.
#
# Inline code spans are removed before counting: `binary-compatibility-validator` is an
# identifier, not prose complexity. Tokens with no letter in them (stray commas left by
# that removal) are not words either — counting them made an enumeration of backticked
# skill names look like a 25-word sentence.
_NUMBERED_STEP_RE = re.compile(r"^\s*\d+\.\s+(.*)")
_CODE_SPAN_RE = re.compile(r"`[^`]*`")
_MAX_PROCEDURAL_WORDS = 20


def procedural_word_count(text: str) -> int:
    """Prose words in a procedural line, ignoring inline code spans and punctuation."""
    return sum(1 for tok in _CODE_SPAN_RE.sub(" ", text).split() if any(c.isalpha() for c in tok))


def scan_long_procedural_steps(paths: list[Path], label_prefix: str = "") -> list[dict]:
    """Flag a numbered step whose prose runs past the 20-word procedural limit."""
    issues: list[dict] = []
    for path in paths:
        in_fence = False
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = _NUMBERED_STEP_RE.match(line)
            if not m:
                continue
            words = procedural_word_count(m.group(1))
            if words <= _MAX_PROCEDURAL_WORDS:
                continue
            name = path.stem if path.name != "SKILL.md" else path.parent.name
            issues.append({
                "skill": f"{label_prefix}{name}",
                "skill_dir": name,
                "severity": "LOW",
                "check": "long_procedural_step",
                "detail": f"{path.name}:{lineno} — numbered step is {words} prose words (limit 20)",
                "prompt_hint": (
                    f"Step at {path}:{lineno} runs {words} prose words. Per this repo's "
                    f"writing style (docs/reference/writing-style.md), a numbered step "
                    f"holds one instruction and stays under 20 words. Split it into two "
                    f"steps, or move the explanation onto its own line beneath the step."
                ),
                "description": "", "last_updated": "", "lines": words,
            })
    return issues


def scan_commands() -> list[dict]:
    """Apply the same 500-line progressive-disclosure guideline to `commands/*.md`.

    A slash command's whole body loads into context the moment it's invoked — exactly
    the cost `oversized_skill_md` exists to bound for `SKILL.md` — but commands were
    never covered by any size check. Reported per-command using the command's filename
    stem as the `skill_dir` key so `KNOWN_DEBT` gates it the same way as the other two.
    """
    issues: list[dict] = []
    if not COMMANDS_DIR.is_dir():
        return issues

    for cmd_file in sorted(COMMANDS_DIR.glob("*.md")):
        lines = cmd_file.read_text(encoding="utf-8").splitlines()
        if len(lines) <= _AGENTSKILLS_MAX_RECOMMENDED_LINES:
            continue
        name = cmd_file.stem
        issues.append({
            "skill": f"/{name}",
            "skill_dir": name,
            "severity": "MEDIUM",
            "check": "oversized_command_md",
            "detail": (
                f"commands/{cmd_file.name} is {len(lines)} lines — same 500-line "
                f"guideline as SKILL.md and references/*.md"
            ),
            "prompt_hint": (
                f"`/{name}` is {len(lines)} lines and loads in full on every invocation. "
                f"Move the step-by-step detail into the skill(s) it already delegates to, "
                f"or into `references/*.md` under the owning skill, and keep the command "
                f"itself a thin orchestration checklist."
            ),
            "description": "",
            "last_updated": "",
            "lines": len(lines),
        })
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

    all_issues.extend(scan_commands())
    all_issues.extend(scan_long_procedural_steps(sorted(SKILLS_DIR.glob("*/SKILL.md"))))
    all_issues.extend(
        scan_long_procedural_steps(sorted(COMMANDS_DIR.glob("*.md")), label_prefix="/")
    )

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
