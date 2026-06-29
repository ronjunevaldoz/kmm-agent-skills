#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PATTERNS = [
    ("state copy race", re.compile(r"_state\.value\s*=\s*_state\.value\.copy\(")),
    ("sharedflow replay effect", re.compile(r"MutableSharedFlow<.*replay\s*=\s*1")),
    ("network result in ui", re.compile(r"NetworkResult<")),
    ("data import in ui", re.compile(r"import .*\.data\.")),
    ("manual screen capture", re.compile(
        r"playwright|adb\s+screencap|xcrun\s+simctl\s+io|Robot\(\)\.createScreenCapture|ProcessBuilder.*screenshot",
        re.IGNORECASE,
    )),
    ("magic color literal", re.compile(r"\bColor\(0x[0-9A-Fa-f]")),
    ("named color in ui", re.compile(
        r"\bColor\.(Black|White|Gray|LightGray|DarkGray|Red|Green|Blue|Yellow|Cyan|Magenta)\b"
    )),
    ("hardcoded divider color", re.compile(
        r"\b(HorizontalDivider|VerticalDivider|Divider)\b[^)]*color\s*=\s*Color\b"
    )),
    ("system dark theme scatter", re.compile(r"\bisSystemInDarkTheme\(\)")),
    ("hardcoded spacing", re.compile(r"\bpadding\([^)]*[1-9]\d*\.dp")),
    ("livedata in viewmodel", re.compile(r"MutableLiveData|LiveData<")),
    ("direct state assignment", re.compile(r"_state\.value\s*=")),
    ("globalscope usage", re.compile(r"\bGlobalScope\b")),
    ("navcontroller in viewmodel", re.compile(r"NavController.*ViewModel|ViewModel.*NavController")),
    ("dto leak to domain", re.compile(r"import .*\.dto\.|@SerialName.*class.*UseCase")),
]

# ── Roadmap detection ─────────────────────────────────────────────────────────

def _has(root: Path, *globs: str) -> bool:
    return any(root.rglob(g) for g in globs)


def _count_files(root: Path, *globs: str) -> int:
    return sum(1 for g in globs for _ in root.rglob(g))


def _read_all(root: Path, *globs: str) -> str:
    parts = []
    for g in globs:
        for p in root.rglob(g):
            try:
                parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(parts)


def _detect_state_mgmt(root: Path) -> str:
    kt = _read_all(root, "*.kt")
    if "MutableStateFlow" in kt and ("sealed interface Intent" in kt or "sealed class Intent" in kt):
        return "MVI (StateFlow + Contract)"
    if "MutableStateFlow" in kt:
        return "StateFlow (no MVI Contract)"
    if "MutableLiveData" in kt:
        return "LiveData (MVVM)"
    if "MutableState" in kt and "remember" in kt:
        return "Compose remember (no ViewModel)"
    return "unknown"


def _detect_modules(root: Path) -> str:
    settings = root / "settings.gradle.kts"
    if not settings.exists():
        settings = root / "settings.gradle"
    if not settings.exists():
        return "single-module (no settings.gradle found)"
    text = settings.read_text(encoding="utf-8", errors="ignore")
    feature_modules = re.findall(r'include\("[^"]*feature[^"]*"\)', text)
    if len(feature_modules) >= 4:
        return f"multi-module ({len(feature_modules)} feature modules)"
    if feature_modules:
        return f"partial split ({len(feature_modules)} feature modules)"
    return "single-module (no :feature: includes)"


def _detect_di(root: Path) -> str:
    kt = _read_all(root, "*.kt")
    if "@KoinViewModel" in kt or "koinViewModel()" in kt:
        return "Koin 4 (annotated)"
    if "koinInject" in kt or "val module = module {" in kt:
        return "Koin (manual)"
    if "@HiltViewModel" in kt or "@AndroidEntryPoint" in kt:
        return "Hilt"
    if "@Inject" in kt:
        return "Dagger / manual inject"
    return "none detected"


def _detect_tests(root: Path) -> str:
    test_files = _count_files(root, "*Test.kt", "*Spec.kt")
    if test_files == 0:
        return "none"
    if test_files < 5:
        return f"minimal ({test_files} test files)"
    return f"present ({test_files} test files)"


def _detect_detekt(root: Path) -> str:
    if _has(root, "detekt.yml", "detekt.yaml", "detekt-config.yml"):
        return "configured"
    return "missing"


