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
- Requires host-level setup so the agent can route commands through RTK.

Source: [rtk-ai/rtk](https://github.com/rtk-ai/rtk)

## Headroom

- Use when tool output, logs, files, or RAG chunks need compression before LLM context.
- Best for heavy tool sessions where the host already supports Headroom.
- Keep this optional until the setup exists; do not block a task on it.

Source: [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)
