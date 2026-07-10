# Token Saving Tools

This reference stays small on purpose. It only records when to use each tool and what
kind of setup it needs.

## Ponytail

- Use for overengineering checks, YAGNI pressure, and "smallest correct solution" reviews.
- Best when the task is code, architecture, or refactor guidance.
- No extra host setup required once the skill/plugin is installed.

Source: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

## Caveman

- Use when the agent is too verbose and should answer in fewer words.
- Best for response shaping, plan summaries, and tight implementation notes.
- No special runtime setup beyond the skill install.

Source: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

## RTK

- Use when shell output is noisy and should be compressed before it reaches the model.
- Best for test logs, git output, package-manager output, and other verbose commands.
- Setup is **two phases with different authorization needs — do not treat them as one step.**

Source: [rtk-ai/rtk](https://github.com/rtk-ai/rtk)

**Phase 1 — binary install: safe to run directly.**
```bash
brew install rtk        # verified working; local package install, no config changes
rtk --version && rtk gain   # sanity check
```

**Phase 2 — global hook wiring: requires specific, not generic, confirmation.**
`rtk init -g` patches `~/.claude/settings.json` (installs a PreToolUse hook rewriting
every Bash command) and `~/.claude/CLAUDE.md`. This is a global change that persists
across every future session, not just the current task. A generic "go ahead" is **not**
sufficient authorization for it — running `rtk init -g --auto-patch` on a general
approval gets blocked by the auto-mode classifier as unauthorized persistence (verified:
this happened in practice, not a hypothetical). Two correct paths instead:
1. Run `rtk init -g --dry-run` first, show the user the exact preview output, and get
   their confirmation of *that specific diff* — not a repeat of the earlier general
   go-ahead.
2. Tell the user to run `rtk init -g` themselves, interactively, in their own terminal —
   it prompts before touching `settings.json`, so no agent action is needed at all.

**The hook does not apply retroactively.** It only affects Bash commands in sessions
started *after* `rtk init -g` completes — verified by testing `git log` immediately
after install in the same session: output was unfiltered, exactly as expected.

**Tracking savings** (once the hook is live in a fresh session):
- `rtk gain` — summary; empty (`"No tracking data yet"`) until the hook has actually
  processed commands. `-H`/`--history` for per-command log, `-g`/`--graph` for a daily
  trend, `-a`/`--all` for full daily+weekly+monthly, `-q`/`--quota` for a $ estimate,
  `-f json`/`-f csv` for export.
- `rtk discover -p <project>` — retroactive estimate from existing Claude Code session
  history, works without the hook being live. May report 0 sessions depending on where
  the host stores transcripts — not a sign anything is broken.

## Headroom

- Use when tool output, logs, files, or RAG chunks need compression before LLM context.
- Best for heavy tool sessions where the host already supports Headroom.
- Keep this optional until the setup exists; do not block a task on it.

Source: [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)
