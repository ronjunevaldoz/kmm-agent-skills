#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


class BulkRefactorPlan(NamedTuple):
    symbol_mappings: dict[str, str]  # OldSymbol -> NewSymbol
    package_mappings: dict[str, str]  # OldPackage -> NewPackage
    affected_files: dict[Path, str]  # Path -> updated content


def plan_bulk_refactor(
    project_root: Path,
    mappings: dict[str, str],
    is_package: bool = False,
) -> BulkRefactorPlan:
    project_root = project_root.resolve()
    affected_files: dict[Path, str] = {}

    symbol_mappings = mappings if not is_package else {}
    package_mappings = mappings if is_package else {}

    # Compile regex patterns for fast batch execution
    patterns = []
    if is_package:
        for old_pkg, new_pkg in package_mappings.items():
            pkg_pattern = re.compile(
                rf"^(\s*(?:package|import)\s+){re.escape(old_pkg)}(\.[a-zA-Z0-9_.]+)?(\s*(?:;.*)?)$",
                re.MULTILINE,
            )
            patterns.append((pkg_pattern, rf"\1{new_pkg}\2\3", old_pkg, new_pkg))
    else:
        for old_sym, new_sym in symbol_mappings.items():
            sym_pattern = re.compile(rf"\b{re.escape(old_sym)}\b")
            patterns.append((sym_pattern, new_sym, old_sym, new_sym))

    for kt_file in project_root.rglob("*.kt"):
        if any(ignored in kt_file.parts for ignored in (".git", ".gradle", "build", ".idea", ".vscode", "node_modules")):
            continue

        try:
            content = kt_file.read_text(encoding="utf-8")
        except Exception:
            continue

        orig_content = content

        for pattern, replacement, old_val, new_val in patterns:
            content = pattern.sub(replacement, content)
            # Update KDocs
            if is_package:
                content = content.replace(f"[{old_val}.", f"[{new_val}.")
            else:
                content = content.replace(f"[{old_val}]", f"[{new_val}]")

        if content != orig_content:
            affected_files[kt_file] = content

    return BulkRefactorPlan(
        symbol_mappings=symbol_mappings,
        package_mappings=package_mappings,
        affected_files=affected_files,
    )


def execute_bulk_refactor(plan: BulkRefactorPlan, dry_run: bool = False) -> None:
    print(f"\n📦 Bulk Refactor Execution ({len(plan.symbol_mappings or plan.package_mappings)} mappings)")
    for k, v in (plan.symbol_mappings or plan.package_mappings).items():
        print(f"   • '{k}' ➔ '{v}'")
    print(f"   Impacted Files ({len(plan.affected_files)}):")
    for f in plan.affected_files:
        print(f"     - {f}")

    if dry_run:
        print("\n🔍 DRY RUN: No files were modified on disk.")
        return

    for file_path, new_content in plan.affected_files.items():
        file_path.write_text(new_content, encoding="utf-8")

    print(f"✅ Bulk refactor applied cleanly across {len(plan.affected_files)} file(s)!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated bulk/batch Kotlin refactor tool")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--map-file", type=Path, help="JSON file containing key-value mappings {old: new}")
    parser.add_argument("--packages", action="store_true", help="Treat mappings as package prefixes rather than symbols")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying disk")

    args = parser.parse_args()

    if not args.map_file or not args.map_file.exists():
        print("❌ Error: Valid --map-file (JSON) is required.", file=sys.stderr)
        return 1

    try:
        mappings = json.loads(args.map_file.read_text(encoding="utf-8"))
        plan = plan_bulk_refactor(
            project_root=args.project,
            mappings=mappings,
            is_package=args.packages,
        )
        execute_bulk_refactor(plan, dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"❌ Bulk Refactor Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
