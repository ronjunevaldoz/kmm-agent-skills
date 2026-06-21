# /audit-screenshots $ARGUMENTS

**KMM Agent Skills** — analyze Roborazzi golden screenshots for design consistency.
Uses Claude's vision capability to inspect committed PNG files against the design
system rules: color tokens, spacing, typography, TopAppBar structure, dark/light
mode parity, and accessibility contrast.

Screenshot path: `$ARGUMENTS` (defaults to `**/src/jvmTest/snapshots/` if empty)

This is a visual audit — it catches design regressions that logic tests miss:
wrong colors, broken dark mode, inconsistent spacing, or missing TopAppBar chrome.

---

## Step 1 — Find screenshots

```bash
find "${ARGUMENTS:-.}" -name "*.png" \
  -not -name "*_compare.png" \
  -not -name "*_actual.png" \
  -path "*/snapshots/*" \
  | sort
```

Group files into pairs where possible:
- `FooContent_light.png` + `FooContent_dark.png` → one audit unit
- Unpaired files → audit individually

If no PNG files are found: print `No screenshots found at <path>` and stop.

---

## Step 2 — For each screenshot (or pair), run a visual design audit

Read each image using vision and check all of the following. Flag each issue
with the screenshot filename and a short description.

### Color token compliance
- [ ] No solid blocks of arbitrary color visible that don't match a design token pattern
- [ ] Background uses a neutral surface color (not pure `#000000` or `#FFFFFF` in dark mode unless intentional)
- [ ] Interactive elements (buttons, chips) use a consistent accent color across screens
- [ ] Error states are red-family; success states are green-family — consistent with AppTheme

### Dark mode parity (pairs only)
- [ ] Dark variant has a dark background — if it looks identical to the light variant, it is broken
- [ ] Text is light-on-dark in dark mode, not dark-on-dark (invisible text)
- [ ] No elevation shadows that are too harsh in dark mode (shadows should be subtle)
- [ ] Icons and illustrations adapt — no all-white icons on a white dark-mode background

### AppScaffold structure
- [ ] TopAppBar is present at the top of every screen (not a bare Text title in the content body)
- [ ] Screen title appears in the TopAppBar, not duplicated in the content
- [ ] Back/close button is in the TopAppBar navigation slot if the screen is non-root
- [ ] Primary action buttons (save, confirm) are in TopAppBar actions or a prominent CTA — not a plain text link

### Spacing and layout
- [ ] Content has consistent outer padding — elements don't touch the screen edge
- [ ] List items have consistent internal padding between icon, label, and trailing action
- [ ] No obvious alignment breaks — elements that should be flush are flush

### Typography
- [ ] Body text is readable — not too small (visually under ~12sp equivalent)
- [ ] Headings are visually distinct from body text
- [ ] All text truncates with an ellipsis, not by clipping or overflowing

### Accessibility contrast
- [ ] Text on colored backgrounds appears readable — flag if text and background look low-contrast
- [ ] Disabled state elements are visually distinct (greyed out) but not invisible
- [ ] Icon-only buttons have enough visual weight to be tappable

---

## Step 3 — Output

For each screenshot audited:

```
SCREENSHOT: FooContent_light.png + FooContent_dark.png

  ✅ Color tokens       — consistent with design system
  ✅ Dark mode parity   — dark variant correctly inverts background/text
  ⚠️  AppScaffold       — TopAppBar missing; title appears as plain Text in content body
  ✅ Spacing            — consistent outer padding, no edge-touching elements
  ⚠️  Contrast          — "Cancel" button label may be low-contrast on the gray background
  ✅ Typography         — heading/body hierarchy clear
```

Aggregate summary at the end:

```
AUDIT SUMMARY: <N> screenshots / <N> pairs

  PASS:    <N>
  WARNING: <N>   (design issues that don't block but should be addressed)
  FAIL:    <N>   (broken dark mode, missing TopAppBar, invisible text)

RESULT: PASS | NEEDS ATTENTION
```

---

## Step 4 — Recommended fixes

For each WARNING or FAIL, give a concrete fix tied to the design-system skill:

| Finding | Fix | Skill |
|---|---|---|
| Missing TopAppBar | Wrap content in `AppScaffold { AppTopAppBar(...) }` | `kotlin-multiplatform-design-system` |
| Dark mode identical to light | Check `AppTheme.colors.background` is not hardcoded; use semantic tokens | `kotlin-multiplatform-design-system` |
| Low-contrast text | Replace `Color(0xFFAAAAAA)` with `AppTheme.colors.onSurfaceVariant` | `kotlin-multiplatform-design-system` |
| Inconsistent spacing | Replace `padding(16.dp)` with `AppTheme.spacing.lg` | `kotlin-multiplatform-design-system` |
| Title duplicated in content | Remove `Text(title)` from content; move to `AppTopAppBar(title = "...")` | `kotlin-multiplatform-design-system` |

---

## Notes

- Warnings are not blockers by default — the developer decides whether to fix before merging.
  Use `FAIL` only for clearly broken states (invisible text, completely wrong dark mode, absent TopAppBar).
- This audit is a supplement to, not a replacement for, Roborazzi golden image diffs.
  Diffs catch regressions; this audit checks that the golden itself is correct.
- If the screenshots directory contains `_compare.png` or `_actual.png` files (diff artifacts),
  those indicate a failing `jvmTest` run — resolve the test failure before running this audit.
- Run this after `./gradlew recordRoborazziJvm` on a new screen, or after a design-system token update.
