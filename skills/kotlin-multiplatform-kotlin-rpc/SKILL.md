---
name: kotlin-multiplatform-kotlin-rpc
description: >
  Kotlin RPC for Kotlin Multiplatform full-stack apps. Covers when to use Kotlin RPC
  instead of REST or gRPC, shared request/response contracts, client/server module
  layout, auth boundaries, service interface design, and a scaffold script for initial
  RPC project setup. Use this for Kotlin-to-Kotlin service boundaries, especially when
  the client and server both live in the same KMP ecosystem.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-13'
  keywords:
    - kotlin rpc
    - kRPC
    - kotlinx rpc
    - Ktor RPC
    - RPC
    - service interface
    - client server contract
    - KMP backend
    - Kotlin-first transport
    - typed contract
    - service stub
    - shared contract
---

## When to Use This Skill

Use this skill when you need to:
- Design a Kotlin-first RPC boundary for a KMP app
- Decide whether RPC fits better than REST or gRPC
- Split shared service contracts from server implementation
- Build an authenticated RPC flow in a Ktor-backed app
- Scaffold the initial client/server RPC module layout

**Recommended default:** use Kotlin RPC only when both sides are Kotlin-first and the
procedure style is a better fit than resource-oriented REST.

**Trigger keywords:** kotlin rpc, kRPC, kotlinx rpc, Ktor RPC, RPC service, typed
contract, service stub, client/server contract, shared RPC models, Kotlin-first API.

## Recommendation First

Default to this approach:

1. **Use Kotlin RPC for Kotlin-to-Kotlin boundaries.**
2. **Keep contracts small and explicit.**
3. **Keep auth outside the RPC transport** and guard the server route first.
4. **Keep public REST APIs separate** when non-Kotlin clients need stable HTTP semantics.

Why:
- Kotlin RPC is a good fit when the codebase already shares Kotlin models and logic
- REST is still the clearer choice for public, mixed-client APIs
- auth, persistence, and transport should remain separate concerns

## Project Structure

Keep the shared contract and the server implementation split cleanly:

```text
shared/
  rpc/
    GreetingService.kt
    model/GreetingRequest.kt
    model/GreetingResponse.kt
server/
  rpc/
    GreetingRpcModule.kt
  auth/
    ...
client/
  rpc/
    GreetingRpcClient.kt
```

Rules:
- service interfaces and request/response types live in shared code
- server modules install and expose the RPC implementation
- client modules own the transport setup and generated stubs
- auth stays at the Ktor route boundary, not inside domain logic

## Core Pattern

Model the RPC boundary as a service interface plus shared DTOs:

```kotlin
interface GreetingService {
    suspend fun greet(request: GreetingRequest): GreetingResponse
}

data class GreetingRequest(val name: String)
data class GreetingResponse(val message: String)
```

Then wire the implementation behind a Ktor server boundary:

```kotlin
// Pseudocode sketch - adapt to the current official Ktor RPC API
fun Application.rpcModule() {
    routing {
        // authenticate("auth-bearer") { rpc(...) }
        // expose GreetingServiceImpl behind the RPC transport
    }
}
```

Keep the client side thin:

```kotlin
class GreetingRpcClient(
    // transport + generated stub setup lives here
) {
    suspend fun greet(name: String): String
}
```

## When Not to Use It

Do not default to Kotlin RPC when:
- the API is public and must support many non-Kotlin consumers
- the domain is already resource-oriented and REST is simpler
- the transport needs to be easy to inspect with standard HTTP tooling
- you need a stable cross-language contract with minimal Kotlin coupling

## Docs to Recheck First

Before changing this skill, re-read the current official docs:
- [First steps with Kotlin RPC](https://ktor.io/docs/tutorial-first-steps-with-kotlin-rpc.html)
- [Build a full-stack application with Kotlin Multiplatform](https://ktor.io/docs/full-stack-development-with-kotlin-multiplatform.html)
- [Authentication and authorization in Ktor Server](https://ktor.io/docs/server-auth.html)
- [Type-safe routing](https://ktor.io/docs/type-safe-routing.html)

## Scaffold Script

- `scripts/scaffold_kotlin_rpc.py` - creates a starter shared/server/client RPC layout.

---

## Related Skills

- `kotlin-multiplatform-ktor-auth-service` — auth guards for the RPC route live here
- `kotlin-multiplatform-mongodb-database` — RPC service implementations often delegate to a MongoDB repository
- `kotlin-multiplatform-feature-scaffold` — the shared contract module is a peer of the server and client modules
- `kotlin-multiplatform-network-layer` — use this instead of RPC when the client is non-Kotlin or the API is public

---

## Common Anti-Patterns

- using Kotlin RPC for a public API consumed by non-Kotlin clients — REST is clearer
- putting auth logic inside the RPC service interface — auth belongs at the Ktor route boundary
- keeping the RPC contract in the server module — it must live in shared code so the client can use it
- using RPC for simple CRUD resources that REST already handles well — adds complexity without benefit
- skipping the `authenticated {}` Ktor block before the RPC route — exposes the service unauthenticated

If the contract needs to be consumed by a browser frontend or a non-Kotlin mobile client, use REST.

---

## Output Style

When asked about Kotlin RPC, respond in this order:
1. recommendation (use RPC only when both sides are Kotlin-first)
2. project structure (shared contract, server module, client module)
3. code snippet (service interface + server wiring sketch)
4. why RPC fits (or doesn't fit) the stated use case
5. main alternative (REST, gRPC)

Lead with the fit/no-fit decision. Keep the code snippet to the interface and one route binding.
