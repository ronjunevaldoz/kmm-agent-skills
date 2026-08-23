# In-flight Cancellation

Part of `kmp-mvi`. Load this file when working on: in-flight cancellation.

---

When an intent triggers a job that should supersede any prior job of the same type
(search, filter, reload), cancel the previous job before launching the new one.

```kotlin
private var searchJob: Job? = null

private fun search(query: String) {
    searchJob?.cancel()
    if (query.isBlank()) {
        updateState { copy(results = emptyList(), isSearching = false) }
        return
    }
    searchJob = viewModelScope.launch {
        updateState { copy(isSearching = true) }
        delay(300)                    // debounce — skip if cancelled during delay
        val results = repo.search(query)
        updateState { copy(results = results, isSearching = false) }
    }
}
```

The `delay(300)` acts as a debounce: if a new `SearchQueryChanged` intent arrives within
300 ms the coroutine is cancelled before the network call fires.

**When NOT to cancel:** submit, save, and delete actions should not be cancellable by
re-typing — guard those with an `isLoading` flag instead (see `login()` example above).
