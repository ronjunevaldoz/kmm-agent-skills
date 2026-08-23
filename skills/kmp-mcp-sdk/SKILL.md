---
name: kmp-mcp-sdk
description: >
  Model Context Protocol (MCP) for Kotlin Multiplatform using the official
  modelcontextprotocol/kotlin-sdk (maintained with JetBrains). Covers building
  an MCP server that exposes tools/resources/prompts to an LLM client (Claude,
  Claude Code, MCP Inspector), building an MCP client that connects to an
  external MCP server from a Kotlin app, transport selection (STDIO,
  Streamable HTTP, SSE, WebSocket, ChannelTransport for tests), and Ktor
  wiring since the SDK does not bundle a Ktor engine transitively. Targets
  JVM, Native, JS, and Wasm from commonMain.
license: Apache-2.0
metadata:
  author: kmp-agent-skills
  last-updated: '2026-08-23'
  keywords:
    - MCP
    - Model Context Protocol
    - kotlin-sdk
    - modelcontextprotocol
    - MCP server
    - MCP client
    - MCP tool
    - MCP resource
    - MCP prompt
    - StreamableHttp
    - StdioServerTransport
    - Claude tool
    - LLM tool
    - agent tool
---

## When to Use This Skill

Use when you need to:
- Expose Kotlin/KMP functionality as tools, resources, or prompts an LLM client
  (Claude Desktop, Claude Code, MCP Inspector) can call
- Build an MCP client that connects a Kotlin app to an external MCP server
- Choose a transport (stdio for CLI/editor-spawned tooling, Streamable HTTP for
  a remote/hosted server, WebSocket for long-lived full-duplex sessions)
- Wire the SDK's server/client APIs onto a Ktor engine (the SDK doesn't pull
  one in transitively)

**Trigger keywords:** MCP, Model Context Protocol, kotlin-sdk, modelcontextprotocol,
MCP server, MCP client, MCP tool, MCP resource, MCP prompt, expose tool to Claude,
Streamable HTTP, StdioServerTransport, WebSocket transport, agent tool, LLM tool.

**Freshness rule:** the SDK ships frequently (0.15.0 as of 2026-08-23) and the MCP
spec itself is still evolving (elicitation, completions are newer additions) —
recheck the [Maven Central badge](https://central.sonatype.com/artifact/io.modelcontextprotocol/kotlin-sdk)
and the real README before pinning a version or relying on a capability flag
this skill doesn't cover.

---

## Recommendation First

**Default to the server-only artifact + Streamable HTTP transport** for the common
case — exposing Kotlin functionality as tools an LLM client calls. Use STDIO
instead only when the process is spawned directly by the client (an editor
plugin, a CLI helper) with no networking involved. Pull in the client artifact
only if the Kotlin app itself needs to call *out* to another MCP server —
that's a different role from serving tools, don't default to the umbrella
`kotlin-sdk` artifact if only one side is ever used.

Why Streamable HTTP over SSE for a new project: the README states it directly —
"Prefer Streamable HTTP for new projects." SSE exists for backwards
compatibility with older MCP clients, not as the current default.

---

## Installation

Three artifacts — pick based on which side you're building:

```kotlin
dependencies {
    // Both sides
    implementation("io.modelcontextprotocol:kotlin-sdk:$mcpVersion")
    // Server only
    implementation("io.modelcontextprotocol:kotlin-sdk-server:$mcpVersion")
    // Client only
    implementation("io.modelcontextprotocol:kotlin-sdk-client:$mcpVersion")
    // In-process client/server testing, no networking — see Testing below
    testImplementation("io.modelcontextprotocol:kotlin-sdk-testing:$mcpVersion")
}
```

**The SDK uses Ktor but does not add a Ktor engine transitively** — declare it
yourself:

```kotlin
dependencies {
    // Server, hosting on CIO
    implementation("io.ktor:ktor-server-cio:$ktorVersion")
    implementation("io.modelcontextprotocol:kotlin-sdk-server:$mcpVersion")

    // Client
    implementation("io.ktor:ktor-client-cio:$ktorVersion")
    implementation("io.modelcontextprotocol:kotlin-sdk-client:$mcpVersion")
}
```

In a KMP project, add it to `commonMain` — it works as both the common and
platform dependency:

```kotlin
commonMain {
    dependencies {
        implementation("io.modelcontextprotocol:kotlin-sdk:$mcpVersion")
    }
}
```

---

## Quickstart — Server Exposing a Tool

```kotlin
val mcpServer = Server(
    serverInfo = Implementation(name = "example-server", version = "1.0.0"),
    options = ServerOptions(
        capabilities = ServerCapabilities(tools = ServerCapabilities.Tools(listChanged = true)),
    )
)

mcpServer.addTool(
    name = "example-tool",
    description = "An example tool",
    inputSchema = ToolSchema(
        properties = buildJsonObject { put("input", buildJsonObject { put("type", "string") }) }
    )
) { request ->
    CallToolResult(content = listOf(TextContent("Hello, world!")))
}

embeddedServer(CIO, host = "127.0.0.1", port = 3000) {
    mcpStreamableHttp { mcpServer }
}.start(wait = true)
```

**Don't `install(ContentNegotiation)` yourself** — `mcpStreamableHttp {}` (and
`mcp {}` for SSE) install it automatically with `McpJson`; a second install
logs a warning.

