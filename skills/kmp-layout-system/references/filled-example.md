# Filled Example

Part of `kmp-layout-system`. Load this file when working on: filled example.

---

The templates above filled in for a generic messaging app (2 screens shown). Note
the second screen doesn't reuse Pattern B's card-grid rects literally — it swaps
them for stacked list rows, since that's what this screen's real content needs.
Templates are a starting shape, not a fixed mold; edit the region rects freely.

**`docs/layout-system/inbox.md`** (Pattern A — nav + thread list + message view)

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 420">
  <rect x="0" y="0" width="64" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="32" y="15">Nav</tspan>
    <tspan x="32" y="33">Chats*</tspan>
    <tspan x="32" y="51">Contacts</tspan>
    <tspan x="32" y="69">Settings</tspan>
  </text>
  <rect x="64" y="0" width="180" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="154" y="13">Thread List</tspan>
    <tspan x="154" y="31">Alice</tspan>
    <tspan x="154" y="49">Bob</tspan>
    <tspan x="154" y="67">Team Alpha</tspan>
  </text>
  <rect x="244" y="0" width="516" height="360" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="502" y="13">Message View</tspan>
    <tspan x="502" y="40">Hey, are you free tonight?</tspan>
    <tspan x="502" y="58">Yeah! What did you have in mind?</tspan>
  </text>
  <rect x="244" y="360" width="516" height="60" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="502" y="390">Type a message...          [Send]</tspan>
  </text>
</svg>

**`docs/layout-system/contacts.md`** (Pattern B — nav + main, Thread List hidden;
card grid swapped for a plain list to fit real content)

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 420">
  <rect x="0" y="0" width="64" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="32" y="24">Nav</tspan>
    <tspan x="32" y="42">Chats</tspan>
    <tspan x="32" y="60">Contacts*</tspan>
    <tspan x="32" y="78">Settings</tspan>
  </text>
  <rect x="64" y="0" width="696" height="40" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="412" y="20">[tab] All    [tab] Favorites    [tab] Groups</tspan>
  </text>
  <rect x="64" y="40" width="696" height="380" fill="white" stroke="#333" stroke-width="1"/>
  <rect x="84" y="60" width="656" height="50" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="412" y="90">Alice Romano — alice@example.com</tspan>
  </text>
  <rect x="84" y="110" width="656" height="50" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="412" y="140">Bob Tanaka — bob@example.com</tspan>
  </text>
  <rect x="84" y="160" width="656" height="50" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="412" y="190">Team Alpha — 3 members</tspan>
  </text>
</svg>

---

## Screen File Format

Each screen file follows this structure:

```
# <Screen name>

## Components

| Component      | Width   | Visible         | Notes                     |
|----------------|---------|-----------------|---------------------------|
| <Component A>  | <N> dp  | <always / when> | <short note>              |
| <Component B>  | flex 1  | Yes             | <short note>              |

---

## <Variant name>

<svg wireframe here>

---

## Interaction notes

- <tap / swipe / gesture> → <what happens>
- <state change> → <how it looks>
```

---
