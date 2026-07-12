---
name: kotlin-multiplatform-shadcn-compose
description: >
  Consumes the published shadcn-compose library (io.github.ronjunevaldoz:shadcn-compose) —
  a shadcn/ui-inspired Compose Multiplatform component library with 70+ components. Covers
  Maven Central setup, the required @OptIn(ExperimentalFoundationStyleApi::class), the
  ShadcnTheme wrapper and its preset/baseColor/accent/isDark/baseRadius/ring parameters, and
  real component usage (ShadcnButton, ShadcnCard, etc.) verified against the library's own
  source. Alternative to kotlin-multiplatform-design-system's generated/owned approach — not
  both in the same project. Carries a real risk this skill exists specifically to disclose:
  a hard dependency on the experimental Compose Foundation Styles API that can break on any
  CMP upgrade, with no fix available except an upstream shadcn-compose release.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-07-12'
  keywords:
    - shadcn-compose
    - ShadcnButton
    - ShadcnTheme
    - ShadcnCard
    - shadcn ui kotlin
    - ExperimentalFoundationStyleApi
    - shadcn kmp
    - shadcn compose multiplatform
---

## When to Use This Skill

Use only when:
- The project's `/kmm-new-project` Step 6a design draft chose the shadcn-compose component
  library option (not the default owned scaffold), or
- The user explicitly asks to add shadcn-compose to an existing project, having accepted
  the experimental-API risk

**Never combine with `kotlin-multiplatform-design-system`.** They are alternative component
sources for the same layer — pick one.

**Actually adding this dependency requires explicit user choice** — via `/kmm-new-project`
Step 6a, `/kmm-migrate-to-shadcn`, or an equivalent direct confirmation. Never add it
silently.

**Mentioning a specific `Shadcn*` component as an option is fine, even in a project that
doesn't use this library yet** — for example, a layout-quality finding (mixed flat/card/
tabbed patterns across screens, per `scan_design_violations.py`'s `layout_inconsistency`
check) may suggest the matching component (`ShadcnTabsList`, `ShadcnItem`/`ShadcnItemGroup`,
etc.) as one option alongside consolidating to the project's existing pattern manually.
**Every such suggestion must state the experimental-API risk inline, in the same
message** — never a bare "use ShadcnTabsList" with the risk left for the user to discover
later. `kotlin-multiplatform-design-system`'s Ownership Model exists specifically to avoid
this risk (a hard dependency on `@OptIn(ExperimentalFoundationStyleApi::class)`, an actual
Jetpack Compose Foundation experimental annotation the Compose team can change or remove in
any release) — a suggestion that omits it isn't a complete recommendation.

**Trigger keywords:** shadcn-compose, ShadcnButton, ShadcnTheme, ShadcnCard, shadcn ui
kotlin, shadcn compose multiplatform, ExperimentalFoundationStyleApi, shadcn kmp.

