---
name: kmp-compose-web-performance
description: >
  Live browser performance analysis for a Compose Multiplatform Web (wasmJs) target,
  using the official Chrome DevTools MCP server (github.com/ChromeDevTools/chrome-devtools-mcp)
  — performance traces, Lighthouse audits, network waterfall, and Wasm bundle-size
  awareness specific to Skiko's canvas-based rendering. Does NOT cover micro-benchmarking
  Kotlin functions (see kmp-benchmark) — this is live, real-browser profiling of the
  running app, not isolated function timing.
license: Apache-2.0
metadata:
  author: kmp-agent-skills
  last-updated: '2026-08-31'
  keywords:
    - web performance
    - chrome devtools
    - lighthouse
    - performance trace
    - wasm bundle size
    - core web vitals
    - network waterfall
    - skiko performance
    - compose web performance
    - first paint
    - wasmJs performance
    - js glue minification
    - wasmJsBrowserProductionWebpack
    - webpack minification
---

## When to Use This Skill

Use this skill when:
- profiling a Compose Multiplatform Web (`wasmJs`) target's real load/runtime performance
  in an actual browser — first paint, time-to-interactive, dropped frames
- running a Lighthouse audit against a deployed or locally-served Compose Web build
- investigating a slow network waterfall (large `.wasm` binary, unoptimized resource
  loading) for the web target specifically
- comparing before/after performance for a change believed to affect Web target load time

Do NOT use this skill when:
- micro-benchmarking a Kotlin function's execution time in isolation — that's
  `kmp-benchmark` (kotlinx-benchmark), not live browser profiling
- the performance concern is Android/iOS/Desktop — this skill is Web/Wasm-specific;
  Android has its own profiler (Android Studio), Desktop/JVM has JFR/async-profiler
- general browser automation/testing with no performance angle — that's outside this
  collection's current scope entirely

**Trigger keywords:** web performance, chrome devtools, lighthouse, lighthouse audit,
performance trace, wasm bundle size, core web vitals, network waterfall, skiko
performance, compose web performance, first paint, time to interactive, wasmJs
performance, slow web load.

**Freshness rule:** Compose Multiplatform for Web (wasmJs) only reached Beta in CMP
1.9.0 (September 2025, verified against JetBrains' own release blog) — bundle-size
optimization guidance is actively evolving with no single consolidated official doc as
of this writing. Recheck [JetBrains' Kotlin blog](https://blog.jetbrains.com/kotlin/)
and the [chrome-devtools-mcp repo](https://github.com/ChromeDevTools/chrome-devtools-mcp)
before treating any specific number in this skill as current.

---

## Recommendation First

Wire the official `chrome-devtools-mcp` (not a third-party reimplementation — verified
directly against its own repo) and use its trace/Lighthouse tools against a locally
served Compose Web build, rather than guessing at performance from reading Kotlin
source. Skiko's canvas-based rendering and the Wasm binary's own load time are real,
measurable factors a static code read cannot estimate — profile first, then act on
what the trace actually shows.

---

## Setup: Chrome DevTools MCP

```bash
# Claude Code — MCP only
claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest
```

Or as a standard MCP client config:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

For headless CI-style runs, isolated per invocation:

```json
"args": ["-y", "chrome-devtools-mcp@latest", "--headless", "--isolated=true"]
```

Performance tools may send URLs to Google's CrUX API for real-world field-data
comparison — disable with `--no-performance-crux` if that's not wanted (e.g. a
not-yet-public staging URL).

---

## Workflow: profiling a Compose Web build

1. **Serve the build locally** — `./gradlew wasmJsBrowserDevelopmentRun` (dev) or serve
   the `wasmJsBrowserDistribution` output (prod-like) — profile the prod build for
   real numbers; dev builds are unminified and unrepresentative.
2. **Navigate and record a trace**:
   - `navigate_page` to the local URL
   - `performance_start_trace`
   - Interact with the app the way a real user would (the input-automation tools —
     `click`, `fill`, `hover` — or just let it idle through initial load)
   - `performance_stop_trace`
   - `performance_analyze_insight` for the actionable summary
3. **Run a Lighthouse audit** (`lighthouse_audit`) for a standardized score plus
   Core Web Vitals (LCP, CLS, TBT) — useful as a single before/after number to track
   across changes, alongside the raw trace for root-causing a regression.
4. **Check the network waterfall** (`list_network_requests` / `get_network_request`)
   for the `.wasm` binary's own size and load time — this is usually the single
   largest asset on first load for a Compose Web app and the first thing to check
   before assuming a rendering-side cause.

---

## Wasm/Skiko-specific things to check

- **Canvas-based rendering**: Compose Web renders through Skiko's WASM runtime onto an
  HTML5 Canvas — this is architecturally different from a DOM-based web framework, so
  DOM-inspection-oriented performance advice (virtual-DOM diffing, layout thrashing from
  CSS) mostly doesn't apply here. What does apply: dropped frames during animation
  (visible in the trace as long frame times), and canvas resize/redraw cost.
- **Bundle size is a real, acknowledged, still-evolving concern** — JetBrains' own
  contributors have flagged that pulling in `compose-resources` currently drags in
  `compose-foundation`/`compose-ui`/Skiko transitively, bloating the bundle even for
  code paths that don't need canvas rendering (verified via a real, open
  JetBrains/compose-multiplatform GitHub issue, not assumed). Check the network
  waterfall's `.wasm` file size before and after adding a new dependency to catch this
  early, rather than discovering it once the bundle is already large.
- **No fabricated size targets** — this skill deliberately does not state a "keep it
  under N KB" number. No such official target exists as of this writing (Beta status,
  per the Freshness rule above). Track your own project's `.wasm` size trend over time
  via the network waterfall instead of comparing against an unsourced number.

