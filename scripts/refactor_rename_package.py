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


class PackageRenamePlan(NamedTuple):
    old_package: str
    new_package: str
    moved_files: list[tuple[Path, Path]]  # (source_path, target_path)
    modified_files: dict[Path, str]  # Path -> new content


def plan_package_rename(
    project_root: Path,
    old_package: str,
    new_package: str,
) -> PackageRenamePlan:
    project_root = project_root.resolve()
    moved_files: list[tuple[Path, Path]] = []
    modified_files: dict[Path, str] = {}

    old_pkg_parts = old_package.split(".")
    new_pkg_parts = new_package.split(".")

    # 1. Identify all files residing in the old package directory tree
    for kt_file in project_root.rglob("*.kt"):
        if any(ignored in kt_file.parts for ignored in (".git", ".gradle", "build", ".idea", ".vscode", "node_modules")):
            continue

        try:
            content = kt_file.read_text(encoding="utf-8")
        except Exception:
            continue

        orig_content = content

        # Check if file has old_package declaration or subpackage (e.g. package com.old.sub)
        pkg_match = re.search(r"^\s*package\s+([a-zA-Z0-9_.]+)", content, re.MULTILINE)
        if pkg_match:
            curr_pkg = pkg_match.group(1)
            if curr_pkg == old_package or curr_pkg.startswith(f"{old_package}."):
                # Compute new subpackage name
                sub_suffix = curr_pkg[len(old_package) :]
                target_sub_pkg = f"{new_package}{sub_suffix}"

                # Update package statement in source file
                content = re.sub(
                    rf"^\s*package\s+{re.escape(curr_pkg)}",
                    f"package {target_sub_pkg}",
                    content,
                    flags=re.MULTILINE,
                )

                # Compute new physical target path
                parts = list(kt_file.parts)
                kotlin_idx = -1
                for i in range(len(parts) - 1, -1, -1):
                    if parts[i] in ("kotlin", "java"):
                        kotlin_idx = i
                        break

                if kotlin_idx != -1:
                    base_dir = Path(*parts[: kotlin_idx + 1])
                    new_rel_path = Path(*target_sub_pkg.split(".")) / kt_file.name
                    target_file = base_dir / new_rel_path
                    if target_file != kt_file:
                        moved_files.append((kt_file, target_file))

        # 2. Update imports and KDoc references across all project files
        # Replace: import com.old.Symbol -> import com.new.Symbol
        content = re.sub(
            rf"^(\s*import\s+){re.escape(old_package)}(\.[a-zA-Z0-9_.]+)?(\s*(?:;.*)?)$",
            rf"\1{new_package}\2\3",
            content,
            flags=re.MULTILINE,
        )

        # Replace KDoc links [com.old.Symbol] -> [com.new.Symbol]
        content = content.replace(f"[{old_package}.", f"[{new_package}.")

        if content != orig_content or any(src == kt_file for src, _ in moved_files):
            modified_files[kt_file] = content

    return PackageRenamePlan(
        old_package=old_package,
        new_package=new_package,
        moved_files=moved_files,
        modified_files=modified_files,
    )


def execute_package_rename(plan: PackageRenamePlan, dry_run: bool = False) -> None:
    print(f"\n📦 Refactor Package Rename: '{plan.old_package}' ➔ '{plan.new_package}'")
    print(f"   Files to move on disk ({len(plan.moved_files)}):")
    for src, dst in plan.moved_files:
        print(f"     • {src} ➔ {dst}")
    print(f"   Files with updated references ({len(plan.modified_files)}):")
    for f in plan.modified_files:
        print(f"     • {f}")

    if dry_run:
        print("\n🔍 DRY RUN: No files were modified on disk.")
        return

    # Write content updates
    for file_path, new_content in plan.modified_files.items():
        file_path.write_text(new_content, encoding="utf-8")

    # Move files to new directories
    for src, dst in plan.moved_files:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(plan.modified_files.get(src, src.read_text(encoding="utf-8")), encoding="utf-8")
        src.unlink()

        # Clean up empty parent directories
        try:
            parent = src.parent
            while parent != parent.parent:
                if not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                else:
                    break
        except Exception:
            pass

    print("✅ Package rename and import migration applied cleanly across all project modules!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated semantic Kotlin refactor package rename tool")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--old-package", type=str, required=True, help="Old package prefix to rename")
    parser.add_argument("--new-package", type=str, required=True, help="New package prefix")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying disk")

    args = parser.parse_args()

    try:
        plan = plan_package_rename(
            project_root=args.project,
            old_package=args.old_package,
            new_package=args.new_package,
        )
        execute_package_rename(plan, dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"❌ Package Rename Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