def _detect_version_catalog(root: Path) -> str:
    if _has(root, "libs.versions.toml"):
        return "present"
    return "missing"


def assess_project(root: Path) -> dict:
    vm_info = _detect_viewmodel_size(root)
    return {
        "state_mgmt":       _detect_state_mgmt(root),
        "modules":          _detect_modules(root),
        "feature_split":    _detect_feature_split(root),
        "di":               _detect_di(root),
        "tests":            _detect_tests(root),
        "detekt":           _detect_detekt(root),
        "version_catalog":  _detect_version_catalog(root),
        "viewmodel_max_lines": vm_info["max_lines"],
        "large_vms":        vm_info["large_vms"],
    }


ADOPTION_PLAN = [
    # (condition_fn, priority, skill, reason, action)
    (
        lambda s: s["detekt"] == "missing",
        "HIGH",
        "kotlin-multiplatform-code-quality",
        "No Detekt gates — new violations accumulate faster than you migrate them",
        "Add detekt.yml with layer rules before touching any architecture code",
    ),
    (
        lambda s: s["version_catalog"] == "missing",
        "HIGH",
        "kotlin-multiplatform-feature-scaffold",
        "No version catalog — dependency versions drift across modules",
        "Add gradle/libs.versions.toml and migrate build files to use it",
    ),
    (
        lambda s: "LiveData" in s["state_mgmt"],
        "HIGH",
        "kotlin-multiplatform-mvi",
        "LiveData detected — migrate to StateFlow+MVI screen by screen",
        "Pick the highest-traffic screen, write tests for it, then migrate to StateFlow (Path A Step 1)",
    ),
    (
        lambda s: s["state_mgmt"] == "StateFlow (no MVI Contract)",
        "MEDIUM",
        "kotlin-multiplatform-mvi",
        "StateFlow present but no MVI Contract — effects may be using SharedFlow or callbacks",
        "Add Contract (State/Intent/Effect) to screens that have navigation side-effects",
    ),
    (
        lambda s: "single-module" in s["modules"],
        "MEDIUM",
        "kotlin-multiplatform-clean-architecture",
        "Single module — no layer isolation; UI can import data layer directly",
        "Extract :model first (zero-logic move), then :api, then :domain (see migration Path B)",
    ),
    (
        lambda s: "partial split" in s["modules"],
        "MEDIUM",
        "kotlin-multiplatform-clean-architecture",
        "Partial module split — some features separated, others still monolithic",
        "Complete the split for the highest-churn feature first",
    ),
    (
        lambda s: s["tests"] == "none",
        "MEDIUM",
        "kotlin-multiplatform-unit-testing",
        "No tests — migrating without tests risks invisible regressions",
        "Add ViewModel tests (with FakeRepository) before migrating each screen",
    ),
    (
        lambda s: "Hilt" in s["di"] or "Dagger" in s["di"],
        "LOW",
        "kotlin-multiplatform-dependency-injection",
        "Hilt/Dagger detected — not compatible with KMP non-Android targets",
        "Migrate one @Module at a time to Koin 4 (Path C); Hilt and Koin can coexist during migration",
    ),
    (
        lambda s: s["tests"] == "minimal",
        "LOW",
        "kotlin-multiplatform-unit-testing",
        "Few tests — coverage is too thin to migrate safely at speed",
        "Add tests for every ViewModel being migrated before the migration PR",
    ),
    (
        lambda s: s["viewmodel_max_lines"] >= 300,
        "HIGH",
        "kotlin-multiplatform-mvi",
        "God ViewModel detected (300+ lines) — business logic has leaked into the ViewModel",
        "Extract business operations into use cases (see 'ViewModel Size and Decomposition' in mvi skill); "
        "each handleIntent branch that touches 2+ repos belongs in a use case",
    ),
    (
        lambda s: 150 <= s["viewmodel_max_lines"] < 300,
        "MEDIUM",
        "kotlin-multiplatform-mvi",
        "Large ViewModel detected (150–299 lines) — growing toward monolithic",
        "Review handleIntent branches for inline logic that can be extracted to use cases before size crosses 300 lines",
    ),
    (
        lambda s: "no feature layer split" in s["feature_split"] and "multi-module" in s["modules"],
        "HIGH",
        "kotlin-multiplatform-clean-architecture",
        "Multi-module project but features have no :presenter / :domain / :ui layer split",
        "Apply the start-thin tier decision: each feature needs at least :ui; add :presenter when "
        "the screen has its own ViewModel; add :domain when use cases are shared or complex",
    ),
    (
        lambda s: "thin split" in s["feature_split"],
        "MEDIUM",
        "kotlin-multiplatform-clean-architecture",
        "Features have :ui modules only — no :presenter separation",
        "Promote features with complex ViewModels to medium tier (:presenter + :ui); "
        "reserve full tier for CRUD / offline-first features",
    ),
]


