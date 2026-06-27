---
name: kotlin-multiplatform-layout-system
description: >-
  Drafts and documents screen layouts for any KMP consumer project. Creates
  docs/layout-system/ with one markdown file per screen — each file has a component
  table and an ASCII wireframe. A shared _components.md holds the project-wide
  component registry. Use this skill whenever a new screen is being designed, an
  existing screen changes, a layout review is requested, or a project has no
  layout-system docs yet. Trigger proactively on any new project or new screen —
  layout-system docs should exist before or alongside implementation, not after.
  Trigger keywords: layout system, screen layout, wireframe, layout spec, layout docs,
  draft screen, add screen layout, document layout, layout-system, component layout,
  screen wireframe, layout diagram, screen structure, layout missing, no layout docs,
  create layout, update layout, design screen, sketch layout, plan screen.
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
    - layout draft
    - layout diagram
---

## Purpose

This skill drafts and documents app screens — it is a **living spec**, not a constraint.
Wireframes here describe intent before (or alongside) implementation. They are updated
as the design evolves, not frozen once written.

Use this skill to:
- Sketch a new screen before writing a single line of Compose
- Record what a screen looks like after a layout change
- Give the team a shared visual reference that lives in the repo

Do NOT use this skill for Compose implementation — use `kotlin-multiplatform-adaptive-layout`
for breakpoint-driven responsive layouts.

**Freshness rule:** recheck wireframes whenever a panel is added or removed, navigation
chrome changes (e.g. bottom bar replaces NavRail on phone), or a modal becomes a full screen.

---

## When to Use This Skill

- New screen being designed — draft before or alongside implementation
- Existing screen layout changes
- Layout review or audit requested
- Project has no `docs/layout-system/` yet

**Trigger automatically on project setup.** If the directory is missing, create it before
finishing any screen implementation task.

**Trigger keywords:** layout system, screen layout, wireframe, layout spec, draft screen,
document layout, layout diagram, sketch layout, plan screen, no layout docs.

---

## Directory Structure

```
docs/layout-system/
├── _components.md        <- shared component registry (read this first)
├── home.md
├── jobs.md
├── settings.md
└── <screen-name>.md      <- one file per distinct screen
```

Naming rules:
- Directory: `docs/layout-system/` (kebab-case)
- Screen files: kebab-case, named after the screen
- `_components.md` uses a leading underscore so it sorts first

---

## Bootstrap (project has no layout-system yet)

When `docs/layout-system/` does not exist:

1. Create the directory.
2. Create `_components.md` from the Component Registry format below.
3. Create one screen file per major screen already in the project.
4. Link to `docs/layout-system/` from `docs/architecture.md` or `README.md`.

---

## `_components.md` — Component Registry

```markdown
# Component Registry

Update this file when a component's dimensions, visibility, or behavior changes.

| Component   | Width / Height | Visibility             | Notes                       |
|-------------|----------------|------------------------|-----------------------------|
| NavRail     | 52 dp          | Always visible         | Icon-only. Emoji in legend. |
| ModePanel   | 180 dp         | Home only              | Hidden on all other screens.|
| BottomBar   | full / 56 dp   | Phone (Compact) only   | Replaces NavRail on phone.  |
| Toolbar row | full / 48 dp   | Context-dependent      | Mode-specific action row.   |
| Input bar   | full / 56 dp   | Always visible (chat)  | Single row. Send on Enter.  |
| Sheet       | modal          | Overlay — no swap      | Help and Settings only.     |
```

---

## ASCII Wireframe Format

### Rules

- **No emoji inside the grid.** Emoji are double-width in monospace fonts and break
  alignment. Use short `[label]` placeholders inside the grid. Map labels to emoji
  in a **Legend** line directly below the wireframe.
- Active nav item: append `*` to the label — e.g. `[home]*`.
- Borders: `+` at corners/intersections, `-` horizontal, `|` vertical. ASCII only.
- All rows in a wireframe must be the **same character width**.
- Sub-region breaks (toolbar, input bar): use `|---|` only on the column being split.
  Columns that are not split keep `|   |` on that row.
- Column widths are fixed per wireframe. Pick widths that reflect proportions and
  stay consistent across all rows, then stick to them.

### Standard column widths — 78 chars total

```
+------------+--------------+------------------------------------------------+
  12 inner      14 inner        48 inner
```

- NavRail: 12 inner chars (14 with both `|`)
- ModePanel: 14 inner chars (15 with right `|`)
- Canvas: 48 inner chars (49 with right `|`)
- Total: 1 + 12 + 1 + 14 + 1 + 48 + 1 = **78**

When ModePanel is hidden, canvas expands: 1 + 12 + 1 + 62 + 1 = **77**.
(Adjust the canvas width to keep all rows the same length.)

---

## Wireframe Templates

### Three-column — NavRail + ModePanel + Canvas

```
+------------+--------------+------------------------------------------------+
| NavRail    | ModePanel    | Chat Canvas                                    |
| 52 dp      | 180 dp       | flex 1                                         |
+------------+--------------+------------------------------------------------+
|            |              |                                                |
| [home]*    | Image        | [bubble] Hello, create a video                 |
|            | Video        | [bubble] Sure! Pick a style:                   |
|            | Short        |   [card] Cinematic   [card] Anime              |
|            | Voice        |                                                |
|            | Text         |                                                |
|            |              |                                                |
|            |              |------------------------------------------------|
| [help]     |              | [Model v]  [Style v]  [Ratio v]                |
| [settings] |              |------------------------------------------------|
|            |              | [ Type a prompt...              ]  [Send]      |
+------------+--------------+------------------------------------------------+
Legend: [home] = Home  [help] = Help / FAQ  [settings] = Settings
        * = active
```

