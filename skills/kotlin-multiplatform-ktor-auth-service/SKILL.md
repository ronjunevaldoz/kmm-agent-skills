---
name: kotlin-multiplatform-ktor-auth-service
description: >
  Ktor-based auth service pattern for Kotlin Multiplatform full-stack apps. Covers:
  bearer and JWT auth, sessions when stateful browser-style sessions are a better fit,
  Ktor RPC when the client and server are both Kotlin-first, typed auth errors, route
  guards, refresh/logout flows, and a small scaffold script for repeated auth module
  setup. Use this for server-side auth, not shared UI auth state.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-13'
  keywords:
    - auth
    - authentication
    - authorization
    - Ktor auth
    - bearer token
    - JWT
    - sessions
    - Ktor RPC
    - login
    - refresh token
    - logout
    - KMP backend
    - server auth
---

## When to Use This Skill

Use this skill when you need to:
- Build or review a Ktor auth service for a KMP full-stack app
- Choose between bearer/JWT auth, sessions, or Ktor RPC
- Add login, refresh, logout, and protected routes
- Keep auth state and transport errors out of shared UI code
- Scaffold the repeated auth service files for a new project

**Recommended default:** bearer + JWT for API auth, sessions only when you need
stateful browser-style persistence, and Ktor RPC only when both sides are Kotlin-first.

**Trigger keywords:** auth, authentication, authorization, bearer token, JWT, sessions,
Ktor auth, Ktor RPC, login, refresh token, logout, protected route, auth service.

---

## Recommendation First

Default to this stack:

1. **Bearer + JWT** for request authorization.
2. **Sessions** only when the product truly wants server-managed session state.
3. **Ktor RPC** only when the client and server are both Kotlin and the contract is
   better expressed as Kotlin procedures than REST resources.

Why:
- bearer/JWT is the most explicit boundary for APIs
- sessions are useful, but they add server state you should choose deliberately
- Ktor RPC is nice for Kotlin-first systems, but it is not the default for every app

---

## Project Structure

Keep auth code separate from the rest of the backend:

```text
server/
  auth/
    routes/AuthRoutes.kt
    service/AuthService.kt
    service/TokenService.kt
    model/AuthRequest.kt
    model/AuthResponse.kt
    model/AuthError.kt
    di/AuthModule.kt
  user/
    repository/UserRepository.kt
    data/UserRepositoryImpl.kt
```

Rules:
- routes stay thin
- business rules live in services
- token issuing and verification stay in one place
- user persistence sits behind a repository boundary

---

## Core Pattern

Use Ktor auth with typed auth errors and explicit route guards:

```kotlin
install(Authentication) {
    bearer("auth-bearer") {
        authenticate { tokenCredential ->
            authService.verifyAccessToken(tokenCredential.token)
        }
    }
    jwt("auth-jwt") {
        verifier(authService.jwtVerifier)
        validate { credential -> authService.validateClaims(credential) }
    }
}

routing {
    authRoutes()
    authenticate("auth-bearer") {
        protectedRoutes()
    }
}
```

For login and refresh:

```kotlin
val result = authService.login(email, password)
when (result) {
    is AuthResult.Success -> call.respond(result.body)
    is AuthResult.InvalidCredentials -> call.respond(HttpStatusCode.Unauthorized)
    is AuthResult.Locked -> call.respond(HttpStatusCode.Forbidden)
}
```

---

## Ktor RPC Guidance

Use Ktor RPC only when the boundary is Kotlin-to-Kotlin and the procedure style is a
better fit than REST resources.

Good fit:
- internal service calls
- Kotlin client and Kotlin server under one product
- strongly typed request/response pairs

Not a good fit:
- public APIs with many non-Kotlin consumers
- simple REST resources
- auth flows that need obvious HTTP semantics

---

## Scaffold Script

- `scripts/scaffold_auth_service.py` — creates a starter auth-service folder with route,
  service, model, and DI files.

