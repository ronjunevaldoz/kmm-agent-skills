#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


class ComposeViolation(NamedTuple):
    file: Path
    line: int
    rule: str
    message: str
    snippet: str


IGNORED_DIRS = {".git", ".gradle", "build", ".idea", ".vscode", ".claude", "node_modules", ".system_generated"}


def audit_compose_performance(project_root: Path) -> list[ComposeViolation]:
    project_root = project_root.resolve()
    violations: list[ComposeViolation] = []

    # Patterns
    composable_def_re = re.compile(r"^\s*@Composable\s+(?:(?:public|internal|private)\s+)?fun\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)", re.MULTILINE)
    raw_color_re = re.compile(r"\bColor\.(Red|Green|Blue|Yellow|Cyan|Magenta|Black|White|Gray|LightGray|DarkGray)\b|\bColor\(0x[0-9a-fA-F]+\)")
    unstable_param_re = re.compile(r"\b([a-zA-Z0-9_]+)\s*:\s*(List<|Set<|Map<)")
    unkeyed_items_re = re.compile(r"\bitems\s*\(\s*([a-zA-Z0-9_.]+)\s*\)\s*\{")

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for file in files:
            if not file.endswith(".kt"):
                continue

            file_path = Path(root) / file
            # Skip test files and reference token files
            if "Test" in file_path.name or "Tokens" in file_path.name or "Palette" in file_path.name:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            lines = content.splitlines()

            for idx, line in enumerate(lines, 1):
                # 1. Unkeyed Lazy List Items
                if unkeyed_items_re.search(line):
                    violations.append(ComposeViolation(
                        file=file_path,
                        line=idx,
                        rule="UNKEYED_LAZY_ITEMS",
                        message="Lazy layout uses unkeyed items() — add 'key = { it.id }' to prevent full recomposition on dataset updates.",
                        snippet=line.strip(),
                    ))

                # 2. Hardcoded raw colors in UI component files (under components/ or ui/)
                if ("components" in file_path.parts or "ui" in file_path.parts) and not ("Theme" in file_path.name or "Color" in file_path.name):
                    match = raw_color_re.search(line)
                    if match and not ("// ok: raw-color" in line or "Color.Unspecified" in line or "Color.Transparent" in line):
                        violations.append(ComposeViolation(
                            file=file_path,
                            line=idx,
                            rule="HARDCODED_COLOR_TOKEN",
                            message=f"Hardcoded raw color '{match.group(0)}' used in UI component — use semantic 'AppTheme.colors' or 'theme.palette' token.",
                            snippet=line.strip(),
                        ))

            # 3. Composable parameter audits
            for match in composable_def_re.finditer(content):
                fn_name = match.group(1)
                params = match.group(2)
                line_idx = content[:match.start()].count("\n") + 1

                for un_match in unstable_param_re.finditer(params):
                    param_name = un_match.group(1)
                    type_prefix = un_match.group(2)
                    violations.append(ComposeViolation(
                        file=file_path,
                        line=line_idx,
                        rule="UNSTABLE_COLLECTION_PARAM",
                        message=f"@Composable '{fn_name}' takes unstable '{type_prefix}...' param '{param_name}' — consider using ImmutableList/ImmutableSet.",
                        snippet=f"fun {fn_name}(... {param_name}: {type_prefix} ...)",
                    ))

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose Multiplatform Performance & Stability Linter")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    args = parser.parse_args()

    print(f"\n⚡ Scanning Compose Multiplatform Stability & Performance in {args.project.name}...")
    print(f"{'=' * 75}")

    violations = audit_compose_performance(args.project)

    if not violations:
        print("🎉 Zero Compose stability or performance violations found!\n")
        return 0

    print(f"Found {len(violations)} Compose stability / performance suggestion(s):\n")
    for v in violations:
        rel_path = v.file.relative_to(args.project) if v.file.is_relative_to(args.project) else v.file
        print(f"  • [{v.rule}] {rel_path}:{v.line}")
        print(f"    Message : {v.message}")
        print(f"    Snippet : {v.snippet}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
