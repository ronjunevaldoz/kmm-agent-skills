# Framework vs Game Pack Boundary Guide

This guide establishes the architectural boundaries for AI agent skills across **Core Engine Frameworks**, **Starter Kit Extensions**, and **Game/Application Packs**.

---

## The 3-Tier Skills Taxonomy

```
┌────────────────────────────────────────────────────────┐
│ 1. CORE ENGINE FRAMEWORK (e.g. Awake Engine)           │
│    • Low-level primitives: ECS, Vulkan/WebGPU, Math    │
│    • ONLY commit engine-specific skills in .agents/    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ Extended By
┌────────────────────────────────────────────────────────┐
│ 2. MODULAR STARTER KITS (e.g. awake-lab/starter-kits)  │
│    • Subsystem Extensions: 4-Pillar Taxonomy           │
│    • Viewpoint, World, Network, Genre extensions       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ Consumed By
┌────────────────────────────────────────────────────────┐
│ 3. CONSUMER GAME / APP (e.g. flyffawaken, Mobile App)  │
│    • Game-specific converters (.o3d, .lnd)             │
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
