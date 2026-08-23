# Compliance & Legal Audit

Part of `kmp-api-mimicry`. Load this file when auditing an *existing* mimicry
project for IP/trademark/license risk — not when designing the mimicry itself
(that's the main `SKILL.md`).

Generic to any reference API being mimicked (Jetpack Compose, SwiftUI,
Retrofit, Room, or anything else) and any organization that owns it (Google,
Apple, Square, JetBrains, ...) — none of the four categories below are
Compose- or Vulkan-specific. Substitute the actual reference API, its real
owner, and your project's actual custom runtime before running this.

Act as a software compliance reviewer. For every issue found, report:
**file path (and line number where applicable) → risk category → concrete fix.**

---

## 1) Trademark & Package Naming

- Real namespace collision: does any file import or declare a package under
  the reference library's actual namespace (e.g. `androidx.compose.*` if
  mimicking Jetpack Compose, `com.squareup.retrofit2.*` if mimicking
  Retrofit)? Mechanical — run `scripts/scan_mimicry_compliance.py` with
  `--namespace-prefix <the real one>`.
- Endorsement-implying naming: does the project name, README title, or
  published artifact ID use the reference API's or its owner's trademarked
  name in a way that could be read as "official" or "affiliated with X"?
  This is a judgment call, not a grep — "inspired by X" is fine, "X for
  Vulkan" or an artifact literally named after the trademark is not. Check the
  project name, `rootProject.name`, README's first heading, and any
  published-artifact `groupId`/`artifactId`.

## 2) Code Origin & Re-implementation Risk

Judgment call, not mechanically detectable — a script can't tell "independently
re-derived from the reference API's public docs" apart from "copy-pasted from
its actual source" by shape alone; both can produce identical code.

- **Fair use / re-implementation** (fine, this is what `kmp-api-mimicry`'s main
  guidance is *for*): matching public API *shape* — same annotation pattern,
  same chainable-modifier signature, same slot-lambda convention — independently
  written against the reference API's public documentation, not its source.
- **Real risk**: an internal helper, algorithm, or state-management routine
  that reads as directly ported from the reference library's actual source
  tree, with no accompanying license header/NOTICE-file attribution for the
  license that source was under (often Apache 2.0 for AOSP-derived code, but
  verify per-project — it's whatever license the *actual* source you're
  suspicious of ships under).
- If Apache-2.0-licensed source genuinely was ported: per the real license
  text, that requires (a) including the full license text, (b) marking the
  file as changed, (c) preserving the original copyright/attribution notices,
  and (d) carrying forward the source project's NOTICE file content if it has
  one. Missing any of these on ported code is the actual violation — the port
  itself is often permitted, silent attribution isn't.
- Read each suspicious function against the reference library's real public
  source (when available) before flagging — a coincidentally similar 3-line
  helper is not evidence of copying; a byte-for-byte block with renamed
  variables is.

### Clean-Room Provenance Record

"Do we have proof of non-copyright-violation" — verified what that actually
means before writing this, rather than assuming: the real "clean room"
process (upheld in *Sega v. Accolade*; the Columbia Data Products/IBM BIOS
case is the textbook example) is a **two-team model** — one team studies the
target and writes a behavior-only functional spec, a second team implements
from that spec *without ever accessing the original source*. It exists to
defend against copyright/trade-secret claims when reverse-engineering
**closed-source, proprietary** software.

**That full apparatus is usually the wrong tool here.** Most reference APIs
this skill mimics (Jetpack Compose, Retrofit, Room) are already open-source
under a permissive license — their source isn't a secret you're barred from
seeing, so there's nothing to wall off. The actual risk for an open-source
reference API is narrower and already covered above: verbatim copying without
attribution, not "you had access to code you shouldn't have." A lightweight
**Provenance Record** — documenting each mimicked primitive was derived from
public docs, not copy-pasted from source — is the right-sized artifact for
that case.

**Escalate to the real two-team process (and actual legal counsel, not this
skill) only when the reference API is genuinely closed-source or
proprietary** and there's real commercial exposure — mimicking SwiftUI's
shape from Apple's public documentation is a materially different legal
position than mimicking Compose's shape from AOSP's public, Apache-2.0
source, precisely because Compose's source was never off-limits to begin
with.

**Provenance Record template** — one file, one row per mimicked primitive
(pairs with `docs/MIRROR_MAP.md`, doesn't replace it):

```markdown
# Provenance Record

| Primitive | Author | Date | Sources consulted | Reference source viewed? |
|---|---|---|---|---|
| `EngineModifier.padding()` | @handle | 2026-08-23 | [Compose Modifier docs](https://developer.android.com/reference/kotlin/androidx/compose/ui/Modifier) | No — public docs only |
| `EngineScope.Box()` | @handle | 2026-08-23 | Compose Layouts guide | No — public docs only |
```

**"Reference source viewed?" — answer honestly, not defensively.** "Yes, for
research" is fine and common; what matters is what happens next: if source
was viewed, the record should say what was verified from it (behavior,
naming) versus what was independently written (the actual implementation).
"No" is the stronger position when true — don't claim it if a source browse
actually happened.

## 3) Font Licensing & Assets

Applies to every project bundling fonts, mimicry or not — not specific to any
reference API.

- Mechanical — run `scripts/scan_mimicry_compliance.py` (font check always
  runs, no flags needed): finds every `.ttf`/`.otf`/`.woff`/`.woff2` in the
  repo and flags one with no license file in the same directory.
- Verified real license requirements, don't assume:
  - **SIL Open Font License (OFL)**: font + `OFL.txt` (or equivalent license
    text) must travel together on every redistribution. The font may be
    bundled or sold *inside* software; it can never be sold standalone. Any
    modified version must stay under the OFL.
  - **Apache 2.0** (some font families use it): same rules as source code —
    include the license text, and the NOTICE file's content if the font
    family ships one.
  - **Commercial/proprietary fonts**: check the foundry's actual license
    terms for redistribution/embedding rights before bundling at all — a
    desktop-use license does not automatically grant app-embedding rights.
- A font file with no adjacent license file and no clear provenance is a
  finding regardless of which of the three cases above applies — the missing
  piece is "which license," not "whether one is needed."

## 4) Accidental Re-linking Dependencies

- Mechanical — run `scripts/scan_mimicry_compliance.py` with
  `--dependency-coordinate <the real artifact>` (e.g.
  `androidx.compose.ui:` if mimicking Jetpack Compose without meaning to
  depend on the real thing).
- Check `build.gradle.kts`, `libs.versions.toml`, and any `pom.xml` for the
  reference library's actual runtime artifact. A real dependency on it
  contradicts the mimicry premise — either it's there by accident (drop it)
  or the project has quietly stopped being mimicry and started being a
  wrapper around the real library (a different, legitimate thing — but
  `kmp-api-mimicry` no longer applies, this is ordinary consumption).

---

## Output Format

```
file/path.kt:42 — TRADEMARK & PACKAGE NAMING — imports androidx.compose.ui.Modifier;
    rename to your own package, e.g. com.myengine.ui.Modifier

assets/fonts/Inter-Regular.ttf — FONT LICENSING — no license file alongside it;
    Inter ships under OFL — add OFL.txt to assets/fonts/

build.gradle.kts:18 — ACCIDENTAL RE-LINKING — declares androidx.compose.ui:1.7.0;
    remove unless real Compose Multiplatform is a deliberate dependency
```

One line per finding: location, category, concrete fix — matching this
collection's own audit-finding shape (`kmp-audit`'s Output Format), not a
prose report.
