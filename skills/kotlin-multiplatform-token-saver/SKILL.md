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
  last-updated: '2026-07-09'
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

Default to the narrowest non-setup option:
1. Ponytail for overengineering and YAGNI pressure.
2. Caveman for terser replies.
3. RTK for noisy shell output.
4. Headroom only if the host already has it configured.

If Headroom is not configured, keep it optional and continue with Ponytail, Caveman,
or RTK instead.

## Tool Choice

Pick the narrowest tool that solves the problem:

- **Ponytail**: review/planning guardrail for "do we need this at all?" and
  "what is the smallest correct thing?"
- **Caveman**: make the model speak tersely without losing accuracy
- **RTK**: compress command output before it reaches the model
- **Headroom**: compress tool output, logs, files, and RAG chunks when the host is
  already set up

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
| 2026-07-09 | Initial release — token-saving routing for Ponytail, Caveman, RTK, and optional Headroom. |
