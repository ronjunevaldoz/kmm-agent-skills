#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import os
from pathlib import Path

# Directories to always skip during AST refactoring
IGNORED_DIRS = {
    ".git",
    ".gradle",
    "build",
    ".idea",
    ".vscode",
    ".claude",
    "node_modules",
    ".system_generated",
    "build-logic/build",
}


def should_skip_path(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORED_DIRS:
            return True
        if part.startswith(".") and part not in (".", ".."):
            return True
    return False


def iter_kotlin_files(project_root: Path):
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for file in files:
            if file.endswith(".kt") or file.endswith(".kts"):
                p = Path(root) / file
                if not should_skip_path(p):
                    yield p