**Freshness rule:** this library is young and moves fast — three releases (`0.1.0` →
`0.2.0` → `0.2.1`) shipped within 3 days of each other during this skill's own research.
Recheck [the README](https://github.com/ronjunevaldoz/shadcn-compose#readme) and
[Maven Central's actual repository](https://repo1.maven.org/maven2/io/github/ronjunevaldoz/shadcn-compose/)
directly — not `search.maven.org`, which lagged the real publish by over a day when
verified — before pinning a version.

---

## Recommendation First

Default to `kotlin-multiplatform-design-system` unless the user has explicitly chosen this
library and confirmed they accept the experimental-API risk (see
`kotlin-multiplatform-design-system`'s Ownership Model note, and the warning-gated Step 6a
flow in `/kmm-new-project`).

Why:
- `ExperimentalFoundationStyleApi` (`androidx.compose.foundation.style`) is a real Jetpack
  Compose Foundation experimental annotation — not something this library controls. A
  future Compose release can change or remove it with no migration path except waiting for
  shadcn-compose itself to catch up.
- This is a real dependency, not generated code — a CMP upgrade that breaks the
  experimental API breaks your build until shadcn-compose ships a compatible release,
  whereas the owned scaffold in `kotlin-multiplatform-design-system` stays on your own
  upgrade schedule.
- Once genuinely chosen (faster start, 70+ components, real published maintenance), use it
  as documented below — this skill isn't gatekeeping the choice, just making sure it's made
  with the risk visible.

---

## Prerequisites

- Project scaffolded with `kotlin-multiplatform-feature-scaffold`
- The `/kmm-new-project` Step 6a component-library choice was shadcn-compose, with the
  second confirmation given — or the user has otherwise explicitly accepted the
  experimental-API risk
- Compose Multiplatform 1.11.1+ / Kotlin 2.4.0+ (matches this library's own CI pin —
  recheck the README before assuming an older toolchain works)

---

## Step 1: Gradle setup

```toml
# gradle/libs.versions.toml
[versions]
shadcn-compose = "0.2.1"

[libraries]
shadcn-compose = { module = "io.github.ronjunevaldoz:shadcn-compose", version.ref = "shadcn-compose" }
```

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.shadcn.compose)
        }
    }
}
```

Every file that references a component's `style` parameter needs the opt-in:

```kotlin
@file:OptIn(ExperimentalFoundationStyleApi::class)
```

**Do not also load `kotlin-multiplatform-design-system` in the same project** — the two are
alternative component sources for the same layer.

---

## Step 2: Theme setup

Wrap the app root in `ShadcnTheme` — verified against the library's real source
(`shadcn/core/.../theme/ShadcnTheme.kt`), not assumed:

```kotlin
import io.github.ronjunevaldoz.shadcncompose.theme.ShadcnTheme
import io.github.ronjunevaldoz.shadcncompose.tokens.ShadcnStylePreset
import io.github.ronjunevaldoz.shadcncompose.tokens.ShadcnBaseColor
import io.github.ronjunevaldoz.shadcncompose.tokens.ShadcnAccent
import androidx.compose.foundation.isSystemInDarkTheme

