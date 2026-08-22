# Governance & CI Enforcement

Run the governance check in a consumer project's CI so violations block the build automatically — no manual audit required.

## Step 1 — Add a `.kmp-skills` version file to the consumer project root

```json
{
  "skills_repo": "ronjunevaldoz/kmp-agent-skills",
  "version": "1.24.1"
}
```

Commit this file. It declares which skills collection version the project targets and
must pin a release tag, not a mutable ref like `main`. The governance check prints it
on every run and fails if the file is missing or the version is not tag-pinned.

## Step 2 — Wire the reusable workflow

Create `.github/workflows/governance.yml` in the consumer project:

```yaml
name: KMP Governance

on:
  pull_request:
  push:
    branches: [main]

jobs:
  kmp-governance:
    uses: ronjunevaldoz/kmp-agent-skills/.github/workflows/kmp-audit.yml@main
    with:
      project_root: .
      fail_on: HIGH
      skills_ref: v1.24.1   # pin to a tag for reproducibility
```

That is the complete consumer setup — no scripts to copy, no dependencies to install beyond Python 3.12 (provided by the workflow).

## What the governance check runs

| Scanner | Detects | Severity |
|---|---|---|
| `scan_design_violations.py` | Hardcoded colors, dp literals, Material theme usage, TextStyle construction, nested containers, layout inconsistency | HIGH (error), MEDIUM (warning) |
| `audit_project.py` | State copy races, SharedFlow replay effects, NetworkResult in UI state, DTO import in UI layer, magic color literals, hardcoded spacing, missing preview stubs | HIGH |
| `validate_module_graph.py` | Missing feature module files, missing `androidApp` UI link, missing `*ContentPreview.kt` stub beside feature UI content | HIGH |

Findings at or above `fail_on` exit non-zero and fail the CI job. Findings below the threshold are reported but do not fail.

## Threshold guide

| `fail_on` value | When to use |
|---|---|
| `HIGH` | Default. Fails only on correctness violations and architecture boundary breaks. |
| `MEDIUM` | Stricter. Also fails on design-token warnings and layout inconsistencies. Recommended once the project is stable. |
| `LOW` | Full enforcement. Fails on any finding. Use for highly regulated or greenfield projects. |

## Running locally before pushing

```bash
# From inside the skills repo (development)
python3 skills/kmp-audit/scripts/governance_check.py /path/to/consumer/project

# From a consumer project with the skills repo checked out alongside it
python3 ../kmp-agent-skills/skills/kmp-audit/scripts/governance_check.py .
```