---

## Build-Time: JS Glue-Code Minification

The `.wasm` binary isn't the only build output — Kotlin/Wasm also generates a JS
loader/glue file that bootstraps and calls into it. Verified against
[kotlinlang.org's Kotlin/JS production build docs](https://kotlinlang.org/docs/js-project-setup.html)
(the `wasmJs` browser target shares the same webpack-based Kotlin Gradle plugin
pipeline as the `js` target, just task-name-prefixed `wasmJs` instead of `js`):

- **`./gradlew wasmJsBrowserProductionWebpack`** runs webpack in production mode against
  the glue code — dead-code elimination and minification, same as the `js` target's
  `jsBrowserProductionWebpack`.
- **`./gradlew wasmJsBrowserDistribution`** (the task already referenced above for
  profiling) depends on the production webpack build and assembles the full deployable
  output at `build/dist/wasmJs/productionExecutable` — this is the minified, deployable
  artifact; `wasmJsBrowserDevelopmentRun`'s output is not.
- **Verify it actually happened** — don't assume: open the built `.js` file in
  `build/dist/wasmJs/productionExecutable` and confirm it's a single dense minified
  line, not readable multi-line source. A glue file that's still readable after a
  "production" build means the distribution task silently ran in dev mode, or a custom
  webpack config disabled minification.
- **Customizing or disabling minification** goes through the same mechanism as any
  Kotlin/JS webpack target: a `commonWebpackConfig { }` block in `build.gradle.kts`, or
  a `webpack.config.d/*.js` file for raw webpack config overrides (e.g.
  `config.optimization.minimize = false` to intentionally disable it, which you'd only
  ever want for debugging a production-only bug, never for a real deploy).

This is a build-config check, not a live-profiling one — for the Android counterpart
(class/function/property renaming via R8), see `kmp-proguard-r8`; a KMP app targeting
both Android and Web should verify both, not just the platform that happened to get
checked first.

---

## Testing a Performance Claim

A performance claim ("this is slow," "this got faster") is only as good as the
measurement behind it. Before reporting a result:

1. **Re-run the trace at least twice** — a single trace can be noise (a stray GC
   pause, a background tab stealing CPU). Confirm the pattern repeats.
2. **Compare against the same build type** — a prod-vs-dev comparison is meaningless
   (see the anti-pattern below); before/after must both be `wasmJsBrowserDistribution`
   output, same machine, same network conditions if possible (`--isolated=true`
   reduces cross-run state leakage).
3. **Confirm the Lighthouse score and the raw trace agree** — if Lighthouse says LCP
   improved but the raw trace shows no change in paint timing, one of the two runs is
   unrepresentative; re-run rather than reporting a contradiction as a result.

---

## Common Anti-Patterns

- **Profiling a dev build and drawing prod conclusions** — `wasmJsBrowserDevelopmentRun`
  output is unminified and includes dev-only overhead; always profile the
  `wasmJsBrowserDistribution` (or equivalent prod) output for real numbers.
- **Reading Kotlin source to guess at performance instead of tracing** — Skiko's
  rendering cost and the Wasm binary's load time are runtime facts, not something a
  static code read can estimate accurately.
- **Treating a third-party Puppeteer-script reimplementation as equivalent to the
  official MCP** — use `github.com/ChromeDevTools/chrome-devtools-mcp` directly; a
  third-party wrapper found elsewhere may not track the official tool's own
  trace/Lighthouse capabilities or maintenance.
- **Fixating on a specific bundle-size number found in a blog post or forum** — no
  official target exists yet (Beta status); track your own trend instead.

---

## Related Skills

- `kmp-benchmark` — micro-benchmarking a Kotlin function's execution time in isolation
  (kotlinx-benchmark), not live browser profiling; use that first to isolate *which*
  function is slow, this skill to see the actual browser-side impact
- `kmp-ci-github-actions` — Web (JS + WasmJs) test matrix; a Lighthouse/trace check
  could be added as a CI step once a baseline is established
- `kmp-network-layer` — the Ktor Web engine (JS/CIO); a network-layer misconfiguration
  can show up in this skill's network waterfall as redundant/slow requests
- `kmp-proguard-r8` — the Android counterpart (R8 class/function/property renaming);
  covers Android release builds only, not `wasmJs`'s JS glue-code minification

---

## Output Style

When asked to investigate Web/Wasm performance, respond in this order:
1. whether the report is about a dev or prod build (ask if unclear — dev-build numbers
   are not actionable)
2. the profiling steps to run (trace, Lighthouse, network waterfall)
3. what the results actually show, not a guess from reading source
4. the specific fix, tied to what the trace/audit showed

Keep this scoped to Web/Wasm — route Android/iOS/Desktop performance questions
elsewhere; this skill's tooling (Chrome DevTools) doesn't apply to those targets.

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-31 | Added "Build-Time: JS Glue-Code Minification" — user asked whether this collection covers wasmJs JS-glue minification the way `kmp-proguard-r8` covers Android R8 renaming, and it didn't. Verified real against kotlinlang.org's Kotlin/JS production build docs (the `wasmJs` browser target shares the same webpack pipeline as `js`, just task-prefixed differently): `wasmJsBrowserProductionWebpack` applies dead-code elimination + minification, `wasmJsBrowserDistribution` depends on it and assembles the deployable output, customization goes through `commonWebpackConfig`/`webpack.config.d`. Cross-referenced `kmp-proguard-r8` in both directions so a KMP app targeting both Android and Web has a path to verify both platforms' minification, not just whichever got checked first. |
| 2026-08-03 | Initial skill — wires the official `chrome-devtools-mcp` (verified against its own repo, not a third-party reimplementation found via a skill-listing site) for live Compose Web/Wasm performance profiling. Covers setup, the trace/Lighthouse/network-waterfall workflow, and Wasm/Skiko-specific considerations (canvas rendering vs DOM, the real but still-evolving bundle-size concern) — deliberately with no fabricated size targets, since CMP Web is Beta as of CMP 1.9.0 (Sept 2025) with no single consolidated official optimization doc yet. |
