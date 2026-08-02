from __future__ import annotations

import unittest

from _helpers import REPO_ROOT, load_module

generate_palette = load_module(
    "generate_palette",
    REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "generate_palette.py",
)


class HexRgbRoundTripTests(unittest.TestCase):
    def test_hex_to_rgb_six_digit(self) -> None:
        self.assertEqual(generate_palette.hex_to_rgb("#1E3A5F"), (0x1E, 0x3A, 0x5F))

    def test_hex_to_rgb_three_digit_shorthand(self) -> None:
        self.assertEqual(generate_palette.hex_to_rgb("#FFF"), (0xFF, 0xFF, 0xFF))

    def test_rgb_to_hex_round_trip(self) -> None:
        r, g, b = generate_palette.hex_to_rgb("#1E3A5F")
        self.assertEqual(generate_palette.rgb_to_hex(r, g, b), "#1E3A5F")


class HslRoundTripTests(unittest.TestCase):
    def test_rgb_hsl_rgb_round_trip_within_tolerance(self) -> None:
        r, g, b = 30, 58, 95
        h, s, l = generate_palette.rgb_to_hsl(r, g, b)
        r2, g2, b2 = generate_palette.hsl_to_rgb(h, s, l)
        for a, b_ in zip((r, g, b), (r2, g2, b2)):
            self.assertLessEqual(abs(a - b_), 1)

    def test_grayscale_has_zero_saturation(self) -> None:
        h, s, l = generate_palette.rgb_to_hsl(128, 128, 128)
        self.assertEqual(s, 0.0)


class ContrastTests(unittest.TestCase):
    def test_black_on_white_is_max_contrast(self) -> None:
        lum_black = generate_palette.luminance(0, 0, 0)
        lum_white = generate_palette.luminance(255, 255, 255)
        ratio = generate_palette.contrast_ratio(lum_black, lum_white)
        self.assertAlmostEqual(ratio, 21.0, delta=0.1)

    def test_same_color_has_ratio_one(self) -> None:
        lum = generate_palette.luminance(100, 100, 100)
        self.assertAlmostEqual(generate_palette.contrast_ratio(lum, lum), 1.0)

    def test_on_color_picks_higher_contrast_side(self) -> None:
        # A dark seed should get a near-white "on" color, not near-black.
        on = generate_palette.on_color(20, 20, 20)
        self.assertEqual(on, (250, 250, 250))


class DeriveFamilyTests(unittest.TestCase):
    def test_derive_family_light_has_all_expected_keys(self) -> None:
        fam = generate_palette.derive_family_light("#1E3A5F")
        self.assertEqual(
            set(fam.keys()),
            {"color", "onColor", "container", "onContainer", "hover", "pressed", "disabled"},
        )
        for value in fam.values():
            self.assertTrue(value.startswith("0xFF"))


class ParseBrandArgsTests(unittest.TestCase):
    def test_parses_name_and_hex(self) -> None:
        result = generate_palette.parse_brand_args(["primary=#1E3A5F", "accent=E67E22"])
        self.assertEqual(result["primary"], "#1E3A5F")
        self.assertEqual(result["accent"], "#E67E22")

    def test_normalizes_dashes_and_case_in_name(self) -> None:
        result = generate_palette.parse_brand_args(["Brand-Accent=#000000"])
        self.assertIn("brand_accent", result)

    def test_raises_on_missing_equals(self) -> None:
        with self.assertRaises(ValueError):
            generate_palette.parse_brand_args(["not-a-valid-entry"])


if __name__ == "__main__":
    unittest.main()
