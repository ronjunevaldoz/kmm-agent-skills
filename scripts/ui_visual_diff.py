#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import NamedTuple

try:
    from PIL import Image, ImageChops
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class VisualDiffResult(NamedTuple):
    reference_path: Path
    actual_path: Path
    diff_output_path: Path | None
    total_pixels: int
    different_pixels: int
    match_percentage: float


def compare_images(ref_path: Path, actual_path: Path, diff_out: Path | None = None, threshold: int = 10) -> VisualDiffResult:
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow is required for pixel diffing: pip install pillow")

    ref_img = Image.open(ref_path).convert("RGBA")
    act_img = Image.open(actual_path).convert("RGBA")

    # Match dimensions by bounding box if needed
    width = max(ref_img.width, act_img.width)
    height = max(ref_img.height, act_img.height)

    ref_canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    act_canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ref_canvas.paste(ref_img, (0, 0))
    act_canvas.paste(act_img, (0, 0))

    ref_data = ref_canvas.load()
    act_data = act_canvas.load()

    diff_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    diff_data = diff_img.load()

    different_pixels = 0
    total_pixels = width * height

    for y in range(height):
        for x in range(width):
            r1, g1, b1, a1 = ref_data[x, y]
            r2, g2, b2, a2 = act_data[x, y]

            delta = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2) + abs(a1 - a2)
            if delta > threshold:
                different_pixels += 1
                # Highlight mismatch in magenta (255, 0, 255, 255)
                diff_data[x, y] = (255, 0, 255, 255)
            else:
                # Dim background for context
                diff_data[x, y] = (r2, g2, b2, max(20, int(a2 * 0.3)))

    match_percentage = ((total_pixels - different_pixels) / total_pixels) * 100.0

    if diff_out and different_pixels > 0:
        diff_out.parent.mkdir(parents=True, exist_ok=True)
        diff_img.save(diff_out)

    return VisualDiffResult(
        reference_path=ref_path,
        actual_path=actual_path,
        diff_output_path=diff_out if different_pixels > 0 else None,
        total_pixels=total_pixels,
        different_pixels=different_pixels,
        match_percentage=match_percentage,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated UI Visual & Pixel Baseline Diff Tool")
    parser.add_argument("--ref", type=Path, required=True, help="Reference baseline image (upstream shadcn PNG)")
    parser.add_argument("--actual", type=Path, required=True, help="Actual rendered component screenshot")
    parser.add_argument("--diff-out", type=Path, default=None, help="Path to write visual mismatch diff image")
    parser.add_argument("--tolerance", type=float, default=99.0, help="Minimum passing match percentage (default: 99.0%)")

    args = parser.parse_args()

    if not PIL_AVAILABLE:
        print("❌ Error: Pillow is required. Install via `pip install pillow`", file=sys.stderr)
        return 1

    try:
        res = compare_images(args.ref, args.actual, args.diff_out)
        badge = "✅ PASS" if res.match_percentage >= args.tolerance else "❌ FAIL"
        print(f"\n🔬 Visual Pixel Baseline Comparison")
        print(f"{'=' * 65}")
        print(f"  Reference : {res.reference_path.name}")
        print(f"  Actual    : {res.actual_path.name}")
        print(f"  Total Pix : {res.total_pixels:,}")
        print(f"  Delta Pix : {res.different_pixels:,}")
        print(f"  Match %   : {res.match_percentage:.2f}% [{badge}]")
        if res.diff_output_path:
            print(f"  Diff Map  : {res.diff_output_path}")
        print(f"{'=' * 65}\n")
        return 0 if res.match_percentage >= args.tolerance else 1
    except Exception as e:
        print(f"❌ Visual Diff Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
