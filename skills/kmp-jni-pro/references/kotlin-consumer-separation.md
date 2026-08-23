# Phase 0f — Kotlin-side Consumer Separation

Part of `kmp-jni-pro`. Load this file when working on: Kotlin-side consumer
separation.

---

Phase 0e's wrapper structure (`vendor header → your wrapper.cpp → your
jni.cpp`) stops at the JNI boundary. The boundary discipline doesn't end
there — once native calls surface as generated or hand-bound Kotlin
functions, the **Kotlin code that consumes them** needs the same rule:
**never interleave raw binding calls with business/domain logic in the same
function.**

Real, evidence-backed pattern (found in a real KMP native-binding
consumer, generalized here to a native audio DSP scenario instead of the
domain it was found in — the shape is identical regardless of which native
library is bound):

```kotlin
// ❌ WRONG — raw binding calls and business logic welded into one function
fun processAudioFrame(handle: NativeAudioHandle, frame: AudioFrame, history: GainHistory) {
    NativeAudio.dspBeginFrame(handle)                    // raw binding call
    val gain = computeAdaptiveGain(frame, history)       // business logic
    NativeAudio.dspSetGain(handle, gain)                 // raw binding call
    val filtered = applyNoiseGate(frame, gain)           // business logic
    NativeAudio.dspProcessSamples(handle, filtered.data, filtered.size)  // raw binding call
    NativeAudio.dspEndFrame(handle)                      // raw binding call
}
```

```kotlin
// ✓ CORRECT — a thin session facade owns every raw call; business logic never
// touches the binding, and is independently unit-testable without the native
// library loaded at all
class DspSession(private val handle: NativeAudioHandle) {
    fun record(block: DspRecorder.() -> Unit) {
        NativeAudio.dspBeginFrame(handle)
        DspRecorder(handle).block()
        NativeAudio.dspEndFrame(handle)
    }
}

class DspRecorder(private val handle: NativeAudioHandle) {
    fun setGain(gain: Float) = NativeAudio.dspSetGain(handle, gain)
    fun processSamples(samples: FloatArray) =
        NativeAudio.dspProcessSamples(handle, samples, samples.size)
}

fun processAudioFrame(session: DspSession, frame: AudioFrame, history: GainHistory) {
    val gain = computeAdaptiveGain(frame, history)   // business logic — no binding calls
    val filtered = applyNoiseGate(frame, gain)        // business logic — no binding calls
    session.record {
        setGain(gain)
        processSamples(filtered.data)
    }
}
```

**Why this matters, concretely**: a function that welds raw binding calls to
business logic can't be unit-tested without the real native library loaded —
`computeAdaptiveGain`/`applyNoiseGate` are exactly the logic you'd want
covered by a fast JVM unit test, and they can't be, because they're fused to
native calls in the same function. Splitting them the way `DspSession`/
`DspRecorder` do above makes the business logic plain, native-free Kotlin —
test it with `kmp-unit-testing`'s fake-over-mock approach, no native library
on the test classpath at all.

## The naming-leak variant of the same violation

The facade layer (`DspSession`/`DspRecorder` above) must never import
domain/business types either — if it needs to know about `AudioFrame` or
`GainHistory` directly, that's the same layer violation in reverse: a
binding-facing facade that only exists to wrap raw calls has started
carrying business vocabulary it has no business knowing about. Keep the
facade's public surface in terms of primitives (`Float`, `FloatArray`) or its
own binding-scoped types, not the caller's domain types.

A second real shape of this same mistake: copying one platform's binding
class as the starting point for a sibling platform's binding, then never
finishing the rename. If a WebGPU-backed implementation still declares
Vulkan-shaped fields (`instance`, `physicalDevice`, `graphicsQueue`) left
over from copy-pasting the Vulkan implementation, unused, that's a real
signal the `actual` was never redesigned for its own binding's actual
shape — see `kmp-expect-actual`'s "Copy-pasted `actual` leaves a sibling's
vocabulary behind" for the general version of this mistake.
