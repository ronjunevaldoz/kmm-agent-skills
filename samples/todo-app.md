# Sample: Todo App

**E2E test spec for KMM Agent Skills.**

Build a KMP todo app targeting Android and Desktop.
No backend. No auth. Local persistence only.

---

## Features

### Todo list screen
- Show all todos in a scrollable list
- Each todo shows: title, completion checkbox, delete button
- Empty state when no todos exist
- Loading state while fetching from database
- Error state if database read fails

### Add todo screen
- Single text field for the todo title
- Title is required — show inline validation error if submitted empty
- Submit button disabled until title is non-empty
- On success: navigate back to list, new todo appears at top
- On error: show error message, stay on screen

### Mark complete / incomplete
- Tapping the checkbox on a list item toggles completion
- Completed todos show strikethrough title
- State persists across app restarts

### Delete todo
- Delete button on each list item
- No confirmation dialog — deletes immediately
- Deletion is reflected in the list without a full reload

### Persistence
- Store todos in a local SQLite database via SQLDelight
- Todos survive process kill and device restart

---

## Design requirements

- Light mode and dark mode — both must be tested with Roborazzi
- Use the project design system: `AppTheme`, `AppScaffold`, `AppTopAppBar`, spacing tokens
- No hardcoded colors, no hardcoded `padding(N.dp)`
- Empty, loading, and error states all need distinct visual treatments

---

## Quality bar

This spec is used to test whether the KMM skills pipeline can produce a complete,
correct project from a minimal description. The following must all be true when
`/kmm-new-project samples/todo-app.md` finishes:

- [ ] `python3 skills/kotlin-multiplatform-audit/scripts/audit_project.py .` → zero findings
- [ ] `./gradlew jvmTest` → all tests pass
- [ ] Roborazzi goldens exist for every screen state (empty, loading, error, populated) in light + dark
- [ ] `/kmm-audit-screenshots .` → no FAIL findings (TopAppBar present, dark mode distinct, no raw colors)
- [ ] Every `:presenter` ViewModel has unit tests covering at least: load success, load error, action happy path
- [ ] No screen imports from `:data` or `:domain` directly
- [ ] Koin modules wire every ViewModel and repository

---

## Expected skills exercised

| Skill | Why |
|---|---|
| `kotlin-multiplatform-feature-scaffold` | Project foundation, version catalog, build-logic |
| `kotlin-multiplatform-clean-architecture` | 6-layer module structure |
| `kotlin-multiplatform-dependency-injection` | Koin modules for all layers |
| `kotlin-multiplatform-sqldelight-setup` | Local todo persistence |
| `kotlin-multiplatform-repository-pattern` | TodoRepository interface + implementation |
| `kotlin-multiplatform-mvi` | ViewModel, UiState, UiEffect, Channel |
| `kotlin-multiplatform-form-validation` | Add todo title validation |
| `kotlin-multiplatform-navigation` | List → Add screen, back navigation |
| `kotlin-multiplatform-design-system` | AppTheme, AppScaffold, AppTopAppBar, tokens |
| `kotlin-multiplatform-unit-testing` | Presenter tests with runTest + Turbine |
| `kotlin-multiplatform-roborazzi` | Screenshot tests for all screen states |
| `kotlin-multiplatform-logging` | Debug logging in repository and use cases |

12 skills. A passing run validates that these skills compose correctly with no gaps.