def build_roadmap(state: dict) -> list[dict]:
    plan = []
    for condition, priority, skill, reason, action in ADOPTION_PLAN:
        if condition(state):
            plan.append({
                "priority": priority,
                "skill":    skill,
                "reason":   reason,
                "action":   action,
            })
    plan.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]])
    return plan


def print_roadmap(root: Path, state: dict, plan: list[dict]) -> None:
    print(f"\n{'='*60}")
    print("  KMP ADOPTION ROADMAP")
    print(f"  Project: {root}")
    print(f"{'='*60}\n")

    print("Current state:")
    print(f"  State management : {state['state_mgmt']}")
    print(f"  Module structure : {state['modules']}")
    print(f"  Feature split    : {state['feature_split']}")
    print(f"  DI               : {state['di']}")
    print(f"  Tests            : {state['tests']}")
    print(f"  Detekt           : {state['detekt']}")
    print(f"  Version catalog  : {state['version_catalog']}")
    vm_max = state["viewmodel_max_lines"]
    if vm_max > 0:
        vm_label = "god ViewModel (300+)" if vm_max >= 300 else "large (150–299)"
        print(f"  Largest ViewModel: {vm_max} lines ({vm_label})")
        if state["large_vms"]:
            top = state["large_vms"][:3]
            for rel, n in top:
                print(f"    - {rel} ({n} lines)")
    else:
        print(f"  Largest ViewModel: not detected")
    print()

    if not plan:
        print("No adoption gaps detected. Project appears well-structured.")
        print("Run without --roadmap to check for implementation violations.\n")
        return

    print(f"Adoption plan ({len(plan)} items):\n")
    for i, item in enumerate(plan, 1):
        print(f"  {i}. [{item['priority']}] {item['skill']}")
        print(f"     Why:    {item['reason']}")
        print(f"     Action: {item['action']}")
        print()

    print("Run audit_project.py without --roadmap to check for implementation violations.")
    print()


# ── Agent & consumer setup checks ────────────────────────────────────────────

def _detect_agent_setup(root: Path) -> list[str]:
    # Only meaningful for real Gradle projects; skip bare temp dirs used in unit tests.
    is_gradle_project = (root / "settings.gradle.kts").exists() or (root / "settings.gradle").exists()
    if not is_gradle_project:
        return []

    findings: list[str] = []
    claude = root / ".claude"

    if not (root / "CLAUDE.md").exists():
        findings.append("agent-setup [HIGH]: CLAUDE.md missing — skills context never loads (run /kmm-setup-agents)")

    if not (claude / "AGENTS.md").exists():
        findings.append("agent-setup [HIGH]: .claude/AGENTS.md missing — no skill routing table (run /kmm-setup-agents)")

    commands_dir = claude / "commands"
    if not commands_dir.exists() or not any(commands_dir.iterdir()):
        findings.append("agent-setup [MEDIUM]: .claude/commands/ missing — consumer commands not installed")

    skills_dir = claude / "skills"
    if not skills_dir.exists() or not any(skills_dir.iterdir()):
        findings.append("agent-setup [MEDIUM]: .claude/skills/ missing or empty — skills not deployed")

    # Multi-surface project: AGENTS.md exists but only mentions one surface
    agents_md = claude / "AGENTS.md"
    if agents_md.exists():
        text = agents_md.read_text(encoding="utf-8", errors="ignore")
        settings = root / "settings.gradle.kts"
        if settings.exists():
            s = settings.read_text(encoding="utf-8", errors="ignore")
            has_studio = "studio" in s or "shared" in s
            has_core   = ":core:" in s or ":native" in s
            if has_studio and has_core:
                mentions_studio = "studio" in text.lower() or "shared" in text.lower()
                mentions_core   = "core" in text.lower() or "native" in text.lower()
                if not (mentions_studio and mentions_core):
                    findings.append(
                        "agent-setup [MEDIUM]: AGENTS.md covers only one surface of a multi-surface project "
                        "— add routing for the missing surface"
                    )

    return findings


