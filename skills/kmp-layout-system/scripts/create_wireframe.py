#!/usr/bin/env python3
"""
KMP Layout System — per-screen wireframe file creator.

Creates EXACTLY ONE screen file per invocation at docs/layout-system/<screen>.md, with the
correct section skeleton (Components table, a starting wireframe block, Interaction notes).
It never combines multiple screens into one file and never overwrites an existing screen
file (edit those in place). Bootstraps docs/layout-system/_components.md if missing.

The agent fills in the SVG wireframe's labels and component values — the script guarantees
the one-file-per-screen structure, naming, location, and a real-proportioned starting SVG.

Usage:
  python3 create_wireframe.py --screen "Inbox" --pattern A
  python3 create_wireframe.py --screen "Login" --pattern D --root /path/to/project
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CANVAS_W = 760
CANVAS_H = 420
FONT = 'font-family="sans-serif" font-size="13" fill="#333"'


def _rect(x: int, y: int, w: int, h: int, fill: str = "white") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#333" stroke-width="1"/>'


def _esc(text: str) -> str:
    """XML-escape a label. Placeholders use `<name>` — a literal `<`/`>` in SVG text
    content is invalid XML (parses as a tag start, not text) unless escaped."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _text_lines(x: int, y: int, lines: list[str]) -> str:
    """Stacked <tspan> lines, vertically centered around y. Labels are XML-escaped."""
    line_height = 18
    start_y = y - (len(lines) - 1) * line_height / 2
    tspans = "".join(
        f'<tspan x="{x}" y="{start_y + i * line_height:.0f}">{_esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f'<text text-anchor="middle" {FONT}>{tspans}</text>'


def _svg(body: str) -> str:
    return f'<svg viewBox="0 0 {CANVAS_W} {CANVAS_H}" xmlns="http://www.w3.org/2000/svg">\n{body}\n</svg>'


def _pattern_a() -> str:
    nav = _rect(0, 0, 64, CANVAS_H) + _text_lines(32, 60, ["Nav", "nav-1*", "nav-2", "nav-3", "nav-4", "nav-5"])
    side = _rect(64, 0, 180, CANVAS_H) + _text_lines(154, 40, ["Side Panel", "<item>", "<item>", "<item>"])
    main_w = CANVAS_W - 244
    main_top = _rect(244, 0, main_w, 320) + _text_lines(244 + main_w // 2, 160, ["Main Area", "<primary content>"])
    main_action = _rect(244, 320, main_w, 40) + _text_lines(244 + main_w // 2, 340, ["<action row>"])
    main_input = _rect(244, 360, main_w, 60) + _text_lines(244 + main_w // 2, 390, ["<input area>"])
    return _svg(nav + side + main_top + main_action + main_input)


def _pattern_b() -> str:
    nav = _rect(0, 0, 64, CANVAS_H) + _text_lines(32, 60, ["Nav", "nav-1", "nav-2*", "nav-3", "nav-4"])
    main_w = CANVAS_W - 64
    tabs = _rect(64, 0, main_w, 40) + _text_lines(64 + main_w // 2, 20, ["[tab] Tab A    [tab] Tab B    [tab] Tab C"])
    content = _rect(64, 40, main_w, CANVAS_H - 40)
    card_y, card_w, card_h, gap = 100, 140, 100, 20
    cards = ""
    for i in range(4):
        cx = 84 + i * (card_w + gap)
        cards += _rect(cx, card_y, card_w, card_h) + _text_lines(cx + card_w // 2, card_y + card_h + 16, ["<label>"])
    return _svg(nav + tabs + content + cards)


def _pattern_c() -> str:
    nav = _rect(0, 0, 64, CANVAS_H) + _text_lines(32, 60, ["Nav", "nav-1", "nav-2*", "nav-3"])
    canvas_w = CANVAS_W - 64
    canvas = _rect(64, 0, canvas_w, CANVAS_H, fill="#f5f5f5") + _text_lines(
        64 + canvas_w // 2, 40, ["[canvas stays in place — no swap]"]
    )
    sheet_x, sheet_y, sheet_w, sheet_h = 250, 110, 380, 220
    sheet_title = _rect(sheet_x, sheet_y, sheet_w, 40) + _text_lines(
        sheet_x + sheet_w // 2, sheet_y + 20, ["<Sheet title>          X"]
    )
    sheet_body = _rect(sheet_x, sheet_y + 40, sheet_w, sheet_h - 40) + _text_lines(
        sheet_x + sheet_w // 2, sheet_y + 40 + (sheet_h - 40) // 2, ["<content line>", "<content line>"]
    )
    return _svg(nav + canvas + sheet_title + sheet_body)


def _pattern_d() -> str:
    title = _rect(0, 0, CANVAS_W, 50) + _text_lines(CANVAS_W // 2, 25, ["<Screen Title> — full width"])
    header = _rect(0, 50, CANVAS_W, 120) + _text_lines(CANVAS_W // 2, 110, ["<header / hero content>"])
    content = _rect(0, 170, CANVAS_W, 180) + _text_lines(CANVAS_W // 2, 260, ["<content row>  [scroll]", "<content row>"])
    primary = (
        _rect(0, 350, CANVAS_W, 40, fill="#333")
        + f'<text x="{CANVAS_W // 2}" y="375" text-anchor="middle" font-family="sans-serif" '
          f'font-size="13" fill="white">&lt; Primary action &gt;</text>'
    )
    secondary = _text_lines(CANVAS_W // 2, 405, ["<secondary action>"])
    return _svg(title + header + content + primary + secondary)


PATTERNS = {"A": _pattern_a, "B": _pattern_b, "C": _pattern_c, "D": _pattern_d}

_COMPONENTS_TEMPLATE = """\
# Component Registry

Update this file when a component's dimensions, visibility, or behavior changes.

| Component       | Width / Height | Visibility               | Platform             | Notes              |
|-----------------|----------------|--------------------------|-----------------------|--------------------|
| <Component A>   | <N> dp         | <always / screen X only> | Both / Android / iOS | <short description> |
"""


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    return s.strip("-")[:60] or "screen"


# Slot-grid frontmatter per pattern: which named slots exist and which render at each
# breakpoint. Weights are simple fractions from a closed set — never arbitrary floats.
# Unaffected by the ASCII-to-SVG switch — this contract drives generate_slot_scaffold.py,
# not the visual wireframe.
PATTERN_GRIDS = {
    "A": ("[nav, side, main]",
          "{compact: [main], medium: [nav, main], expanded: [nav, side, main]}",
          "{nav: fixed, side: 1f, main: 3f}"),
    "B": ("[nav, main]",
          "{compact: [main], medium: [nav, main], expanded: [nav, main]}",
          "{nav: fixed, main: 1f}"),
    "C": ("[nav, main, sheet]",
          "{compact: [main, sheet], medium: [nav, main, sheet], expanded: [nav, main, sheet]}",
          "{nav: fixed, main: 1f, sheet: overlay}"),
    "D": ("[main]",
          "{compact: [main], medium: [main], expanded: [main]}",
          "{main: 1f}"),
}


def render(screen: str, pattern: str) -> str:
    wireframe = PATTERNS[pattern]()
    slots, grid, weights = PATTERN_GRIDS[pattern]
    return f"""\
---
screen: {slugify(screen)}
pattern: {pattern}
slots: {slots}
grid: {grid}
weights: {weights}
---

# {screen.strip()}

## Components

| Component      | Width   | Visible         | Notes                     |
|----------------|---------|-----------------|---------------------------|
| <Component A>  | <N> dp  | <always / when> | <short note>              |
| <Component B>  | flex 1  | Yes             | <short note>              |

---

## Default

{wireframe}

---

## Interaction notes

- <tap / swipe / gesture> → <what happens>
- <state change> → <how it looks>
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Create ONE per-screen wireframe file in docs/layout-system/.")
    p.add_argument("--screen", required=True, help="Screen name (becomes the heading + kebab filename).")
    p.add_argument("--pattern", default="A", choices=sorted(PATTERNS), help="Starting wireframe pattern (A/B/C/D).")
    p.add_argument("--root", type=Path, default=Path("."), help="Consumer project root (default: .).")
    args = p.parse_args()

    ls_dir = args.root / "docs" / "layout-system"
    ls_dir.mkdir(parents=True, exist_ok=True)

    # Bootstrap the shared registry once.
    components = ls_dir / "_components.md"
    if not components.exists():
        components.write_text(_COMPONENTS_TEMPLATE, encoding="utf-8")
        print(f"✅  Bootstrapped registry: {components}")

    screen_file = ls_dir / f"{slugify(args.screen)}.md"
    if screen_file.exists():
        print(f"⚠  {screen_file} already exists — edit it in place (not overwriting).", file=sys.stderr)
        return 1

    screen_file.write_text(render(args.screen, args.pattern), encoding="utf-8")
    print(f"✅  Created screen file: {screen_file}")
    print("    One file per screen — run create_wireframe.py again for the next screen.")
    print("    Now fill in the component table and the SVG wireframe's <text> labels with")
    print("    the project's real component names and content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
