# Typography Scale Rationale and Text Resilience

Part of `kmp-compose-design-system`. Load this when choosing/justifying a type
scale ratio, fixing text overflow/truncation, or making a layout resilient to
translated strings.

---

## Type Scale Rationale — Modular Scales, Golden Ratio Included

`AppTypography`'s default scale (Step 2) wasn't derived from a single ratio —
real type scales rarely are. A **modular scale** multiplies a base size by a
fixed ratio to generate the rest of the steps; which ratio to pick is a real
decision worth stating explicitly, not leaving implicit.

| Ratio | Name | Fits |
|---|---|---|
| 1.125 | Minor second | Dense UI — data tables, admin tools, many small hierarchy jumps |
| 1.2 | Minor third | General UI default — close to this skill's own `AppTypography` steps |
| 1.25 | Major third | A bit more contrast between levels than 1.2, still UI-appropriate |
| 1.333 | Perfect fourth | Marketing/editorial screens wanting clearer hierarchy jumps |
| 1.5 | Perfect fifth | Large display type, hero sections |
| 1.618 | Golden ratio (φ) | Strong, dramatic hierarchy — display/marketing surfaces, not dense UI |

**Verified, not assumed**: the golden ratio (`Φ = 1.618`) is a real, widely-used
scaling ratio — base 16px × 1.618 ≈ 26px, and so on up the scale. NN/g's own
guidance on it is the honest caveat worth carrying into this skill: it's "a
helpful reference... one tool among many," not a rule that overrides the
practical need. A 1.618 jump between every step is usually **too aggressive
for dense UI** (a settings screen doesn't need `bodyMedium` and `bodySmall` to
differ by 62%) — reserve it for the top of a display/marketing scale, use a
tighter ratio (1.125–1.25) for the UI-density steps beneath it.

**Applying it to `AppTypography`**: pick one ratio, generate the scale, then
round to sane `sp` values — don't chase the ratio to the decimal. A scale
that's internally consistent (even a `1.2` scale used cleanly) reads better
than one that hits `1.618` exactly at one step and something else everywhere
else with no stated reason.

---

## Fixing Text Overflow — "Text Hell"

Three behaviors, same as any text-heavy UI — pick deliberately per Text, don't
default to whichever one happens not to crash:

| Behavior | Compose API | Use when |
|---|---|---|
| Wrap | default `Text()` behavior | Body copy, anywhere multi-line is expected and there's room |
| Truncate (single line) | `maxLines = 1, overflow = TextOverflow.Ellipsis` | Labels, list-item titles, table cells with fixed available width |
| Truncate (multi-line) | `maxLines = 2, overflow = TextOverflow.Ellipsis` | Card titles, previews — 2-3 lines then cut |
| Wrap then truncate | `maxLines = N, overflow = TextOverflow.Ellipsis` | Same as above, just naming the combined case explicitly |

```kotlin
// Truncated single-line label — the common "text hell" fix
Text(
    text = itemTitle,
    maxLines = 1,
    overflow = TextOverflow.Ellipsis,
    modifier = Modifier.weight(1f),   // shares remaining row width, doesn't hardcode it
)
```

**Never truncate without a way to read the full text.** A tooltip, a detail
screen, or an expand toggle — silently cutting text with no recovery path is
an accessibility and usability failure, not just a visual one.

**Line height, dense UI vs. long-form** — verified against real typography
guidance: **1.4–1.5×** font size for dense UI copy (table cells, form labels,
list items — vertical space is scarce and text runs short anyway), **1.6×**
for long-form body/article text where reading rhythm matters more than
density. `AppTypography`'s `bodyLarge`/`bodyMedium` steps above already sit
in the 1.4–1.5 range — that's correct for UI copy; don't blanket-raise every
line height to 1.6 assuming "more is safer."

**Line length** — verified: **50–75 characters per line** is the readable
range for body text (66 CPL is the commonly-cited sweet spot), narrower
(30–50 CPL) on mobile. In Compose, bound a body-text container's width
(`Modifier.widthIn(max = ...)`, sized to roughly 70 characters at the current
font) rather than letting it stretch full-bleed across a wide desktop/tablet
layout — full-width body text on a large screen is exactly the "line too
long, eye loses its place" failure this range exists to prevent.

---

## i18n Text Expansion — the Layout-Breaking Case

**Real, verified numbers, not a hunch**: translated strings are almost always
longer than English, and short strings expand the *most proportionally* —
a button label often expands more than a paragraph does:

| English | Translation | Expansion |
|---|---|---|
| "Save" (4 chars) | German "Speichern" (10 chars) | +150% |
| "Save" (4 chars) | French "Enregistrer" (12 chars) | +200% |
| "Save" (4 chars) | Finnish "Tallenna" (8 chars) | +100% |

**Design rule of thumb, verified**: size UI for strings up to **2× the
English original's length** — a button/label sized to fit its English text
exactly will overflow the moment the locale changes, and by then it's
shipped.

**CJK is the opposite failure mode** — Chinese/Japanese/Korean translations
are often *shorter* than English. A layout only tuned for expansion leaves
CJK labels floating in too much empty space, looking disconnected from their
container.

**Compose-specific fixes**:
- Never size a `Text`-containing `Row`/`Box` with a fixed `Modifier.width(Dp)`
  around translatable text — use `Modifier.weight(1f)` or `wrapContentWidth()`
  plus `widthIn(min = ...)` so the container grows with the string instead of
  clipping it.
- Prefer `overflow = TextOverflow.Ellipsis` with a sane `maxLines` as the
  fallback for the cases 2× sizing still doesn't cover (some Finnish compound
  words genuinely don't fit anywhere reasonable) — don't rely on manual sizing
  alone to prevent every overflow.
- Test with a pseudolocale before real translations arrive — a build variant
  or debug flag that renders every string artificially lengthened (roughly
  the 2× rule above) surfaces fixed-width assumptions long before a real
  translator's string does.
- RTL (Arabic, Hebrew): Compose's layout direction follows `LocalLayoutDirection`
  automatically for most built-ins, but a custom `Row`/`Modifier.padding` with
  hardcoded `start`/`end` already RTL-aware — auditing for hardcoded `left`/
  `right` (not `start`/`end`) is the actual thing to check, not a redesign.

---

## Related Skills

- `kmp-shared-resources` — owns the actual string catalog these length
  numbers apply to; this doc's job is layout resilience to what that catalog
  contains, not string management itself
- `kmp-compose-accessibility` — text scaling for accessibility (system font
  size up to 200%) is a related but distinct resilience case — same "don't
  hardcode a size that assumes one string length" principle, different cause
- `kmp-compose-adaptive-layout` — width-class breakpoints intersect with line
  length; a body-text column that's correctly bounded on Compact can still
  need the same `widthIn(max = ...)` cap on Expanded

---

## Sources

- [Figma — The Golden Ratio](https://www.figma.com/resource-library/golden-ratio/)
- [NN/g — The Golden Ratio and User-Interface Design](https://www.nngroup.com/articles/golden-ratio-ui-design/)
- [UXPin — Optimal Line Length for Readability](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/)
- [SimpleLocalize — Why text expansion breaks your UI and how to fix it](https://simplelocalize.io/blog/posts/text-expansion-ui-localization/)
