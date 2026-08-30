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

try:
    from refactor_common import substitute_outside_string_literals
except ImportError:  # imported as scripts.refactor_rename by the test suite
    from scripts.refactor_common import substitute_outside_string_literals


class RenamePlan(NamedTuple):
    old_name: str
    new_name: str
    target_file: Path | None
    new_target_file: Path | None
    affected_files: dict[Path, str]  # Path -> modified content


def plan_rename(
    project_root: Path,
    old_symbol: str,
    new_symbol: str,
    target_file: Path | None = None,
) -> RenamePlan:
    project_root = project_root.resolve()
    affected_files: dict[Path, str] = {}

    target_file_resolved = target_file.resolve() if target_file else None
    new_target_file: Path | None = None

    if target_file_resolved:
        if not target_file_resolved.exists():
            raise FileNotFoundError(f"Target file not found: {target_file_resolved}")
        if target_file_resolved.name == f"{old_symbol}.kt":
            new_target_file = target_file_resolved.parent / f"{new_symbol}.kt"

    # Regex for symbol boundaries in Kotlin: word boundary matching
    # Ensures OldSymbol matches in:
    #   - class OldSymbol
    #   - : OldSymbol
    #   - <OldSymbol>
    #   - OldSymbol(
    #   - import pkg.OldSymbol
    #   - [OldSymbol]
    # But does NOT match prefix/suffix like OldSymbolExtra or SomeOldSymbol
    symbol_pattern = re.compile(rf"\b{re.escape(old_symbol)}\b")

    for kt_file in project_root.rglob("*.kt"):
        if any(ignored in kt_file.parts for ignored in (".git", ".gradle", "build", ".idea", ".vscode", "node_modules")):
            continue

        try:
            content = kt_file.read_text(encoding="utf-8")
        except Exception:
            continue

        if symbol_pattern.search(content):
            new_content = substitute_outside_string_literals(symbol_pattern, new_symbol, content)
            if new_content != content:
                affected_files[kt_file] = new_content

    return RenamePlan(
        old_name=old_symbol,
        new_name=new_symbol,
        target_file=target_file_resolved,
        new_target_file=new_target_file,
        affected_files=affected_files,
    )


def execute_rename(plan: RenamePlan, dry_run: bool = False) -> None:
    print(f"\n🔄 Refactor Rename: '{plan.old_name}' ➔ '{plan.new_name}'")
    if plan.target_file and plan.new_target_file:
        print(f"   Renaming file: {plan.target_file.name} ➔ {plan.new_target_file.name}")
    print(f"   Impacted Files ({len(plan.affected_files)}):")
    for f in plan.affected_files:
        print(f"     • {f}")

    if dry_run:
        print("\n🔍 DRY RUN: No files were modified on disk.")
        return

    # Write all modified files
    for file_path, new_content in plan.affected_files.items():
        if plan.target_file and file_path == plan.target_file and plan.new_target_file:
            continue  # Will write to new_target_file
        file_path.write_text(new_content, encoding="utf-8")

    # Rename file if applicable
    if plan.target_file and plan.new_target_file and plan.target_file != plan.new_target_file:
        plan.new_target_file.write_text(plan.affected_files[plan.target_file], encoding="utf-8")
        plan.target_file.unlink()

    print("✅ Symbol rename applied cleanly across all project modules!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated semantic Kotlin refactor rename tool")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--old", type=str, required=True, help="Old class/interface/symbol name")
    parser.add_argument("--new", type=str, required=True, help="New class/interface/symbol name")
    parser.add_argument("--file", type=Path, default=None, help="Primary definition file (if renaming file too)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying disk")

    args = parser.parse_args()

    try:
        plan = plan_rename(
            project_root=args.project,
            old_symbol=args.old,
            new_symbol=args.new,
            target_file=args.file,
        )
        execute_rename(plan, dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"❌ Rename Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
