# /audit-design-visual

Runs a visual-only audit of your app's Roborazzi screenshots using Claude vision.
Detects design inconsistencies that have no code-level signal: spacing rhythm,
color contrast, typography hierarchy, icon sizing, and alignment drift across screens.

Use this **after** `/fix-design` and `/record-design-baselines` — it reads the committed
golden PNG files, not a live running app.

---

## Step 1 — Locate baseline PNGs

```bash
find "$PROJECT_ROOT" \
  -path "*/snapshots/*.png" \
  | sort
```

If no PNGs are found:
```
⚠️ No Roborazzi baselines found.
Run /record-design-baselines first to generate golden screenshots.
```

Group PNGs by module:
- `core/designsystem/src/jvmTest/snapshots/` — component-level
- `feature/*/ui/src/jvmTest/snapshots/` — screen-level

---

## Step 2 — Visual audit pass

For each PNG, read it with the Read tool and evaluate against these criteria:

### Component-level checks (design system PNGs)

| Check | Pass | Fail signal |
|---|---|---|
| Light variant has white/light background | ✅ | Dark or grey background |
| Dark variant has dark background | ✅ | White card on white background |
| Button uses consistent brand color | ✅ | Raw red, pure black, or pure white as brand |
| No double shadow / double elevation | ✅ | Two concentric shadow rings |
| Typography hierarchy visible | ✅ | All text at same visual weight |
| Spacing between elements looks rhythmic | ✅ | One side cramped, other loose |
| Interactive states present (hover, pressed, disabled) | ✅ | Only one state shown |

### Screen-level checks (feature PNGs)

| Check | Pass | Fail signal |
|---|---|---|
| Consistent button size across screens | ✅ | Buttons different heights in different screens |
| Same spacing rhythm as component level | ✅ | Margins differ between screens |
| Primary action is visually dominant | ✅ | Two equal-weight CTAs competing |
| No orphaned hardcoded color vs system color | ✅ | Brand color in one screen, plain grey in another |
| Error states use the same error color token | ✅ | Red in one screen, orange in another |
| Navigation bar / TopAppBar consistent across screens | ✅ | Height or icon size varies |

---

## Step 3 — Report findings

After reviewing all PNGs, print a structured report:

```
/audit-design-visual — N screens reviewed

Component level:
  ✅ AppButton (4 variants) — consistent color, clear hover/disabled states
  ✅ AppCard — no double shadow, correct dark background
  ⚠️  AppTextField — dark mode: placeholder text barely visible against surface
        → consider increasing `placeholderAlpha` from 0.38 to 0.50 in dark mode

Screen level:
  ✅ AuthScreen — spacing rhythmic, primary CTA dominant
  ⚠️  HomeScreen — product cards use slightly different corner radius than AppCard
        → confirm this is intentional or use AppCard directly
  ❌  ProfileScreen — TopAppBar icon appears 8px taller than on HomeScreen
        → check IconButtonSize token vs inline Modifier.size()

Overall:
  ✅ Passed: 5
  ⚠️  Review: 2
  ❌ Fix: 1

Next:
  • For ⚠️ items: run /fix-design on the flagged files if the issue is code-level,
    or update the token if it's a design decision.
  • For ❌ items: high confidence regression — fix before merging.
  • Re-run /record-design-baselines after fixing to update goldens.
```

---

## Step 4 — Optional: cross-screen consistency matrix

If there are 4+ screens, run a second pass that compares PNGs side by side:

For each UI element category (buttons, cards, text, spacing), print:

```
Buttons across screens:
  AuthScreen.png    height ≈ 48dp  ✅ consistent
  HomeScreen.png    height ≈ 48dp  ✅ consistent
  ProfileScreen.png height ≈ 56dp  ❌ DIFFERS — 8dp taller than other screens
```

This cross-screen pass is what pure code analysis cannot do — it catches drift that
happens when different team members independently implement the same visual element.

---

## Rules

- **Only read PNGs, never modify them.** This command is read-only.
- **Do not flag artistic choices as failures.** The audit checks for *consistency*
  and *system violations*, not personal taste.
- **When a finding is ambiguous, mark it ⚠️ (review) not ❌ (fix).** The developer
  may have intentionally diverged from the pattern.
- **Reference the token name when possible.** Instead of "this button is the wrong
  color," say "this appears to be `Color(0xFF...)` rather than `appTheme.colors.primary`."
