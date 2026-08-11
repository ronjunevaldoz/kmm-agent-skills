# Wireframe Templates

Part of `kmp-layout-system`. Load this file when working on: wireframe templates.

---

Use whichever pattern matches the screen. Replace every `<placeholder>` with the
project's real component name, size, label, or content — remember to XML-escape
any literal `<`/`>` left in a label (`&lt;`/`&gt;`), same as the templates below.
These are the exact SVGs `create_wireframe.py` generates for each pattern — edit
the `<text>`/`<tspan>` content and `<rect>` geometry in place, don't hand-draw a
new one from scratch.

### Pattern A — narrow nav + secondary panel + main area

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 420">
  <rect x="0" y="0" width="64" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="32" y="15">Nav</tspan>
    <tspan x="32" y="33">nav-1*</tspan>
    <tspan x="32" y="51">nav-2</tspan>
    <tspan x="32" y="69">nav-3</tspan>
    <tspan x="32" y="87">nav-4</tspan>
    <tspan x="32" y="105">nav-5</tspan>
  </text>
  <rect x="64" y="0" width="180" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="154" y="13">Side Panel</tspan>
    <tspan x="154" y="31">&lt;item&gt;</tspan>
    <tspan x="154" y="49">&lt;item&gt;</tspan>
    <tspan x="154" y="67">&lt;item&gt;</tspan>
  </text>
  <rect x="244" y="0" width="516" height="320" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="502" y="151">Main Area</tspan>
    <tspan x="502" y="169">&lt;primary content&gt;</tspan>
  </text>
  <rect x="244" y="320" width="516" height="40" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="502" y="340">&lt;action row&gt;</tspan>
  </text>
  <rect x="244" y="360" width="516" height="60" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="502" y="390">&lt;input area&gt;</tspan>
  </text>
</svg>

`nav-1*` — the trailing `*` marks the active nav item, same convention as before.
Add/remove nav item `<tspan>` lines to match the project's real nav item count.

### Pattern B — narrow nav + main area (secondary panel hidden)

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 420">
  <rect x="0" y="0" width="64" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="32" y="24">Nav</tspan>
    <tspan x="32" y="42">nav-1</tspan>
    <tspan x="32" y="60">nav-2*</tspan>
    <tspan x="32" y="78">nav-3</tspan>
    <tspan x="32" y="96">nav-4</tspan>
  </text>
  <rect x="64" y="0" width="696" height="40" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="412" y="20">[tab] Tab A    [tab] Tab B    [tab] Tab C</tspan>
  </text>
  <rect x="64" y="40" width="696" height="380" fill="white" stroke="#333" stroke-width="1"/>
  <rect x="84" y="100" width="140" height="100" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="154" y="216">&lt;label&gt;</tspan>
  </text>
  <rect x="244" y="100" width="140" height="100" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="314" y="216">&lt;label&gt;</tspan>
  </text>
  <rect x="404" y="100" width="140" height="100" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="474" y="216">&lt;label&gt;</tspan>
  </text>
  <rect x="564" y="100" width="140" height="100" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="634" y="216">&lt;label&gt;</tspan>
  </text>
</svg>

The 4 card rects are a grid placeholder — replace the count/size to match the
project's real card grid, or delete them and describe a non-grid layout instead.

### Pattern C — modal / sheet overlay

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 420">
  <rect x="0" y="0" width="64" height="420" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="32" y="33">Nav</tspan>
    <tspan x="32" y="51">nav-1</tspan>
    <tspan x="32" y="69">nav-2*</tspan>
    <tspan x="32" y="87">nav-3</tspan>
  </text>
  <rect x="64" y="0" width="696" height="420" fill="#f5f5f5" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="412" y="40">[canvas stays in place — no swap]</tspan>
  </text>
  <rect x="250" y="110" width="380" height="40" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="440" y="130">&lt;Sheet title&gt;          X</tspan>
  </text>
  <rect x="250" y="150" width="380" height="180" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="440" y="231">&lt;content line&gt;</tspan>
    <tspan x="440" y="249">&lt;content line&gt;</tspan>
  </text>
</svg>

The light-gray (`#f5f5f5`) canvas rect signals "dimmed, still mounted underneath"
— keep that fill distinct from the sheet's white so the overlay reads as on top.

### Pattern D — full-screen (no persistent nav)

For login, onboarding, splash, or any screen where no nav chrome is visible.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 420">
  <rect x="0" y="0" width="760" height="50" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="380" y="25">&lt;Screen Title&gt; — full width</tspan>
  </text>
  <rect x="0" y="50" width="760" height="120" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="380" y="110">&lt;header / hero content&gt;</tspan>
  </text>
  <rect x="0" y="170" width="760" height="180" fill="white" stroke="#333" stroke-width="1"/>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="380" y="251">&lt;content row&gt;  [scroll]</tspan>
    <tspan x="380" y="269">&lt;content row&gt;</tspan>
  </text>
  <rect x="0" y="350" width="760" height="40" fill="#333" stroke="#333" stroke-width="1"/>
  <text x="380" y="375" text-anchor="middle" font-family="sans-serif" font-size="13" fill="white">&lt; Primary action &gt;</text>
  <text text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">
    <tspan x="380" y="405">&lt;secondary action&gt;</tspan>
  </text>
</svg>

The primary-action rect is filled dark (`#333`) with white text — the one
deliberate color inversion in these templates, marking the screen's single most
important action.

---
