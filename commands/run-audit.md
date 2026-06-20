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

---

## Step 2 — Explain each finding

For every finding, load the relevant skill and give a concrete fix:

| Finding | Skill | Fix |
|---|---|---|
| `state copy race` | `presenter-module`, `mvi` | `_state.update { it.copy(...) }` — atomic, race-free |
| `sharedflow replay effect` | `mvi` | `Channel<Effect>(Channel.BUFFERED).receiveAsFlow()` |
| `network result in ui` | `clean-architecture`, `network-layer` | Unwrap `NetworkResult` in `:presenter`; pass only `UiState` to `:ui` |
| `data import in ui` | `clean-architecture` | Move the shared type to `:model` or `:api`; import from there |
| `manual screen capture` | `roborazzi` | `captureRoboImage("name.png") { ... }` in `jvmTest` — no device needed |

---

## Step 3 — Output

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

## Step 4 — Optional auto-fix

If the user says "fix it", load `agents/fixer.md`.

Apply only HIGH confidence fixes automatically. Present MEDIUM and LOW to the user
for a decision before touching anything.
