# /update-skills

Pull the latest kmm-agent-skills release and re-deploy to the current consumer project.

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
bash .claude/skills/scripts/update-consumer-skills.sh --source ~/dev/kmm-agent-skills --agent-dir .claude/skills
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

## Step 3 — Report to user

```
Skills updated: v<old> → v<new>
<N> skill(s) redeployed to <agent-dir>

What changed:
<changelog excerpt for new version>

Audit: clean / <N> findings
```

---

## Notes

- The script does a fast-forward pull only — it will not rebase or force-merge.
- If the source has uncommitted local changes, the pull will fail. Report this and ask the user to stash or commit in the skills repo first.
- For agents deployed via git submodule, the script auto-detects the submodule path.
- For `npx skills add` installs, re-run `npx skills add ronjunevaldoz/kmm-agent-skills` instead.