@Composable
fun App() {
    ShadcnTheme(
        preset = ShadcnStylePreset.Vega,   // default — real shadcn/ui also ships other presets
        baseColor = ShadcnBaseColor.Neutral,
        accent = ShadcnAccent.Base,
        isDark = isSystemInDarkTheme(),
    ) {
        // app content
    }
}
```

`ShadcnTheme` also accepts `baseRadius` (default `6.dp`) and `ring` (defaults to the
preset's own ring) if the project needs a different corner radius or focus-ring style than
the chosen preset ships.

### Picking a preset by app vibe

`ShadcnStylePreset` isn't a cosmetic label — each value carries a real, documented
personality (shape, spacing, animation timing, icon weight), verified against
`ShadcnStylePreset.kt`'s own KDoc:

| Preset | Documented personality | Fits |
|---|---|---|
| `Vega` | "Clean, neutral, and familiar" — balanced default | General-purpose, e-commerce, finance |
| `Nova` | "Reduced padding and margins," snappy, ultra-tight | Productivity tools, dense utility apps |
| `Maia` | "Rounded, with generous spacing," fluid and bouncy | Social, community, consumer/playful apps |
| `Lyra` | "Boxy and sharp. For mono fonts," blueprint aesthetic | Developer tools, technical/admin apps |
| `Mira` | "Made for compact interfaces," tightest timings | Dense dashboards, data-heavy screens |
| `Luma` | "Fluid, luminous, and soft," slow elegant fades | Wellness, travel, lifestyle, premium feel |
| `Sera` | "Editorial and typographic" | Content/reading apps, education |
| `Rhea` | Luma's softness, Nova's compactness | Soft aesthetic that still needs density |

`ShadcnBaseColor` (`Neutral`, `Stone`, `Zinc`, `Mauve`, `Olive`, `Mist`, `Taupe`) is the
neutral gray family for background/foreground/border — `Neutral` is a safe default;
`Stone` (warm) and `Zinc` (cool) are the two with an unambiguous undertone, useful when
the app's existing palette leans warm or cool. `ShadcnAccent` has 18 real named colors
(`Amber`, `Blue`, `Cyan`, `Emerald`, `Fuchsia`, `Green`, `Indigo`, `Lime`, `Orange`,
`Pink`, `Purple`, `Red`, `Rose`, `Sky`, `Teal`, `Violet`, `Yellow`, plus `Base` for no
override) — pick whichever matches the project's already-chosen brand accent by name.

`/kmm-new-project` Step 6a-ii runs this exact inference automatically from the project's
app type, using the same app-type category as the color-palette draft, and confirms the
choice with the user before generating — don't skip that confirmation when adding this
library outside the new-project flow either; always present the inferred preset/base
color/accent as a recommendation, not a silent default.

### Suggesting a component for a layout-quality problem

When an audit finds a genuine layout smell, the matching component below is worth
mentioning as one option — regardless of whether the project uses shadcn-compose yet —
**as long as the experimental-API risk is stated in the same message**:

| Layout smell (existing detector) | Suggested component |
|---|---|
| Mixed flat/card/tabbed patterns across screens (`scan_design_violations.py`'s `layout_inconsistency`, majority `tabbed`) | `ShadcnTabsList` |
| Same, majority `card` | `ShadcnCard` (consistent header/content/footer slots) |
| Same, majority `flat` | `ShadcnItem`/`ShadcnItemGroup` |
| Ad-hoc empty states with no consistent pattern | `ShadcnEmpty` |
| Ad-hoc multi-pane/split layouts | `ShadcnResizablePanelGroup` |
| Ad-hoc data grids | `ShadcnTable` |

This is a suggestion, not an instruction — the fix that doesn't add a new dependency
(consolidating to the project's own existing pattern) is still valid and often the
right call for a project not otherwise considering shadcn-compose. Present both options
when a layout-quality finding fires; don't default to only the shadcn-compose one.

---

## Step 3: Using components

### The one rule that matters more than any example below

**Never call a `Shadcn*` component with a parameter you haven't verified exists on its
real signature.** Do not assume a parameter exists by analogy to Jetpack Compose's own
`TextField`/Material components, to HTML/CSS attributes, or to another `Shadcn*`
component's shape — every component here has its own specific, independently-designed
API. Two confirmed, real examples of what guessing produces, found by fetching the
actual source rather than trusting a table like the one below:

- `ShadcnTextField` has **no `singleLine` parameter** — a real project's implementation
  used `singleLine = false` (a real Compose `TextField`/`BasicTextField` parameter,
  assumed to carry over) and it would not compile. The real multi-line component is the
  separate `ShadcnTextarea` (see below) — not a parameter toggle on `ShadcnTextField`.
- The component commonly assumed to be `ShadcnTabs` is actually named **`ShadcnTabsList`**
  — this skill's own component table said `ShadcnTabs` until this was checked against
  the real source.

Before writing a call to any component **not** shown with a verified signature below,
fetch the real one first — one command, no need to remember the file path or grep
pattern by hand:
```bash
python3 skills/kotlin-multiplatform-shadcn-compose/scripts/fetch_component_signature.py <ComponentName>
```
It handles the two cases that break a naive lookup: a component living in a
differently-named file (checks the obvious filename first, then searches every
component file), and nested parens in a default value (uses a balanced-paren scan, not
a single-level regex, so the signature isn't truncated early). Or, if the project
already resolves the dependency, read it directly from the Gradle cache / IDE-decompiled
sources. Never skip this to save a lookup — a wrong guess costs more time than the
lookup would have.

### Verified signatures (checked against real source, 2026-07-12)

```kotlin
ShadcnButton(onClick = {}) { ShadcnText("Click me") }
ShadcnButton(onClick = {}, variant = ButtonVariant.Outline, size = ButtonSize.Sm) { ShadcnText("Outline") }
ShadcnButton(onClick = {}, variant = ButtonVariant.Destructive) { ShadcnText("Delete") }
// ButtonVariant: Default | Outline | Secondary | Ghost | Destructive | Link — 6 variants, 5 sizes

ShadcnTextField(value = text, onValueChange = { text = it }, placeholder = "Email")
// value, onValueChange, modifier, enabled, label, placeholder, leadingIcon, trailingIcon,
// isError, supportingText, variant, style, keyboardOptions, keyboardActions, visualTransformation
// NO singleLine parameter — this is a single-line-only field by design.

