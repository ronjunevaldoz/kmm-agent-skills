# Framework-Agnostic Store — No ViewModel, No Compose

Part of `kmp-mvi`. Load this file when working on: framework-agnostic store.

---

## When this applies

The Contract pattern (`State`/`Intent`/`Effect`) is plain Kotlin — nothing about it
requires Compose or `androidx.lifecycle.ViewModel`. Use the framework-agnostic `Store`
variant instead of `MviViewModel` when the consumer has **no ambient coroutine scope
driving recomposition** — a custom Vulkan/WebGPU/OpenGL renderer, a game engine's UI
layer, or any immediate-mode toolkit running its own manual frame loop instead of
Compose's recomposition loop.

Two things change from the Compose/`MviViewModel` version; nothing else does:

1. **No `ViewModel` base class.** A plain class instead — nothing renderer-side needs
   lifecycle awareness or `viewModelScope`.
2. **Pull-based effect draining, not push-based collection.** `Channel.receiveAsFlow()` +
   `LaunchedEffect` assumes a suspend collector is always running. A manual draw loop
   isn't a coroutine by default — it calls a plain function once per frame. Drain the
   channel with `tryReceive()` in a loop instead of `collect`.

## The Store

```kotlin
internal object StudioContract {
    enum class Tool { Layers, Grid, Environment, History, Panels }

    data class ExampleState(val activeExampleId: String = StudioExamples.first().id)
    data class InspectorState(val selectedEntityId: Int? = null)
    data class ToolRailState(val activeTool: Tool = Tool.Layers)

    // One root State composed of cohesive sub-states — the same "nested data class"
    // fix documented in references/viewmodel-size-decomposition.md, applied here to
    // solve BOTH problems at once: the god-class State AND cross-tree sharing between
    // sibling panels (ExamplePicker, Inspector, ToolRail) that would otherwise need
    // prop-drilling through a common parent with no natural owner.
    data class State(
        val examples: ExampleState = ExampleState(),
        val inspector: InspectorState = InspectorState(),
        val toolRail: ToolRailState = ToolRailState(),
    )

    sealed interface Intent {
        data class SelectExample(val id: String) : Intent
        data class SelectEntity(val id: Int?) : Intent
        data class SelectTool(val tool: Tool) : Intent
    }

    sealed interface Effect {
        // World mutation is a side effect; a reducer shouldn't perform it directly.
        data class LoadExample(val exampleId: String) : Effect
    }
}

internal class StudioStore(
    private val exampleRepository: ExampleRepository,
) {
    // No viewModelScope available — own the scope explicitly, and expose a way to
    // cancel it. Whatever owns the Store's lifecycle (the render surface's
    // create/destroy hooks) must call close() — there is no onCleared() doing it for you.
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    private val _state = MutableStateFlow(StudioContract.State())
    val state: StateFlow<StudioContract.State> = _state.asStateFlow()

    private val effects = Channel<StudioContract.Effect>(Channel.BUFFERED)

    fun dispatch(intent: StudioContract.Intent) {
        when (intent) {
            is StudioContract.Intent.SelectExample -> {
                _state.update { it.copy(examples = it.examples.copy(activeExampleId = intent.id)) }
                effects.trySend(StudioContract.Effect.LoadExample(intent.id))
            }

            is StudioContract.Intent.SelectEntity -> {
                _state.update { it.copy(inspector = it.inspector.copy(selectedEntityId = intent.id)) }
            }

            is StudioContract.Intent.SelectTool -> {
                _state.update { it.copy(toolRail = it.toolRail.copy(activeTool = intent.tool)) }
            }
        }
    }

    // Async Intent handling still needs a coroutine — this is where MviViewModel would
    // use viewModelScope.launch. The Store launches on its own scope instead.
    fun loadExampleAsync(exampleId: String) {
        scope.launch {
            val example = exampleRepository.load(exampleId)
            _state.update { it.copy(examples = it.examples.copy(activeExampleId = example.id)) }
        }
    }

    // Pull-based effect drain — call once per frame from the render loop, not from a
    // suspend collector. Exactly-once delivery is preserved: tryReceive() consumes the
    // buffered element, same guarantee Channel gives receiveAsFlow() consumers.
    fun drainEffects(): List<StudioContract.Effect> = buildList {
        while (true) {
            val effect = effects.tryReceive().getOrNull() ?: break
            add(effect)
        }
    }

    fun close() {
        scope.cancel()
        effects.close()
    }
}
```

## Consuming from a manual render loop

```kotlin
// Pseudocode — the shape is the same regardless of which renderer calls it
fun onFrame() {
    for (effect in store.drainEffects()) {
        when (effect) {
            is StudioContract.Effect.LoadExample -> store.loadExampleAsync(effect.exampleId)
        }
    }
    val state = store.state.value   // StateFlow.value — no collector needed for a snapshot read
    render(state)
}

fun onSurfaceDestroyed() {
    store.close()   // no onCleared() equivalent — this must be called explicitly
}
```

## Testing

Still fully unit-testable without a ViewModel/Compose test dependency — `dispatch()` and
`state.value` are plain synchronous calls. `runTest` still applies to `loadExampleAsync`'s
coroutine, same as `MviViewModel`'s Turbine-based tests in `references/testing.md`; only
the collection mechanism (`state.value` snapshot vs `state.test { }`) differs.

## When to use `MviViewModel` instead

If the consumer *is* Compose (even a Compose Desktop/Web canvas, not just Android/iOS),
use `MviViewModel` — `viewModelScope`'s automatic cancellation and `LaunchedEffect`'s
lifecycle-aware collection are strictly less code than owning a `CoroutineScope` and a
manual per-frame drain by hand. This pattern exists specifically for consumers with no
Compose recomposition loop to hook into.
