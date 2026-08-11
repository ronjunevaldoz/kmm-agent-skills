# Detekt Architecture Rules

Part of `kmp-clean-architecture`.

---

Add to `detekt.yml` to fail the build when import-level violations are detected:

```yaml
libraries:
  rules:
    - name: 'NoPresentationInDomain'
      active: true
      includes: ['**/domain/**']
      excludes: []
      forbidden:
        - 'androidx.lifecycle.*'
        - 'androidx.compose.*'
        - '*.presenter.*'
        - '*.ui.*'

    - name: 'NoDataInUi'
      active: true
      includes: ['**/ui/**']
      excludes: []
      forbidden:
        - '*.data.*'
        - '*.domain.*'
        - 'io.ktor.*'
        - 'app.cash.sqldelight.*'

    - name: 'NoComposeInPresenter'
      active: true
      includes: ['**/presenter/**']
      excludes: []
      forbidden:
        - 'androidx.compose.*'
        - 'org.jetbrains.compose.*'
```

These rules complement the Gradle dependency graph — they catch cases where a developer
adds a compile dep and imports it directly rather than through a proper module boundary.