Verify with the MCP Inspector before wiring a real client:
```bash
npx -y @modelcontextprotocol/inspector
# connect to http://localhost:3000/mcp
```

## Quickstart — Client

```kotlin
val httpClient = HttpClient { install(SSE) }
val client = Client(clientInfo = Implementation(name = "example-client", version = "1.0.0"))
val transport = StreamableHttpClientTransport(client = httpClient, url = "http://localhost:3000/mcp")

client.connect(transport)
val tools = client.listTools().tools
```

---

## MCP Primitives

| Primitive | Server Role | Client Role |
|---|---|---|
| **Tools** | `addTool` — model-controlled functions the LLM invokes | `listTools()`/`callTool()` |
| **Resources** | `addResource` — application-driven context (files, API data) at a stable URI | `listResources()`/`readResource()` |
| **Prompts** | `addPrompt` — user-controlled templates (think slash commands) | `listPrompts()`/`getPrompt()` |
| **Sampling** | requests an LLM completion *from the client* — reverse direction | executes the model call, returns the result |

Set a capability's `listChanged = true` only if that catalog can change at
runtime and the server actually emits the matching `notifications/*/list_changed`
— declaring it without emitting the notification is a real client-facing lie
about what the server does.

---

## Transport Selection

| Transport | Use when | Notes |
|---|---|---|
| **STDIO** (`StdioServerTransport`/`StdioClientTransport`) | Process is spawned directly by the client (editor plugin, CLI helper) | No networking setup; tunnels over stdin/stdout |
| **Streamable HTTP** (`mcpStreamableHttp`/`StreamableHttpClientTransport`) | Remote/hosted server — the recommended default for new projects | Single endpoint, default path `/mcp`, optional JSON-only or SSE streaming |
| **SSE** (`mcp {}` / `Application.mcp {}`) | Backwards compatibility with older MCP clients only | Not the default for new projects — Streamable HTTP supersedes it |
| **WebSocket** (`WebSocketClientTransport`) | Long-lived, full-duplex sessions behind a proxy that already terminates WebSockets | Heavier setup than Streamable HTTP; only reach for it when notification volume genuinely needs it |
| **ChannelTransport** | Tests / local development | Coroutine-channel-based, no network — full-duplex client↔server without spinning up a real server |

**Browser-based clients (MCP Inspector) need CORS** — install Ktor's CORS
plugin allowing/exposing `Mcp-Session-Id` and `Mcp-Protocol-Version` headers;
the README documents the exact block, don't guess at the header names.

