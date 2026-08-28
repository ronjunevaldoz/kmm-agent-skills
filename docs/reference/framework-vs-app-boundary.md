# Framework vs App Boundary Guide

This guide establishes the architectural boundaries for AI agent skills across **Core Engine / SDK Frameworks**, **Modular Extension Kits**, and **Consumer Apps / Games**.

---

## The 3-Tier Skills Taxonomy

```
┌────────────────────────────────────────────────────────┐
│ 1. CORE ENGINE / SDK FRAMEWORK (e.g. Engine Core, SDK) │
│    • Low-level primitives: ECS, Vulkan/WebGPU, Math    │
│    • ONLY commit engine/framework skills in .agents/   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ Extended By
┌────────────────────────────────────────────────────────┐
│ 2. MODULAR STARTER KITS (e.g. Subsystems, Templates)   │
│    • Subsystem Extensions: Viewpoint, World, Genre     │
│    • Turnkey Starter Kits with kit.json manifests      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ Consumed By
┌────────────────────────────────────────────────────────┐
│ 3. CONSUMER APP / GAME (e.g. Mobile App, Game Pack)    │
│    • End-user screens, domain converters, UI layouts   │
│    • Proprietary business logic & assets               │
└────────────────────────────────────────────────────────┘
```

---

## Golden Rules for Repositories

1. **Never Bulk-Copy All 74 Generic KMP Skills into Specialized Repositories**:
   - Committing mobile in-app purchases, biometrics, or MongoDB into a 3D graphics engine dilutes agent context.
   - Use **Global Installation** (`~/.agents/skills/`) for generic Kotlin Multiplatform rules.
2. **Use .agents/skills.lock for Version Pinning**:
   - When cherry-picking specific skills for a project, generate a `.agents/skills.lock` to track upstream release provenance.
