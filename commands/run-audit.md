# /run-audit $ARGUMENTS

**KMM Agent Skills** — run the architecture audit on a KMP project and get
per-finding remediation steps from the matching skill.

Target project: `$ARGUMENTS` (defaults to `.` if empty)

---

## Step 1 — Run the script

```bash
python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py "${ARGUMENTS:-.}"
```

The script detects 5 architectural smells:

| Pattern | What it catches |
|---|---|
| `state copy race` | `_state.value = _state.value.copy(...)` — race condition in ViewModel |
| `sharedflow replay effect` | `MutableSharedFlow(replay=1)` used for one-shot UI effects |
| `network result in ui` | `NetworkResult<T>` leaking into `:ui` or `:presentation` layer |
| `data import in ui` | `*.data.*` imported from `:ui` — layer boundary violation |
| `manual screen capture` | `playwright`, `adb screencap`, `xcrun simctl io` — replace with Roborazzi |
| `magic color literal` | `Color(0xFF…)` written directly in a composable instead of `AppTheme.colors.X` — design token bypass |
| `system dark theme scatter` | `isSystemInDarkTheme()` called inside a composable instead of the theme entry point — dark/light logic scattered |
| `hardcoded spacing` | `padding(16.dp)` or `padding(horizontal = 8.dp)` in a UI file instead of `AppTheme.spacing.X` — layout inconsistency |

---

## Step 2 — Quality scan

```bash
python3 scripts/scan_skill_issues.py
```

Parse the JSON output (`total_issues`, `by_severity`, `issues[]`).

Print a brief summary before the architecture findings:

```
SKILLS QUALITY SCAN:
  Total issues:   <N>
  🔴 HIGH:        <N>   (testing gaps)
  🟡 MEDIUM:      <N>   (missing sections, stale skills)
  🔵 LOW:         <N>   (minor gaps)
```

If `total_issues > 0`, append:
```
  Run /summarize-issues for the full report with paste-ready fix prompts.
```

This step is non-blocking — continue to Step 4 regardless of the scan result.

---

## Step 4 — Explain each finding

For every finding, load the relevant skill and give a concrete fix:

| Finding | Skill | Fix |
|---|---|---|
| `state copy race` | `presenter-module`, `mvi` | `_state.update { it.copy(...) }` — atomic, race-free |
| `sharedflow replay effect` | `mvi` | `Channel<Effect>(Channel.BUFFERED).receiveAsFlow()` |
| `network result in ui` | `clean-architecture`, `network-layer` | Unwrap `NetworkResult` in `:presenter`; pass only `UiState` to `:ui` |
| `data import in ui` | `clean-architecture` | Move the shared type to `:model` or `:api`; import from there |
| `manual screen capture` | `roborazzi` | `captureRoboImage("name.png") { ... }` in `jvmTest` — no device needed |
| `magic color literal` | `design-system` | Replace `Color(0xFF…)` with `AppTheme.colors.X`; define the token in `AppColors.kt` |
| `system dark theme scatter` | `design-system` | Remove `isSystemInDarkTheme()` from the composable; use a semantic token (`AppTheme.colors.X`) instead |
| `hardcoded spacing` | `design-system`, `design-system-extended` | Replace `N.dp` with `AppTheme.spacing.X`; load the Screen Layout Contract from the design-system skill |

---

## Step 5 — Output

On findings:
```
PROJECT: <path>
RESULT:  <N> findings

FINDINGS:
  state copy race: feature/auth/presenter/AuthViewModel.kt
  → Fix: replace _state.value = _state.value.copy(...) with _state.update { it.copy(...) }
  → Full guidance: kotlin-multiplatform-mvi / kotlin-multiplatform-presenter-module

SUMMARY:
  Total:    <N>
  Blockers: <N>
```

On clean:
```
PROJECT: <path>
RESULT:  CLEAN — no architecture smells found
```

---

## Step 6 — Optional auto-fix

If the user says "fix it", load `agents/fixer.md`.

Apply only HIGH confidence fixes automatically. Present MEDIUM and LOW to the user
for a decision before touching anything.