def _detect_mvi_placement(root: Path) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("MviViewModel.kt"):
        rel = path.relative_to(root).as_posix()
        # Flag if it's inside a feature module, not in shared/core
        if any(seg in rel for seg in ("feature", "studio", "app")) and not any(
            seg in rel for seg in ("shared/core", "core/mvi", "core/common", ":core:mvi")
        ):
            findings.append(
                f"arch [MEDIUM]: MviViewModel base class in feature module ({rel}) "
                f"— move to :shared:core or :core:mvi so all features can extend it"
            )
    return findings


def _detect_design_system_wiring(root: Path) -> list[str]:
    findings: list[str] = []
    theme_pattern    = re.compile(r"MaterialTheme\s*\(")
    dark_hardcoded   = re.compile(r"darkTheme\s*=\s*false")
    token_file_pattern = re.compile(r"(ULong|Long)\s*=\s*0x[0-9A-Fa-f]{6,}")

    token_files: list[Path] = []
    for path in root.rglob("*Tokens.kt"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if token_file_pattern.search(text):
            token_files.append(path)

    if len(token_files) >= 2:
        rel_paths = ", ".join(str(p.relative_to(root)) for p in token_files[:3])
        findings.append(
            f"design-system [LOW]: multiple parallel token files with raw ULong constants "
            f"({rel_paths}) — consolidate under a single AppColors data class"
        )

    for path in root.rglob("*.kt"):
        if not any(part in path.stem for part in ("Theme", "theme")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(root)
        if theme_pattern.search(text):
            findings.append(
                f"design-system [MEDIUM]: {rel} wraps MaterialTheme — "
                f"blocks custom token ownership; use CompositionLocalProvider + AppTheme"
            )
        if dark_hardcoded.search(text):
            findings.append(
                f"design-system [MEDIUM]: {rel} hardcodes darkTheme=false — "
                f"replace with isSystemInDarkTheme() default"
            )

    return findings


# ── Standard audit ────────────────────────────────────────────────────────────

def _detect_viewmodel_size(root: Path) -> dict:
    """Return max line count and list of oversized ViewModel files."""
    large: list[tuple[Path, int]] = []
    for path in root.rglob("*ViewModel.kt"):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        count = len(lines)
        if count >= 150:
            large.append((path, count))
    large.sort(key=lambda x: x[1], reverse=True)
    return {
        "max_lines": large[0][1] if large else 0,
        "large_vms": [(str(p.relative_to(root)), n) for p, n in large],
    }


def _detect_feature_split(root: Path) -> str:
    """Detect whether features follow the layer split convention."""
    settings = root / "settings.gradle.kts"
    if not settings.exists():
        settings = root / "settings.gradle"
    if not settings.exists():
        return "unknown (no settings.gradle)"
    text = settings.read_text(encoding="utf-8", errors="ignore")
    presenter = re.findall(r'include\("[^"]*:presenter[^"]*"\)', text)
    domain    = re.findall(r'include\("[^"]*:domain[^"]*"\)', text)
    ui        = re.findall(r'include\("[^"]*:ui[^"]*"\)', text)
    if presenter and domain and ui:
        return f"full split (presenter={len(presenter)}, domain={len(domain)}, ui={len(ui)})"
    if ui and not presenter:
        return f"thin split (:ui only, {len(ui)} modules — no :presenter or :domain)"
    if presenter and not domain:
        return f"medium split (:presenter+:ui, no :domain)"
    return "no feature layer split detected"


_MULTI_VM_RE = re.compile(r'\bkoinViewModel\s*<')
_LAUNCHED_EFFECT_RE = re.compile(r'\bLaunchedEffect\s*\(')
_EFFECT_COLLECT_RE = re.compile(r'\.effect\s*\.\s*collect\b')


def _detect_multi_viewmodel_screen(root: Path) -> list[str]:
    """Flag Screen composables that instantiate 3+ ViewModels directly.

    Each koinViewModel<>() in a Screen creates tight coupling and makes the
    screen untestable in isolation.  The fix: move each koinViewModel() into
    the child composable that actually owns it, or extract a coordinator VM.
    """
    findings: list[str] = []
    for path in root.rglob("*Screen.kt"):
        if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        count = len(_MULTI_VM_RE.findall(text))
        if count >= 3:
            findings.append(
                f"multi viewmodel screen [MEDIUM]: {path.relative_to(root)} "
                f"— {count} koinViewModel<> calls; move each into the child composable "
                f"that owns it, or extract a coordinator ViewModel"
            )
    return findings


def _detect_god_composable(root: Path) -> list[str]:
    """Flag Screen/Content composables that orchestrate too much side-effect logic.

    Signals of a 'god composable' — orchestration that belongs in a coordinator
    ViewModel but leaked into the UI layer:
      - 5+ LaunchedEffect blocks (effect collection / persistence / restore in UI), OR
      - 3+ .effect.collect calls (the composable is acting as a VM-to-VM message bus)

    The fix is a coordinator ViewModel: move state assembly, effect collection,
    and persistence into viewModelScope so the screen shrinks to state + onIntent.
    """
    findings: list[str] = []
    for path in root.rglob("*.kt"):
        if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
            continue
        if not any(part in path.stem for part in ("Screen", "Content", "Page")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        le_count = len(_LAUNCHED_EFFECT_RE.findall(text))
        collect_count = len(_EFFECT_COLLECT_RE.findall(text))
        if le_count >= 5 or collect_count >= 3:
            severity = "HIGH" if (le_count >= 8 or collect_count >= 5) else "MEDIUM"
            findings.append(
                f"god composable [{severity}]: {path.relative_to(root)} "
                f"— {le_count} LaunchedEffect blocks, {collect_count} effect.collect calls; "
                f"extract a coordinator ViewModel — move state assembly, effect collection, "
                f"and persistence into viewModelScope so the screen is just state + onIntent"
            )
    return findings


_EXCLUDED_DIRS = {
    "build", ".gradle", ".git", "vendor", "third_party",
    "node_modules", ".idea", ".kotlin", "kotlin-js-store",
    "worktrees",  # .claude/worktrees/ — agent scratch copies of the repo
}

# ── Redundant title detection ─────────────────────────────────────────────────

# Matches a heading-style text call: AppText/Text with a style that looks like a
# page-level title (H1/H2/Heading/HeadlineLarge/TitleLarge/DisplaySmall).
_HEADING_STYLE_RE = re.compile(
    r"\b(AppText|Text)\s*\([^)]*style\s*=\s*[A-Za-z.]*"
    r"(?:H1|H2|Heading|HeadlineLarge|TitleLarge|DisplaySmall)\b",
)
_TOPBAR_RE = re.compile(r"\b(AppTopAppBar|TopAppBar|CenterAlignedTopAppBar)\b")
_TOPBAR_SLOT_RE = re.compile(r"\btopBar\s*=\s*\{")


def _detect_redundant_title(root: Path) -> list[str]:
    """Flag Screen/Content files that have a scaffold topBar AND a heading-style
    Text in the content body — the title is shown twice visually."""
    findings: list[str] = []
    for path in root.rglob("*.kt"):
        if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
            continue
        if not any(part in path.stem for part in ("Screen", "Content", "Page")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        has_topbar = _TOPBAR_RE.search(text) and _TOPBAR_SLOT_RE.search(text)
        has_heading = _HEADING_STYLE_RE.search(text)
        if has_topbar and has_heading:
            findings.append(
                f"redundant screen title [MEDIUM]: {path.relative_to(root)} "
                f"— AppTopAppBar in topBar slot AND a heading-style Text in content; "
                f"the title appears twice — remove the in-body heading"
            )
    return findings


# ── Missing adaptive breakpoint coverage ──────────────────────────────────────

_WINDOW_SIZE_CLASS_RE = re.compile(r"\bWindowSizeClass\b")
_WINDOW_SIZE_CLASS_PARAM_RE = re.compile(r"windowSizeClass\s*:")


def _detect_missing_adaptive_coverage(root: Path) -> list[str]:
    """If any file in the project uses WindowSizeClass, every Screen composable in
    a :ui module should accept a windowSizeClass param.  Flag screens that don't."""
    # First pass — is adaptive layout in use at all?
    project_uses_adaptive = False
    for path in root.rglob("*.kt"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _WINDOW_SIZE_CLASS_RE.search(text):
            project_uses_adaptive = True
            break

    if not project_uses_adaptive:
        return []

    findings: list[str] = []
    for path in root.rglob("*Screen.kt"):
        if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not _WINDOW_SIZE_CLASS_PARAM_RE.search(text):
            findings.append(
                f"adaptive coverage [LOW]: {path.relative_to(root)} "
                f"— project uses WindowSizeClass but this Screen has no windowSizeClass param; "
                f"add windowSizeClass: WindowSizeClass and branch layout per breakpoint"
            )
    return findings


def _is_excluded(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(
        part in _EXCLUDED_DIRS or part.endswith(".cpp")  # excludes llama.cpp/, stable-diffusion.cpp/ submodules
        for part in parts
    )


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path, root):
            continue
        if path.suffix in {".kt", ".kts"}:
            yield path


# ── Lesson / positive pattern detection ──────────────────────────────────────

def _detect_positive_patterns(root: Path) -> list[dict]:
    """
    Scan the consumer for patterns that exceed or are absent from current skill guidance.
    Returns structured lesson candidates for upstreaming.
    Each entry: { skill, pattern, description, evidence }
    """
    lessons: list[dict] = []
    kt_all = _read_all(root, "*.kt")

    # ── Design system ──────────────────────────────────────────────────────────

    theme_kt = _read_all(root, "*Theme*.kt", "*theme*.kt")

    if "compositionLocalOf<Boolean?>" in theme_kt and "isSystemInDarkTheme()" in theme_kt:
        lessons.append({
            "skill": "kotlin-multiplatform-design-system",
            "pattern": "LocalAppDarkTheme compositionLocalOf<Boolean?> override",
            "description": (
                "Consumer defines LocalAppDarkTheme = compositionLocalOf<Boolean?> { null } "
                "so in-app theme toggles override isSystemInDarkTheme() without changing AppTheme's signature. "
                "null = follow system, true/false = force. Skill should document this as the canonical override pattern."
            ),
            "evidence": "grep -r 'compositionLocalOf<Boolean?>' in *Theme*.kt",
        })

    if "userPreference" in theme_kt and ("LocalStorage" in theme_kt or "DataStore" in theme_kt or "SharedPreferences" in theme_kt):
        lessons.append({
            "skill": "kotlin-multiplatform-design-system",
            "pattern": "ThemeSettings persistent override with cross-platform storage",
            "description": (
                "Consumer persists theme preference via LocalStorage/DataStore into a ThemeSettings object "
                "backed by mutableStateOf<Boolean?>. Survives app restart. "
                "Skill should add a 'persisting theme choice' step after LocalAppDarkTheme is wired."
            ),
            "evidence": "grep -r 'userPreference' in *Theme*.kt",
        })

    # currentIsDark() helper
    if "fun currentIsDark()" in theme_kt or "fun isDark()" in theme_kt:
        lessons.append({
            "skill": "kotlin-multiplatform-design-system",
            "pattern": "currentIsDark() single-call-site helper",
            "description": (
                "Consumer wraps the preference-or-system fallback into a @Composable fun currentIsDark(): Boolean. "
                "Reduces duplication across multiple theme entry points (Android, iOS, Desktop, Web). "
                "Skill should recommend this helper in multi-platform entry wiring (Step 7)."
            ),
            "evidence": "grep -r 'fun currentIsDark' in *Theme*.kt",
        })

    # ── MVI ───────────────────────────────────────────────────────────────────

    if "BaseViewModel" in kt_all and ("Channel.BUFFERED" in kt_all or "receiveAsFlow()" in kt_all):
        lessons.append({
            "skill": "kotlin-multiplatform-mvi",
            "pattern": "Project-level BaseViewModel wrapping MviViewModel",
            "description": (
                "Consumer defines a thin BaseViewModel<S,E,I> that extends MviViewModel from :core, "
                "adding project-specific defaults (e.g. error handling, logging hooks). "
                "Skill should mention this as an optional layer between :core:mvi and feature ViewModels."
            ),
            "evidence": "grep -r 'class BaseViewModel' in *.kt",
        })

    if "UNDO_WINDOW_MS" in kt_all or (re.search(r"undoJob.*cancel|cancel.*undoJob", kt_all) and "delay(" in kt_all):
        lessons.append({
            "skill": "kotlin-multiplatform-mvi",
            "pattern": "Timed undo window (soft-delete + cancel)",
            "description": (
                "Consumer implements undo via a coroutine Job: on delete intent, schedule actual deletion "
                "after UNDO_WINDOW_MS delay; an undo intent cancels the Job. "
                "Skill should add this as a named recipe under 'one-shot delete with undo'."
            ),
            "evidence": "grep -r 'UNDO_WINDOW_MS\\|undoJob' in *.kt",
        })

    # Contract pattern: all three in one sealed object
    has_intent = re.search(r"sealed (interface|class) Intent", kt_all)
    has_effect = re.search(r"sealed (interface|class) Effect", kt_all)
    has_contract_obj = re.search(r"object \w+Contract", kt_all)
    if has_intent and has_effect and has_contract_obj:
        lessons.append({
            "skill": "kotlin-multiplatform-mvi",
            "pattern": "Contract object groups State + Intent + Effect",
            "description": (
                "Consumer colocates State (data class), Intent (sealed interface), and Effect (sealed interface) "
                "inside a single object FooContract. Improves discoverability vs three separate top-level files. "
                "Skill already recommends this but should show the grouping as the default."
            ),
            "evidence": "grep -r 'object.*Contract' in *.kt",
        })

    # ── Architecture / structure ───────────────────────────────────────────────

    if (root / "build-logic").exists() and any((root / "build-logic").rglob("*.gradle.kts")):
        lessons.append({
            "skill": "kotlin-multiplatform-clean-architecture",
            "pattern": "build-logic/ convention plugins",
            "description": (
                "Consumer uses a build-logic/ includeBuild with convention plugins to centralize AGP/KMP "
                "configuration across modules. Eliminates copy-paste Gradle config. "
                "Skill should recommend this pattern for multi-module projects."
            ),
            "evidence": "ls build-logic/convention/src/",
        })

    # FuzzyMatcher for search UX
    if "FuzzyMatcher" in kt_all or re.search(r"fun fuzzyMatch|levenshtein|editDistance", kt_all, re.IGNORECASE):
        lessons.append({
            "skill": "kotlin-multiplatform-clean-architecture",
            "pattern": "FuzzyMatcher utility for search",
            "description": (
                "Consumer ships a FuzzyMatcher (Levenshtein/edit-distance) utility in :core for member/item search. "
                "Purely platform-agnostic, testable, reusable. "
                "Skill could mention domain utilities like matchers as candidates for :core:util."
            ),
            "evidence": "grep -r 'FuzzyMatcher' in *.kt",
        })

    # ── CI ────────────────────────────────────────────────────────────────────

    if _has(root, ".github/workflows/governance.yml", ".github/workflows/governance.yaml"):
        lessons.append({
            "skill": "kotlin-multiplatform-ci-github-actions",
            "pattern": "governance.yml quality gate",
            "description": (
                "Consumer has a separate governance.yml workflow (distinct from build/test) "
                "that enforces merge rules, code ownership, or audit checks. "
                "Skill should add governance workflow as an optional CI step."
            ),
            "evidence": "ls .github/workflows/governance.yml",
        })

    # Multi-surface deployment (separate deploy workflows per target)
    deploy_workflows = list((root / ".github" / "workflows").glob("deploy-*.yml")) if (root / ".github" / "workflows").exists() else []
    if len(deploy_workflows) >= 2:
        lessons.append({
            "skill": "kotlin-multiplatform-ci-github-actions",
            "pattern": "Per-surface deploy workflows (deploy-web.yml, deploy-image.yml, …)",
            "description": (
                f"Consumer has {len(deploy_workflows)} separate deploy-*.yml workflows, one per deployment surface. "
                "Keeps CI graphs readable and allows surface-specific secrets/environments. "
                "Skill should recommend this split for multi-surface KMP projects."
            ),
            "evidence": f"ls .github/workflows/deploy-*.yml  ({len(deploy_workflows)} found)",
        })

    # ── Agent setup ───────────────────────────────────────────────────────────

    claude = root / ".claude"
    if (claude / "AGENTS.md").exists() and (claude / "commands").exists() and (root / "CLAUDE.md").exists():
        lessons.append({
            "skill": "kotlin-multiplatform-audit",
            "pattern": "Full agent setup (CLAUDE.md + AGENTS.md + commands)",
            "description": (
                "Consumer has all three agent setup artifacts in place. "
                "This project is a good reference for what the /kmm-setup-agents command should produce."
            ),
            "evidence": "ls CLAUDE.md .claude/AGENTS.md .claude/commands/",
        })

    return lessons


def harvest_project(root: Path) -> dict:
    """Return findings + positive lessons as a structured dict (for --harvest JSON output)."""
    return {
        "project": str(root),
        "findings": audit_project(root),
        "lessons": _detect_positive_patterns(root),
    }


def audit_project(root: Path) -> list[str]:
    findings: list[str] = []

    # ── Agent & consumer setup ─────────────────────────────────────────────────
    findings.extend(_detect_agent_setup(root))

    # ── MVI base class placement ───────────────────────────────────────────────
    findings.extend(_detect_mvi_placement(root))

    # ── Design system wiring ───────────────────────────────────────────────────
    findings.extend(_detect_design_system_wiring(root))

    # ── Multi-ViewModel screen ─────────────────────────────────────────────────
    findings.extend(_detect_multi_viewmodel_screen(root))

    # ── God composable (side-effect orchestration in UI) ───────────────────────
    findings.extend(_detect_god_composable(root))

    # ── Redundant screen title ─────────────────────────────────────────────────
    findings.extend(_detect_redundant_title(root))

    # ── Missing adaptive breakpoint coverage ───────────────────────────────────
    findings.extend(_detect_missing_adaptive_coverage(root))

    # ── ViewModel size check (not regex-detectable, needs line count) ──────────
    vm_info = _detect_viewmodel_size(root)
    for rel_path, line_count in vm_info["large_vms"]:
        severity = "god viewmodel" if line_count >= 300 else "large viewmodel"
        findings.append(f"{severity} ({line_count} lines): {rel_path}")

    for path in iter_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PATTERNS:
            if label == "network result in ui" and not any(
                token in path.as_posix() for token in ("/ui/", "/presentation/")
            ):
                continue
            if label == "data import in ui":
                in_ui_path = any(token in path.as_posix() for token in ("/ui/", "/presentation/"))
                is_viewmodel = path.stem.endswith("ViewModel")
                if not in_ui_path or is_viewmodel:
                    continue
            if label == "dto leak to domain" and "/domain/" not in path.as_posix():
                continue
            if label == "navcontroller in viewmodel" and "/presenter/" not in path.as_posix():
                continue
            if label == "magic color literal":
                if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
                    continue
                if any(part in path.stem for part in ("Color", "Token", "Theme", "color", "token", "theme")):
                    continue
            if label == "named color in ui":
                if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
                    continue
                if any(part in path.stem for part in ("Color", "Token", "Theme", "color", "token", "theme")):
                    continue
            if label == "hardcoded divider color":
                if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
                    continue
            if label == "system dark theme scatter" and any(
                part in path.stem for part in ("Theme", "theme", "App")
            ):
                continue
            if label == "hardcoded spacing":
                if not any(token in path.as_posix() for token in ("/ui/", "/presentation/")):
                    continue
                if any(part in path.stem for part in ("Spacing", "spacing", "Token", "token", "Theme", "theme")):
                    continue
            if pattern.search(text):
                findings.append(f"{label}: {path.relative_to(root)}")

    return findings


def main() -> int:
    import json as _json

    parser = argparse.ArgumentParser(description="KMP architecture audit and adoption roadmap.")
    parser.add_argument("project_root", type=Path, help="Path to the KMP project root")
    parser.add_argument(
        "--roadmap",
        action="store_true",
        help="Output a prioritized adoption plan instead of violation findings",
    )
    parser.add_argument(
        "--harvest",
        action="store_true",
        help="Output findings + positive lessons as JSON for upstreaming to skills",
    )
    args = parser.parse_args()

    root = args.project_root.resolve()

    if args.roadmap:
        state = assess_project(root)
        plan  = build_roadmap(state)
        print_roadmap(root, state, plan)
        return 1 if plan else 0

    if args.harvest:
        result = harvest_project(root)
        print(_json.dumps(result, indent=2))
        # Exit 1 if there are HIGH findings (so CI can gate on it)
        has_high = any("[HIGH]" in f or "[HIGH]:" in f for f in result["findings"])
        return 1 if has_high else 0

    findings = audit_project(root)

    if findings:
        print("FINDINGS:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("OK: no architecture violations detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
