#!/usr/bin/env python3
"""
scan_mimicry_compliance.py — mechanical checks for kmp-api-mimicry's Compliance &
Legal Audit: namespace/trademark collision and accidental real-dependency
re-linking (both opt-in, see below), plus font-license-file presence (always on).

Deliberately NOT here: code-origin/attribution review (was this function
independently re-derived from public docs, or copy-pasted?) and trademarked-term
scanning in project text. Both are judgment calls a script can't safely make —
same reasoning as kmp-audit's "Construction/execution lifecycle coupling"
inspection item for a different smell. See references/compliance-audit.md for
the manual checklist covering those.

Namespace/dependency checks require explicit --namespace-prefix/
--dependency-coordinate flags, on purpose — this collection's own primary
audience builds real Compose Multiplatform apps constantly, so a *default*
flagging `androidx.compose.*` would false-positive on nearly every normal
consumer project. Only run these two checks with the specific reference
library's package/coordinate you are actually mimicking.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

FONT_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
LICENSE_FILENAMES = {"license.txt", "license.md", "license", "ofl.txt", "notice.txt", "notice"}

_KT_PACKAGE_IMPORT_RE = re.compile(r"^\s*(?:package|import)\s+([\w.]+)", re.MULTILINE)


def _iter_kt_files(root: Path):
    for path in root.rglob("*.kt"):
        if "/build/" in str(path) or "/.git/" in str(path):
            continue
        yield path


def scan_namespace_violations(root: Path, prefixes: tuple[str, ...]) -> list[str]:
    findings = []
    for path in _iter_kt_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in _KT_PACKAGE_IMPORT_RE.finditer(text):
            ns = m.group(1)
            for prefix in prefixes:
                if ns.startswith(prefix):
                    line_no = text.count("\n", 0, m.start()) + 1
                    findings.append(
                        f"namespace violation [HIGH]: {path.relative_to(root)}:{line_no} "
                        f"— uses reference-library namespace '{ns}' (prefix '{prefix}') "
                        f"— rename to your own package before publishing"
                    )
                    break
    return findings


def scan_font_licenses(root: Path) -> list[str]:
    findings = []
    for font in root.rglob("*"):
        if not font.is_file() or font.suffix.lower() not in FONT_EXTENSIONS:
            continue
        if "/build/" in str(font) or "/.git/" in str(font):
            continue
        sibling_names = {p.name.lower() for p in font.parent.iterdir() if p.is_file()}
        if not (sibling_names & LICENSE_FILENAMES):
            findings.append(
                f"font license missing [HIGH]: {font.relative_to(root)} has no "
                f"LICENSE.txt/OFL.txt/NOTICE.txt alongside it in "
                f"{font.parent.relative_to(root)} — every bundled font needs its "
                f"license text shipped with it (OFL fonts: OFL.txt; Apache-licensed "
                f"fonts: LICENSE.txt, plus NOTICE.txt if the font ships one)"
            )
    return findings


def scan_dependency_relinking(root: Path, coordinates: tuple[str, ...]) -> list[str]:
    findings = []
    targets = list(root.rglob("build.gradle.kts")) + list(root.rglob("libs.versions.toml"))
    for path in targets:
        if "/build/" in str(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for coord in coordinates:
            if coord in text:
                line_no = text[: text.find(coord)].count("\n") + 1
                findings.append(
                    f"accidental re-linking [HIGH]: {path.relative_to(root)}:{line_no} "
                    f"declares '{coord}' — the real reference library, not your own "
                    f"mimicked implementation; remove it unless deliberately depending "
                    f"on the real thing (which means this project isn't mimicry anymore)"
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan an API-mimicry project for namespace collisions, missing "
        "font license files, and accidental real-dependency re-linking."
    )
    parser.add_argument("root", type=Path, help="Project root")
    parser.add_argument(
        "--namespace-prefix", action="append", default=[],
        help="Reference-library package prefix to flag if imported, e.g. "
        "androidx.compose. (repeatable; no default — must name the real one)",
    )
    parser.add_argument(
        "--dependency-coordinate", action="append", default=[],
        help="Maven coordinate substring to flag in build files, e.g. "
        "androidx.compose.ui: (repeatable; no default)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    findings: list[str] = []
    findings.extend(scan_font_licenses(root))

    if args.namespace_prefix:
        findings.extend(scan_namespace_violations(root, tuple(args.namespace_prefix)))
    else:
        print("skipped: namespace check (pass --namespace-prefix to enable)")

    if args.dependency_coordinate:
        findings.extend(scan_dependency_relinking(root, tuple(args.dependency_coordinate)))
    else:
        print("skipped: dependency-relinking check (pass --dependency-coordinate to enable)")

    for f in findings:
        print(f)
    if not findings:
        print("OK: no findings in the checks that ran")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
