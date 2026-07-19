# /update-skills

Pull the latest kmm-agent-skills release and re-deploy skills to the current consumer project.

> **Skills vs commands:** `skills/` (passive reference docs) are deployed automatically.
> `commands/` (executable agent slash commands) are NOT. Commands require explicit user
> review before install — see Step 3 if you also want to update commands.

---

## Step 1 — Run the update script

```bash
bash .claude/skills/scripts/update-consumer-skills.sh
```

**Exit 0, "Already up to date"** → skills are current. Continue with your work.

**Exit 0, "v1.X.Y → v1.Z.W"** → skills were updated. Continue to Step 2.

**Exit 0, "Could not reach remote"** → offline. Warn the user and continue with local skills.

**Exit 1** → could not locate skills source or agent directory. Ask the user:
- Where is the kmm-agent-skills clone? Pass `--source PATH`.
- Where are skills deployed? Pass `--agent-dir PATH`.

Then retry:
```bash
bash .claude/skills/scripts/update-consumer-skills.sh --source /path/to/kmm-agent-skills --agent-dir .claude/skills
```

If this happens across multiple consumer projects on the same machine, suggest setting
`$KMM_AGENT_SKILLS_SOURCE` once instead of passing `--source` every time — auto-detect
checks it first, before falling back to guessed paths:

```bash
export KMM_AGENT_SKILLS_SOURCE=/path/to/kmm-agent-skills   # add to shell profile
```

---

## Step 2 — Post-update verification

After a successful update, run the audit against the project:

```bash
python3 .claude/skills/kotlin-multiplatform-audit/scripts/audit_project.py .
```

Report the result:
- **Zero findings** → update complete.
- **New findings** → show them to the user and explain which skills to apply.

---

## Step 2b — Mandatory baseline check (existing project scaffolded on an older release)

A project scaffolded before a given kmm-agent-skills version may predate skills that
later became part of the mandatory baseline (see `kotlin-multiplatform-migration`'s
Tier 1 Foundation table). `audit_project.py` catches architecture *smells* in code that
exists — it can't flag a skill nobody has adopted yet, since there's no violating code
to find. Check for the baseline explicitly:

```bash
# code-quality — Detekt + Ktlint config present?
test -f detekt.yml || find . -maxdepth 3 -name detekt.yml
grep -rl "ktlint" **/build.gradle.kts 2>/dev/null

# unit-testing — any real test source with an assertion, not just an empty dir?
find . -path '*/src/*Test/kotlin' -name '*.kt' | xargs grep -l '@Test' 2>/dev/null

# project-docs-maintainer — docs/reference/ synced?
test -d docs/reference

# android-cli — no file footprint to grep for (it wraps a terminal tool, doesn't
# scaffold files); ask directly instead: "Is the Android target built/run via the
# android CLI, or still through Android Studio only?"
```

Report any missing item as a gap, not a blocker:

```
Mandatory baseline check:
  [x] code-quality   — detekt.yml found
  [ ] unit-testing   — no @Test found under any *Test/kotlin source set
  [x] project-docs-maintainer — docs/reference/ present
  [?] android-cli    — ask the user directly, no file signal exists

Missing: unit-testing. Load kotlin-multiplatform-unit-testing to retrofit test source
sets and fakes/mocks conventions before continuing feature work.
```

Do not auto-apply a missing skill — this is a report, same as the audit findings above.
Let the user decide whether and when to retrofit it.

---

## Step 3 — Updating commands (manual — requires explicit approval)

Commands are NOT auto-deployed. If the user wants to update slash commands, run the guided
installer. It shows each command file with its first line and asks `[y/N]` before copying:

```bash
bash .claude/skills/scripts/update-consumer-skills.sh \
  --source /path/to/kmm-agent-skills \
  --agent-dir .claude/skills \
  --install-commands
```

Only run this step if the user explicitly asks to update commands.

## Related

If you want to refresh the local assistant bundles on this Mac too, use `/kmm-sync-local-skills`.

---

## Step 4 — Report to user

```
Skills updated: v<old> → v<new>
<N> skill(s) redeployed to <agent-dir>

What changed:
<changelog excerpt for new version>

Audit: clean / <N> findings

Note: slash commands were not updated. Run with --install-commands to review and update them.
```

---

## Notes

- The script does a fast-forward pull only — it will not rebase or force-merge.
- If the source has uncommitted local changes, the pull will fail. Report this and ask the user to stash or commit in the skills repo first.
- For `npx skills add` installs, re-run `npx skills add ronjunevaldoz/kmm-agent-skills` instead.
