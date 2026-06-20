# /run-audit $ARGUMENTS

Run the full KMP architecture audit on the project at `$ARGUMENTS` (defaults to current directory if empty).

---

## Step 1: Resolve project root

If `$ARGUMENTS` is empty, use `.` (current directory).
If `$ARGUMENTS` is a relative path, resolve it.

```bash
PROJECT_ROOT="${ARGUMENTS:-.}"
```

---

## Step 2: Run the audit script

```bash
python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py "$PROJECT_ROOT"
```

---

## Step 3: Interpret findings

For each finding, load the relevant skill and explain the remediation:

| Finding label | Skill to load | What to fix |
|---|---|---|
| `state copy race` | `presenter-module`, `mvi` | Replace `_state.value = _state.value.copy(...)` with `_state.update { it.copy(...) }` |
| `sharedflow replay effect` | `mvi` | Replace `MutableSharedFlow(replay=1)` with `Channel(Channel.BUFFERED).receiveAsFlow()` |
| `network result in ui` | `clean-architecture`, `network-layer` | Move `NetworkResult` unwrapping to `:presenter`; `:ui` receives only `UiState` |
| `data import in ui` | `clean-architecture` | Remove `*.data.*` import from `:ui`; expose the type via `:api` or `:model` |
| `manual screen capture` | `roborazzi` | Replace with `captureRoboImage(...)` in `jvmTest`; no device or emulator needed |

---

## Step 4: Output

```
PROJECT: <resolved path>
AUDIT RESULT: PASS | <N findings>

FINDINGS:
- <label>: <file path>
  → Fix: <what to change>
  → Skill: <skill name for full guidance>

SUMMARY:
  Total findings: <N>
  Blockers:       <N>
  Estimated fix time: <rough estimate>
```

If `PASS`, output:
```
✓ No architecture smells found. Project is clean.
```

---

## Step 5: Optional — auto-fix

If the user says "fix it" after seeing the findings, load `agents/fixer.md` and apply fixes for HIGH confidence findings only. Leave LOW and MEDIUM for user review.
