---
name: kmp-heal-docs
description: Self-heal project documentation sitemap (docs/README.md), verify link hygiene, and archive stale task plans.
---

# Self-Heal Project Documentation

Run the self-healing documentation engine across the project:

```bash
python3 .agents/skills/kmp-project-docs-maintainer/scripts/heal_docs.py || python3 skills/kmp-project-docs-maintainer/scripts/heal_docs.py
```

This command:
1. Rebuilds the high-density sitemap table in `docs/README.md`.
2. Archives finished tasks from `docs/tasks/*.md` into `docs/tasks/archive/`.
3. Verifies zero broken relative links.
4. Prevents AI agents from performing expensive recursive scans.
