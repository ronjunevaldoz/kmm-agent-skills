---
name: kotlin-multiplatform-layout-system
description: >-
  Creates and maintains a docs/layout-system/ directory in any KMP consumer project.
  Each screen gets its own markdown file with a component table and ASCII wireframe.
  A shared _components.md holds the project-wide component registry. Use this skill
  whenever a new screen is added, an existing screen's layout changes, a layout review
  is requested, or a project has no layout-system docs yet. Trigger proactively on
  project setup — every project should have this. Trigger keywords: layout system,
  screen layout, wireframe, layout spec, layout docs, add screen layout, document layout,
  layout-system, component layout, screen wireframe, layout diagram, screen structure,
  layout missing, no layout docs, create layout, update layout.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-27'
  keywords:
    - layout system
    - wireframe
    - screen layout
    - ASCII wireframe
    - component registry
    - layout spec
    - docs layout-system
    - screen structure
    - layout docs
    - layout diagram
---

## When to Use This Skill

Use whenever you:
- Add a new screen to a KMP project
- Change an existing screen's layout (panels added/removed, nav changes, modal added)
- Are asked to review, document, or audit screen layouts
- Set up a project that has no `docs/layout-system/` yet

**Trigger automatically on project setup** — every project should have this directory.
If it is missing, create it before finishing any screen implementation task.

Do NOT use this skill for:
- Compose implementation details (use `kotlin-multiplatform-adaptive-layout` for breakpoint-driven responsiveness)
- Design tokens or theming (use `kotlin-multiplatform-design-system`)

**Freshness rule:** this skill produces static markdown — no library versions to track.
Recheck the ASCII format rules if the project's screen topology changes significantly
(e.g., bottom bar replaces NavRail on phone, or a new persistent panel is introduced).

---

## Directory Structure

```
docs/layout-system/
├── _components.md        ← shared component registry (always read this first)
├── home.md
├── jobs.md
├── settings.md
└── <screen-name>.md      ← one file per distinct screen
```

**Naming rules:**
- Directory: `docs/layout-system/` (kebab-case)
- Screen files: kebab-case, named after the screen (`jobs.md`, `profile.md`)
- `_components.md` uses a leading underscore so it sorts first

---

## Bootstrap (project has no layout-system yet)

When `docs/layout-system/` does not exist:

1. Create the directory.
2. Create `_components.md` using the Component Registry format below.
3. Create one screen file per major screen already in the project.
4. Link from `docs/architecture.md` or `README.md` if either exists.

---

## File Formats

### `_components.md` — Component Registry

```markdown
# Component Registry

Components shared across screens. Update this file whenever a component's
dimensions, visibility rules, or behavior changes.

| Component     | Width / Height | Visibility              | Notes                        |
|---------------|---------------|-------------------------|------------------------------|
| NavRail       | 52 dp         | Always visible          | Icon-only. Emoji icons.      |
| ModePanel     | 180 dp        | Home only               | Hidden on all other screens. |
| BottomBar     | full / 56 dp  | Phone only              | Replaces NavRail on Compact. |
| Toolbar row   | full / 48 dp  | Context-dependent       | Mode-specific action buttons.|
| Input bar     | full / 56 dp  | Always visible (chat)   | Single row. Send on Enter.   |
| Sheet         | modal         | Overlay — no canvas swap| Help and Settings only.      |
```

### Screen file — `<screen>.md`

Each screen file has three sections:

1. **Components table** — which components are visible and at what size
2. **Wireframe(s)** — one ASCII block per layout variant (default, empty state, modal open, etc.)
3. **Interaction notes** — navigation, gestures, state transitions

---

## ASCII Wireframe Format

### Rules

- Total width: **80 characters** (including the outer `|` borders)
- Borders: `+` at corners and intersections, `-` for horizontal, `|` for vertical
- **No Unicode box-drawing characters** — ASCII only (`+`, `-`, `|`)
- **Emoji allowed** for nav icons and media-type indicators
- Column widths: fixed, must add up to 80 chars including borders
- Header row: always present — shows component name on line 1, size on line 2
- Sub-region break: `+----+` partial divider **only on the column being split**
- Active nav item: `[ * ]` suffix on the same row as the emoji and label
- Inactive nav item: emoji + label only, no suffix

### Column width reference

| Component   | Chars (incl. borders) |
|-------------|----------------------|
| NavRail     | 12                   |
| ModePanel   | 15                   |
| Main canvas | remainder to 80      |

Total: 12 + 15 + 1 (border) + canvas + 1 (border) = 80 → canvas = 51 chars

Adjust when ModePanel is hidden: canvas takes the full 80 − 12 = 68 chars.

### Wireframe template — three-column (NavRail + ModePanel + Canvas)

```
+------------+---------------+---------------------------------------------------+
| NavRail    | ModePanel     | <Canvas Name>                                     |
| 52 dp      | 180 dp        | flex 1                                            |
+------------+---------------+---------------------------------------------------+
|            |               |                                                   |
| 🏠 [ * ]   | Image         | [bubble] User message                             |
|            | Video         | [bubble] Assistant reply                          |
|            | Short         |                                                   |
|            | Voice         |                                                   |
|            | Text          |                                                   |
|            |               |                                                   |
| - - - - -  |               +---------------------------------------------------+
|            |               | [Model v]  [Style v]  [Ratio v]  (toolbar row)    |
| ❓          |               +---------------------------------------------------+
| ⚙️          |               | [ Type a prompt...                    ]  [Send]   |
+------------+---------------+---------------------------------------------------+
```

