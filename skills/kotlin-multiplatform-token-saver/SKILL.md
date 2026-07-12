---
name: kotlin-multiplatform-token-saver
description: >
  Token-saving workflow for KMP agent work. Use when the user asks to reduce token
  usage, shorten replies, compress noisy tool output, or choose the smallest correct
  solution. Covers Ponytail for YAGNI and overengineering checks, Caveman for terse
  replies, RTK for shell output compression, and Headroom for tool/log/file/RAG
  compression when the host is already configured. Headroom stays optional until setup
  exists; do not block the task on it.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-07-12'
  keywords:
    - token saver
    - prompt compression
    - context compression
    - terse replies
    - overengineering
    - caveman
    - ponytail
    - headroom
    - rtk
---

# Kotlin Multiplatform Token Saver

## When to Use This Skill

Use this skill when the request is about:
- token or context reduction
- shorter replies or less ceremony
- compressing verbose command output
- choosing the smallest correct implementation
- deciding whether a setup-heavy compressor is worth enabling yet

**Trigger keywords:** token saver, token reduction, prompt compression, context compression,
too much output, terse, caveman, ponytail, headroom, rtk, smallest correct solution, YAGNI.

## Recommendation First

These four are not equally available by default — verified against each tool's real
install method, not assumed:

1. **RTK** — real risk profile: low. Installs via `brew install rtk` (an official
   Homebrew bottle). Once installed and its hook wired, it runs automatically; nothing
   further to enable per-session.
2. **Ponytail** — real risk profile: low. Installs through Claude Code's own plugin
   marketplace (`/plugin marketplace add DietrichGebert/ponytail`, then
   `/plugin install ponytail@ponytail`) — these are slash commands the *user* runs
   interactively; an agent cannot invoke them on the user's behalf.
3. **Caveman** — real risk profile: elevated. Its documented install is
   `curl -fsSL .../install.sh | bash` (or the PowerShell equivalent) — executing a
   remote script directly from a personal GitHub account, with no package-manager
   verification step. Do not run this yourself; if the user wants it, they run the
   installer themselves after reviewing it.
4. **Headroom** — real risk profile: heaviest setup, not risk per se. It's a local
   proxy server (`headroom proxy --port 8787`) sitting between the agent and the LLM
   provider, requires the user's own provider API keys, and downloads a model from
   HuggingFace on first run. Never enter API keys into it on the user's behalf — that's
   a hard rule regardless of tool. Keep this optional until the user has set it up
   themselves; do not block a task on it.

RTK itself has two install phases with different authorization needs — the binary
install (`brew install rtk`) is safe to run directly, but the hook wiring
(`rtk init -g`, which patches global `settings.json`/`CLAUDE.md`) needs specific
confirmation of the exact diff, not a repeat of an earlier general go-ahead. See
`references/token-saving-tools.md` for the verified details — this was hit in
practice, not a hypothetical.

## Tool Choice

Pick the narrowest tool that solves the problem — and check what's actually installed
before recommending one, rather than assuming all four are equally available:

- **Ponytail**: review/planning guardrail for "do we need this at all?" and
  "what is the smallest correct thing?" — real Claude Code plugin, install via
  `/plugin marketplace add`, user-run
- **Caveman**: make the model speak tersely without losing accuracy — real tool, but
  installs via `curl | bash` from an unverified source; recommend it, don't install it
- **RTK**: compress command output before it reaches the model — the one most likely to
  already be installed; check with `rtk --version` before assuming it needs setup
- **Headroom**: compress tool output, logs, files, and RAG chunks when the host is
  already set up — needs a running local proxy and the user's own API keys; heaviest
  setup of the four, never something to "just enable"

## Default Rules

- Prefer the standard library or existing repo tooling before adding a new helper.
- Prefer the smallest correct change before adding a wrapper or abstraction.
- Prefer terse outputs, but never drop technical facts that change the answer.
- Do not make setup-heavy tools mandatory until the environment is actually configured.

**Freshness rule:** recheck the upstream setup docs for Ponytail, Caveman, Headroom, and
RTK before changing installation guidance or host integration notes, because token-saving
tooling changes quickly.

## Testing

Validate this skill with short prompt-routing checks, not heavy integration scaffolds.

- `@Test` the trigger map: token-saving prompts should route to this skill, not to a feature skill.
- `runTest` the fallback rule: if Headroom is unavailable, the skill should still recommend Ponytail,
  Caveman, or RTK.
- Use a fake/no-op host setup when verifying that "Headroom optional until setup" stays true.

## Common Anti-Patterns

- loading Headroom before the host has it configured
- adding a wrapper when stdlib or an existing command is enough
- using a verbose reply when a shorter one preserves the same facts
- enabling every compressor at once
- treating Ponytail as a replacement for architecture judgment
- running `rtk init -g --auto-patch` on a generic "go ahead" — global config patches need confirmation of the specific diff, not a repeat of an earlier general approval; show `--dry-run` output first or have the user run it themselves interactively
- assuming the RTK hook is active immediately after `rtk init -g` — it only applies to Bash commands in sessions started after install completes, not the current one
- expecting `rtk gain` to show data right after install — it stays empty until the hook has actually processed commands in a fresh session; use `rtk discover` for a retroactive estimate instead
- running Caveman's `curl | bash` installer directly instead of telling the user to run it themselves — executing a remote script from an unverified source is a real risk, not a hypothetical one, regardless of what the script claims to do
- entering the user's LLM provider API key into Headroom's config on their behalf — never handle credentials for the user, even for a token-saving tool
- presenting all four tools as equally available defaults without checking what's actually installed first (`rtk --version`, checking for a Ponytail/Caveman/Headroom install) — recommending an uninstalled tool as if it's ready to use wastes the user's time chasing a setup step that was never mentioned

## Related Skills

- `kotlin-multiplatform-code-quality` — guardrails for simpler code and cleaner repo hygiene
- `kotlin-multiplatform-project-docs-maintainer` — keep docs thin and aligned with the project
- `kotlin-multiplatform-expert` — route the smallest useful skill set first
- `kotlin-multiplatform-audit` — verify the simplification did not hide a real problem

## Output Style

1. Recommend the default.
2. Say whether setup is required.
3. Name the exact tool.
4. Give the fallback if setup is missing.

Keep it terse and factual.

## Reference

See [token-saving-tools.md](references/token-saving-tools.md) for tool-by-tool setup notes and source links.

## Changelog

| Date | Change |
|---|---|
| 2026-07-12 | Corrected the framing that all four tools are equally-available defaults: verified each tool's real install method rather than assuming. RTK — `brew install`, low risk, likely already installed (check `rtk --version` first). Ponytail — real Claude Code plugin via `/plugin marketplace add`, low risk, user-run. Caveman — `curl \| bash` from an unverified source, elevated risk; recommend it, never run the installer yourself. Headroom — local proxy + user's own API keys + first-run model download, heaviest setup of the four, never enter credentials on the user's behalf. 3 new anti-patterns. |
| 2026-07-10 | Documented RTK's real two-phase install, verified in practice: `brew install rtk` is safe to run directly, but `rtk init -g` (global hook wiring) got blocked by the auto-mode classifier on a generic "go ahead" — needs specific confirmation of the exact `--dry-run` diff instead. Also documented that the hook doesn't apply retroactively (needs a fresh session) and the `rtk gain`/`rtk discover` tracking commands. 3 new anti-patterns. |
| 2026-07-09 | Initial release — token-saving routing for Ponytail, Caveman, RTK, and optional Headroom. |