ShadcnTextarea(value = prompt, onValueChange = { prompt = it }, placeholder = "Describe the scene")
// value, onValueChange, modifier, enabled, label, placeholder, isError, supportingText,
// variant, style, keyboardOptions, keyboardActions — the multi-line equivalent of
// ShadcnTextField above; wraps it internally. Use this for an HTML wireframe's <textarea>,
// never ShadcnTextField with a guessed multi-line parameter.

ShadcnSelect(value = selected, options = listOf("A", "B"), onValueChange = { selected = it }, label = { it })
// fun <T> ShadcnSelect(value: T?, options: List<T>, onValueChange: (T) -> Unit, modifier,
// label: (T) -> String = { it.toString() }, placeholder: String, variant, style, icon)

ShadcnCard(header = { ShadcnCardHeader(title = "Title") }) { ShadcnText("Body content") }
// fun ShadcnCard(modifier, variant, size, style, header: (@Composable () -> Unit)?,
// footer: (@Composable () -> Unit)?, content: @Composable ColumnScope.() -> Unit)
// Slot-based — header/footer are optional composable slots, not string parameters.
// ShadcnCardHeader(title, description, action, modifier) is a separate helper composable.

ShadcnCheckbox(checked = isChecked, onCheckedChange = { isChecked = it })
// checked, onCheckedChange: ((Boolean) -> Unit)?, modifier, indeterminate, enabled, style

ShadcnSwitch(checked = isOn, onCheckedChange = { isOn = it })
// checked, onCheckedChange: ((Boolean) -> Unit)?, modifier, enabled, style

ShadcnAvatar { ShadcnAvatarFallback("JD") }
// fun ShadcnAvatar(modifier, size: ShadcnAvatarSize, content: @Composable BoxScope.() -> Unit)
// Slot-based, with separate companion composables: ShadcnAvatarFallback(text, modifier),
// ShadcnAvatarBadge(modifier), ShadcnAvatarGroup(modifier) { content }.

