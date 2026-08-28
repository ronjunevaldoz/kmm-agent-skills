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


class RefactorPlan(NamedTuple):
    source_file: Path
    target_file: Path
    old_package: str
    new_package: str
    old_symbols: list[str]
    new_symbols: list[str]
    affected_files: dict[Path, str]  # Path -> modified content


def extract_package_and_symbols(file_path: Path) -> tuple[str, list[str]]:
    content = file_path.read_text(encoding="utf-8")
    pkg_match = re.search(r"^\s*package\s+([a-zA-Z0-9_.]+)", content, re.MULTILINE)
    package = pkg_match.group(1) if pkg_match else ""

    # Extract top-level classes, interfaces, objects, and typealiases
    symbols = []
    for match in re.finditer(
        r"^\s*(?:(?:public|internal|private|sealed|data|abstract|open)\s+)*(?:class|interface|object|typealias|enum\s+class)\s+([a-zA-Z0-9_]+)",
        content,
        re.MULTILINE,
    ):
        symbols.append(match.group(1))

    # If no class was found, fallback to filename without .kt
    if not symbols and file_path.name.endswith(".kt"):
        symbols.append(file_path.stem)

    return package, symbols


def compute_target_path(source_file: Path, new_package: str, new_filename: str | None = None) -> Path:
    # Look for standard Kotlin source directory root (e.g. src/commonMain/kotlin or src/main/kotlin)
    parts = list(source_file.parts)
    kotlin_idx = -1
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] == "kotlin" or parts[i] == "java":
            kotlin_idx = i
            break

    filename = new_filename if new_filename else source_file.name

    if kotlin_idx != -1:
        base_dir = Path(*parts[: kotlin_idx + 1])
        pkg_rel_path = Path(*new_package.split("."))
        return base_dir / pkg_rel_path / filename
    else:
        # Fallback if outside standard source tree
        return source_file.parent / filename


def plan_refactor(
    project_root: Path,
    source_file: Path,
    target_package: str,
    rename_symbol: str | None = None,
) -> RefactorPlan:
    source_file = source_file.resolve()
    project_root = project_root.resolve()

    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    old_package, old_symbols = extract_package_and_symbols(source_file)
    new_symbols = list(old_symbols)

    new_filename = source_file.name
    if rename_symbol and old_symbols:
        old_primary = old_symbols[0]
        new_symbols[0] = rename_symbol
        new_filename = f"{rename_symbol}.kt"

    target_file = compute_target_path(source_file, target_package, new_filename)

    affected_files: dict[Path, str] = {}

    # 1. Update source file package header and class definition
    src_content = source_file.read_text(encoding="utf-8")
    if old_package:
        src_content = re.sub(
            rf"^\s*package\s+{re.escape(old_package)}",
            f"package {target_package}",
            src_content,
            flags=re.MULTILINE,
        )
    else:
        src_content = f"package {target_package}\n\n" + src_content

    if rename_symbol and old_symbols:
        old_primary = old_symbols[0]
        src_content = re.sub(
            rf"\b(class|interface|object|typealias)\s+{re.escape(old_primary)}\b",
            rf"\1 {rename_symbol}",
            src_content,
        )

    # Replace self-references in KDocs within source file
    for old_sym, new_sym in zip(old_symbols, new_symbols):
        old_fqn = f"{old_package}.{old_sym}" if old_package else old_sym
        new_fqn = f"{target_package}.{new_sym}"
        src_content = src_content.replace(f"[{old_fqn}]", f"[{new_fqn}]")

    affected_files[source_file] = src_content

    # 2. Update imports and references across all .kt files in the project
    for kt_file in project_root.rglob("*.kt"):
        if any(ignored in kt_file.parts for ignored in (".git", ".gradle", "build", ".idea", ".vscode", "node_modules")):
            continue
        if kt_file.resolve() == source_file:
            continue

        content = kt_file.read_text(encoding="utf-8")
        orig_content = content

        for old_sym, new_sym in zip(old_symbols, new_symbols):
            old_fqn = f"{old_package}.{old_sym}" if old_package else old_sym
            new_fqn = f"{target_package}.{new_sym}"

            # Replace exact imports: import old.package.MyClass
            content = re.sub(
                rf"^(\s*import\s+){re.escape(old_fqn)}(\s*(?:;.*)?)$",
                rf"\1{new_fqn}\2",
                content,
                flags=re.MULTILINE,
            )

            # Replace KDoc cross references [old.package.MyClass] -> [new.package.MyClass]
            content = content.replace(f"[{old_fqn}]", f"[{new_fqn}]")

        if content != orig_content:
            affected_files[kt_file] = content

    return RefactorPlan(
        source_file=source_file,
        target_file=target_file,
        old_package=old_package,
        new_package=target_package,
        old_symbols=old_symbols,
        new_symbols=new_symbols,
        affected_files=affected_files,
    )


def execute_refactor(plan: RefactorPlan, dry_run: bool = False) -> None:
    print(f"\n🔄 Refactoring: {plan.old_package}.{plan.old_symbols} ➔ {plan.new_package}.{plan.new_symbols}")
    print(f"   Source : {plan.source_file}")
    print(f"   Target : {plan.target_file}")
    print(f"   Impacted Files ({len(plan.affected_files)}):")
    for f in plan.affected_files:
        print(f"     • {f}")

    if dry_run:
        print("\n🔍 DRY RUN: No files were modified or moved.")
        return

    # Write modifications to all affected files
    for file_path, new_content in plan.affected_files.items():
        if file_path == plan.source_file and plan.source_file != plan.target_file:
            continue  # Will write to target_file directly
        file_path.write_text(new_content, encoding="utf-8")

    # Move source file to target file location
    if plan.source_file != plan.target_file:
        plan.target_file.parent.mkdir(parents=True, exist_ok=True)
        plan.target_file.write_text(plan.affected_files[plan.source_file], encoding="utf-8")
        plan.source_file.unlink()

        # Clean up empty parent directory if empty
        try:
            parent = plan.source_file.parent
            while parent != parent.parent:
                if not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                else:
                    break
        except Exception:
            pass

    print("✅ Refactoring applied successfully!")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated semantic Kotlin refactor tool (move package / rename)")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--file", type=Path, required=True, help="Kotlin source file to move")
    parser.add_argument("--target-package", type=str, required=True, help="Target package name")
    parser.add_argument("--rename", type=str, default=None, help="Rename the primary class and file")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying disk")

    args = parser.parse_args()

    try:
        plan = plan_refactor(
            project_root=args.project,
            source_file=args.file,
            target_package=args.target_package,
            rename_symbol=args.rename,
        )
        execute_refactor(plan, dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"❌ Refactor Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
