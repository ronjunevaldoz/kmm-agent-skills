#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import os
import re
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


# Matches Kotlin string and char literals so a blanket \bSymbol\b substitution can skip
# them — the concrete corruption case kmp-refactor/SKILL.md warns about (a @SerialName("Old")
# wire-format string, or a log message, silently rewritten by a naive rename). Comments are
# deliberately NOT masked here: existing callers rely on KDoc `[Symbol]` cross-references
# getting renamed too, and arbitrary comment prose drifting is lower-severity than a broken
# wire format or a string literal a test asserts on.
# ponytail: string-template expressions (`"${OldSymbol.thing()}"`) are masked along with
# their enclosing string and never renamed, so a rename inside a template needs a manual
# follow-up pass — full Kotlin lexing would fix this, not worth it for a regex-hardening pass.
_STRING_LITERAL_RE = re.compile(
    r'"""(?:[^"]|"(?!""))*"""'   # triple-quoted string
    r'|"(?:\\.|[^"\\\n])*"'      # regular string (escapes, no raw newline)
    r"|'(?:\\.|[^'\\\n])*'",     # char literal
    re.DOTALL,
)


def _mask_string_literals(content: str) -> str:
    def _mask(m: re.Match) -> str:
        return "".join(ch if ch == "\n" else "\0" for ch in m.group(0))

    return _STRING_LITERAL_RE.sub(_mask, content)


def substitute_outside_string_literals(pattern: re.Pattern, replacement, content: str) -> str:
    """Like pattern.sub(replacement, content), but skips any match that falls inside a
    Kotlin string or char literal, so a rename can't corrupt a @SerialName("Old") wire
    format or user-facing log text."""
    mask = _mask_string_literals(content)

    def _replace(m: re.Match) -> str:
        if "\0" in mask[m.start():m.end()]:
            return m.group(0)
        return m.expand(replacement) if isinstance(replacement, str) else replacement(m)

    return pattern.sub(_replace, content)
