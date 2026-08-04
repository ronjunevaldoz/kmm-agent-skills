#!/usr/bin/env python3
"""
check_compat_matrix.py — verify docs/reference/compatibility-matrix.md
matches the pinned versions in the skill files.

Exit 0: matrix is in sync
Exit 1: matrix is stale or has drift

Usage:
    python3 scripts/check_compat_matrix.py
    python3 scripts/check_compat_matrix.py --repo-root /path/to/repo
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# Maps matrix "Library" column → list of (skill-relative-dir, toml-key-in-versions-block)
# checked against it. Every skill that pins the same library must agree with the
# matrix AND with each other — this is what catches cross-skill drift like a library
# scaffold pinning an older Kotlin than the rest of the collection (see PR history:
# library-publishing pinned kotlin=2.1.21 while feature-scaffold had moved to 2.4.0).
# Skill dir is relative to skills/
LIBRARY_MAP: dict[str, list[tuple[str, str]]] = {
    "Kotlin": [
        ("kmp-feature-scaffold", "kotlin"),
        ("kmp-library-publishing", "kotlin"),
    ],
    "AGP":                    [("kmp-feature-scaffold", "agp")],
    "KSP":                    [("kmp-feature-scaffold", "ksp")],
    "Compose Multiplatform":  [("kmp-feature-scaffold", "compose-multiplatform")],
    "Coroutines":             [("kmp-feature-scaffold", "coroutines")],
    "AndroidX Lifecycle":     [("kmp-feature-scaffold", "androidx-lifecycle")],
    "Koin":                   [("kmp-feature-scaffold", "koin")],
    "Ktor":                   [("kmp-feature-scaffold", "ktor")],
    "SQLDelight":             [("kmp-feature-scaffold", "sqldelight")],
    "BuildKonfig":            [("kmp-feature-scaffold", "buildkonfig")],
    "Roborazzi":              [("kmp-feature-scaffold", "roborazzi")],
    "Navigation Compose (KMP)": [("kmp-navigation",    "navigation-compose")],
    "Decompose":              [("kmp-navigation",        "decompose")],
}


def parse_matrix_versions(text: str) -> dict[str, str]:
    """Extract Library → version from the Pinned Versions table rows.

    Matches both plain and bold library names:
      | Kotlin | `2.4.0` | ...
      | **Kotlin** | `2.4.0` | ...
    Skips rows where the version cell is not a simple backtick-quoted string
    (e.g. constraint rows like '`{kotlinVersion}-{kspPatch}`').
    """
    versions: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*\*{0,2}([A-Za-z][^|*]+?)\*{0,2}\s*\|\s*`([^`{]+)`\s*\|", line)
        if m:
            library = m.group(1).strip()
            version = m.group(2).strip()
            # Skip header separator rows and rows with variable placeholders
            if re.match(r"^[- ]+$", version) or "{" in version:
                continue
            versions[library] = version
    return versions


def parse_toml_versions(text: str) -> dict[str, str]:
    """Extract key = "version" pairs from a toml-style versions block."""
    versions: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r'\s*([a-z][a-z0-9-]*)\s*=\s*"([^"]+)"', line)
        if m:
            # Only take the first occurrence (avoids picking up library module paths)
            key = m.group(1)
            if key not in versions:
                versions[key] = m.group(2)
    return versions


def check(repo_root: Path) -> list[str]:
    matrix_path = repo_root / "docs" / "reference" / "compatibility-matrix.md"
    if not matrix_path.exists():
        return ["docs/reference/compatibility-matrix.md not found — run 'fix' to create it"]

    matrix_text = matrix_path.read_text(encoding="utf-8")
    matrix_versions = parse_matrix_versions(matrix_text)

    if not matrix_versions:
        return ["compatibility-matrix.md has no parseable Pinned Versions table"]

    # Cache parsed skill files to avoid re-reading
    skill_versions_cache: dict[str, dict[str, str]] = {}

    findings: list[str] = []

    for library, pins in LIBRARY_MAP.items():
        matrix_ver = matrix_versions.get(library)
        if matrix_ver is None:
            findings.append(f"compat-matrix: '{library}' missing from Pinned Versions table")
            continue

        for skill_dir, toml_key in pins:
            if skill_dir not in skill_versions_cache:
                skill_md = repo_root / "skills" / skill_dir / "SKILL.md"
                if skill_md.exists():
                    skill_text = skill_md.read_text(encoding="utf-8")
                    references_dir = repo_root / "skills" / skill_dir / "references"
                    if references_dir.is_dir():
                        skill_text += "\n" + "\n".join(
                            ref.read_text(encoding="utf-8")
                            for ref in sorted(references_dir.glob("*.md"))
                        )
                    skill_versions_cache[skill_dir] = parse_toml_versions(skill_text)
                else:
                    skill_versions_cache[skill_dir] = {}

            skill_ver = skill_versions_cache[skill_dir].get(toml_key)

            if skill_ver is None:
                findings.append(
                    f"compat-matrix: '{library}' in matrix ({matrix_ver}) but "
                    f"'{toml_key}' not found in {skill_dir}/SKILL.md"
                )
            elif matrix_ver != skill_ver:
                findings.append(
                    f"compat-matrix drift: {library} — matrix={matrix_ver}, "
                    f"{skill_dir}={skill_ver} — update compatibility-matrix.md or {skill_dir}/SKILL.md"
                )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check compatibility matrix drift")
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parent.parent,
        help="Repository root (default: parent of scripts/)"
    )
    args = parser.parse_args()

    findings = check(args.repo_root)

    if findings:
        print(f"❌  Compatibility matrix has {len(findings)} drift finding(s):")
        for f in findings:
            print(f"    {f}")
        print()
        print("    Update docs/reference/compatibility-matrix.md → Pinned Versions table.")
        return 1

    matrix_path = args.repo_root / "docs" / "reference" / "compatibility-matrix.md"
    matrix_text = matrix_path.read_text(encoding="utf-8")
    count = len(parse_matrix_versions(matrix_text))
    print(f"✅  Compatibility matrix in sync ({count} libraries verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
