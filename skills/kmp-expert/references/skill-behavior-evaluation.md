# Skill Behavior Evaluation

Use the versioned prompt corpus to evaluate a real agent's routing and boundary behavior.
This checks the agent result; it does not claim that metadata validation proves runtime behavior.

## Run an evaluation

1. Give each prompt in `../fixtures/skill-behavior-cases.json` to the target agent in an isolated task.
2. Record one result per case in this format:

```json
[
  {
    "id": "jni-bridge-not-cinterop",
    "selected_skills": ["kmp-jni-pro"],
    "boundary": "JNI is JVM-only; do not route this work to Kotlin/Native cinterop.",
    "evidence": [
      "phase-0-library-discovery",
      "phase-0.5-header-audit",
      "third-party-read-only"
    ]
  }
]
```

3. Score the recorded results:

```bash
python3 skills/kmp-expert/scripts/evaluate_skill_behavior.py \
  --responses /path/to/agent-results.json
```

The evaluator requires an exact skill set and boundary statement. Evidence tokens make the
required safety actions explicit, but a reviewer must still confirm the agent's cited work.

## Corpus coverage

The corpus includes the high-risk routing boundaries found in the audit:

| Boundary | Correct behavior |
|---|---|
| JNI vs Kotlin/Native cinterop | Route JVM JNI work to `kmp-jni-pro`; route `CPointer` and `.def` work to `kmp-expect-actual`. |
| Repository vs offline-first | Select offline-first only for synchronization or conflict resolution, with repository-pattern for repository boundaries. |
| Presenter vs Compose MVI | Use presenter-module for pure Kotlin ViewModels; use MVI for Compose Screen/Content and effect handling. |
| Custom design system vs shadcn-compose | Do not mix `AppTheme`/`App*` guidance into a `ShadcnTheme` project. |

Add a case whenever an incorrect routing decision reaches review or production. Keep each case
small, one-boundary-focused, and specific enough for another evaluator to reproduce.