ShadcnTabsList(items = tabItems, selected = selectedId, onSelectedChange = { selectedId = it })
// NOT "ShadcnTabs" — items: List<ShadcnTabItem>, selected: String, onSelectedChange: (String) -> Unit, modifier
```

See the
[component catalog](https://github.com/ronjunevaldoz/shadcn-compose/blob/main/docs/components.md)
for the full 70+ component list; each entry links to a live usage page in the library's own
catalog app (`app/shared/.../catalog/docs/*Doc.kt`) — treat that catalog app as the
authoritative usage reference for anything not verified above, not a guess from the name
alone.

No icon-library dependency exists — every component draws from this library's own tokens,
not `heroicons-compose` or any other icon package. An icon needed in a screen built with
these components must come from a separate source (`kotlin-multiplatform-imagevector-generator`
or a third-party Compose icon library) — this is a real gap to plan for, not an oversight
to work around with a guessed API.

---

## Testing

No tests to write for the library itself — it's an external dependency, and its own CI
already covers it. For screens built with these components, use
`kotlin-multiplatform-roborazzi`'s screenshot-testing pattern the same as any other Compose
UI; nothing shadcn-compose-specific changes that workflow.

---

## Common Anti-Patterns

- combining this skill with `kotlin-multiplatform-design-system` in the same project — pick one component source, never both
- adding this dependency without the user having seen the experimental-API warning — route through `/kmm-new-project` Step 6a or get explicit confirmation first
- forgetting `@OptIn(ExperimentalFoundationStyleApi::class)` on a file that references a component's `style` parameter — a compile error, not a runtime issue, but confusing without knowing the cause
- pinning a version from `search.maven.org` — it lagged the real Maven Central publish by over a day when verified; check `repo1.maven.org` or the README directly
- assuming heroicons-compose integration exists — this library explicitly has "no icon-library dependency"; every component draws from its own tokens
- treating this as a stable, slow-moving dependency — 3 releases shipped in 3 days during this skill's own research; recheck before every use, not just once
- suggesting a `Shadcn*` component for a layout-quality finding without stating the experimental-API risk in the same message — a suggestion that omits it isn't complete, even if it's "just an option"
- suggesting a `Shadcn*` component as the *only* fix for a layout-quality finding — the no-new-dependency fix (consolidate to the project's existing pattern) is still valid and should be presented alongside it, not replaced by it
- assuming a component's parameter exists by analogy to Jetpack Compose's own Material components (e.g. `singleLine` on a text field) — every `Shadcn*` component has its own independently-designed API; a real project's implementation used a hallucinated `singleLine` parameter on `ShadcnTextField` that doesn't exist
- guessing a component's top-level name from a pattern (e.g. assuming "ShadcnTabs" because `ShadcnButton`/`ShadcnCard` follow that shape) instead of checking the real source — the real name is `ShadcnTabsList`, found only by verifying, not by pattern-matching against other components in the same family

---

## Output Style

When asked to add or use shadcn-compose, respond in this order:
1. Confirm the choice was made deliberately (via `/kmm-new-project` Step 6a or explicit
   request) and the experimental-API risk was seen — ask if unclear, don't add it silently
2. Gradle setup (version catalog entry + dependency)
3. `ShadcnTheme` wrapper at the app root
4. The specific component(s) requested, with the exact variant/size parameters needed
5. Note the `@OptIn(ExperimentalFoundationStyleApi::class)` requirement on any new file

---

## Related Skills

- `kotlin-multiplatform-design-system` — the default, owned-scaffold alternative this skill exists to be compared against; see its Ownership Model note for the full risk tradeoff
- `kotlin-multiplatform-feature-scaffold` — project must be scaffolded first
- `kotlin-multiplatform-roborazzi` — screenshot-test screens built with these components the same as any other Compose UI
- `/kmm-migrate-to-shadcn` — the file-by-file migration path from an existing `kotlin-multiplatform-design-system` project to this library, with the full `App*`→`Shadcn*` mapping table

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-12 | Fixed two real bugs found in a consumer project's implementation, both from this skill's own incomplete verification: `ShadcnTextField` was called with a hallucinated `singleLine` parameter (doesn't exist — real multi-line component is the separate `ShadcnTextarea`), and this skill's own component table said `ShadcnTabs` when the real name is `ShadcnTabsList` (also wrong in `scan_design_violations.py`'s layout-quality suggestion, now fixed with a regression test). Rewrote Step 3 with 9 signatures verified directly against real source (Button, TextField, Textarea, Select, Card+CardHeader, Checkbox, Switch, Avatar+companions, TabsList) and a mandatory rule: never call a component with a parameter not verified against its real signature, with the fetch command to do that verification. Added `scripts/fetch_component_signature.py` — turns that verification from a manual GitHub lookup into one command; handles a component living in a differently-named file (checks the obvious filename first, then searches every component file) and nested parens in a default value (balanced-paren scan, not a single-level regex). Verified 6 more signatures with it (Checkbox, RadioGroup/RadioButton, Slider, Table, Dialog) to expand `kotlin-multiplatform-layout-system`'s HTML mapping table. 2 new anti-patterns, 3 new script regression tests. |
| 2026-07-11 | Initial release — Maven Central setup, `ShadcnTheme` wrapper (verified against real source), component usage (verified against real KDoc examples), and the experimental-API risk this skill exists specifically to disclose rather than hide. Gated to explicit user choice via `/kmm-new-project` Step 6a, never suggested unprompted. Added "Picking a preset by app vibe" — full `ShadcnStylePreset`/`ShadcnBaseColor`/`ShadcnAccent` reference (verified against their own KDoc/source), and wired `/kmm-new-project` Step 6a-ii to auto-infer a preset/base color/accent recommendation from the same app-type category as the color-palette draft, always confirmed before generating, never a silent default. Added `/kmm-migrate-to-shadcn` — a full `App*`→`Shadcn*` migration command for existing design-system projects, with an honest mapping table (verified against the real component catalog, not assumed 1:1 parity) flagging the components with no direct equivalent (`AppScaffold`, `AppTopAppBar`, `AppNavigationBar`, `AppIcon`, `AppIconButton`) for explicit user decision rather than a guessed replacement. Wired `scan_design_violations.py`'s `layout_inconsistency` finding to suggest a matching `Shadcn*` component (`ShadcnTabs`/`ShadcnCard`/`ShadcnItem`) as an option regardless of whether the project uses shadcn-compose yet — every such suggestion states the experimental-API risk inline, and is presented alongside (never instead of) the no-new-dependency fix. |
