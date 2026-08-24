---
name: kmp-kotlinpoet
description: >
  Building a custom KSP (Kotlin Symbol Processing) annotation processor that
  generates Kotlin source with KotlinPoet — FileSpec/TypeSpec/FunSpec/
  PropertySpec builders, format specifiers, the two-module processor
  structure, ServiceLoader registration, and the kotlinpoet-ksp interop
  module for converting KSP's KSType/KSClassDeclaration into KotlinPoet's
  TypeName/ClassName. Use when a project wants compile-time code generation
  from annotations instead of runtime reflection. Does NOT cover consuming
  an existing KSP processor (Koin's annotated mode, Room, etc.) — that's
  ordinary dependency usage; this skill is for authoring a new processor.
license: Apache-2.0
metadata:
  author: kmp-agent-skills
  last-updated: '2026-08-24'
  keywords:
    - KotlinPoet
    - KSP
    - Kotlin Symbol Processing
    - annotation processor
    - code generation
    - SymbolProcessor
    - SymbolProcessorProvider
    - FileSpec
    - TypeSpec
    - FunSpec
    - custom annotation
    - compile-time codegen
---

## When to Use This Skill

Use when you need to:
- Generate Kotlin source files at compile time from a custom annotation
  (e.g. `@GenerateKoinModule`, `@AutoMapper`, `@Parcelize`-style codegen)
- Build a KSP processor and want type-safe source generation instead of
  hand-built string templates
- Convert a KSP `KSType`/`KSClassDeclaration` into a KotlinPoet `TypeName`/`ClassName`

Do NOT use this skill to consume an already-published KSP processor (Koin's
`@KoinViewModel`, Room, Moshi codegen) — that's ordinary dependency usage,
nothing to author. This skill is for writing a *new* processor.

**Trigger keywords:** KotlinPoet, KSP, Kotlin Symbol Processing, annotation
processor, code generation, SymbolProcessor, SymbolProcessorProvider,
FileSpec, TypeSpec, FunSpec, custom annotation, compile-time codegen,
generate Kotlin source.

**Freshness rule:** KSP version tracks the Kotlin compiler version closely
(a KSP version mismatched to the project's Kotlin version fails to load) —
recheck the current KSP/Kotlin compatibility table before pinning a version.

---

## Recommendation First

**KSP over kapt** — verified: KSP runs up to twice as fast because it skips
kapt's intermediate Java stub generation, and its API is lazy by design.
There's no real reason to reach for kapt for a new processor in 2026.
**KotlinPoet over hand-built string templates** — type-safe builders catch a
malformed generated file at processor-compile time instead of producing
Kotlin that fails to parse only when the *consumer* project builds.

---

## KotlinPoet API — Builders and Format Specifiers

```kotlin
val greeterClass = ClassName("", "Greeter")

val file = FileSpec.builder("", "HelloWorld")
    .addType(
        TypeSpec.classBuilder("Greeter")
            .primaryConstructor(
                FunSpec.constructorBuilder()
                    .addParameter("name", String::class)
                    .build()
            )
            .addProperty(
                PropertySpec.builder("name", String::class)
                    .initializer("name")
                    .build()
            )
            .addFunction(
                FunSpec.builder("greet")
                    .addStatement("println(%P)", "Hello, \$name")
                    .build()
            )
            .build()
    )
    .addFunction(
        FunSpec.builder("main")
            .addParameter("args", String::class, VARARG)
            .addStatement("%T(args[0]).greet()", greeterClass)
            .build()
    )
    .build()

file.writeTo(System.out)
```

| Specifier | Meaning |
|---|---|
| `%S` | String literal — escapes and quotes automatically |
| `%T` | Type reference — resolves and adds the import automatically |
| `%M` | Member reference (top-level function/property) |
| `%N` | Name reference to another generated declaration |
| `%L` | Literal — inserted verbatim, no escaping |
| `%P` | String template — interpolates `$name`-style placeholders |

**Use `%S`/`%T`, never raw string concatenation, for anything that becomes
generated source** — `%T` also resolves the import automatically; hand-building
`"import " + clazz.qualifiedName` duplicates work KotlinPoet already does
correctly, including nested-type and same-package edge cases.

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.squareup:kotlinpoet:1.18.1")
    implementation("com.squareup:kotlinpoet-ksp:1.18.1")   // KSP interop — see below
}
```

**Design note, real and worth knowing**: KotlinPoet generates code with
explicit visibility modifiers by default — this keeps generated code
compatible with a consumer project that has `explicitApi()` turned on. Don't
strip visibility modifiers from generated declarations expecting a smaller
diff; the explicitness is deliberate.

---

## KSP Processor Structure — Two Modules

```
project-root/
├── annotations/        ← the @annotation itself, shared by processor + consumers
├── processor/           ← the KSP processor module (JVM-only)
│   └── src/main/kotlin/.../GenerateKoinModuleProcessor.kt
│   └── src/main/resources/META-INF/services/
│       com.google.devtools.ksp.processing.SymbolProcessorProvider
└── app/                 ← the consuming module, applies `ksp(project(":processor"))`
```

```kotlin
// processor/build.gradle.kts
plugins { kotlin("jvm") }
dependencies {
    implementation(project(":annotations"))
    implementation("com.google.devtools.ksp:symbol-processing-api:2.3.6")
    implementation("com.squareup:kotlinpoet-ksp:1.18.1")
}
```

```kotlin
// app/build.gradle.kts — the consumer
plugins { id("com.google.devtools.ksp") }
dependencies {
    implementation(project(":annotations"))
    ksp(project(":processor"))
}
```

KSP discovers the processor via Java's `ServiceLoader` — the
`META-INF/services/com.google.devtools.ksp.processing.SymbolProcessorProvider`
file (containing the provider's fully-qualified class name) is not optional
boilerplate; a processor with `SymbolProcessorProvider` implemented but this
file missing silently never runs.

---

## Worked Example — `@GenerateKoinModule`

Consistent with this collection's own Koin convention (`kmp-dependency-injection`):
an annotation that generates a Koin module wiring every annotated class.

```kotlin
// annotations module
@Target(AnnotationTarget.CLASS)
annotation class GenerateKoinModule
```

```kotlin
// processor module
class GenerateKoinModuleProcessor(
    private val codeGenerator: CodeGenerator,
    private val logger: KSPLogger,
) : SymbolProcessor {

    override fun process(resolver: Resolver): List<KSAnnotated> {
        val symbols = resolver.getSymbolsWithAnnotation(GenerateKoinModule::class.qualifiedName!!)
        val classes = symbols.filterIsInstance<KSClassDeclaration>()
        if (classes.none()) return emptyList()

        val fileSpec = FileSpec.builder("com.example.di", "GeneratedKoinModule")
            .addProperty(
                PropertySpec.builder("generatedModule", ClassName("org.koin.core.module", "Module"))
                    .initializer(
                        buildCodeBlock {
                            add("org.koin.dsl.module {\n")
                            classes.forEach { cls ->
                                add("    factoryOf(::%T)\n", cls.toClassName())
                            }
                            add("}")
                        }
                    )
                    .build()
            )
            .build()

        // Originating-file tracking — required for KSP's incremental compilation.
        // Skipping this means the processor silently fails to re-run when the
        // annotated source file changes, a real and easy-to-miss bug class.
        val dependencies = Dependencies(aggregating = true, *classes.mapNotNull { it.containingFile }.toTypedArray())
        fileSpec.writeTo(codeGenerator, dependencies)

        return emptyList()
    }
}

class GenerateKoinModuleProcessorProvider : SymbolProcessorProvider {
    override fun create(environment: SymbolProcessorEnvironment) =
        GenerateKoinModuleProcessor(environment.codeGenerator, environment.logger)
}
```

`cls.toClassName()` is the `kotlinpoet-ksp` interop module doing the real
work — converting a `KSClassDeclaration` into a KotlinPoet `ClassName`
without hand-parsing the qualified name string.

---

## `kotlinpoet-ksp` Interop — Converting KSP Types

```kotlin
// KSType → TypeName
val typeName = ksProperty.type.toTypeName()          // e.g. kotlin.String as a ClassName

// KSModifier → KModifier
val modifiers = ksProperty.modifiers.mapNotNull { it.toKModifier() }   // [KModifier.INLINE]

// Visibility → KModifier
val visibility = ksProperty.getVisibility().toKModifier()              // KModifier.INTERNAL
```

For generic types, resolve with a `TypeParameterResolver` rather than
converting a type parameter in isolation — a bare type parameter name (`T`)
has no meaning outside the declaration that introduces it; the resolver
carries that scope through nested generic contexts correctly.

---

## Common Anti-Patterns

- **Hand-building generated Kotlin via string concatenation** instead of
  KotlinPoet's builders — a missing import or an unescaped string in the
  generated file only surfaces as a *consumer* build failure, not a
  processor-compile-time error.
- **Skipping originating-file tracking in `Dependencies`** — breaks KSP's
  incremental compilation; the processor silently doesn't re-run when the
  source it depends on changes, and a stale generated file ships.
- **Missing the `META-INF/services` provider registration file** — the
  processor compiles fine and simply never runs; no error, no generated
  output, confusing to debug without knowing this file is required.
- **Hand-parsing a KSP `KSType`'s qualified name as a string** instead of
  using `kotlinpoet-ksp`'s `toTypeName()` — misses nested types, generic
  parameters, and platform type nuances the interop module already handles.
- **Reaching for kapt for a new processor** — no real reason to in 2026;
  KSP is faster and is what the ecosystem's current tooling targets.

---

## Testing

The generated `FileSpec`'s own `toString()` is a plain string — assert on it
directly without needing a real KSP compilation pass for most processor
logic:

```kotlin
class GenerateKoinModuleProcessorTest {
    @Test
    fun `generates a factoryOf binding per annotated class`() {
        val fileSpec = buildModuleFileSpec(listOf(fakeKsClassDeclaration("UserRepository")))
        val generated = fileSpec.toString()
        assertTrue(generated.contains("factoryOf(::UserRepository)"))
    }
}
```

For end-to-end verification that the processor actually runs correctly
against real annotated source (not just that the builder logic produces the
right string), use `com.github.tschuchortdev:kotlin-compile-testing-ksp` —
compiles a fixture source file through the real KSP pipeline and asserts on
the actual compiler output, closer to integration than unit testing.

---

## Related Skills

- `kmp-dependency-injection` — the Koin module convention this skill's
  worked example generates into
- `kmp-code-quality` — generated code should still follow this collection's
  naming/architecture conventions, not get a free pass for being generated
- `kmp-imagevector-generator` — a different codegen path (Python emitting
  Kotlin text via string templates, not a JVM-side KSP processor) — contrast
  case for when KotlinPoet doesn't apply (no JVM classpath to depend on it from)

---

## Output Style

When asked about KSP/KotlinPoet codegen, respond in this order:
1. confirm KSP (not kapt) and KotlinPoet (not string templates) as the default
2. the two-module structure (`annotations` + `processor` + consumer)
3. the processor's `process()` logic using KotlinPoet builders
4. the `META-INF/services` registration file — call it out explicitly, it's
   the most common reason a new processor "does nothing"
5. originating-file tracking in `Dependencies` if the processor will run
   incrementally (it should, by default)

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-24 | Initial release. User asked whether KotlinPoet was used anywhere in this collection — confirmed no, and that the collection's one real Kotlin-codegen tool (`kmp-imagevector-generator`) is a Python script emitting Kotlin text, where KotlinPoet (a JVM library) couldn't apply at all. Real gap: no skill teaches authoring a custom KSP processor, the actual scenario KotlinPoet exists for. Verified the real API (FileSpec/TypeSpec/FunSpec/PropertySpec, format specifiers), the real two-module processor structure and `META-INF/services` ServiceLoader registration requirement, and the `kotlinpoet-ksp` interop module's real conversion functions (`toTypeName()`, `toKModifier()`, `TypeParameterResolver`) before writing. Worked example generates a Koin module, consistent with this collection's own `kmp-dependency-injection` convention rather than an unrelated domain. |
