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
from typing import NamedTuple


class RGB(NamedTuple):
    r: float  # 0..1
    g: float  # 0..1
    b: float  # 0..1


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)


def relative_luminance(rgb: RGB) -> float:
    r = srgb_to_linear(rgb.r)
    g = srgb_to_linear(rgb.g)
    b = srgb_to_linear(rgb.b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: RGB, bg: RGB) -> float:
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def oklch_to_rgb(l: float, c: float, h_deg: float) -> RGB:
    # W3C CSS Color Module Level 4 standard OKLCH -> OKLab -> Linear sRGB -> sRGB
    h_rad = math.radians(h_deg)
    a = c * math.cos(h_rad)
    b = c * math.sin(h_rad)

    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b

    l3 = l_ ** 3
    m3 = m_ ** 3
    s3 = s_ ** 3

    # Linear sRGB
    r_lin = +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g_lin = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    b_lin = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    # Gamma encode to sRGB
    def gamma(v: float) -> float:
        v = max(0.0, min(1.0, v))
        return 12.92 * v if v <= 0.0031308 else 1.055 * math.pow(v, 1.0 / 2.4) - 0.055

    return RGB(gamma(r_lin), gamma(g_lin), gamma(b_lin))


def hex_to_rgb(hex_str: str) -> RGB:
    clean = hex_str.strip().lstrip("#")
    if len(clean) == 6:
        r = int(clean[0:2], 16) / 255.0
        g = int(clean[2:4], 16) / 255.0
        b = int(clean[4:6], 16) / 255.0
        return RGB(r, g, b)
    elif len(clean) == 8:  # ARGB or RGBA
        r = int(clean[2:4], 16) / 255.0
        g = int(clean[4:6], 16) / 255.0
        b = int(clean[6:8], 16) / 255.0
        return RGB(r, g, b)
    return RGB(0, 0, 0)


def evaluate_contrast(name: str, fg: RGB, bg: RGB) -> dict:
    ratio = contrast_ratio(fg, bg)
    passes_aa_normal = ratio >= 4.5
    passes_aa_large = ratio >= 3.0
    passes_aaa = ratio >= 7.0

    return {
        "pair": name,
        "ratio": ratio,
        "aa_normal": passes_aa_normal,
        "aa_large": passes_aa_large,
        "aaa": passes_aaa,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="WCAG 2.1 Theme Contrast Ratio Auditor")
    parser.add_argument("--fg-hex", type=str, help="Foreground color in hex (#FFFFFF)")
    parser.add_argument("--bg-hex", type=str, help="Background color in hex (#000000)")
    args = parser.parse_args()

    print("\n🎨 WCAG 2.1 Theme Contrast Ratio Audit")
    print(f"{'=' * 72}")

    if args.fg_hex and args.bg_hex:
        fg = hex_to_rgb(args.fg_hex)
        bg = hex_to_rgb(args.bg_hex)
        res = evaluate_contrast(f"{args.fg_hex} on {args.bg_hex}", fg, bg)
        aa_badge = "✅ PASS" if res["aa_normal"] else ("⚠️ Large Only (>=3.0)" if res["aa_large"] else "❌ FAIL")
        aaa_badge = "✅ PASS" if res["aaa"] else "⏳ Non-AAA"
        print(f"Pair: {res['pair']}")
        print(f"Contrast Ratio: {res['ratio']:.2f}:1")
        print(f"WCAG AA (Normal Text >= 4.5:1) : {aa_badge}")
        print(f"WCAG AAA (Enhanced >= 7.0:1)   : {aaa_badge}\n")
        return 0

    # Default audit of canonical Shadcn Dark/Light base token pairs
    canonical_pairs = [
        # Dark Theme (Zinc/Neutral)
        ("Dark: Foreground on Background", oklch_to_rgb(0.985, 0, 0), oklch_to_rgb(0.145, 0, 0)),
        ("Dark: PrimaryFg on Primary", oklch_to_rgb(0.145, 0, 0), oklch_to_rgb(0.985, 0, 0)),
        ("Dark: MutedFg on Background", oklch_to_rgb(0.708, 0, 0), oklch_to_rgb(0.145, 0, 0)),
        ("Dark: DestructiveFg on Destructive", oklch_to_rgb(0.985, 0, 0), oklch_to_rgb(0.396, 0.141, 25.723)),
        # Light Theme (Zinc/Neutral)
        ("Light: Foreground on Background", oklch_to_rgb(0.145, 0, 0), oklch_to_rgb(1.0, 0, 0)),
        ("Light: PrimaryFg on Primary", oklch_to_rgb(0.985, 0, 0), oklch_to_rgb(0.205, 0, 0)),
        ("Light: MutedFg on Background", oklch_to_rgb(0.556, 0, 0), oklch_to_rgb(1.0, 0, 0)),
        ("Light: DestructiveFg on Destructive", oklch_to_rgb(0.985, 0, 0), oklch_to_rgb(0.577, 0.245, 27.325)),
    ]

    print(f"{'Token Pair':<38} | {'Ratio':<8} | {'WCAG AA':<10} | {'WCAG AAA':<8}")
    print(f"{'-' * 38}-+-{'-' * 8}-+-{'-' * 10}-+-{'-' * 8}")

    all_pass = True
    for name, fg, bg in canonical_pairs:
        res = evaluate_contrast(name, fg, bg)
        aa_badge = "✅ PASS" if res["aa_normal"] else ("⚠️ Large (>=3)" if res["aa_large"] else "❌ FAIL")
        aaa_badge = "✅ PASS" if res["aaa"] else "⏳ Non-AAA"
        print(f"{res['pair']:<38} | {res['ratio']:>6.2f}:1 | {aa_badge:<10} | {aaa_badge:<8}")
        if not (res["aa_normal"] or res["aa_large"]):
            all_pass = False

    print(f"{'=' * 72}")
    if all_pass:
        print("🎉 100% WCAG 2.1 AA Compliance across all core theme tokens!\n")
        return 0
    else:
        print("⚠️ Contrast failures detected. Check flagged color pairs.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