### Two-column — NavRail + Canvas (ModePanel hidden)

```
+------------+--------------------------------------------------------------+
| NavRail    | Artifacts Canvas                                             |
| 52 dp      | flex 1  (ModePanel not rendered)                             |
+------------+--------------------------------------------------------------+
|            |                                                              |
| [home]     | [tab] All  [tab] Images  [tab] Video  [tab] Audio  [tab] +   |
|            +--------------------------------------------------------------+
| [jobs]*    |                                                              |
|            |  +--------+  +--------+  +--------+  +--------+              |
|            |  |        |  |        |  | ~~~~~~ |  |  [>]   |              |
|            |  +--------+  +--------+  +--------+  +--------+              |
|            |  image        image        audio       video                 |
|            |  2 min ago    5 min ago    12 min ago  1 hr ago              |
|            |                                                              |
| [help]     |                                                              |
| [settings] |                                                              |
+------------+--------------------------------------------------------------+
Legend: [home] = Home  [jobs] = Jobs / Artifacts  [help] = Help / FAQ
        [settings] = Settings  * = active
```

### Modal sheet overlay

```
+------------+--------------------------------------------------------------+
| NavRail    | [canvas stays in place — no swap]                            |
| 52 dp      |                                                              |
+------------+--------------------------------------------------------------+
|            |                                                              |
| [home]     |     +----------------------------------------------+         |
|            |     | Help / FAQ                                 X |         |
| [jobs]     |     | -------------------------------------------- |         |
|            |     | Getting started                              |         |
| [help]*    |     | Connecting to your server                    |         |
| [settings] |     | Modes: Image / Video / Short                 |         |
|            |     +----------------------------------------------+         |
+------------+--------------------------------------------------------------+
Legend: [home] = Home  [jobs] = Jobs / Artifacts  [help] = Help / FAQ
        [settings] = Settings  * = active
```

---

## Screen File Format

Each screen file has four sections: **Components table**, **Wireframe(s)**,
and **Interaction notes**. Example:

---

**`# Home screen`**

**`## Components`**

| Component   | Width   | Visible | Notes                      |
|-------------|---------|---------|----------------------------|
| NavRail     | 52 dp   | Yes     | Icon-only.                 |
| ModePanel   | 180 dp  | Yes     | Creation modes list.       |
| Chat canvas | flex 1  | Yes     | Bubbles + toolbar + input. |
| Toolbar row | full    | Yes     | Mode-specific buttons.     |
| Input bar   | full    | Yes     | Always-on. Send on Enter.  |
| Sheet       | modal   | On tap  | Overlay — no canvas swap.  |

**`## Default — creation mode active`**

```
+------------+--------------+------------------------------------------------+
| NavRail    | ModePanel    | Chat Canvas                                    |
| 52 dp      | 180 dp       | flex 1                                         |
+------------+--------------+------------------------------------------------+
|            |              |                                                |
| [home]*    | Image        | [bubble] Hello, create a video                 |
|            | Video        | [bubble] Sure! Pick a style:                   |
|            | Short        |   [card] Cinematic   [card] Anime              |
|            | Voice        |                                                |
|            | Text         |                                                |
|            |              |                                                |
|            |              |------------------------------------------------|
| [help]     |              | [Model v]  [Style v]  [Ratio v]                |
| [settings] |              |------------------------------------------------|
|            |              | [ Type a prompt...              ]  [Send]      |
+------------+--------------+------------------------------------------------+
Legend: [home] = Home  [help] = Help / FAQ  [settings] = Settings
        * = active
```

**`## Interaction notes`**

- Tapping a ModePanel item switches the toolbar row — canvas does not reload.
- [help] and [settings] open a bottom sheet overlay. Canvas stays in place.
- Input bar is always visible; toolbar row appears only when a mode is selected.
- NavRail active state: append `*` to the label in the wireframe.

---

## Validation Checklist

| Check | Expected |
|---|---|
| `_components.md` updated | Any new or changed component appears in the registry |
| Screen file exists | One `.md` per screen |
| No emoji in grid | All emoji are in the Legend line below the wireframe |
| Active state shown | Active nav item uses `*` suffix, e.g. `[home]*` |
| All rows same width | Longest and shortest row in the wireframe are identical |
| Sub-region dividers | `|---|` only on the column being split; others show `|   |` |
| Variants present | Separate wireframe block per layout variant (modal, empty state, etc.) |
| Interaction notes | Each screen file ends with a short notes section |

---

## Related Skills

- `kotlin-multiplatform-adaptive-layout` — Compose implementation of breakpoint-driven
  layouts (Compact/Medium/Expanded). Layout-system docs describe intent; this skill
  implements it.
- `kotlin-multiplatform-design-system` — Design tokens, colors, and typography used
  by the components listed in `_components.md`.
- `kotlin-multiplatform-project-docs-maintainer` — Keeps `docs/` healthy. Layout-system
  files follow the same kebab-case and line-limit hygiene rules.

---

## Changelog

| Date | Change |
|---|---|
| 2026-06-27 | Reframed as a draft/document tool, not an enforcement layer. Fixed ASCII wireframe: removed emoji from grid, added Legend line below wireframes, fixed all row widths to 78 chars, replaced partial `+---+` dividers with `\|---\|` style. |
| 2026-06-27 | Initial release — layout system format, ASCII wireframe spec, component registry, screen file template, bootstrap flow. |
