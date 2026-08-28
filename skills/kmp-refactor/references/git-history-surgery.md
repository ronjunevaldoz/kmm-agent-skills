# Git History Surgery: Fixing Unintentional Data in Stacked Commits

How to surgically fix a bad commit buried under multiple stacked commits without losing subsequent work.

---

## The Scenario

You are working across multiple features, and an unintended file or secret was committed in **Commit 2**, which is now buried under **Commits 3, 4, and 5**:

```text
Commit 5: feat(editor): add inspector panel (HEAD)
Commit 4: feat(auth): add password validator
Commit 3: fix(ui): resolve button padding
Commit 2: feat(camera): add orbit camera  <-- ⚠️ Accidental secret/file introduced here!
Commit 1: feat(auth): add login screen
```

---

## Method 1: The Autosquash Fixup (Fastest & Safest)

This method lets you fix the mistake at `HEAD` and let Git automatically move the fix down into the target past commit.

### Step 1: Remove or fix the bad file at `HEAD`
```bash
git rm path/to/unintended-file.txt   # or delete the secret in code
```

### Step 2: Commit as a `--fixup` targeting the bad commit
```bash
# Find the commit hash of Commit 2 (e.g. abc1234)
git log --oneline -n 5

# Create a fixup commit linked to that SHA:
git commit --fixup abc1234
```

### Step 3: Run autosquash rebase
```bash
# Rebase back to before Commit 2 (Commit 1's hash):
git rebase -i --autosquash abc1234~1
```
*Git will automatically re-order the fixup commit directly below Commit 2, squash them into a single clean commit, and replay Commits 3, 4, and 5 cleanly on top!*

---

## Method 2: Interactive Rebase with `edit`

When you need to make complex edits to a buried commit.

### Step 1: Start interactive rebase
```bash
git rebase -i HEAD~5
```

In the editor that opens, change `pick` to `edit` (or `e`) on the offending commit:
```text
pick abc1234 feat(camera): add orbit camera  ---> change 'pick' to 'edit'
pick def5678 fix(ui): resolve button padding
pick ghi9012 feat(auth): add password validator
pick jkl3456 feat(editor): add inspector panel
```
Save and close.

### Step 2: Git pauses at that exact commit. Fix the mistake:
```bash
# Remove the bad file from this commit:
git rm --cached path/to/unintended-file.txt
git commit --amend --no-edit
```

### Step 3: Continue rebase
```bash
git rebase --continue
```
*Git finishes applying Commits 3, 4, and 5. The bad file is completely wiped from history.*

---

## What to do if you already pushed to a remote branch

- **On a Personal Feature Branch (PR)**:
  ```bash
  git push origin <branch-name> --force-with-lease
  ```
  *(Never use raw `--force`; `--force-with-lease` protects against overwriting upstream work).*

- **On a Shared Branch (`main`)**:
  - If it's a **Secret / API Key**: Invalidate/rotate the secret immediately, then purge it with `git-filter-repo`.
  - If it's a **Regular File**: Do NOT rebase shared history — commit a `fix: remove unintended file` commit.
