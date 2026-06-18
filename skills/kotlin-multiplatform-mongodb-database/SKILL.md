---
name: kotlin-multiplatform-mongodb-database
description: >
  MongoDB Kotlin Coroutine Driver pattern for Kotlin Multiplatform full-stack apps.
  Covers: server-side MongoDB access, document mapping, repository boundaries,
  typed database errors, reactive reads with Flow, change streams, and a scaffold
  script for repeated database setup. Use this for the backend data layer, not
  shared client persistence.
license: Apache-2.0
metadata:
  author: kmm-agent-skills
  last-updated: '2026-06-13'
  keywords:
    - MongoDB
    - Kotlin coroutine driver
    - database
    - repository
    - Flow
    - change stream
    - server-side Kotlin
    - KMP backend
    - document mapping
    - collection
    - query
---

## When to Use This Skill

Use this skill when you need to:
- Build or review a MongoDB-backed backend data layer for a KMP app
- Keep document mapping and repository code cleanly separated
- Use Flow or change streams for reactive reads
- Model typed database failures instead of leaking driver exceptions upward
- Scaffold repeated database setup for a new service

**Recommended default:** keep MongoDB on the server side behind a repository boundary,
map documents to domain models at the edge, and expose typed errors to the caller.

**Trigger keywords:** MongoDB, database, collection, repository, document mapping,
Flow, change stream, server-side Kotlin, coroutine driver, typed errors, backend data.

**Freshness rule:** the MongoDB Kotlin coroutine driver evolves independently of the JVM
driver — recheck the [official docs](https://www.mongodb.com/docs/drivers/kotlin/coroutine/)
before upgrading or scaffolding.

---

## Recommendation First

Default to this pattern:

1. **Server-side MongoDB only** with the official Kotlin coroutine driver.
2. **Repository boundary** between collection access and the rest of the app.
3. **Typed document mapping** at the edge, not in route handlers.
4. **Flow / change streams** for reactive reads when the data should update live.

Why:
- the driver is officially positioned for server-side Kotlin coroutine apps
- repositories keep route handlers and services small
- typed mapping keeps BSON/documents from leaking through the app

---

## Project Structure

Keep the database layer separate from auth and routes:

```text
server/
  database/
    MongoClientFactory.kt
    di/DatabaseModule.kt
  user/
    data/UserCollection.kt
    data/UserDocument.kt
    repository/UserRepository.kt
    repository/UserRepositoryImpl.kt
```

Rules:
- database bootstrap lives in one place
- collection access is not spread across route handlers
- document mapping happens in the data layer
- repositories expose domain models, not BSON documents

---

## Core Pattern

Use the coroutine driver with a client + database + collection boundary:

```kotlin
class UserRepositoryImpl(
    private val collection: MongoCollection<UserDocument>,
) : UserRepository {

    override suspend fun findById(id: String): User? =
        collection.findOneById(id)?.toDomain()

    override fun watchUsers(): Flow<List<User>> =
        collection.watch().map { events -> events.map { it.fullDocument.toDomain() } }
}
```

Typed errors stay close to the repository:

```kotlin
sealed interface DatabaseError {
    data object NotFound : DatabaseError
    data object Unauthorized : DatabaseError
    data class Unknown(val message: String) : DatabaseError
}
```

---

## Reactive Reads

Use `Flow` when the UI or service should react to updates:
- live dashboards
- collections that change often
- admin views
- background sync listeners

Do not overuse change streams for simple CRUD if a plain repository call is enough.

---

## Scaffold Script

- `scripts/scaffold_mongodb_database.py` — creates a starter MongoDB data-layer folder
  with client, repository, document, and DI files.

---

## Related Skills

- `kotlin-multiplatform-ktor-auth-service` — auth service depends on the `UserRepository` built here
- `kotlin-multiplatform-kotlin-rpc` — RPC service implementations delegate to MongoDB repositories
- `kotlin-multiplatform-repository-pattern` — the same repository interface/implementation pattern applied server-side
- `kotlin-multiplatform-dependency-injection` — `MongoClient` and collection bindings are registered as Koin singletons

---

## Common Anti-Patterns

- accessing collections directly from route handlers — always go through a repository
- leaking `BsonDocument` or `MongoCollection` types out of the data layer — map to domain types at the boundary
- using change streams for every collection by default — use them only when live updates are needed
- constructing `MongoClient` in every call instead of sharing one instance via Koin — exhausts connection pools
- catching `MongoException` globally and swallowing it — return a typed `DatabaseError` instead

If the connection pool is exhausted or queries are slow, check that only one `MongoClient` is registered per DI scope.

---

## Output Style

When asked about MongoDB setup or data access, respond in this order:
1. recommendation (server-side only, repository boundary, typed errors)
2. project structure (client factory, collection, repository, DI module)
3. code snippet (repository impl with one findById and one Flow)
4. why that approach is preferred
5. main alternative (direct collection access, other drivers)

Keep the snippet to one repository method. Map to the user's actual collection and document names when provided.