---

## Connecting a Real Client

```bash
# MCP Inspector
npx -y @modelcontextprotocol/inspector --connect http://localhost:3000

# Claude Code
claude mcp add --transport http kotlin-mcp http://localhost:3000
```

---

## Testing — `ChannelTransport` (no real networking)

`ChannelTransport.createLinkedPair()` returns a connected `(clientTransport,
serverTransport)` pair over Kotlin coroutine channels — connect both
concurrently, then exercise the client as if it were talking to a real server.
Real pattern, verified against the SDK's own test suite:

```kotlin
@OptIn(ExperimentalMcpApi::class)
class MyServerTest {
    @Test
    fun `server registers the tool with the correct schema`() = runTest {
        val (clientTransport, serverTransport) = ChannelTransport.createLinkedPair()

        val client = Client(
            clientInfo = Implementation(name = "test-client", version = "1.0"),
            options = ClientOptions(),
        )

        joinAll(
            launch { client.connect(clientTransport) },
            launch { myServer.createSession(serverTransport) },
        )

        val tools = client.listTools().tools
        assertEquals(1, tools.size)

        client.close()
    }
}
```

`ChannelTransport` lives in a separate `kotlin-sdk-testing` artifact and is
marked `@ExperimentalMcpApi` — the `@OptIn` is required, not optional
boilerplate. This is the standard way to test tool/resource/prompt
registration without ever binding a real port.

---

## Common Anti-Patterns

- installing `ContentNegotiation` manually alongside `mcpStreamableHttp {}`/`mcp {}`
  — both already install it with `McpJson`; a second install just logs a warning
  for nothing
- pulling in the umbrella `kotlin-sdk` artifact when only one side (server or
  client) is ever used — pick `kotlin-sdk-server`/`kotlin-sdk-client` instead
- assuming a Ktor engine ships transitively — it doesn't; declare
  `ktor-server-cio`/`ktor-client-cio` (or your engine of choice) explicitly
- defaulting to SSE for a new server — Streamable HTTP is the current
  recommendation; SSE exists only for older-client compatibility
- setting `listChanged = true` on a capability without ever emitting the
  matching `notifications/*/list_changed` — the flag is a promise to the client,
  not decoration
- testing against a real HTTP server when `ChannelTransport` already gives a
  full-duplex client↔server pair with no networking

---

## Related Skills

- `kmp-network-layer` — the general Ktor client setup this SDK's client-side
  transports build on
- `kmp-kotlin-rpc` — a different Kotlin-to-Kotlin RPC mechanism; use MCP
  specifically when the peer is an LLM client, not another Kotlin service
- `kmp-ktor-auth-service` — if the MCP server needs authenticated access
- `kmp-feature-scaffold` — the module this SDK's server/client code slots into

---

## Output Style

When asked to add MCP support, respond in this order:
1. server or client (or both) — confirm which role is actually needed
2. the artifact(s) + Ktor engine dependency
3. transport choice with a one-line reason (Transport Selection table)
4. the minimal `addTool`/`addResource`/`addPrompt` registration for the actual ask
5. how to verify (`npx @modelcontextprotocol/inspector`)

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-23 | Initial release. User asked whether this collection covers `modelcontextprotocol/kotlin-sdk` — confirmed a real, zero-coverage gap (no MCP mention anywhere in the repo). Verified real and official (maintained with JetBrains, 1,441 stars, actively pushed, Apache-2.0-equivalent, KMP-native across JVM/Native/JS/Wasm) via `gh api` against the real repo and README before writing. Covers server/client artifact selection, the undocumented "no transitive Ktor engine" gotcha, transport selection (STDIO/Streamable HTTP/SSE/WebSocket/ChannelTransport), and the `ContentNegotiation` double-install warning — all pulled from the real README, not assumed. |
