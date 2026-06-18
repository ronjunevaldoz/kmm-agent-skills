# Test coverage

All tests live in `tests/test_skill_scripts.py` and run with:

```
python3 -m pytest tests/ -v
```

Current status: **16 tests, 16 passing**.

---

## Coverage by script

### `kotlin-multiplatform-expert` — `validate_skill_map.py`

| Test | What it verifies |
|---|---|
| `test_validate_skill_map_ok` | No findings when README, expert SKILL.md, and skill folders are all consistent |
| `test_validate_skill_map_reports_missing_skill` | Reports "declares N skills but repo has M skill folders" when the expert skill count is stale |

**Not covered:** README missing a skill that exists in the folder list; expert SKILL.md referencing a skill that has no directory.

---

### `kotlin-multiplatform-feature-scaffold` — `validate_module_graph.py`

| Test | What it verifies |
|---|---|
| `test_validate_module_graph_ok` | No findings when all four feature modules exist and `androidApp` references `:feature:auth:ui` |
| `test_validate_module_graph_reports_missing_reference` | Reports missing typesafe project reference when `androidApp/build.gradle.kts` omits the dependency |

**Not covered:** missing individual submodules (api/domain/data); missing `settings.gradle.kts`; missing `build-logic` directory.

---

### `kotlin-multiplatform-audit` — `audit_project.py`

Detects four architecture smell patterns in `.kt`/`.kts`/`.md` files:

| Pattern | Label | Tested? |
|---|---|---|
| `_state.value = _state.value.copy(` | `state copy race` | ✅ |
| `MutableSharedFlow<.*replay = 1` | `sharedflow replay effect` | ✅ |
| `NetworkResult<` in `/ui/` or `/presentation/` | `network result in ui` | ✅ |
| `NetworkResult<` outside `/ui/` — should NOT fire | `network result in ui` false-positive | ✅ |
| `import *.data.*` in `/ui/` or `/presentation/` | `data import in ui` | ✅ |

**Not covered:** empty directory; non-Kotlin files ignored correctly.

---

### `kotlin-multiplatform-audit` — `audit_skills_repo.py`

| Test | What it verifies |
|---|---|
| `test_audit_skills_repo_flags_missing_freshness_and_markers` | Reports "missing freshness guidance" when a skill touches Ktor but has no freshness/recheck/latest text |
| `test_audit_skills_repo_flags_missing_all_targets_branch_guidance` | Reports missing `all-targets` when `feature-scaffold` SKILL.md lacks it |
| `test_audit_skills_repo_flags_missing_build_logic_toml_guidance` | Reports missing `build-logic` + `libs.versions.toml` when feature-scaffold SKILL.md lacks both |

**Not covered:** `references/` directory without references guidance in SKILL.md; `scripts/` directory without script guidance; README missing "Start here" or "Roadmap"; missing `README.md`; skill directory with no SKILL.md.

---

### `kotlin-multiplatform-audit` — `draft_issue.py`

| Test | What it verifies |
|---|---|
| `test_render_issue_includes_attribution_footer` | Rendered markdown contains the title as a heading and the attribution footer |

**Not covered:** `kind="question"` output differs from `kind="issue"`; empty evidence or recommendation fields; special characters in title.

---

### `kotlin-multiplatform-ktor-auth-service` — `scaffold_auth_service.py`

| Test | What it verifies |
|---|---|
| `test_scaffold_auth_service_writes_expected_files` | All 7 expected `.kt` files are created; package declarations match the given package prefix |

**Not covered:** idempotency (running scaffold twice doesn't corrupt files); custom package prefix with nested namespaces; generated file content structure (service methods, DI bindings).

---

### `kotlin-multiplatform-mongodb-database` — `scaffold_mongodb_database.py`

| Test | What it verifies |
|---|---|
| `test_scaffold_mongodb_database_writes_expected_files` | All 5 expected `.kt` files are created; package declarations match the given package prefix |

**Not covered:** idempotency; `UserCollection.kt` existence; generated repository method stubs.

---

### `kotlin-multiplatform-kotlin-rpc` — `scaffold_kotlin_rpc.py`

| Test | What it verifies |
|---|---|
| `test_scaffold_kotlin_rpc_writes_expected_files` | All 5 expected `.kt` files are created across shared/server/client; package declarations match |

**Not covered:** idempotency; `GreetingResponse.kt` and `GreetingRequest.kt` package declarations; server module Ktor wiring stub.

---

## Scripts with no tests

These scripts exist but have no test coverage:

| Script | Skill |
|---|---|
| *(none — all scripts are covered)* | — |

---

## Skills with no scripts

These 18 skills have no scaffold or validation scripts, so there is nothing to test:

`ci-github-actions`, `compose-slot-api`, `compose-state-container`, `compose-state-hoisting`,
`dependency-injection`, `design-system`, `design-system-extended`, `expect-actual`,
`flavor-environment`, `graphics-modifiers`, `mvi`, `navigation`, `network-layer`,
`repository-pattern`, `shared-resources`, `sqldelight-setup`, `xcframework-spm`,
`(plus kotlin-multiplatform-audit references/ only)`

---

## Coverage gaps — priority order

| Gap | Priority | Notes |
|---|---|---|
| `network result in ui` smell not tested | ~~high~~ ✅ | Fixed — fires in `/ui/`, silent outside it |
| `audit_skills_repo` missing-marker tests | ~~high~~ ✅ | Fixed — all 4 markers checked; false-positive guard added |
| `audit_skills_repo` scripts/references directory checks | medium | No test covers the "has scripts/ but no script guidance" or "has references/ but no reference guidance" paths |
| `draft_issue` kind="question" output | low | Different rendering path, no test |
| Scaffold idempotency | low | All three scaffold scripts lack a second-run test |
| `validate_module_graph` missing submodule | low | Only the missing androidApp reference is tested; missing individual layer subfolders are not |

---

## Running the suite

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run one class
python3 -m pytest tests/test_skill_scripts.py::AuditProjectTests -v

# Run and stop on first failure
python3 -m pytest tests/ -x
```
