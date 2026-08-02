#!/usr/bin/env python3
"""
scan_command_shell_portability.py — scan commands/*.md for shell syntax inside
fenced bash blocks that is known to break under a command-rewriting hook (e.g.
the RTK proxy hook). Scoped to confirmed failure modes only, not speculative
guesses about any specific tool's internals.

Confirmed failure modes:
  - `find` using `-not` as a word-form predicate. This broke under a real user's
    RTK proxy hook (2026-07-10) on commands/kmp-audit-screenshots.md's screenshot
    scan. Fixed there by moving the exclusion out of find's predicate grammar
    entirely into a `grep -v` pipe — flag any other occurrence the same way.

Exit codes:
  0 — no issues found
  1 — issues found (expected; not an error)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = ROOT / "commands"

_BASH_BLOCK_RE = re.compile(r"```bash\n(.*?)```", re.DOTALL)
_FIND_NOT_RE = re.compile(r"\bfind\b.*?\s-not\s", re.DOTALL)


def _bash_blocks(text: str) -> list[tuple[int, str]]:
    """Return (start_line, block_text) for every fenced ```bash block."""
    blocks = []
    for m in _BASH_BLOCK_RE.finditer(text):
        start_line = text.count("\n", 0, m.start()) + 1
        blocks.append((start_line, m.group(1)))
    return blocks


def scan_command_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    text = path.read_text(encoding="utf-8", errors="ignore")
    for block_start, block in _bash_blocks(text):
        if _FIND_NOT_RE.search(block):
            offset = _FIND_NOT_RE.search(block).start()
            line_no = block_start + block.count("\n", 0, offset)
            findings.append(
                f"find -not predicate [MEDIUM]: {display_path}:{line_no} "
                f"— a `find ... -not ...` predicate broke under a real user's RTK "
                f"proxy hook; move the exclusion into a `grep -v` pipe instead "
                f"(`find ... | grep -v -e 'pattern1' -e 'pattern2'`)"
            )
    return findings


def main() -> int:
    all_findings: list[str] = []
    for path in sorted(COMMANDS_DIR.glob("*.md")):
        all_findings.extend(scan_command_file(path))

    if not all_findings:
        print("OK: no fragile find -not predicates in commands/*.md bash blocks")
        return 0

    for finding in all_findings:
        print(finding)
    return 1


if __name__ == "__main__":
    sys.exit(main())
