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


class ImportCleanPlan(NamedTuple):
    affected_files: dict[Path, str]
    removed_count: int


def clean_unused_imports_in_file(file_path: Path) -> tuple[str, int] | None:
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    lines = content.splitlines()
    pkg_line_idx = -1
    import_start_idx = -1
    import_end_idx = -1

    imports = []
    for idx, line in enumerate(lines):
        if re.match(r"^\s*package\s+", line):
            pkg_line_idx = idx
        elif re.match(r"^\s*import\s+", line):
            if import_start_idx == -1:
                import_start_idx = idx
            import_end_idx = idx
            imports.append((idx, line))

    if not imports:
        return None

    # Code body without the import lines
    body_lines = lines[:import_start_idx] + lines[import_end_idx + 1 :]
    body_text = "\n".join(body_lines)

    kept_imports = []
    removed = 0

    for idx, imp_line in imports:
        # Extract imported symbol: import com.pkg.Symbol as Alias or import com.pkg.Symbol
        match = re.search(r"^\s*import\s+([a-zA-Z0-9_.]+)(?:\s+as\s+([a-zA-Z0-9_]+))?", imp_line)
        if not match:
            kept_imports.append(imp_line)
            continue

        fqn = match.group(1)
        alias = match.group(2)
        symbol = alias if alias else fqn.split(".")[-1]

        # If it's a wildcard import, keep it
        if symbol == "*":
            kept_imports.append(imp_line)
            continue

        # Check if symbol is referenced anywhere in the rest of the file (code, annotations, KDocs)
        # Word-boundary check: \bSymbol\b
        if re.search(rf"\b{re.escape(symbol)}\b", body_text):
            kept_imports.append(imp_line)
        else:
            removed += 1

    if removed == 0:
        return None

    # Reassemble file
    # Sort kept imports alphabetically
    sorted_imports = sorted(list(set(kept_imports)))

    new_lines = (
        lines[:import_start_idx]
        + sorted_imports
        + lines[import_end_idx + 1 :]
    )

    return "\n".join(new_lines), removed


def plan_optimize_imports(project_root: Path) -> ImportCleanPlan:
    project_root = project_root.resolve()
    affected_files: dict[Path, str] = {}
    total_removed = 0

    for kt_file in project_root.rglob("*.kt"):
        if any(ignored in kt_file.parts for ignored in (".git", ".gradle", "build", ".idea", ".vscode", "node_modules")):
            continue

        res = clean_unused_imports_in_file(kt_file)
        if res:
            new_content, removed = res
            affected_files[kt_file] = new_content
            total_removed += removed

    return ImportCleanPlan(affected_files=affected_files, removed_count=total_removed)


def execute_optimize_imports(plan: ImportCleanPlan, dry_run: bool = False) -> None:
    print(f"\n🧹 Optimizing Imports: Found {plan.removed_count} unused import(s) across {len(plan.affected_files)} file(s).")
    for f in plan.affected_files:
        print(f"   • {f}")

    if dry_run:
        print("\n🔍 DRY RUN: No files were modified on disk.")
        return

    for file_path, new_content in plan.affected_files.items():
        file_path.write_text(new_content, encoding="utf-8")

    print(f"✅ Cleaned and sorted imports across {len(plan.affected_files)} file(s)!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated unused import cleaner & optimizer for Kotlin")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying disk")

    args = parser.parse_args()

    try:
        plan = plan_optimize_imports(args.project)
        execute_optimize_imports(plan, dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"❌ Optimize Imports Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
