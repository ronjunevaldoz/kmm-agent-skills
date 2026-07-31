#!/usr/bin/env python3
"""
generate_skills_report.py — writes docs/reference/skills-report.md, a compact
health-at-a-glance table for all skills. Built so a developer can scan the
state of the collection without reading through 64 individual SKILL.md files
or raw scan_skill_issues.py JSON output.

Sourced from skills.json (name, description, last_updated) plus
scan_skill_issues.py's own per-skill checks (line count, flags), so it never
drifts from what those two already compute — this script only formats.

Usage:
    python3 scripts/generate_skills_report.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = REPO_ROOT / "skills.json"
SKILLS_DIR = REPO_ROOT / "skills"
REPORT_MD = REPO_ROOT / "docs" / "reference" / "skills-report.md"

import sys
sys.path.insert(0, str(Path(__file__).parent))
from scan_skill_issues import scan_skill, KNOWN_DEBT  # noqa: E402


def build_report() -> str:
    manifest = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    rows: list[tuple[str, int, str, str]] = []  # name, lines, last_updated, flags

    for entry in manifest["skills"]:
        skill_dir = SKILLS_DIR / entry["name"]
        issues = scan_skill(skill_dir) if skill_dir.is_dir() else []
        blocking = [i for i in issues if (i["skill_dir"], i["check"]) not in KNOWN_DEBT]
        lines = issues[0]["lines"] if issues else len((skill_dir / "SKILL.md").read_text(encoding="utf-8").splitlines()) if (skill_dir / "SKILL.md").is_file() else 0

        if blocking:
            flags = f"🔴 {len(blocking)} blocking"
        elif issues:
            flags = f"🟡 {len(issues)} known debt"
        else:
            flags = "✅"

        rows.append((entry["name"], lines, entry.get("last_updated", ""), flags))

    rows.sort(key=lambda r: -r[1])  # largest first — same ordering that surfaced KI-008

    total = len(rows)
    clean = sum(1 for r in rows if r[3] == "✅")
    oversized = sum(1 for r in rows if r[1] > 500)

    lines_out = [
        "# Skills Report",
        "",
        f"Generated {date.today().isoformat()} by `scripts/generate_skills_report.py` — "
        "run it after any skill edit to refresh; not auto-run on every commit.",
        "",
        f"**{total} skills** — {clean} clean, {oversized} over the 500-line "
        "agentskills.io guideline (tracked as "
        "[KI-008](../../KNOWN_ISSUES.md#ki-008--22-of-64-skillmd-files-exceed-agentskillsios-recommended-500-line-body)).",
        "",
        "| Skill | Lines | Last Updated | Status |",
        "|---|---|---|---|",
    ]
    for name, lines_count, last_updated, flags in rows:
        lines_out.append(f"| [`{name}`](../../skills/{name}/) | {lines_count} | {last_updated} | {flags} |")

    lines_out += [
        "",
        "**Status legend:** ✅ no issues · 🟡 known, tracked debt (doesn't block a "
        "release — see KI-008) · 🔴 blocking (would fail `scan_skill_issues.py`, a new "
        "regression, not tracked debt)",
        "",
        "## Related",
        "",
        "- `scripts/scan_skill_issues.py` — the source of truth this report formats; run "
        "it directly for full JSON detail (prompt hints, exact check names)",
        "- `docs/reference/agentskills-io-standards.md` — what \"agentskills.io compliant\" "
        "actually means and how it's verified",
        "",
    ]
    return "\n".join(lines_out)


def main() -> int:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(), encoding="utf-8")
    print(f"✅  Wrote {REPORT_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