### Wireframe template — two-column (NavRail + Canvas, ModePanel hidden)

```
+------------+------------------------------------------------------------------+
| NavRail    | <Canvas Name>                                                    |
| 52 dp      | flex 1  (ModePanel not rendered)                                 |
+------------+------------------------------------------------------------------+
|            |                                                                  |
| 🏠          | [tab] All   [tab] Images   [tab] Video   [tab] Audio             |
|            +------------------------------------------------------------------+
| 📦 [ * ]   |                                                                  |
|            |  +----------+  +----------+  +----------+  +----------+         |
|            |  |          |  |          |  |  ~~~~~~  |  |  [>]     |         |
|            |  +----------+  +----------+  +----------+  +----------+         |
|            |  image         image         audio          video                |
| - - - - -  |  2 min ago     5 min ago     12 min ago     1 hr ago             |
|            |                                                                  |
| ❓          |                                                                  |
| ⚙️          |                                                                  |
+------------+------------------------------------------------------------------+
```

### Wireframe template — modal sheet overlay

```
+------------+------------------------------------------------------------------+
| NavRail    | [current canvas stays behind — no swap]                         |
| 52 dp      |                                                                  |
+------------+------------------------------------------------------------------+
|            |                                                                  |
| 🏠          |     +------------------------------------------------+           |
|            |     | Help / FAQ                                   X |           |
| 📦          |     | ---------------------------------------------- |           |
|            |     | Getting started                                 |           |
| ❓ [ * ]   |     | Connecting to your server                       |           |
|            |     | Modes: Image / Video / Short                    |           |
| ⚙️          |     |                                                 |           |
|            |     +------------------------------------------------+           |
+------------+------------------------------------------------------------------+
```

---

## Screen File Example — `home.md`

```markdown
# Home screen

## Components

| Component   | Width   | Visible | Notes                                      |
|-------------|---------|---------|---------------------------------------------|
| NavRail     | 52 dp   | Yes     | Icon-only. Active: 🏠 [ * ]                 |
| ModePanel   | 180 dp  | Yes     | Creation modes list.                        |
| Chat canvas | flex 1  | Yes     | Bubble list + toolbar row + input bar.      |
| Toolbar row | full    | Yes     | Mode-specific buttons above input.          |
| Input bar   | full    | Yes     | Always-on. Send on Enter.                   |
| Sheet       | modal   | On tap  | Help / Settings — overlay, no canvas swap.  |

---

## Default — creation mode active

+------------+---------------+---------------------------------------------------+
| NavRail    | ModePanel     | Chat Canvas                                       |
| 52 dp      | 180 dp        | flex 1                                            |
+------------+---------------+---------------------------------------------------+
|            |               |                                                   |
| 🏠 [ * ]   | Image         | [bubble] Hello, create a video of a sunset        |
|            | Video         | [bubble] Sure! Pick a style:                      |
|            | Short         |   [card] Cinematic   [card] Anime                 |
|            | Voice         |                                                   |
|            | Text          |                                                   |
|            |               |                                                   |
| - - - - -  |               +---------------------------------------------------+
|            |               | [Model v]  [Style v]  [Ratio v]                   |
| ❓          |               +---------------------------------------------------+
| ⚙️          |               | [ Type a prompt...                    ]  [Send]   |
+------------+---------------+---------------------------------------------------+

---

## Interaction notes

- Tapping a ModePanel item switches the toolbar row buttons — canvas does not reload.
- ❓ and ⚙️ open a bottom sheet overlay. Canvas stays in place.
- NavRail active state uses `[ * ]` suffix on the icon row.
- Input bar is always visible; toolbar row appears only when a mode is selected.
```

---

## Validation Checklist

Before finishing any layout-system update, verify:

| Check | Expected |
|---|---|
| `_components.md` updated | Any new or changed component appears in the registry |
| Screen file exists | One `.md` per screen in the project |
| Header row present | Every wireframe has a component-name row and a size row |
| Column widths sum to 80 | Count chars across the widest row |
| No Unicode box chars | Only `+`, `-`, `|` in wireframe borders |
| Active state shown | Active nav item uses `[ * ]` suffix |
| Modal variant present | Any screen with a sheet/dialog has a separate wireframe block |
| Interaction notes | Each screen file has a short notes section |

---

## Related Skills

- `kotlin-multiplatform-adaptive-layout` — use when implementing breakpoint-driven
  Compose layouts (Compact/Medium/Expanded). Layout-system docs describe intent;
  adaptive-layout implements it.
- `kotlin-multiplatform-design-system` — design tokens, colors, typography used
  by the components listed in `_components.md`.
- `kotlin-multiplatform-project-docs-maintainer` — keeps `docs/` structure healthy;
  layout-system files follow the same kebab-case and line-limit rules.

---

## Changelog

| Date | Change |
|---|---|
| 2026-06-27 | Initial release — layout system format, ASCII wireframe spec, component registry, screen file template, bootstrap flow. |
