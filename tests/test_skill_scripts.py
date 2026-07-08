from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


expert_scripts = load_module(
    "validate_skill_map",
    REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "scripts" / "validate_skill_map.py",
)
keyword_routing_scripts = load_module(
    "validate_keyword_routing",
    REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "scripts" / "validate_keyword_routing.py",
)
scaffold_scripts = load_module(
    "validate_module_graph",
    REPO_ROOT / "skills" / "kotlin-multiplatform-feature-scaffold" / "scripts" / "validate_module_graph.py",
)
audit_scripts = load_module(
    "audit_project",
    REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "audit_project.py",
)
auth_service_scripts = load_module(
    "scaffold_auth_service",
    REPO_ROOT / "skills" / "kotlin-multiplatform-ktor-auth-service" / "scripts" / "scaffold_auth_service.py",
)
mongodb_scripts = load_module(
    "scaffold_mongodb_database",
    REPO_ROOT / "skills" / "kotlin-multiplatform-mongodb-database" / "scripts" / "scaffold_mongodb_database.py",
)
rpc_scripts = load_module(
    "scaffold_kotlin_rpc",
    REPO_ROOT / "skills" / "kotlin-multiplatform-kotlin-rpc" / "scripts" / "scaffold_kotlin_rpc.py",
)
audit_repo_scripts = load_module(
    "audit_skills_repo",
    REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "audit_skills_repo.py",
)
draft_issue_scripts = load_module(
    "draft_issue",
    REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "draft_issue.py",
)
scan_skill_issues_scripts = load_module(
    "scan_skill_issues",
    REPO_ROOT / "scripts" / "scan_skill_issues.py",
)
check_updates_scripts = load_module(
    "check_updates",
    REPO_ROOT / "scripts" / "check_updates.py",
)
release_scripts = load_module(
    "release",
    REPO_ROOT / "scripts" / "release.py",
)
create_lesson_scripts = load_module(
    "create_lesson",
    REPO_ROOT / "skills" / "kotlin-multiplatform-lessons" / "scripts" / "create_lesson.py",
)
create_wireframe_scripts = load_module(
    "create_wireframe",
    REPO_ROOT / "skills" / "kotlin-multiplatform-layout-system" / "scripts" / "create_wireframe.py",
)
imagevector_scripts = load_module(
    "convert_image_to_imagevector",
    REPO_ROOT / "skills" / "kotlin-multiplatform-imagevector-generator" / "scripts" / "convert_image_to_imagevector.py",
)
slot_scaffold_scripts = load_module(
    "generate_slot_scaffold",
    REPO_ROOT / "skills" / "kotlin-multiplatform-layout-system" / "scripts" / "generate_slot_scaffold.py",
)
derive_prefix_scripts = load_module(
    "derive_component_prefix",
    REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "derive_component_prefix.py",
)


class ValidateSkillMapTests(unittest.TestCase):
    def test_validate_skill_map_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                """
                kotlin-multiplatform-a
                kotlin-multiplatform-b
                kotlin-multiplatform-expert
                """.strip(),
                encoding="utf-8",
            )
            # planner.md must reference all non-meta skills (short names)
            (root / "agents").mkdir()
            (root / "agents" / "planner.md").write_text(
                "| feature a | `a`, `b` |\n",
                encoding="utf-8",
            )
            skills_dir = root / "skills"
            for name in ("kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"):
                (skills_dir / name).mkdir(parents=True)
                (skills_dir / name / "SKILL.md").write_text(
                    "## The 3 Skills and What They Own\n"
                    "kotlin-multiplatform-a\n"
                    "kotlin-multiplatform-b\n"
                    "kotlin-multiplatform-expert\n",
                    encoding="utf-8",
                )

            self.assertEqual(expert_scripts.validate_skill_map(root), [])

    def test_validate_skill_map_reports_missing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("kotlin-multiplatform-a", encoding="utf-8")
            skills_dir = root / "skills"
            (skills_dir / "kotlin-multiplatform-a").mkdir(parents=True)
            (skills_dir / "kotlin-multiplatform-a" / "SKILL.md").write_text(
                "## The 1 Skills and What They Own\nkotlin-multiplatform-a\n",
                encoding="utf-8",
            )
            (skills_dir / "kotlin-multiplatform-expert").mkdir(parents=True)
            (skills_dir / "kotlin-multiplatform-expert" / "SKILL.md").write_text(
                "## The 1 Skills and What They Own\nkotlin-multiplatform-a\n",
                encoding="utf-8",
            )
            errors = expert_scripts.validate_skill_map(root)
            self.assertTrue(any("declares 1 skills but repo has 2 skill folders" in e for e in errors))


class DocsScopeBoundaryTests(unittest.TestCase):
    def test_repo_and_consumer_docs_boundary_is_explicit(self) -> None:
        normalize = lambda text: " ".join(text.lower().split())

        docs_maintainer = normalize((REPO_ROOT / "agents" / "docs-maintainer.md").read_text(encoding="utf-8"))
        planner = normalize((REPO_ROOT / "agents" / "planner.md").read_text(encoding="utf-8"))
        expert = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "SKILL.md").read_text(encoding="utf-8"))
        project_docs = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-project-docs-maintainer" / "SKILL.md").read_text(encoding="utf-8"))
        readme = normalize((REPO_ROOT / "README.md").read_text(encoding="utf-8"))

        self.assertIn("repo-internal docs", docs_maintainer)
        self.assertIn("downstream consumer docs", docs_maintainer)
        self.assertIn("repo-internal docs -> `docs-maintainer`", planner)
        self.assertIn("downstream consumer docs -> `project-docs-maintainer`", planner)
        self.assertIn("docs scope guard", expert)
        self.assertIn("repo-internal docs", expert)
        self.assertIn("downstream consumer docs", expert)
        self.assertIn("downstream consumer-facing kmp project documentation only", project_docs)
        self.assertIn("if the target is this repository, route to `docs-maintainer` instead.", project_docs)
        self.assertIn("classify it as repo-internal or downstream consumer", readme)


class CommonFirstSharedCodeTests(unittest.TestCase):
    def test_common_first_formatting_rule_is_explicit(self) -> None:
        normalize = lambda text: " ".join(text.lower().replace("`", "").split())

        expert = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-expert" / "SKILL.md").read_text(encoding="utf-8"))
        expect_actual = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-expect-actual" / "SKILL.md").read_text(encoding="utf-8"))
        audit = normalize((REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "SKILL.md").read_text(encoding="utf-8"))

        self.assertIn("string.format", expert)
        self.assertIn("shared formatter", expert)
        self.assertIn("implementing the behavior in commonmain first", expect_actual)
        self.assertIn("commonmain can express it cleanly and portably", expect_actual)
        self.assertIn("jvm-only utility in commonmain", expect_actual)
        self.assertIn("prefer a pure commonmain implementation before abstractions", audit)
        self.assertIn("jvm-only utilities in commonmain", audit)


class ReleaseScriptTests(unittest.TestCase):
    def test_release_validation_invokes_all_gates_in_order(self) -> None:
        calls: list[str] = []

        def record(name: str):
            def inner() -> None:
                calls.append(name)
            return inner

        with (
            mock.patch.object(release_scripts, "run_audit", record("audit")),
            mock.patch.object(release_scripts, "run_scan_skill_issues", record("scan")),
            mock.patch.object(release_scripts, "run_skill_map_validation", record("skill_map")),
            mock.patch.object(release_scripts, "run_keyword_routing_validation", record("keyword_routing")),
            mock.patch.object(release_scripts, "run_tests", record("tests")),
        ):
            release_scripts.run_release_validation()

        self.assertEqual(calls, ["audit", "scan", "skill_map", "keyword_routing", "tests"])

    def test_release_validation_scripts_use_repo_root_flags(self) -> None:
        commands: list[list[str]] = []

        def fake_run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
            commands.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout="OK", stderr="")

        with mock.patch.object(release_scripts, "run", fake_run):
            release_scripts.run_skill_map_validation()
            release_scripts.run_keyword_routing_validation()

        self.assertIn(
            [
                "python3",
                str(release_scripts.VALIDATE_SKILL_MAP_SCRIPT),
                "--repo-root",
                str(release_scripts.REPO_ROOT),
            ],
            commands,
        )
        self.assertIn(
            [
                "python3",
                str(release_scripts.VALIDATE_KEYWORD_ROUTING_SCRIPT),
                "--repo-root",
                str(release_scripts.REPO_ROOT),
            ],
            commands,
        )


class ValidateModuleGraphTests(unittest.TestCase):
    def test_validate_module_graph_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text("", encoding="utf-8")
            (root / "build-logic").mkdir()
            (root / "androidApp").mkdir()
            (root / "androidApp" / "build.gradle.kts").write_text(
                "implementation(projects.feature.auth.ui)",
                encoding="utf-8",
            )
            for module in ("model", "api", "domain", "data", "presenter", "ui"):
                module_dir = root / "feature" / "auth" / module
                module_dir.mkdir(parents=True)
                (module_dir / "build.gradle.kts").write_text("", encoding="utf-8")
            ui_src = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
            ui_src.mkdir(parents=True)
            (ui_src / "LoginContent.kt").write_text(
                "fun LoginContent() { Column { } }",
                encoding="utf-8",
            )
            (ui_src / "LoginContentPreview.kt").write_text(
                "fun LoginContentPreview() { LoginContent() }",
                encoding="utf-8",
            )

            self.assertEqual(scaffold_scripts.validate_module_graph(root, "auth"), [])

    def test_validate_module_graph_reports_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text("", encoding="utf-8")
            (root / "build-logic").mkdir()
            (root / "androidApp").mkdir()
            (root / "androidApp" / "build.gradle.kts").write_text("", encoding="utf-8")
            for module in ("model", "api", "domain", "data", "presenter", "ui"):
                module_dir = root / "feature" / "auth" / module
                module_dir.mkdir(parents=True)
                (module_dir / "build.gradle.kts").write_text("", encoding="utf-8")

            self.assertIn(
                "androidApp/build.gradle.kts does not reference projects.feature.auth.ui",
                scaffold_scripts.validate_module_graph(root, "auth"),
            )

    def test_validate_module_graph_reports_missing_preview_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text("", encoding="utf-8")
            (root / "build-logic").mkdir()
            (root / "androidApp").mkdir()
            (root / "androidApp" / "build.gradle.kts").write_text(
                "implementation(projects.feature.auth.ui)",
                encoding="utf-8",
            )
            for module in ("model", "api", "domain", "data", "presenter", "ui"):
                module_dir = root / "feature" / "auth" / module
                module_dir.mkdir(parents=True)
                (module_dir / "build.gradle.kts").write_text("", encoding="utf-8")
            ui_src = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
            ui_src.mkdir(parents=True)
            (ui_src / "LoginContent.kt").write_text(
                "fun LoginContent() { Column { } }",
                encoding="utf-8",
            )

            errors = scaffold_scripts.validate_module_graph(root, "auth")

            self.assertTrue(any("missing preview stub" in error for error in errors))


class AuditProjectTests(unittest.TestCase):
    def test_audit_project_finds_smells(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "auth" / "ui"
            ui_dir.mkdir(parents=True)
            # ViewModel file — triggers state/sharedflow checks but NOT data-import (by design)
            (ui_dir / "AuthViewModel.kt").write_text(
                """
                _state.value = _state.value.copy(isLoading = true)
                val flow = MutableSharedFlow<Int>(replay = 1)
                """.strip(),
                encoding="utf-8",
            )
            # Non-ViewModel UI file — triggers data import check
            (ui_dir / "AuthScreen.kt").write_text(
                "import foo.bar.data.SecretRepo",
                encoding="utf-8",
            )

            findings = audit_scripts.audit_project(root)

            self.assertTrue(any("state copy race" in finding for finding in findings))
            self.assertTrue(any("sharedflow replay effect" in finding for finding in findings))
            self.assertTrue(any("data import in ui" in finding for finding in findings))

    def test_audit_project_finds_network_result_in_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "auth" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "AuthScreen.kt").write_text(
                "val result: NetworkResult<User> = viewModel.state",
                encoding="utf-8",
            )

            findings = audit_scripts.audit_project(root)

            self.assertTrue(any("network result in ui" in finding for finding in findings))

    def test_audit_project_ignores_network_result_outside_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "feature" / "auth" / "data"
            data_dir.mkdir(parents=True)
            (data_dir / "AuthRemoteDataSource.kt").write_text(
                "suspend fun login(): NetworkResult<User>",
                encoding="utf-8",
            )

            findings = audit_scripts.audit_project(root)

            self.assertFalse(any("network result in ui" in finding for finding in findings))

    def test_audit_project_finds_adb_screencap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "androidApp" / "src"
            src_dir.mkdir(parents=True)
            (src_dir / "ScreenshotHelper.kt").write_text(
                'Runtime.getRuntime().exec("adb screencap /sdcard/screen.png")',
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("manual screen capture" in f for f in findings))

    def test_audit_project_finds_playwright(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "androidApp" / "src"
            src_dir.mkdir(parents=True)
            (src_dir / "UITest.kt").write_text(
                "import com.microsoft.playwright.Page",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("manual screen capture" in f for f in findings))

    def test_audit_project_finds_xcrun_simctl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "iosApp" / "src"
            src_dir.mkdir(parents=True)
            (src_dir / "CaptureHelper.kt").write_text(
                'exec("xcrun simctl io booted screenshot screen.png")',
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("manual screen capture" in f for f in findings))

    def test_audit_project_finds_magic_color_in_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "auth" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "AuthScreen.kt").write_text(
                "Box(modifier = Modifier.background(Color(0xFF6200EE)))",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("magic color literal" in f for f in findings))

    def test_audit_project_ignores_magic_color_in_token_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "core" / "designsystem" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "AppColors.kt").write_text(
                "val primary = Color(0xFF6200EE)",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("magic color literal" in f for f in findings))

    def test_audit_project_ignores_magic_color_outside_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "feature" / "auth" / "data"
            data_dir.mkdir(parents=True)
            (data_dir / "AuthMapper.kt").write_text(
                "val highlight = Color(0xFFFF0000)",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("magic color literal" in f for f in findings))

    def test_audit_project_finds_system_dark_theme_in_composable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "val isDark = isSystemInDarkTheme()\n"
                "val bg = if (isDark) Color.Black else Color.White",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("system dark theme scatter" in f for f in findings))

    def test_audit_project_finds_hardcoded_spacing_in_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeContent.kt").write_text(
                "Column(modifier = Modifier.padding(16.dp)) { }",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("hardcoded spacing" in f for f in findings))

    def test_audit_project_finds_hardcoded_spacing_horizontal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeContent.kt").write_text(
                "Row(modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)) { }",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("hardcoded spacing" in f for f in findings))

    def test_audit_project_ignores_spacing_token_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeContent.kt").write_text(
                "Column(modifier = Modifier.padding(horizontal = AppTheme.spacing.lg)) { }",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded spacing" in f for f in findings))

    def test_audit_project_ignores_zero_dp_padding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeContent.kt").write_text(
                "Column(modifier = Modifier.padding(0.dp)) { }",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded spacing" in f for f in findings))

    def test_audit_project_ignores_hardcoded_spacing_outside_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            comp_dir = root / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            (comp_dir / "AppTopAppBar.kt").write_text(
                ".padding(horizontal = 4.dp)",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded spacing" in f for f in findings))

    def test_audit_project_ignores_system_dark_theme_in_app_theme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "app" / "src"
            src_dir.mkdir(parents=True)
            (src_dir / "AppTheme.kt").write_text(
                "AppTheme(darkTheme = isSystemInDarkTheme()) { content() }",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("system dark theme scatter" in f for f in findings))

    def test_audit_project_finds_named_color_in_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "Modifier.border(1.dp, Color.Gray)",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("named color in ui" in f for f in findings))

    def test_audit_project_ignores_named_color_in_token_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "core" / "designsystem" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "AppColors.kt").write_text(
                "val gray = Color.Gray",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("named color in ui" in f for f in findings))

    def test_audit_project_ignores_named_color_outside_ui(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "feature" / "home" / "domain" / "src"
            src_dir.mkdir(parents=True)
            (src_dir / "HomeUseCase.kt").write_text(
                "val color = Color.Black",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("named color in ui" in f for f in findings))

    def test_audit_project_finds_hardcoded_divider_color(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeContent.kt").write_text(
                "HorizontalDivider(color = Color.LightGray)",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("hardcoded divider color" in f for f in findings))

    def test_audit_project_ignores_token_divider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeContent.kt").write_text(
                "HorizontalDivider(color = AppTheme.colors.outline)",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded divider color" in f for f in findings))

    def test_audit_project_finds_color_in_composable_outside_ui_path(self) -> None:
        # No /ui/ segment, but the file declares @Composable — content detection catches it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "composeApp" / "src" / "commonMain" / "kotlin" / "home"
            d.mkdir(parents=True)
            (d / "HomeScreen.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\n"
                "fun HomeScreen() { Modifier.border(1.dp, Color.Gray) }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("named color in ui" in f for f in findings))

    def test_audit_project_ignores_color_in_non_compose_outside_ui(self) -> None:
        # No /ui/ path AND no Compose content — stays skipped (avoids flagging plain constants).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "core" / "util" / "src"
            d.mkdir(parents=True)
            (d / "Constants.kt").write_text(
                "val brandHex = Color.Gray\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("named color in ui" in f for f in findings))


class MultiViewModelScreenTests(unittest.TestCase):
    def test_flags_screen_with_three_or_more_viewmodels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "studio" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "StudioScreen.kt").write_text(
                "val ttiVm = koinViewModel<TextToImageViewModel>()\n"
                "val img2imgVm = koinViewModel<ImageToImageViewModel>()\n"
                "val videoVm = koinViewModel<VideoViewModel>()\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("multi viewmodel screen" in f for f in findings))

    def test_ignores_screen_with_two_viewmodels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "val vm = koinViewModel<HomeViewModel>()\n"
                "val sharedVm = koinViewModel<SharedViewModel>()\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("multi viewmodel screen" in f for f in findings))

    def test_flags_screen_regardless_of_package_path(self) -> None:
        # The detector no longer requires a /ui/ path — a *Screen.kt with 3+ VMs is
        # flagged wherever it lives (projects don't all use the /ui/ module convention).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "composeApp" / "src" / "commonMain" / "kotlin" / "home"
            src_dir.mkdir(parents=True)
            (src_dir / "StudioScreen.kt").write_text(
                "val a = koinViewModel<AViewModel>()\n"
                "val b = koinViewModel<BViewModel>()\n"
                "val c = koinViewModel<CViewModel>()\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("multi viewmodel screen" in f for f in findings))

    def test_ignores_screen_in_build_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "composeApp" / "build" / "generated"
            src_dir.mkdir(parents=True)
            (src_dir / "StudioScreen.kt").write_text(
                "val a = koinViewModel<AViewModel>()\n"
                "val b = koinViewModel<BViewModel>()\n"
                "val c = koinViewModel<CViewModel>()\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("multi viewmodel screen" in f for f in findings))

    def test_flags_non_screen_composable_with_many_vms(self) -> None:
        # Hardening: a Compose file NOT named *Screen (Dashboard) still counts.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "Dashboard.kt").write_text(
                "@Composable\n"
                "fun Dashboard() {\n"
                "    val a = koinViewModel<AViewModel>()\n"
                "    val b = koinViewModel<BViewModel>()\n"
                "    val c = koinViewModel<CViewModel>()\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("multi viewmodel screen" in f for f in findings))


class AuditHardeningTests(unittest.TestCase):
    def test_vm_in_vm_catches_coordinator_without_viewmodel_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "StudioCoordinator.kt").write_text(
                "class StudioCoordinator(\n"
                "    private val tti: TextToImageViewModel,\n"
                ") : MviViewModel<S, I, E>(S()) {\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel in viewmodel" in f for f in findings))

    def test_large_viewmodel_caught_by_content_not_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            body = (
                "import androidx.lifecycle.viewModelScope\n"
                "class HomePresenter : BaseViewModel() {\n"
                + "\n".join(f"    fun op{i}() {{}}" for i in range(200))
                + "\n}\n"
            )
            (d / "HomePresenter.kt").write_text(body, encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel" in f and "HomePresenter" in f for f in findings))

    def test_dto_leak_caught_in_usecase_outside_domain_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "LoginUseCase.kt").write_text(
                "import com.example.data.dto.UserDto\nclass LoginUseCase {}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("dto leak to domain" in f for f in findings))

    def test_data_model_named_file_is_not_treated_as_viewmodel(self) -> None:
        # Guard against over-broad VM detection: a plain data class must not be flagged.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            body = (
                "data class UserModel(\n"
                + "\n".join(f"    val field{i}: String," for i in range(200))
                + "\n)\n"
            )
            (d / "UserModel.kt").write_text(body, encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("viewmodel" in f and "UserModel" in f for f in findings))


class ViewModelInViewModelTests(unittest.TestCase):
    def test_flags_viewmodel_with_viewmodel_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "studio" / "presenter" / "src"
            d.mkdir(parents=True)
            (d / "StudioCoordinatorViewModel.kt").write_text(
                "class StudioCoordinatorViewModel(\n"
                "    private val tti: TextToImageViewModel,\n"
                "    private val assembler: StudioStateAssembler,\n"
                ") : MviViewModel<S, I, E>(S()) {\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel in viewmodel" in f for f in findings))

    def test_ignores_viewmodel_with_usecase_params(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "home" / "presenter" / "src"
            d.mkdir(parents=True)
            (d / "HomeViewModel.kt").write_text(
                "class HomeViewModel(\n"
                "    private val generateImage: GenerateImageUseCase,\n"
                "    private val savedStateHandle: SavedStateHandle,\n"
                ") : MviViewModel<S, I, E>(S()) {\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("viewmodel in viewmodel" in f for f in findings))

    def test_ignores_state_holder_with_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "studio" / "presenter" / "src"
            d.mkdir(parents=True)
            # A plain state holder is not a *ViewModel.kt file and not a ViewModel class
            (d / "TextToImageStateHolder.kt").write_text(
                "class TextToImageStateHolder(\n"
                "    private val scope: CoroutineScope,\n"
                "    private val generateImage: GenerateImageUseCase,\n"
                ") {\n"
                "    fun onIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("viewmodel in viewmodel" in f for f in findings))

    def test_flags_viewmodel_held_as_injected_property(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "PropCoordinator.kt").write_text(
                "class PropCoordinator : MviViewModel<S, I, E>(S()) {\n"
                "    private val editor: EditorViewModel by inject()\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel in viewmodel" in f for f in findings))

    def test_flags_viewmodel_instantiated_internally(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "InstCoordinator.kt").write_text(
                "class InstCoordinator : MviViewModel<S, I, E>(S()) {\n"
                "    private val editor = EditorViewModel()\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel in viewmodel" in f for f in findings))

    def test_flags_viewmodel_via_di_generic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "GenericCoordinator.kt").write_text(
                "class GenericCoordinator : MviViewModel<S, I, E>(S()) {\n"
                "    private val editor by inject<EditorViewModel>()\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel in viewmodel" in f for f in findings))

    def test_ignores_coordinator_holding_state_holder(self) -> None:
        # The valid Option-2 coordinator holds State Holders + use cases — must NOT flag.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "DashboardCoordinatorViewModel.kt").write_text(
                "class DashboardCoordinatorViewModel(\n"
                "    private val saveItem: SaveItemUseCase,\n"
                "    private val assembler: DashboardStateAssembler,\n"
                ") : MviViewModel<S, I, E>(S()) {\n"
                "    private val editor = EditorStateHolder(viewModelScope, saveItem)\n"
                "    override suspend fun handleIntent(intent: I) {}\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("viewmodel in viewmodel" in f for f in findings))


_SAMPLE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path fill="#1E3A5F" d="M10 10 L90 10 L90 90 L10 90 Z"/>
  <path fill="#E67E22" d="M50 20 C70 20 80 40 80 50 S70 80 50 80 Q30 80 25 50 T50 20 Z"/>
  <path fill="none" d="M0 0 L1 1"/>
</svg>
"""


class ImageVectorConverterTests(unittest.TestCase):
    def _convert(self, svg: str = _SAMPLE_SVG, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "logo.svg"
            src.write_text(svg, encoding="utf-8")
            return imagevector_scripts.convert(
                src, kw.get("name", "Logo"), kw.get("group_id", "com.example.app"),
                kw.get("viewport", 24.0), kw.get("color_mode", "literal"),
                kw.get("colors", 6), kw.get("max_nodes", 400),
            )

    def test_generates_header_and_property(self) -> None:
        kotlin, report = self._convert()
        self.assertIn("GENERATED by convert_image_to_imagevector", kotlin)
        self.assertIn("val Logo: ImageVector by lazy", kotlin)
        self.assertEqual(report["layers"], 2)  # fill=none path skipped

    def test_rescales_to_viewport(self) -> None:
        kotlin, _ = self._convert()
        # 10..90 in a 100-viewBox scaled to 24 → 2.4..21.6
        self.assertIn("moveTo(2.4f, 2.4f)", kotlin)
        self.assertIn("lineTo(21.6f, 21.6f)", kotlin)

    def test_smooth_and_quad_commands_emitted(self) -> None:
        kotlin, _ = self._convert()
        self.assertIn("curveTo(", kotlin)   # C and S both become curveTo
        self.assertIn("quadTo(", kotlin)    # Q and T both become quadTo

    def test_semantic_mode_merges_to_single_layer(self) -> None:
        kotlin, report = self._convert(color_mode="semantic")
        self.assertEqual(report["layers"], 1)
        self.assertIn("SolidColor(Color.Black)", kotlin)
        self.assertNotIn("0xFFE67E22", kotlin)

    def test_semantic_mode_fill_call_properly_closed(self) -> None:
        # Regression: the "color-agnostic" comment was once embedded inside the
        # path(fill = ...) argument list, so `//` commented out the closing `) {`
        # and broke every semantic-mode icon's generated Kotlin syntax.
        kotlin, _ = self._convert(color_mode="semantic")
        self.assertIn("SolidColor(Color.Black)) {", kotlin)
        self.assertNotIn("Color.Black)  //", kotlin)

    def test_node_budget_refuses_bloat(self) -> None:
        with self.assertRaises(SystemExit):
            self._convert(max_nodes=3)

    def test_arc_command_flattened_to_curves(self) -> None:
        # Real Heroicons paths are full of arcs (bell, user-circle, clock, etc.) —
        # these must convert to curveTo(...) calls, not raise.
        arc_svg = '<svg viewBox="0 0 10 10"><path fill="#000" d="M0 5 A5 5 0 0 1 10 5"/></svg>'
        kotlin, _ = self._convert(svg=arc_svg)
        self.assertIn("curveTo(", kotlin)
        self.assertNotIn("NaN", kotlin)

    def test_arc_semicircle_endpoint_is_accurate(self) -> None:
        # A semicircle of radius 5 from (0,5) to (10,5) (sweep=1) must end exactly
        # at the SVG endpoint regardless of how many cubic sub-segments it's split into.
        cmds = imagevector_scripts.parse_path("M0 5 A5 5 0 0 1 10 5")
        last = cmds[-1]
        self.assertEqual(last.op, "curve")
        self.assertAlmostEqual(last.args[-2], 10.0, places=3)
        self.assertAlmostEqual(last.args[-1], 5.0, places=3)

    def test_arc_packed_flags_parsed_correctly(self) -> None:
        # Arc flags are single 0/1 digits that may be packed with no separator before
        # the next number (e.g. "1110" = large-arc=1, sweep=1, x=10) — a classic SVG
        # arc-parsing gotcha that a naive float tokenizer misreads as one number "1110".
        cmds = imagevector_scripts.parse_path("M0 0A5 5 0 1110 0")
        curves = [c for c in cmds if c.op == "curve"]
        self.assertTrue(len(curves) >= 1)
        self.assertAlmostEqual(curves[-1].args[-2], 10.0, places=3)
        self.assertAlmostEqual(curves[-1].args[-1], 0.0, places=3)

    def test_zero_radius_arc_emits_line_not_curve(self) -> None:
        # rx=0 (or ry=0) is a degenerate ellipse — a straight line. Emitting a real
        # lineTo instead of a curveTo whose control points sit on that line is cheaper
        # against --max-nodes for the same visual result (matches picosvg's approach).
        cmds = imagevector_scripts.parse_path("M0 0A0 5 0 0 1 10 0")
        non_move = [c for c in cmds if c.op != "move"]
        self.assertEqual(len(non_move), 1)
        self.assertEqual(non_move[0].op, "line")
        self.assertAlmostEqual(non_move[0].args[0], 10.0, places=3)
        self.assertAlmostEqual(non_move[0].args[1], 0.0, places=3)

    def test_near_quarter_circle_roundoff_uses_one_segment(self) -> None:
        # This specific radius/start-angle combination is a verified reproduction of
        # a real case where the endpoint-to-center parameterization's acos/atan2 chain
        # computes dtheta as 1.570796326794897 instead of exactly math.pi/2
        # (1.5707963267948966) — a 90-degree arc, off by ~4e-16. Without the
        # picosvg-matching epsilon in the segment-count ceil(), that sliver pushes the
        # arc from 1 segment to 2 unnecessary ones.
        segments = imagevector_scripts._arc_to_cubics(
            -7.580376014150292, 0.2294545431208891,
            7.58384796150766, 7.58384796150766, 0,
            False, True,
            -0.2294545431208862, -7.580376014150292,
        )
        self.assertEqual(len(segments), 1)

    def test_relative_commands_become_absolute(self) -> None:
        rel_svg = '<svg viewBox="0 0 24 24"><path fill="#000" d="m2 2 l4 0 v4 h-4 z"/></svg>'
        kotlin, _ = self._convert(svg=rel_svg)
        self.assertIn("moveTo(2f, 2f)", kotlin)
        self.assertIn("lineTo(6f, 2f)", kotlin)
        self.assertIn("lineTo(6f, 6f)", kotlin)
        self.assertIn("lineTo(2f, 6f)", kotlin)


class SlotScaffoldTests(unittest.TestCase):
    def _wireframe(self, tmp: str, pattern: str = "A") -> Path:
        root = Path(tmp)
        ls = root / "docs" / "layout-system"
        ls.mkdir(parents=True)
        f = ls / "inbox.md"
        f.write_text(create_wireframe_scripts.render("Inbox", pattern), encoding="utf-8")
        return f

    def test_contract_parsed_and_kotlin_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            contract = slot_scaffold_scripts.load_contract(self._wireframe(tmp))
            kotlin = slot_scaffold_scripts.generate_kotlin(contract, "com.example.app")
            self.assertIn("GENERATED by generate_slot_scaffold", kotlin)
            self.assertIn("fun InboxLayout(", kotlin)
            for slot in ("nav", "side", "main"):
                self.assertIn(f"{slot}: @Composable () -> Unit,", kotlin)
            for bp in ("Compact", "Medium", "Expanded"):
                self.assertIn(f"WindowWidthSizeClass.{bp} ->", kotlin)
            self.assertIn("else ->", kotlin)  # exhaustive fall-back

    def test_weights_come_from_closed_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f = self._wireframe(tmp)
            text = f.read_text().replace("main: 3f", "main: 0.37f")
            f.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                slot_scaffold_scripts.load_contract(f)

    def test_missing_breakpoint_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f = self._wireframe(tmp)
            text = f.read_text().replace("compact: [main], ", "")
            f.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                slot_scaffold_scripts.load_contract(f)


class HandwrittenImageVectorTests(unittest.TestCase):
    def _builder(self, cmds: int, header: bool = False) -> str:
        lines = "\n".join(f"        lineTo({i}f, {i}f)" for i in range(cmds))
        head = "// GENERATED by convert_image_to_imagevector — do not edit\n" if header else ""
        return (f"{head}val V = ImageVector.Builder(name=\"V\").apply {{\n"
                f"    path {{\n        moveTo(0f, 0f)\n{lines}\n    }}\n}}.build()\n")

    def test_flags_handwritten_builder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "BadIcon.kt").write_text(self._builder(15), encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("handwritten imagevector" in f for f in findings))

    def test_ignores_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "GenIcon.kt").write_text(self._builder(15, header=True), encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("handwritten imagevector" in f for f in findings))

    def test_ignores_tiny_builder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "TinyIcon.kt").write_text(self._builder(3), encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("handwritten imagevector" in f for f in findings))


class RasterInCommonMainTests(unittest.TestCase):
    def test_flags_png_in_commonmain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "composeApp" / "src" / "commonMain" / "composeResources" / "drawable"
            d.mkdir(parents=True)
            (d / "ic_search.png").write_bytes(b"\x89PNG")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("raster asset in commonMain" in f for f in findings))

    def test_photos_dir_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "composeApp" / "src" / "commonMain" / "composeResources" / "photos"
            d.mkdir(parents=True)
            (d / "hero.jpg").write_bytes(b"\xff\xd8")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("raster asset in commonMain" in f for f in findings))

    def test_outside_commonmain_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "composeApp" / "src" / "androidMain" / "res" / "drawable"
            d.mkdir(parents=True)
            (d / "splash.png").write_bytes(b"\x89PNG")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("raster asset in commonMain" in f for f in findings))


class EmptyPlatformSourceSetTests(unittest.TestCase):
    def test_flags_directory_with_no_kt_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "auth" / "domain" / "src" / "androidMain" / "kotlin" / "com" / "example"
            d.mkdir(parents=True)
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("empty platform source set" in f for f in findings))

    def test_flags_file_with_only_package_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "auth" / "domain" / "src" / "iosMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "Stub.kt").write_text("package com.example.feature.auth.domain\n\n// nothing here yet\n",
                                        encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("empty platform source set" in f for f in findings))

    def test_ignores_common_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "auth" / "domain" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "LoginUseCase.kt").write_text("package com.example\nclass LoginUseCase\n", encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("empty platform source set" in f for f in findings))

    def test_ignores_populated_platform_sourceset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "auth" / "data" / "src" / "androidMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "AndroidHttpEngine.kt").write_text(
                "package com.example\nactual fun httpEngine() = Android.create()\n", encoding="utf-8"
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("empty platform source set" in f for f in findings))


class FocusedStateBorderWidthTests(unittest.TestCase):
    def _write(self, root: Path, filename: str, content: str) -> None:
        d = root / "src" / "commonMain" / "kotlin" / "ui"
        d.mkdir(parents=True, exist_ok=True)
        (d / filename).write_text(content, encoding="utf-8")

    def test_flags_focused_block_animating_border_width(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "ButtonStyles.kt",
                "internal val buttonInteractionStyle = Style {\n"
                "    focused { animate { borderWidth(2.dp); borderColor(colors.borderFocus) } }\n"
                "}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("focused state animates border width" in f for f in findings))

    def test_flags_selected_block_animating_border_bottom_width(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "ChipStyles.kt",
                "data object Selected : ChipVariant {\n"
                "    override val style = Style {\n"
                "        selected { animate { borderBottomWidth(1.dp); borderColor(colors.borderFocus) } }\n"
                "    }\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("focused state animates border width" in f for f in findings))

    def test_ignores_focused_block_animating_color_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "ButtonStyles.kt",
                "internal val buttonInteractionStyle = Style {\n"
                "    focused { animate { borderColor(colors.borderFocus) } }\n"
                "}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("focused state animates border width" in f for f in findings))

    def test_ignores_border_width_outside_state_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "ButtonStyles.kt",
                "data object Default : ButtonVariant {\n"
                "    override val style = Style {\n"
                "        borderWidth(2.dp)\n"
                "        borderColor(Color.Transparent)\n"
                "        focused { animate { borderColor(colors.borderFocus) } }\n"
                "    }\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("focused state animates border width" in f for f in findings))


class ToggleLayoutStabilityTests(unittest.TestCase):
    def _write(self, root: Path, filename: str, content: str) -> None:
        d = root / "src" / "commonMain" / "kotlin" / "ui"
        d.mkdir(parents=True, exist_ok=True)
        (d / filename).write_text(content, encoding="utf-8")

    def test_flags_icon_swap_between_chevron_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "Trigger.kt",
                "@Composable\nfun Trigger(isExpanded: Boolean) {\n"
                "    if (isExpanded) {\n"
                "        Icon(imageVector = Icons.Default.KeyboardArrowUp, contentDescription = null)\n"
                "    } else {\n"
                "        Icon(imageVector = Icons.Default.KeyboardArrowDown, contentDescription = null)\n"
                "    }\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("toggle icon swap instead of rotation" in f for f in findings))

    def test_ignores_icon_swap_when_graphics_layer_rotation_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "Trigger.kt",
                "@Composable\nfun Trigger(isExpanded: Boolean) {\n"
                "    val rotation by animateFloatAsState(if (isExpanded) 180f else 0f)\n"
                "    Icon(\n"
                "        imageVector = Icons.Default.KeyboardArrowDown,\n"
                "        contentDescription = null,\n"
                "        modifier = Modifier.graphicsLayer { rotationZ = rotation },\n"
                "    )\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("toggle icon swap instead of rotation" in f for f in findings))

    def test_ignores_single_icon_with_no_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "Trigger.kt",
                "@Composable\nfun Trigger() {\n"
                "    Icon(imageVector = Icons.Default.KeyboardArrowDown, contentDescription = null)\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("toggle icon swap instead of rotation" in f for f in findings))

    def test_flags_bare_conditional_around_composable_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "Collapsible.kt",
                "@Composable\nfun Collapsible(isExpanded: Boolean) {\n"
                "    Column {\n        TriggerRow()\n"
                "        if (isExpanded) {\n            Text(\"content\")\n        }\n    }\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("bare conditional collapse" in f for f in findings))

    def test_ignores_animated_visibility_wrapped_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "Collapsible.kt",
                "@Composable\nfun Collapsible(isExpanded: Boolean) {\n"
                "    Column {\n        TriggerRow()\n"
                "        AnimatedVisibility(visible = isExpanded) {\n            Text(\"content\")\n        }\n    }\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("bare conditional collapse" in f for f in findings))

    def test_ignores_bare_conditional_without_composable_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "Toggle.kt",
                "@Composable\nfun Toggle(isExpanded: Boolean) {\n"
                "    if (isExpanded) {\n        println(\"expanded\")\n    }\n}\n",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("bare conditional collapse" in f for f in findings))


class DesignSystemPrefixMismatchTests(unittest.TestCase):
    def _write_docs(self, root: Path, prefix: str) -> None:
        d = root / "docs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "design-system.md").write_text(
            f"| Field | Value |\n|---|---|\n| Component prefix | {prefix} |\n",
            encoding="utf-8",
        )

    def _write_component(self, root: Path, filename: str, fn_name: str) -> None:
        d = root / "core" / "designsystem" / "components"
        d.mkdir(parents=True, exist_ok=True)
        (d / filename).write_text(
            f"@Composable\nfun {fn_name}(onClick: () -> Unit) {{}}\n", encoding="utf-8"
        )

    def test_flags_app_named_component_when_prefix_resolved_differently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_docs(root, "GuildBase")
            self._write_component(root, "AppButton.kt", "AppButton")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("design system prefix mismatch" in f for f in findings))

    def test_ignores_consistent_resolved_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_docs(root, "GuildBase")
            self._write_component(root, "GuildBaseButton.kt", "GuildBaseButton")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("design system prefix mismatch" in f for f in findings))

    def test_ignores_when_prefix_genuinely_app(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_docs(root, "App")
            self._write_component(root, "AppButton.kt", "AppButton")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("design system prefix mismatch" in f for f in findings))

    def test_ignores_when_no_design_system_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_component(root, "AppButton.kt", "AppButton")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("design system prefix mismatch" in f for f in findings))

    def test_ignores_unfilled_template_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_docs(root, "COMPONENT_PREFIX")
            self._write_component(root, "AppButton.kt", "AppButton")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("design system prefix mismatch" in f for f in findings))


class StyleApiComplianceTests(unittest.TestCase):
    def _write(self, root: Path, name: str, content: str) -> None:
        d = root / "app" / "src" / "commonMain" / "kotlin"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(content, encoding="utf-8")

    def test_flags_style_default_with_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Bad.kt",
                "@Composable\nfun BadButton(style: Style = Style { background(Color.Red) }) {}\n")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("style default with body" in f for f in findings))

    def test_ignores_empty_style_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Good.kt", "@Composable\nfun GoodButton(style: Style = Style) {}\n")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("style default with body" in f for f in findings))

    def test_flags_style_state_wrong_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Bad.kt",
                "fun x() {\n    val styleState = remember { MutableStyleState(i) }\n    styleState.enabled = true\n}\n")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("style state wrong enabled property" in f for f in findings))

    def test_ignores_correct_is_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Good.kt",
                "fun x() {\n    val styleState = rememberUpdatedStyleState(i) { it.isEnabled = true }\n}\n")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("style state wrong enabled property" in f for f in findings))

    def test_flags_style_param_on_screen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Bad.kt", "@Composable\nfun HomeScreen(style: Style = Style) {}\n")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("style param on screen composable" in f for f in findings))

    def test_ignores_style_param_on_component(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Good.kt", "@Composable\nfun AppButton(style: Style = Style) {}\n")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("style param on screen composable" in f for f in findings))

    def test_flags_stale_compositionlocal_in_style_function(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Bad.kt",
                "@Composable\n"
                "fun containerStyle(): Style {\n"
                "    val background = MaterialTheme.colorScheme.background\n"
                "    return Style {\n"
                "        background(background)\n"
                "    }\n"
                "}\n")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("stale compositionlocal in style function" in f for f in findings))

    def test_ignores_style_scope_extension_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Good.kt",
                "val containerStyle = Style {\n    background(colors.background)\n}\n")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("stale compositionlocal in style function" in f for f in findings))

    def test_flags_missing_indication_null(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Bad.kt",
                "val s = Style {\n    pressed { animate { background(Color.Red) } }\n}\n"
                "fun x() {\n    Modifier.clickable(onClick = {})\n}\n")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("missing indication null with style state" in f for f in findings))

    def test_ignores_when_indication_null_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Good.kt",
                "val s = Style {\n    pressed { animate { background(Color.Red) } }\n}\n"
                "fun x() {\n    Modifier.clickable(onClick = {}, indication = null)\n}\n")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("missing indication null with style state" in f for f in findings))


class HardcodedVersionCodeTests(unittest.TestCase):
    def test_flags_literal_version_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "androidApp"
            d.mkdir(parents=True)
            (d / "build.gradle.kts").write_text(
                'plugins { id("com.android.application") }\n'
                "android {\n"
                "    defaultConfig {\n"
                '        applicationId = "com.example.app"\n'
                "        versionCode = 1\n"
                '        versionName = "1.19.1"\n'
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("hardcoded android versioncode" in f for f in findings))

    def test_ignores_derived_formula(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "androidApp"
            d.mkdir(parents=True)
            (d / "build.gradle.kts").write_text(
                'plugins { id("com.android.application") }\n'
                "android {\n"
                "    defaultConfig {\n"
                '        applicationId = "com.example.app"\n'
                "        versionCode = major * 1_000_000 + minor * 1_000 + patch\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded android versioncode" in f for f in findings))

    def test_ignores_variable_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "androidApp"
            d.mkdir(parents=True)
            (d / "build.gradle.kts").write_text(
                'plugins { id("com.android.application") }\n'
                "val computedVersionCode = 1_000_002\n"
                "android {\n"
                "    defaultConfig {\n"
                '        applicationId = "com.example.app"\n'
                "        versionCode = computedVersionCode\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded android versioncode" in f for f in findings))

    def test_ignores_non_android_app_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "someModule"
            d.mkdir(parents=True)
            (d / "build.gradle.kts").write_text("val versionCode = 1\n", encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("hardcoded android versioncode" in f for f in findings))


class LayoutGuardrailTests(unittest.TestCase):
    def test_flags_arbitrary_weight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "S.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable fun S() { Box(Modifier.weight(0.37f)) }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("raw weight literal" in f for f in findings))

    def test_ignores_simple_fractions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "S.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable fun S() { Row { Box(Modifier.weight(1f)); Box(Modifier.weight(1.5f)) } }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("raw weight literal" in f for f in findings))

    def test_flags_partial_breakpoint_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "P.kt").write_text(
                "fun p(w: WindowSizeClass) { when (w.widthSizeClass) { WindowWidthSizeClass.Compact -> a() } }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("breakpoint branch missing" in f for f in findings))

    def test_full_coverage_and_else_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "commonMain" / "kotlin"
            d.mkdir(parents=True)
            (d / "F.kt").write_text(
                "fun f(w: WindowSizeClass) { when (w.widthSizeClass) {\n"
                "    WindowWidthSizeClass.Compact -> a()\n"
                "    WindowWidthSizeClass.Medium -> b()\n"
                "    WindowWidthSizeClass.Expanded -> c()\n"
                "} }\n",
                encoding="utf-8",
            )
            (d / "E.kt").write_text(
                "fun e(w: WindowSizeClass) { when (w.widthSizeClass) {\n"
                "    WindowWidthSizeClass.Compact -> a()\n"
                "    else -> b()\n"
                "} }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("breakpoint branch missing" in f for f in findings))


class CreateWireframeTests(unittest.TestCase):
    def _write(self, root: Path, screen: str, pattern: str = "A") -> Path:
        ls_dir = root / "docs" / "layout-system"
        ls_dir.mkdir(parents=True, exist_ok=True)
        components = ls_dir / "_components.md"
        if not components.exists():
            components.write_text(create_wireframe_scripts._COMPONENTS_TEMPLATE, encoding="utf-8")
        screen_file = ls_dir / f"{create_wireframe_scripts.slugify(screen)}.md"
        if screen_file.exists():
            return None
        screen_file.write_text(create_wireframe_scripts.render(screen, pattern), encoding="utf-8")
        return screen_file

    def test_each_screen_is_a_separate_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Inbox", "A")
            self._write(root, "Login", "D")
            screens = sorted((root / "docs" / "layout-system").glob("*.md"))
            names = {p.name for p in screens}
            self.assertIn("inbox.md", names)
            self.assertIn("login.md", names)
            self.assertIn("_components.md", names)

    def test_does_not_overwrite_existing_screen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Inbox", "A")
            again = self._write(root, "Inbox", "A")
            self.assertIsNone(again)  # refuses second create

    def test_screen_file_has_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self._write(root, "Inbox", "A")
            text = p.read_text()
            for token in ("# Inbox", "## Components", "## Interaction notes", "```"):
                self.assertIn(token, text)


class CreateLessonTests(unittest.TestCase):
    def _run(self, root: Path, title: str, **kw) -> int:
        import argparse
        args = argparse.Namespace(
            skill=kw.get("skill", "kotlin-multiplatform-mvi"),
            type=kw.get("type", "correction"),
            severity=kw.get("severity", "high"),
            title=title,
            followed=kw.get("followed"), broke=kw.get("broke"), correct=kw.get("correct"),
            evidence=kw.get("evidence"), proposed=kw.get("proposed"),
            root=root, date=kw.get("date", "2026-06-30"),
        )
        # Render + write the way main() does, without argparse/CLI.
        date = args.date
        lessons_dir = root / "docs" / "lessons"
        lessons_dir.mkdir(parents=True, exist_ok=True)
        path = create_lesson_scripts.unique_path(lessons_dir, date, create_lesson_scripts.slugify(title))
        path.write_text(create_lesson_scripts.render(args, date), encoding="utf-8")
        return path

    def test_each_call_creates_a_separate_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run(root, "Effect replayed on nav back")
            self._run(root, "No nested graph guidance", skill="kotlin-multiplatform-navigation", type="gap", severity="medium")
            files = sorted((root / "docs" / "lessons").glob("*.md"))
            self.assertEqual(len(files), 2)

    def test_duplicate_title_does_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p1 = self._run(root, "Same title")
            p2 = self._run(root, "Same title")
            self.assertNotEqual(p1, p2)
            self.assertEqual(len(list((root / "docs" / "lessons").glob("*.md"))), 2)

    def test_file_has_required_frontmatter_and_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self._run(root, "Effect replay", evidence="Foo.kt:10")
            text = p.read_text()
            for token in ("skill:", "date:", "severity:", "type:",
                          "## What we followed", "## Correct pattern", "## Evidence"):
                self.assertIn(token, text)

    def test_slug_and_date_in_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self._run(root, "Effect Replayed!! On Nav Back")
            self.assertEqual(p.name, "2026-06-30-effect-replayed-on-nav-back.md")


class FixedWidthOverflowTests(unittest.TestCase):
    def test_flags_large_fixed_width(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "S.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\nfun S() { Box(Modifier.width(400.dp)) }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("fixed width overflow" in f for f in findings))

    def test_flags_required_width(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "S.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\nfun S() { Card(Modifier.requiredWidth(300.dp)) }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("fixed width overflow" in f for f in findings))

    def test_ignores_small_and_responsive_widths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "S.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\nfun S() { Box(Modifier.width(48.dp).fillMaxWidth()) }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("fixed width overflow" in f for f in findings))


class DeriveComponentPrefixTests(unittest.TestCase):
    def test_pascal_case_project_name(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name("GuildBase"), "GuildBase")

    def test_kebab_case_strips_noise_word(self) -> None:
        # "app" is a generic noise word — stripped when other words remain.
        self.assertEqual(derive_prefix_scripts.derive_from_name("acme-shop-app"), "AcmeShop")

    def test_space_separated_name(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name("Guild Base"), "GuildBase")

    def test_snake_case_name(self) -> None:
        # "admin" is part of the product identity, not generic noise — kept.
        self.assertEqual(derive_prefix_scripts.derive_from_name("lordnine_admin"), "LordnineAdmin")

    def test_pure_noise_word_falls_back_to_app(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name("app"), "App")

    def test_empty_name_falls_back_to_app(self) -> None:
        self.assertEqual(derive_prefix_scripts.derive_from_name(""), "App")

    def test_settings_gradle_kts_takes_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text(
                'rootProject.name = "GuildBase"\n', encoding="utf-8"
            )
            (root / "build.gradle.kts").write_text(
                'group = "com.example.other"\n', encoding="utf-8"
            )
            raw_name, source = derive_prefix_scripts.resolve_source(root, None)
            self.assertEqual(raw_name, "GuildBase")
            self.assertIn("settings.gradle.kts", source)

    def test_falls_back_to_group_id_last_segment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle.kts").write_text(
                'group = "com.example.lordnine"\n', encoding="utf-8"
            )
            raw_name, source = derive_prefix_scripts.resolve_source(root, None)
            self.assertEqual(raw_name, "lordnine")
            self.assertIn("group ID", source)

    def test_explicit_name_overrides_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text(
                'rootProject.name = "Ignored"\n', encoding="utf-8"
            )
            raw_name, source = derive_prefix_scripts.resolve_source(root, "Explicit Name")
            self.assertEqual(raw_name, "Explicit Name")
            self.assertIn("--name", source)

    def test_falls_back_to_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "MyCoolApp"
            root.mkdir()
            raw_name, source = derive_prefix_scripts.resolve_source(root, None)
            self.assertEqual(raw_name, "MyCoolApp")
            self.assertIn("directory", source)

    def test_result_is_legal_kotlin_identifier_start(self) -> None:
        # A name that is purely numeric/symbolic must not produce an invalid prefix.
        self.assertEqual(derive_prefix_scripts.derive_from_name("123"), "App")


class RawComponentBypassTests(unittest.TestCase):
    def _ds_marker(self, d: Path) -> None:
        # A file that establishes the project HAS a design system.
        (d / "AppButton.kt").write_text(
            "import androidx.compose.runtime.Composable\n"
            "@Composable\nfun AppButton(onClick: () -> Unit) { BasicText(\"x\") }\n",
            encoding="utf-8",
        )

    def test_flags_raw_components_when_design_system_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            self._ds_marker(d)
            (d / "HomeScreen.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\n"
                "fun HomeScreen() {\n"
                "    Scaffold {\n"
                "        Button(onClick = {}) { Text(\"Save\") }\n"
                "        Card { Text(\"hi\") }\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("raw component bypass" in f for f in findings))

    def test_ignores_app_wrapper_definition_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            self._ds_marker(d)
            # AppCard.kt defines a wrapper and legitimately uses a raw Card internally
            (d / "AppCard.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\nfun AppCard(content: @Composable () -> Unit) { Card { content() } }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("AppCard.kt" in f and "raw component bypass" in f for f in findings))

    def test_ignores_screen_using_app_components(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            self._ds_marker(d)
            (d / "GoodScreen.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\nfun GoodScreen() { AppScaffold { AppButton(onClick = {}) {} } }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("GoodScreen.kt" in f and "raw component bypass" in f for f in findings))

    def test_ignores_project_without_design_system(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            # No App* / AppTheme anywhere — raw Material is the project's choice.
            (d / "HomeScreen.kt").write_text(
                "import androidx.compose.runtime.Composable\n"
                "@Composable\nfun HomeScreen() { Scaffold { Button(onClick = {}) {} } }\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("raw component bypass" in f for f in findings))


class FindingEvidenceTests(unittest.TestCase):
    def test_findings_include_file_line_and_snippet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "HomeScreen.kt").write_text(
                "@Composable\n"
                "fun HomeScreen() {\n"
                "    HorizontalDivider(color = Color.Gray)\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            divider = next(f for f in findings if "hardcoded divider color" in f)
            # file:line anchor present
            self.assertIn("HomeScreen.kt:3", divider)
            # matched source line included as evidence
            self.assertIn("HorizontalDivider(color = Color.Gray)", divider)
            # severity tag preserved for release-gate parsing
            self.assertTrue(any("[HIGH]" in f or "[MEDIUM]" in f or ":" in f for f in findings))


class RepositoryLeakTests(unittest.TestCase):
    def test_flags_interface_returning_dto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "user" / "api" / "src"
            d.mkdir(parents=True)
            (d / "UserRepository.kt").write_text(
                "interface UserRepository {\n"
                "    suspend fun getUser(id: String): UserDto\n"
                "    fun observeUsers(): Flow<List<UserEntity>>\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("repository leaks data type" in f for f in findings))

    def test_ignores_interface_with_domain_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "product" / "api" / "src"
            d.mkdir(parents=True)
            (d / "ProductRepository.kt").write_text(
                "interface ProductRepository {\n"
                "    suspend fun getProduct(id: String): Product\n"
                "    fun observeProducts(): Flow<List<Product>>\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("repository leaks data type" in f for f in findings))

    def test_ignores_repository_impl_using_dto_internally(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "product" / "data" / "src"
            d.mkdir(parents=True)
            (d / "ProductRepositoryImpl.kt").write_text(
                "class ProductRepositoryImpl(private val api: ProductApi) : ProductRepository {\n"
                "    override suspend fun getProduct(id: String): Product {\n"
                "        val dto: ProductDto = api.fetch(id)\n"
                "        return dto.toDomain()\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("repository leaks data type" in f for f in findings))

    def test_flags_entity_import_in_domain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "user" / "domain" / "src"
            d.mkdir(parents=True)
            (d / "GetUser.kt").write_text(
                "import com.example.data.entity.UserEntity\nclass GetUser {}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("dto leak to domain" in f for f in findings))


class StringNavigationTests(unittest.TestCase):
    def test_flags_string_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "AppNavHost.kt").write_text(
                'NavHost(navController, startDestination = "home") {\n'
                '    composable("home") { HomeScreen() }\n'
                '    composable(route = "detail/{id}") { DetailScreen() }\n'
                '}\n'
                'fun go() { navController.navigate("home") }\n',
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("string navigation" in f for f in findings))

    def test_ignores_type_safe_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "AppNavHost.kt").write_text(
                'NavHost(navController, startDestination = HomeRoute) {\n'
                '    composable<HomeRoute> { HomeScreen() }\n'
                '    composable<DetailRoute> { DetailScreen() }\n'
                '}\n'
                'fun go() { navController.navigate(HomeRoute) }\n',
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("string navigation" in f for f in findings))

    def test_ignores_deep_link_uri_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "app" / "src" / "main" / "kotlin"
            d.mkdir(parents=True)
            (d / "DeepLink.kt").write_text(
                'fun open() { navController.navigate("myapp://detail/42") }\n',
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("string navigation" in f for f in findings))


class ViewModelAsComposableParamTests(unittest.TestCase):
    def test_flags_composable_with_required_viewmodel_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "home" / "ui" / "src"
            d.mkdir(parents=True)
            (d / "HomeScreen.kt").write_text(
                "@Composable\n"
                "fun HomeScreen(studioVm: StudioViewModel, healthVm: HealthViewModel) {}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel as composable param" in f for f in findings))

    def test_ignores_defaulted_koinviewmodel_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "home" / "ui" / "src"
            d.mkdir(parents=True)
            (d / "HomeScreen.kt").write_text(
                "@Composable\n"
                "fun HomeScreen(vm: HomeViewModel = koinViewModel()) {}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("viewmodel as composable param" in f for f in findings))

    def test_ignores_content_composable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "feature" / "home" / "ui" / "src"
            d.mkdir(parents=True)
            (d / "HomeContent.kt").write_text(
                "@Composable\n"
                "fun HomeContent(state: FooState, onIntent: (FooIntent) -> Unit) {}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("viewmodel as composable param" in f for f in findings))

    def test_flags_outside_ui_path(self) -> None:
        # No /ui/ segment — common when a project does not use the layered module convention.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "composeApp" / "src" / "commonMain" / "kotlin" / "home"
            d.mkdir(parents=True)
            (d / "HomeScreen.kt").write_text(
                "@Composable\n"
                "fun HomeScreen(studioVm: StudioViewModel) {}\n",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("viewmodel as composable param" in f for f in findings))


class GodComposableTests(unittest.TestCase):
    def test_flags_screen_with_many_launched_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "studio" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            body = "\n".join(f"LaunchedEffect(key{i}) {{ doThing() }}" for i in range(6))
            (ui_dir / "HomeScreen.kt").write_text(body, encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("god composable" in f for f in findings))

    def test_flags_screen_with_many_effect_collects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "studio" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            body = "\n".join(f"vm{i}.effect.collect {{ relay() }}" for i in range(3))
            (ui_dir / "HomeScreen.kt").write_text(body, encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("god composable" in f for f in findings))

    def test_high_severity_for_extreme_orchestration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "studio" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            body = "\n".join(f"LaunchedEffect(key{i}) {{ x() }}" for i in range(9))
            (ui_dir / "HomeScreen.kt").write_text(body, encoding="utf-8")
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("god composable [HIGH]" in f for f in findings))

    def test_ignores_screen_with_one_launched_effect(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "LaunchedEffect(vm) { vm.effect.collect { } }",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("god composable" in f for f in findings))


class RedundantTitleTests(unittest.TestCase):
    def test_flags_screen_with_topbar_and_heading_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "fun HomeScreen() {\n"
                "  AppScaffold(topBar = { AppTopAppBar(title = \"Home\") }) {\n"
                "    AppText(\"Home\", style = AppTextStyle.HeadlineLarge)\n"
                "  }\n"
                "}",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("redundant screen title" in f for f in findings))

    def test_ignores_screen_with_only_topbar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "fun HomeScreen() {\n"
                "  AppScaffold(topBar = { AppTopAppBar(title = \"Home\") }) {\n"
                "    AppText(\"Welcome back\", style = AppTextStyle.BodyLarge)\n"
                "  }\n"
                "}",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("redundant screen title" in f for f in findings))

    def test_ignores_non_screen_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeViewModel.kt").write_text(
                "fun HomeViewModel() {\n"
                "  AppScaffold(topBar = { AppTopAppBar(title = \"Home\") }) {\n"
                "    AppText(\"Home\", style = AppTextStyle.H1)\n"
                "  }\n"
                "}",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("redundant screen title" in f for f in findings))


class AdaptiveCoverageTests(unittest.TestCase):
    def test_flags_screen_missing_windowsizeclass_when_project_uses_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            # One file that uses WindowSizeClass (triggers the check)
            (ui_dir / "AppRoot.kt").write_text(
                "val wsc: WindowSizeClass = calculateWindowSizeClass()",
                encoding="utf-8",
            )
            # Screen that doesn't receive it
            (ui_dir / "HomeScreen.kt").write_text(
                "fun HomeScreen(onBack: () -> Unit) {}",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertTrue(any("adaptive coverage" in f for f in findings))

    def test_ignores_project_without_windowsizeclass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "HomeScreen.kt").write_text(
                "fun HomeScreen(onBack: () -> Unit) {}",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("adaptive coverage" in f for f in findings))

    def test_ignores_screen_that_has_windowsizeclass_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "home" / "ui" / "src"
            ui_dir.mkdir(parents=True)
            (ui_dir / "AppRoot.kt").write_text(
                "val wsc: WindowSizeClass = calculateWindowSizeClass()",
                encoding="utf-8",
            )
            (ui_dir / "HomeScreen.kt").write_text(
                "fun HomeScreen(windowSizeClass: WindowSizeClass, onBack: () -> Unit) {}",
                encoding="utf-8",
            )
            findings = audit_scripts.audit_project(root)
            self.assertFalse(any("adaptive coverage" in f for f in findings))


class ScaffoldAuthServiceTests(unittest.TestCase):
    def test_scaffold_auth_service_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            auth_service_scripts.scaffold_auth_service(root, "com.example.server")

            expected = {
                "routes/AuthRoutes.kt",
                "service/AuthService.kt",
                "service/TokenService.kt",
                "model/AuthRequest.kt",
                "model/AuthResponse.kt",
                "model/AuthError.kt",
                "di/AuthModule.kt",
            }
            self.assertTrue(expected.issubset({str(p.relative_to(root)) for p in root.rglob("*.kt")}))
            self.assertIn("package com.example.server.auth.model", (root / "model" / "AuthRequest.kt").read_text(encoding="utf-8"))
            self.assertIn("package com.example.server.auth.di", (root / "di" / "AuthModule.kt").read_text(encoding="utf-8"))


class ScaffoldMongoDatabaseTests(unittest.TestCase):
    def test_scaffold_mongodb_database_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            mongodb_scripts.scaffold_mongodb_database(root, "com.example.server")

            expected = {
                "MongoClientFactory.kt",
                "di/DatabaseModule.kt",
                "user/data/UserDocument.kt",
                "user/repository/UserRepository.kt",
                "user/repository/UserRepositoryImpl.kt",
            }
            self.assertTrue(expected.issubset({str(p.relative_to(root)) for p in root.rglob("*.kt")}))
            self.assertIn("package com.example.server.database", (root / "MongoClientFactory.kt").read_text(encoding="utf-8"))
            self.assertIn("package com.example.server.user.repository", (root / "user" / "repository" / "UserRepository.kt").read_text(encoding="utf-8"))


class ScaffoldKotlinRpcTests(unittest.TestCase):
    def test_scaffold_kotlin_rpc_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            rpc_scripts.scaffold_kotlin_rpc(root, "com.example.app")

            expected = {
                "shared/rpc/GreetingService.kt",
                "shared/rpc/model/GreetingRequest.kt",
                "shared/rpc/model/GreetingResponse.kt",
                "server/rpc/GreetingRpcModule.kt",
                "client/rpc/GreetingRpcClient.kt",
            }
            self.assertTrue(expected.issubset({str(p.relative_to(root)) for p in root.rglob("*.kt")}))
            self.assertIn("package com.example.app.rpc", (root / "shared" / "rpc" / "GreetingService.kt").read_text(encoding="utf-8"))
            self.assertIn("package com.example.app.server.rpc", (root / "server" / "rpc" / "GreetingRpcModule.kt").read_text(encoding="utf-8"))


class AuditSkillsRepoTests(unittest.TestCase):
    def test_audit_skills_repo_flags_missing_freshness_and_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            skill_dir = root / "skills" / "example-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Ktor example\n---\n\n## When to Use This Skill\n\nUses ktor client code.\n",
                encoding="utf-8",
            )
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("missing freshness guidance" in finding for finding in findings))

    def test_audit_skills_repo_flags_missing_all_targets_branch_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            scaffold_dir = root / "skills" / "kotlin-multiplatform-feature-scaffold"
            scaffold_dir.mkdir(parents=True)
            (scaffold_dir / "SKILL.md").write_text(
                "---\nname: kotlin-multiplatform-feature-scaffold\ndescription: scaffold\n---\n\n## When to Use This Skill\n\nall-frontends-shared\n",
                encoding="utf-8",
            )
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("missing all-targets branch guidance" in finding for finding in findings))

    def test_audit_skills_repo_flags_missing_build_logic_toml_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            scaffold_dir = root / "skills" / "kotlin-multiplatform-feature-scaffold"
            scaffold_dir.mkdir(parents=True)
            (scaffold_dir / "SKILL.md").write_text(
                "---\nname: kotlin-multiplatform-feature-scaffold\ndescription: scaffold\n---\n\n## When to Use This Skill\n\nbuild-logic only\n",
                encoding="utf-8",
            )
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("missing build-logic and libs.versions.toml guidance" in finding for finding in findings))


    def test_audit_skills_repo_flags_all_missing_required_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            skill_dir = root / "skills" / "example-skill"
            skill_dir.mkdir(parents=True)
            # SKILL.md with none of the 4 required markers
            (skill_dir / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: example\n---\n\nSome content.\n",
                encoding="utf-8",
            )

            findings = audit_repo_scripts.audit_skills_repo(root)
            marker_finding = next((f for f in findings if "missing markers" in f), None)

            self.assertIsNotNone(marker_finding, "expected a 'missing markers' finding")
            self.assertIn("## When to Use This Skill", marker_finding)
            self.assertIn("Trigger keywords:", marker_finding)
            self.assertIn("metadata:", marker_finding)
            self.assertIn("last-updated:", marker_finding)

    def test_audit_skills_repo_no_marker_finding_when_all_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            skill_dir = root / "skills" / "example-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: example\nmetadata:\n  last-updated: '2026-06-18'\n---\n\n"
                "## When to Use This Skill\n\n**Trigger keywords:** example.\n\n## Changelog\n\n| Date | Change |\n|---|---|\n| 2026-06-18 | Initial release. |\n",
                encoding="utf-8",
            )

            findings = audit_repo_scripts.audit_skills_repo(root)

            self.assertFalse(any("missing markers" in f for f in findings))


    # ── Design-system content checks ────────────────────────────────────────────

    def _make_ds_skill(self, root: Path, name: str, content: str) -> None:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    _DS_GOOD_CONTENT = (
        "## When to Use This Skill\n\n**Trigger keywords:** design system.\n\nmetadata:\n"
        "  last-updated: '2026-06-22'\n\n"
        "OptIn(ExperimentalStylesApi\n"
        "fun AppButton(\nfun AppBadge(\nfun AppCard(\nfun AppChip(\nfun AppTextField(\nfun AppText(\n"
        "## Component Previews\n\n### `previews/AppButtonPreview.kt`\n```kotlin\n// preview\n```\n\n"
        "## Changelog\n\n| Date | Change |\n|---|---|\n| 2026-06-22 | v1. |\n"
    )

    def test_ds_flags_missing_component(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            # AppTextField omitted
            content = self._DS_GOOD_CONTENT.replace("fun AppTextField(\n", "")
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("fun AppTextField" in f for f in findings))

    def test_ds_flags_textstyle_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            content = self._DS_GOOD_CONTENT + "enum class TextStyle {\n  BodyMedium\n}\n"
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("enum class TextStyle" in f for f in findings))

    def test_ds_flags_missing_optins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            content = self._DS_GOOD_CONTENT.replace("OptIn(ExperimentalStylesApi\n", "ExperimentalStylesApi\n")
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("ExperimentalStylesApi" in f and "@OptIn" in f for f in findings))

    def test_ds_flags_static_apptheme_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            content = self._DS_GOOD_CONTENT + "padding(AppTheme.spacing.lg)\n"
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("AppTheme" in f and "static" in f for f in findings))

    def test_ds_flags_hardcoded_dp_in_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            content = self._DS_GOOD_CONTENT + "override val contentPadding = 24.dp\n"
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("override val" in f and "N.dp" in f for f in findings))

    def test_ds_exempts_component_dimension_dp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            # `override val dp = 24.dp` is an IconSize/AvatarSize enum — exempt
            content = self._DS_GOOD_CONTENT + "override val dp = 24.dp\n"
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertFalse(any("override val" in f and "N.dp" in f for f in findings))

    def test_ds_clean_passes_all_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", self._DS_GOOD_CONTENT)
            findings = audit_repo_scripts.audit_skills_repo(root)
            ds_findings = [f for f in findings if "design-system" in f]
            self.assertEqual([], ds_findings)

    def test_ds_flags_missing_component_previews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# r\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            content = self._DS_GOOD_CONTENT.replace(
                "## Component Previews\n\n### `previews/AppButtonPreview.kt`\n```kotlin\n// preview\n```\n\n",
                "",
            )
            self._make_ds_skill(root, "kotlin-multiplatform-design-system", content)
            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("Component Previews" in f for f in findings))

    # ── Detekt rules module structure ────────────────────────────────────────────

    def test_detekt_rules_directory_exists(self) -> None:
        """detekt-rules/ directory must exist in the design-system skill."""
        detekt_dir = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "detekt-rules"
        )
        self.assertTrue(detekt_dir.is_dir(), "detekt-rules/ directory missing")

    def test_detekt_rules_contains_all_rule_files(self) -> None:
        rules_dir = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "kotlin"
            / "GROUP_ID" / "designsystem" / "detekt"
        )
        expected = [
            "DesignSystemRuleSetProvider.kt",
            "HardcodedColorRule.kt",
            "HardcodedDpRule.kt",
            "MaterialThemeUsageRule.kt",
            "DirectTextStyleRule.kt",
            "NestedContainerRule.kt",
            "ComponentRegistryRule.kt",
            "ImportBoundaryRule.kt",
            "RedundantScreenTitleRule.kt",
            "HardcodedGridColumnsRule.kt",
        ]
        for fname in expected:
            self.assertTrue((rules_dir / fname).exists(), f"Missing rule file: {fname}")

    def test_detekt_rules_build_gradle_exists(self) -> None:
        build_file = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "build.gradle.kts"
        )
        self.assertTrue(build_file.exists())
        content = build_file.read_text()
        self.assertIn("detekt-api", content)

    def test_detekt_rules_config_exists(self) -> None:
        config_file = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "config" / "detekt-design-system.yml"
        )
        self.assertTrue(config_file.exists())
        content = config_file.read_text()
        for rule in ("HardcodedColor", "HardcodedDp", "MaterialThemeUsage",
                     "DirectTextStyle", "NestedContainer",
                     "ComponentRegistryRule", "ImportBoundaryRule",
                     "RedundantScreenTitleRule", "HardcodedGridColumnsRule"):
            self.assertIn(rule, content, f"Config missing rule: {rule}")

    def test_detekt_rules_service_loader_file_exists(self) -> None:
        svc_file = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "resources"
            / "META-INF" / "services"
            / "io.gitlab.arturbosch.detekt.api.RuleSetProvider"
        )
        self.assertTrue(svc_file.exists())
        self.assertIn("DesignSystemRuleSetProvider", svc_file.read_text())

    def test_detekt_rule_set_provider_has_all_9_rules(self) -> None:
        provider_kt = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "kotlin"
            / "GROUP_ID" / "designsystem" / "detekt"
            / "DesignSystemRuleSetProvider.kt"
        )
        content = provider_kt.read_text()
        for rule in ("HardcodedColorRule", "HardcodedDpRule", "MaterialThemeUsageRule",
                     "DirectTextStyleRule", "NestedContainerRule",
                     "ComponentRegistryRule", "ImportBoundaryRule",
                     "RedundantScreenTitleRule", "HardcodedGridColumnsRule"):
            self.assertIn(rule, content, f"RuleSetProvider missing: {rule}")

    def test_redundant_screen_title_rule_exists(self) -> None:
        rule_kt = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "kotlin"
            / "GROUP_ID" / "designsystem" / "detekt"
            / "RedundantScreenTitleRule.kt"
        )
        content = rule_kt.read_text()
        self.assertIn("RedundantScreenTitle", content)
        self.assertIn("KtTreeVisitorVoid", content)
        self.assertIn("AppTopAppBar", content)

    def test_hardcoded_grid_columns_rule_exists(self) -> None:
        rule_kt = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "kotlin"
            / "GROUP_ID" / "designsystem" / "detekt"
            / "HardcodedGridColumnsRule.kt"
        )
        content = rule_kt.read_text()
        self.assertIn("HardcodedGridColumns", content)
        self.assertIn("GridCells", content)
        self.assertIn("Adaptive", content)

    def test_component_registry_rule_uses_configurable_prefix(self) -> None:
        rule_kt = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "kotlin"
            / "GROUP_ID" / "designsystem" / "detekt"
            / "ComponentRegistryRule.kt"
        )
        content = rule_kt.read_text()
        self.assertIn("componentPrefix", content)
        self.assertIn("valueOrDefault", content)

    def test_import_boundary_rule_scoped_to_feature_ui(self) -> None:
        rule_kt = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "detekt-rules" / "src" / "main" / "kotlin"
            / "GROUP_ID" / "designsystem" / "detekt"
            / "ImportBoundaryRule.kt"
        )
        content = rule_kt.read_text()
        self.assertIn("/feature/", content)
        self.assertIn("/ui/", content)

    # ── New commands exist ────────────────────────────────────────────────────────

    def test_design_system_template_exists(self) -> None:
        template = (
            REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
            / "references" / "design-system-template.md"
        )
        self.assertTrue(template.exists(), "design-system-template.md missing from references/")
        content = template.read_text()
        for section in ("PROJECT_NAME", "GROUP_ID", "COMPONENT_PREFIX",
                        "Color palette", "Typography", "Spacing scale",
                        "Component Inventory", "Ownership Model",
                        "Detekt Rules", "Multi-Device Preview", "Design Audit Log"):
            self.assertIn(section, content, f"Template missing section: {section}")

    def test_record_design_baselines_command_exists(self) -> None:
        cmd = REPO_ROOT / "commands" / "kmm-record-design-baselines.md"
        self.assertTrue(cmd.exists())
        content = cmd.read_text()
        self.assertIn("roborazzi.record=true", content)
        self.assertIn("roborazzi.verify=true", content)

    def test_audit_design_visual_command_exists(self) -> None:
        cmd = REPO_ROOT / "commands" / "kmm-audit-design-visual.md"
        self.assertTrue(cmd.exists())
        content = cmd.read_text()
        self.assertIn("snapshots", content)
        self.assertIn("vision", content.lower())

    def test_fix_design_references_detekt_as_primary(self) -> None:
        cmd = REPO_ROOT / "commands" / "kmm-fix-design.md"
        content = cmd.read_text()
        self.assertIn("detekt", content)
        self.assertIn("detekt-design-system.yml", content)

    # ── Naming conventions ───────────────────────────────────────────────────────

    def test_naming_flags_uppercase_file_in_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            (root / "skills").mkdir()
            cmd_dir = root / "commands"
            cmd_dir.mkdir()
            (cmd_dir / "NewFeature.md").write_text("# cmd\n", encoding="utf-8")

            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("naming" in f and "NewFeature.md" in f for f in findings))

    def test_naming_flags_lowercase_root_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            (root / "skills").mkdir()
            (root / "changelog.md").write_text("# log\n", encoding="utf-8")

            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertTrue(any("naming" in f and "changelog.md" in f for f in findings))

    def test_naming_clean_on_correct_conventions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# repo\n\nStart here\n\nRoadmap\n", encoding="utf-8")
            (root / "PLAN.md").write_text("# plan\n", encoding="utf-8")
            (root / "skills").mkdir()
            cmd_dir = root / "commands"
            cmd_dir.mkdir()
            (cmd_dir / "new-feature.md").write_text("# cmd\n", encoding="utf-8")

            findings = audit_repo_scripts.audit_skills_repo(root)
            self.assertFalse(any("naming" in f for f in findings))


class DraftIssueTests(unittest.TestCase):
    def test_render_issue_includes_attribution_footer(self) -> None:
        content = draft_issue_scripts.render_issue(
            title="Missing freshness note",
            evidence="skills/foo/SKILL.md lacks a freshness rule.",
            recommendation="Add a freshness rule and re-run the audit.",
            skill="kotlin-multiplatform-audit",
            kind="issue",
        )
        self.assertIn("# Missing freshness note", content)
        self.assertIn("Suggested by kotlin-multiplatform-audit", content)

    def test_render_question_uses_question_heading(self) -> None:
        content = draft_issue_scripts.render_issue(
            title="Should X live in :model or :api?",
            evidence="Ambiguous placement.",
            recommendation="Confirm with the team.",
            skill="kotlin-multiplatform-clean-architecture",
            kind="question",
        )
        self.assertIn("## Type\nQuestion", content)

    def test_build_gh_command_includes_repo_and_labels(self) -> None:
        cmd = draft_issue_scripts.build_gh_command(
            title="Test issue",
            body="body text",
            repo="owner/repo",
            labels=["skill-bug", "priority: high"],
        )
        self.assertIn("--repo", cmd)
        self.assertIn("owner/repo", cmd)
        self.assertEqual(cmd.count("--label"), 2)
        self.assertIn("skill-bug", cmd)
        self.assertIn("priority: high", cmd)

    def test_build_gh_command_no_labels(self) -> None:
        cmd = draft_issue_scripts.build_gh_command(
            title="T", body="B", repo="r/r", labels=[]
        )
        self.assertNotIn("--label", cmd)

    def test_submit_dry_run_prints_command_does_not_execute(self) -> None:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = draft_issue_scripts.submit_issue(
                title="T", body="B",
                repo="ronjunevaldoz/kmm-agent-skills",
                labels=["skill-bug"],
                dry_run=True,
            )
        output = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("DRY RUN", output)
        self.assertIn("gh issue create", output)
        self.assertIn("ronjunevaldoz/kmm-agent-skills", output)

    def test_default_repo_constant(self) -> None:
        self.assertEqual(
            draft_issue_scripts.DEFAULT_REPO,
            "ronjunevaldoz/kmm-agent-skills",
        )


class ScanSkillIssuesTests(unittest.TestCase):
    def _make_skill(self, root: Path, name: str, content: str) -> Path:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        return skill_dir

    def _run_scan(self, root: Path) -> dict:
        import json, io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        old_root = scan_skill_issues_scripts.SKILLS_DIR
        old_ki = scan_skill_issues_scripts.KNOWN_ISSUES_FILE
        scan_skill_issues_scripts.SKILLS_DIR = root / "skills"
        scan_skill_issues_scripts.KNOWN_ISSUES_FILE = root / "KNOWN_ISSUES.md"
        try:
            with redirect_stdout(buf):
                rc = scan_skill_issues_scripts.main()
        finally:
            scan_skill_issues_scripts.SKILLS_DIR = old_root
            scan_skill_issues_scripts.KNOWN_ISSUES_FILE = old_ki
        return json.loads(buf.getvalue()), rc

    def test_missing_testing_section_reported_as_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-foo",
                "---\nname: foo\ndescription: Foo skill\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nUse Foo.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nDont do X.\n\n## Related Skills\n\nBar.\n\n"
                "## Output Style\n\nBe concise.\n",
            )
            report, rc = self._run_scan(root)

        self.assertEqual(rc, 1)
        high_issues = [i for i in report["issues"] if i["severity"] == "HIGH"]
        self.assertTrue(len(high_issues) >= 1)
        self.assertTrue(any(i["check"] == "missing_testing" for i in high_issues))

    def test_skill_with_testing_markers_no_high_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-bar",
                "---\nname: bar\ndescription: Bar skill\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nUse Bar.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nDont do X.\n\n## Related Skills\n\nFoo.\n\n"
                "## Output Style\n\nBe concise.\n\n## Testing\n\n```kotlin\n@Test fun fakeBar() {}\n```\n",
            )
            report, rc = self._run_scan(root)

        high_issues = [i for i in report["issues"] if i["check"] == "missing_testing"]
        self.assertEqual(len(high_issues), 0)

    def test_missing_required_sections_reported_as_medium(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-baz",
                # missing: anti_patterns, freshness_rule, recommendation
                "---\nname: baz\ndescription: Baz\nlast-updated: '2026-06-21'\n---\n\n"
                "## Related Skills\n\nFoo.\n\n## Output Style\n\nBe concise.\n\n"
                "## Testing\n\nFakeBaz\n",
            )
            report, _ = self._run_scan(root)

        checks = [i["check"] for i in report["issues"]]
        self.assertIn("missing_anti_patterns", checks)
        self.assertIn("missing_recommendation", checks)

    def test_skipped_skill_not_flagged_for_missing_testing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_skill(
                root,
                "kotlin-multiplatform-expert",
                "---\nname: expert\ndescription: Orchestrator\nlast-updated: '2026-06-21'\n---\n\n"
                "## Recommendation First\n\nLoad skills.\n\nFreshness rule: check monthly\n\n"
                "## Common Anti-Patterns\n\nNone.\n\n## Related Skills\n\nAll.\n\n"
                "## Output Style\n\nBe concise.\n",
            )
            report, _ = self._run_scan(root)

        testing_issues = [i for i in report["issues"] if i["check"] == "missing_testing"]
        self.assertEqual(len(testing_issues), 0)

    def test_report_structure_has_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            report, _ = self._run_scan(root)

        for key in ("generated", "total_issues", "by_severity", "by_check", "open_known_issues", "issues"):
            self.assertIn(key, report)

    def test_clean_scan_returns_exit_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            _, rc = self._run_scan(root)

        self.assertEqual(rc, 0)


class CheckUpdatesTests(unittest.TestCase):
    def test_read_version_valid_json(self) -> None:
        result = check_updates_scripts.read_version('{"version": "1.7.0"}')
        self.assertEqual(result, "1.7.0")

    def test_read_version_missing_key(self) -> None:
        result = check_updates_scripts.read_version('{"other": "x"}')
        self.assertEqual(result, "?")

    def test_read_version_malformed_json(self) -> None:
        result = check_updates_scripts.read_version("not-json")
        self.assertEqual(result, "?")

    def test_read_version_empty_string(self) -> None:
        result = check_updates_scripts.read_version("")
        self.assertEqual(result, "?")

    def _run_main_with_run(self, run_responses: list) -> int:
        """Patch check_updates_scripts.run and call main(), returning the exit code."""
        from unittest.mock import patch
        responses = iter(run_responses)

        def fake_run(cmd: str) -> tuple:
            return next(responses)

        with patch.object(check_updates_scripts, "run", side_effect=fake_run):
            return check_updates_scripts.main()

    def test_main_exit_2_when_fetch_fails(self) -> None:
        # git fetch returns non-zero → offline → exit 2
        rc = self._run_main_with_run([("", 1)])
        self.assertEqual(rc, 2)

    def test_main_exit_0_when_up_to_date(self) -> None:
        # fetch ok, 0 commits behind, 0 commits ahead → exit 0
        rc = self._run_main_with_run([
            ("", 0),    # git fetch
            ("0", 0),   # rev-list behind
            ("0", 0),   # rev-list ahead
        ])
        self.assertEqual(rc, 0)

    def test_main_exit_0_with_local_commits_ahead(self) -> None:
        # fetch ok, 0 behind, 2 ahead (unpushed local commits) → still exit 0
        rc = self._run_main_with_run([
            ("", 0),    # git fetch
            ("0", 0),   # rev-list behind
            ("2", 0),   # rev-list ahead
        ])
        self.assertEqual(rc, 0)

    def test_main_exit_1_when_behind_remote(self) -> None:
        # fetch ok, 3 commits behind → updates available → exit 1
        import tempfile, json as _json
        with tempfile.TemporaryDirectory() as tmp:
            skills_json = Path(tmp) / "skills.json"
            skills_json.write_text(_json.dumps({"version": "1.7.0"}))

            from unittest.mock import patch
            responses = iter([
                ("", 0),                    # git fetch
                ("3", 0),                   # rev-list behind
                (_json.dumps({"version": "1.9.0"}), 0),  # git show remote skills.json
                ("skills/foo/SKILL.md\nagents/planner.md", 0),  # git diff changed files
                ("", 0),                    # git diff changelog
            ])

            def fake_run(cmd: str) -> tuple:
                return next(responses)

            old_root = check_updates_scripts.ROOT
            check_updates_scripts.ROOT = Path(tmp)
            try:
                with patch.object(check_updates_scripts, "run", side_effect=fake_run):
                    rc = check_updates_scripts.main()
            finally:
                check_updates_scripts.ROOT = old_root

        self.assertEqual(rc, 1)


class PipelineContextFlagTests(unittest.TestCase):
    """KI-005 — krpc_established round-trip contract.

    These tests verify that the three files involved in the round-trip
    (pipeline-context.json, implementer.md, reviewer.md) all reference the flag.
    If any file is edited and the reference is removed, the test fails immediately
    rather than silently regressing to re-running the grep every session.
    """

    def _pipeline_context(self) -> dict:
        path = REPO_ROOT / ".claude" / "pipeline-context.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_pipeline_context_has_krpc_established_key(self) -> None:
        ctx = self._pipeline_context()
        self.assertIn("krpc_established", ctx, (
            "pipeline-context.json is missing the 'krpc_established' key. "
            "Add it back as false — it is set to true by the implementer after "
            "confirming kRPC is active."
        ))

    def test_pipeline_context_krpc_established_is_bool(self) -> None:
        ctx = self._pipeline_context()
        self.assertIsInstance(ctx.get("krpc_established"), bool, (
            "'krpc_established' must be a bool (true/false), not a string or null."
        ))

    def test_implementer_sets_krpc_established(self) -> None:
        text = (REPO_ROOT / "agents" / "implementer.md").read_text(encoding="utf-8")
        self.assertIn("krpc_established", text, (
            "agents/implementer.md no longer references 'krpc_established'. "
            "The implementer must set this flag to true in pipeline-context.json "
            "after confirming kRPC is active, so subsequent sessions skip the grep."
        ))

    def test_reviewer_reads_krpc_established(self) -> None:
        text = (REPO_ROOT / "agents" / "reviewer.md").read_text(encoding="utf-8")
        self.assertIn("krpc_established", text, (
            "agents/reviewer.md no longer references 'krpc_established'. "
            "The reviewer must read this flag before running the transport grep "
            "(Check 9) to avoid redundant work in sessions after the flag is set."
        ))


HOOKS_DIR = REPO_ROOT / "hooks"


class HookScriptTests(unittest.TestCase):
    """KI-006 — hook shell script plumbing tests.

    Tests exit-code forwarding and argument handling for the two non-blocking
    hooks. The pre-commit hook is covered indirectly by the Python scripts it
    wraps; these tests cover the shell plumbing that the other tests do not.
    """

    # --- validate-architecture.sh ---

    def test_validate_arch_skips_non_kotlin_file(self) -> None:
        result = subprocess.run(
            ["bash", str(HOOKS_DIR / "validate-architecture.sh"), "readme.txt"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, (
            "validate-architecture.sh should exit 0 (skip) for non-.kt/.kts/.md files. "
            f"stderr: {result.stderr.decode()}"
        ))

    def test_validate_arch_runs_on_kotlin_file(self) -> None:
        # Pass a clean temp dir as $2 so the audit doesn't scan SKILL.md examples.
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "validate-architecture.sh"), "SomeFile.kt", tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "validate-architecture.sh should exit 0 on a clean project for a .kt file. "
            f"stdout: {result.stdout.decode()}  stderr: {result.stderr.decode()}"
        ))

    def test_validate_arch_runs_when_no_arg(self) -> None:
        # No file arg → audit runs; use a clean temp dir as $2 to avoid SKILL.md false positives.
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "validate-architecture.sh"), "", tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "validate-architecture.sh should exit 0 on a clean project when called with no file arg. "
            f"stderr: {result.stderr.decode()}"
        ))

    def test_validate_arch_skips_non_md_non_kt(self) -> None:
        for ext in (".json", ".sh", ".py", ".toml", ".xml"):
            with self.subTest(ext=ext):
                result = subprocess.run(
                    ["bash", str(HOOKS_DIR / "validate-architecture.sh"), f"file{ext}"],
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, (
                    f"validate-architecture.sh should skip and exit 0 for {ext} files."
                ))

    # --- check-skill-freshness.sh ---

    def _make_skill_dir(self, tmp: str, name: str, last_updated: str) -> Path:
        skills_dir = Path(tmp) / "skills"
        skill_dir = skills_dir / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\nmetadata:\n  last-updated: '{last_updated}'\n---\n",
            encoding="utf-8",
        )
        return skills_dir

    def test_freshness_exits_0_when_all_skills_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = self._make_skill_dir(tmp, "kotlin-multiplatform-foo", "2026-06-21")
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(skills_dir)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "check-skill-freshness.sh should exit 0 when all skills are fresh. "
            f"stdout: {result.stdout.decode()}"
        ))

    def test_freshness_exits_1_when_skill_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = self._make_skill_dir(tmp, "kotlin-multiplatform-old", "2020-01-01")
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(skills_dir)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 1, (
            "check-skill-freshness.sh should exit 1 when a skill is >90 days stale. "
            f"stdout: {result.stdout.decode()}"
        ))
        self.assertIn(b"STALE", result.stdout)

    def test_freshness_warns_on_missing_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            skill_dir = skills_dir / "kotlin-multiplatform-nodates"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: kotlin-multiplatform-nodates\n---\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(skills_dir)],
                capture_output=True,
            )
        # No stale count incremented — exits 0 but prints WARN
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"WARN", result.stdout)

    def test_freshness_exits_0_when_no_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            empty_skills = Path(tmp) / "skills"
            empty_skills.mkdir()
            result = subprocess.run(
                ["bash", str(HOOKS_DIR / "check-skill-freshness.sh"), str(empty_skills)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, (
            "check-skill-freshness.sh should exit 0 when the skills directory is empty."
        ))


class ValidateKeywordRoutingTests(unittest.TestCase):
    EXPERT_HEADER = "## Skill Invocation Map\n"
    EXPERT_FOOTER = "\n---\n"

    def _make_repo(self, tmp: str, skill_names: list[str], map_rows: str) -> Path:
        root = Path(tmp)
        skills_dir = root / "skills"
        for name in skill_names:
            (skills_dir / name).mkdir(parents=True)
            (skills_dir / name / "SKILL.md").write_text("", encoding="utf-8")
        # expert SKILL.md with a Skill Invocation Map section
        expert_dir = skills_dir / "kotlin-multiplatform-expert"
        expert_dir.mkdir(parents=True, exist_ok=True)
        (expert_dir / "SKILL.md").write_text(
            self.EXPERT_HEADER + map_rows + self.EXPERT_FOOTER,
            encoding="utf-8",
        )
        return root

    def test_all_skills_present_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"],
                "| keyword-a | `kotlin-multiplatform-a` |\n"
                "| keyword-b | `kotlin-multiplatform-b` |\n",
            )
            self.assertEqual(keyword_routing_scripts.validate_keyword_routing(root), [])

    def test_missing_skill_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-a", "kotlin-multiplatform-b", "kotlin-multiplatform-expert"],
                "| keyword-a | `kotlin-multiplatform-a` |\n",
            )
            errors = keyword_routing_scripts.validate_keyword_routing(root)
            self.assertTrue(any("kotlin-multiplatform-b" in e for e in errors))

    def test_meta_skills_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_repo(
                tmp,
                ["kotlin-multiplatform-audit", "kotlin-multiplatform-expert"],
                "",
            )
            # audit and expert are in SKIP_INVOCATION — no map rows needed
            self.assertEqual(keyword_routing_scripts.validate_keyword_routing(root), [])

    def test_missing_map_section_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expert_dir = root / "skills" / "kotlin-multiplatform-expert"
            expert_dir.mkdir(parents=True)
            (expert_dir / "SKILL.md").write_text("no section here", encoding="utf-8")
            errors = keyword_routing_scripts.validate_keyword_routing(root)
            self.assertTrue(any("not found" in e for e in errors))

    def test_main_exits_0_on_clean_repo(self) -> None:
        result = keyword_routing_scripts.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(result, 0)


generate_release_notes_scripts = load_module(
    "generate_release_notes",
    REPO_ROOT / "scripts" / "generate_release_notes.py",
)


class GenerateReleaseNotesTests(unittest.TestCase):
    def test_read_skill_changelog_parses_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "## Changelog\n\n"
                "| Date | Change |\n"
                "|---|---|\n"
                "| 2026-06-21 | **Breaking** — Step 3 rewritten. |\n"
                "| 2026-06-18 | Initial release. |\n",
                encoding="utf-8",
            )
            entries = generate_release_notes_scripts.read_skill_changelog(skill_md)
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0]["date"], "2026-06-21")
            self.assertIn("Breaking", entries[0]["change"])
            self.assertEqual(entries[1]["date"], "2026-06-18")

    def test_read_skill_changelog_returns_empty_when_section_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text("## When to Use This Skill\n\nSome content.\n", encoding="utf-8")
            entries = generate_release_notes_scripts.read_skill_changelog(skill_md)
            self.assertEqual(entries, [])

    def test_read_unreleased_parses_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text(
                "# Changelog\n\n"
                "## [Unreleased]\n\n"
                "### Added\n- Some thing\n\n"
                "## [v1.0.0] — 2026-06-17\n\n"
                "### Added\n- Initial release\n",
                encoding="utf-8",
            )
            section = generate_release_notes_scripts.read_unreleased(changelog)
            self.assertIn("Some thing", section)
            self.assertNotIn("v1.0.0", section)

    def test_read_unreleased_returns_empty_when_section_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text("# Changelog\n\n## [v1.0.0] — 2026-06-17\n", encoding="utf-8")
            section = generate_release_notes_scripts.read_unreleased(changelog)
            self.assertEqual(section, "")

    def test_main_list_tags_exits_0(self) -> None:
        result = generate_release_notes_scripts.main(["--list-tags"])
        self.assertEqual(result, 0)

    def test_main_since_head_exits_0(self) -> None:
        result = generate_release_notes_scripts.main(["--since", "HEAD~1"])
        self.assertEqual(result, 0)

    def test_main_since_head_outputs_valid_json(self) -> None:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            generate_release_notes_scripts.main(["--since", "HEAD~1"])
        data = json.loads(buf.getvalue())
        self.assertIn("commits", data)
        self.assertIn("skill_changes", data)
        self.assertIn("unreleased_changelog", data)


import sys as _sys
import importlib.util as _ilu

def _load_module_registered(name: str, path: Path):
    spec = _ilu.spec_from_file_location(name, path)
    module = _ilu.module_from_spec(spec)
    _sys.modules[name] = module   # register BEFORE exec so @dataclass can resolve __module__
    spec.loader.exec_module(module)
    return module

detect_data_collection_scripts = _load_module_registered(
    "detect_data_collection",
    REPO_ROOT / "skills" / "kotlin-multiplatform-legal-docs" / "scripts" / "detect_data_collection.py",
)


class DetectDataCollectionTests(unittest.TestCase):
    def _make_project(self, files: dict[str, str]) -> Path:
        tmp = tempfile.mkdtemp()
        root = Path(tmp)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return root

    def test_detects_firebase_analytics(self) -> None:
        root = self._make_project({
            "feature/analytics/src/commonMain/Analytics.kt":
                "import com.google.firebase.analytics.FirebaseAnalytics\n"
                "fun track() = FirebaseAnalytics.getInstance(ctx).logEvent(\"screen_view\", null)\n"
        })
        detections = detect_data_collection_scripts.scan_project(root)
        types = [d.data_type for d in detections]
        self.assertIn("analytics", types)

    def test_detects_location_permission(self) -> None:
        root = self._make_project({
            "androidApp/src/main/AndroidManifest.xml":
                '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>\n'
        })
        detections = detect_data_collection_scripts.scan_project(root)
        types = [d.data_type for d in detections]
        self.assertIn("location_precise", types)

    def test_no_detections_on_empty_project(self) -> None:
        root = self._make_project({"build.gradle.kts": "plugins { }\n"})
        detections = detect_data_collection_scripts.scan_project(root)
        self.assertEqual(detections, [])

    def test_finds_gap_when_analytics_not_in_policy(self) -> None:
        detections = [detect_data_collection_scripts.Detection(data_type="analytics", evidence=["Analytics.kt:1"])]
        gaps = detect_data_collection_scripts.find_gaps(detections, policy_text="we collect your email.")
        self.assertIn("analytics", gaps)

    def test_no_gap_when_analytics_disclosed_in_policy(self) -> None:
        detections = [detect_data_collection_scripts.Detection(data_type="analytics", evidence=["Analytics.kt:1"])]
        gaps = detect_data_collection_scripts.find_gaps(detections, policy_text="usage analytics via firebase analytics sdk.")
        self.assertNotIn("analytics", gaps)

    def test_finds_conflict_when_policy_mentions_location_but_code_does_not(self) -> None:
        policy_text = "we collect your precise location via gps."
        conflicts = detect_data_collection_scripts.find_conflicts(detections=[], policy_text=policy_text)
        self.assertIn("location_precise", conflicts)

    def test_main_exits_0_on_no_gaps(self) -> None:
        root = self._make_project({"build.gradle.kts": "plugins { }\n"})
        result = detect_data_collection_scripts.main([str(root)])
        self.assertEqual(result, 0)

    def test_main_exits_1_on_gaps(self) -> None:
        root = self._make_project({
            "Analytics.kt": "val x = FirebaseAnalytics.getInstance(ctx)\n"
        })
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Privacy Policy\n\nWe collect your email.\n")
            policy_path = f.name
        result = detect_data_collection_scripts.main([str(root), "--policy", policy_path])
        self.assertEqual(result, 1)


scan_design_violations_scripts = load_module(
    "scan_design_violations",
    REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "scan_design_violations.py",
)

scaffold_preview_coverage_scripts = load_module(
    "scaffold_preview_coverage",
    REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "scaffold_preview_coverage.py",
)

update_design_system_scripts = load_module(
    "update_design_system",
    REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "update_design_system.py",
)


class UpdateDesignSystemTests(unittest.TestCase):
    """Tests for update_design_system.py — compare/diff logic."""

    _SKILL_MD_TEMPLATE = (
        "---\nname: test\n---\n\n"
        "### `components/AppFoo.kt`\n"
        "```kotlin\n"
        "fun AppFoo() {{ }}\n"
        "```\n"
        "\n"
        "### `components/AppBar.kt`\n"
        "```kotlin\n"
        "fun AppBar() {{ }}\n"
        "```\n"
    )

    def _write_skill_md(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    _SKILL_MD_WITH_PREVIEWS = (
        "---\nname: test\n---\n\n"
        "### `components/AppFoo.kt`\n"
        "```kotlin\n"
        "fun AppFoo() {{ }}\n"
        "```\n"
        "\n"
        "### `previews/AppFooPreview.kt`\n"
        "```kotlin\n"
        "@Preview\nfun AppFooPreview() {{ AppFoo() }}\n"
        "```\n"
    )

    def test_extract_reference_components_finds_all_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)
        # Keys are now relative paths
        self.assertIn("components/AppFoo.kt", refs)
        self.assertIn("components/AppBar.kt", refs)
        self.assertEqual(len(refs), 2)

    def test_extract_reference_components_body_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)
        self.assertIn("AppFoo", refs["components/AppFoo.kt"])

    def test_extract_reference_components_finds_preview_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_WITH_PREVIEWS)
            refs = update_design_system_scripts.extract_reference_components(skill_md)
        self.assertIn("components/AppFoo.kt", refs)
        self.assertIn("previews/AppFooPreview.kt", refs)
        self.assertEqual(len(refs), 2)

    def test_compare_status_missing_when_no_project_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            results = update_design_system_scripts.compare(root, skill_md)
        statuses = {r["file"]: r["status"] for r in results}
        self.assertEqual(statuses["components/AppFoo.kt"], "MISSING")
        self.assertEqual(statuses["components/AppBar.kt"], "MISSING")

    def test_compare_status_current_when_file_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)

            comp_dir = root / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            (comp_dir / "AppFoo.kt").write_text(refs["components/AppFoo.kt"], encoding="utf-8")

            results = update_design_system_scripts.compare(root, skill_md)
        foo = next(r for r in results if r["file"] == "components/AppFoo.kt")
        self.assertEqual(foo["status"], "CURRENT")

    def test_compare_status_modified_when_file_differs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)

            comp_dir = root / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            (comp_dir / "AppFoo.kt").write_text(
                "fun AppFoo() { /* project customisation */ }", encoding="utf-8"
            )

            results = update_design_system_scripts.compare(root, skill_md)
        foo = next(r for r in results if r["file"] == "components/AppFoo.kt")
        self.assertEqual(foo["status"], "MODIFIED")

    def test_compare_preview_status_current_when_file_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_WITH_PREVIEWS)
            refs = update_design_system_scripts.extract_reference_components(skill_md)

            comp_dir = root / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            (comp_dir / "AppFoo.kt").write_text(refs["components/AppFoo.kt"], encoding="utf-8")

            prev_dir = root / "core" / "designsystem" / "previews"
            prev_dir.mkdir(parents=True)
            (prev_dir / "AppFooPreview.kt").write_text(
                refs["previews/AppFooPreview.kt"], encoding="utf-8"
            )

            results = update_design_system_scripts.compare(root, skill_md)
        preview = next(r for r in results if r["file"] == "previews/AppFooPreview.kt")
        self.assertEqual(preview["status"], "CURRENT")

    def test_compare_preview_status_missing_when_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_WITH_PREVIEWS)
            results = update_design_system_scripts.compare(root, skill_md)
        preview = next(r for r in results if r["file"] == "previews/AppFooPreview.kt")
        self.assertEqual(preview["status"], "MISSING")

    def test_resolve_filename_normalises_component_name(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("AppButton"),
            "components/AppButton.kt",
        )

    def test_resolve_filename_normalises_name_with_app_prefix(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("Button"),
            "components/AppButton.kt",
        )

    def test_resolve_filename_passthrough_for_full_kt_path(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("components/AppButton.kt"),
            "components/AppButton.kt",
        )

    def test_resolve_filename_maps_preview_to_previews_dir(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("AppButtonPreview"),
            "previews/AppButtonPreview.kt",
        )

    def test_resolve_filename_maps_preview_kt_to_previews_dir(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("AppButtonPreview.kt"),
            "previews/AppButtonPreview.kt",
        )

    def test_find_component_dir_returns_none_for_empty_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = update_design_system_scripts.find_component_dir(Path(tmp))
        self.assertIsNone(result)

    def test_find_component_dir_detects_components_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            comp_dir = Path(tmp) / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            result = update_design_system_scripts.find_component_dir(Path(tmp))
        self.assertIsNotNone(result)
        # Returns parent of components/ (i.e. core/designsystem/) so rglob finds previews/ too
        self.assertTrue(str(result).endswith("designsystem"))

    def test_main_exit_2_when_skill_md_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc = update_design_system_scripts.main.__wrapped__ if hasattr(
                update_design_system_scripts.main, "__wrapped__"
            ) else None
            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "update_design_system.py"),
                 tmp,
                 "--skill-root", tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 2)

    def test_main_exit_1_when_components_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_root = root / "fake_skills"
            skill_md_dir = skill_root / "skills" / "kotlin-multiplatform-design-system"
            skill_md_dir.mkdir(parents=True)
            (skill_md_dir / "SKILL.md").write_text(self._SKILL_MD_TEMPLATE, encoding="utf-8")
            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "update_design_system.py"),
                 str(root),
                 "--skill-root", str(skill_root)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 1)

    def test_main_exit_0_when_all_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_root = root / "fake_skills"
            skill_md_dir = skill_root / "skills" / "kotlin-multiplatform-design-system"
            skill_md_dir.mkdir(parents=True)
            skill_md = skill_md_dir / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)

            # refs keys are "components/AppFoo.kt" — write files into their subdirs
            base_dir = root / "core" / "designsystem"
            base_dir.mkdir(parents=True)
            for rel_path, code in refs.items():
                dest = base_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(code, encoding="utf-8")

            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "update_design_system.py"),
                 str(root),
                 "--skill-root", str(skill_root)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0)


class ScanDesignViolationsTests(unittest.TestCase):
    """Tests for scan_design_violations.py."""

    def _write_kt(self, tmp: str, name: str, content: str) -> Path:
        path = Path(tmp) / "feature" / "auth" / "ui" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _scan(self, tmp: str, content: str, name: str = "AuthContent.kt") -> list[dict]:
        path = self._write_kt(tmp, name, content)
        return scan_design_violations_scripts.scan_file(path)

    # ── hardcoded_color ──────────────────────────────────────────────────────

    def test_flags_hardcoded_hex_color(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "val c = Color(0xFF1A73E8)\n")
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_color", types)

    def test_flags_hardcoded_rgb_float_color(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "val c = Color(0.1f, 0.5f, 0.9f)\n")
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_color", types)

    def test_allows_named_color_constants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "val c = Color.Transparent\nval d = Color.White\n")
        types = [f["type"] for f in findings]
        self.assertNotIn("hardcoded_color", types)

    # ── hardcoded_dp ─────────────────────────────────────────────────────────

    def test_flags_hardcoded_padding_dp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "Modifier.padding(16.dp)\n")
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_dp", types)

    def test_flags_hardcoded_height_dp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "Modifier.height(48.dp)\n")
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_dp", types)

    def test_flags_spacer_with_hardcoded_dp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(
                tmp,
                "Spacer(modifier = Modifier.height(8.dp))\n",
            )
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_dp", types)

    def test_allows_zero_and_one_dp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(
                tmp,
                "Modifier.padding(0.dp)\nModifier.height(1.dp)\n",
            )
        types = [f["type"] for f in findings]
        self.assertNotIn("hardcoded_dp", types)

    # ── material_theme ───────────────────────────────────────────────────────

    def test_flags_material_theme_colors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "MaterialTheme.colors.primary\n")
        types = [f["type"] for f in findings]
        self.assertIn("material_theme", types)

    def test_flags_material_theme_typography(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "style = MaterialTheme.typography.bodyMedium\n")
        types = [f["type"] for f in findings]
        self.assertIn("material_theme", types)

    def test_allows_apptheme_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "val t = appTheme\nt.colors.primary\n")
        types = [f["type"] for f in findings]
        self.assertNotIn("material_theme", types)

    # ── direct_textstyle ─────────────────────────────────────────────────────

    def test_flags_direct_textstyle_construction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "val s = TextStyle(fontSize = 16.sp)\n")
        types = [f["type"] for f in findings]
        self.assertIn("direct_textstyle", types)

    def test_allows_apptextstyle_enum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "val s = AppTextStyle.BodyMedium\n")
        types = [f["type"] for f in findings]
        self.assertNotIn("direct_textstyle", types)

    # ── hardcoded_string ────────────────────────────────────────────────────

    def test_flags_hardcoded_text_in_text_composable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "Text(\"Continue\")\n")
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_string", types)

    def test_flags_hardcoded_content_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "Icon(contentDescription = \"Back\")\n")
        types = [f["type"] for f in findings]
        self.assertIn("hardcoded_string", types)

    def test_allows_state_driven_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "Text(text = state.title)\n")
        types = [f["type"] for f in findings]
        self.assertNotIn("hardcoded_string", types)

    def test_allows_string_resource_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(tmp, "Text(stringResource(Res.string.continue_label))\n")
        types = [f["type"] for f in findings]
        self.assertNotIn("hardcoded_string", types)

    # ── nested_container ─────────────────────────────────────────────────────

    def test_flags_nested_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(
                tmp,
                "@Composable\nfun Foo() {\n  Card {\n    Card {\n    }\n  }\n}\n",
            )
        types = [f["type"] for f in findings]
        self.assertIn("nested_container", types)

    def test_flags_nested_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(
                tmp,
                "@Composable\nfun Foo() {\n  Surface {\n    Surface {\n    }\n  }\n}\n",
            )
        types = [f["type"] for f in findings]
        self.assertIn("nested_container", types)

    def test_allows_single_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(
                tmp,
                "@Composable\nfun Foo() {\n  Card {\n    Text(text = state.title)\n  }\n}\n",
            )
        types = [f["type"] for f in findings]
        self.assertNotIn("nested_container", types)
        self.assertNotIn("hardcoded_string", types)

    # ── skip rules ───────────────────────────────────────────────────────────

    def test_skips_styles_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ButtonStyles.kt"
            path.write_text("val c = Color(0xFF1A73E8)\n", encoding="utf-8")
            findings = scan_design_violations_scripts.scan_file.__wrapped__ if hasattr(
                scan_design_violations_scripts.scan_file, "__wrapped__"
            ) else None
            # Use scan() with should_skip — it must skip ButtonStyles.kt
            result = scan_design_violations_scripts.scan(Path(tmp))
        # ButtonStyles.kt is in _SKIP_NAME_SUFFIXES → no findings
        self.assertEqual(result, [])

    def test_skips_designsystem_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ds_dir = Path(tmp) / "core" / "designsystem"
            ds_dir.mkdir(parents=True)
            (ds_dir / "AppButton.kt").write_text(
                "val c = Color(0xFF1A73E8)\n", encoding="utf-8"
            )
            result = scan_design_violations_scripts.scan(Path(tmp))
        self.assertEqual(result, [])

    def test_preview_coverage_flags_missing_preview_and_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui" / "LoginContent.kt"
            content.parent.mkdir(parents=True, exist_ok=True)
            content.write_text(
                """package com.example.feature.auth.ui

import androidx.compose.runtime.Composable

@Composable
fun LoginContent(
    state: LoginUiState,
    onIntent: (LoginIntent) -> Unit,
) {}
""",
                encoding="utf-8",
            )
            findings = scan_design_violations_scripts.scan(root)
        types = [f["type"] for f in findings]
        self.assertIn("preview_coverage", types)
        self.assertTrue(any("Missing preview stub" in f["message"] for f in findings))
        self.assertTrue(any("Missing Roborazzi screenshot test" in f["message"] for f in findings))

    def test_preview_coverage_accepts_multi_device_preview_and_roborazzi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "feature" / "auth" / "ui" / "src"
            common = base / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
            previews = common / "previews"
            tests = base / "jvmTest" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui" / "previews"
            previews.mkdir(parents=True, exist_ok=True)
            tests.mkdir(parents=True, exist_ok=True)

            (common / "LoginContent.kt").write_text(
                """package com.example.feature.auth.ui

import androidx.compose.runtime.Composable

@Composable
fun LoginContent(
    state: LoginUiState,
    onIntent: (LoginIntent) -> Unit,
) {}
""",
                encoding="utf-8",
            )
            (previews / "MultiDevicePreview.kt").write_text(
                """package com.example.feature.auth.ui.previews

import org.jetbrains.compose.ui.tooling.preview.Preview

@Preview(name = "Phone", widthDp = 360, heightDp = 640)
@Preview(name = "Tablet", widthDp = 673, heightDp = 841)
@Preview(name = "Desktop", widthDp = 1280, heightDp = 800)
annotation class MultiDevicePreview
""",
                encoding="utf-8",
            )
            (previews / "LoginContentPreview.kt").write_text(
                """package com.example.feature.auth.ui.previews

import androidx.compose.runtime.Composable

@MultiDevicePreview
@Composable
fun LoginContentPreview() {}
""",
                encoding="utf-8",
            )
            (tests / "LoginContentScreenshotTest.kt").write_text(
                """package com.example.feature.auth.ui.previews

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.github.takahirom.roborazzi.captureRoboImage
import com.example.core.designsystem.theme.AppTheme
import kotlin.test.Test

class LoginContentScreenshotTest {
    @Test fun phone_light() {
        captureRoboImage("login_content_phone_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(360.dp, 640.dp)) {}
            }
        }
    }

    @Test fun phone_dark() {
        captureRoboImage("login_content_phone_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(360.dp, 640.dp)) {}
            }
        }
    }

    @Test fun tablet_light() {
        captureRoboImage("login_content_tablet_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(673.dp, 841.dp)) {}
            }
        }
    }

    @Test fun tablet_dark() {
        captureRoboImage("login_content_tablet_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(673.dp, 841.dp)) {}
            }
        }
    }

    @Test fun desktop_light() {
        captureRoboImage("login_content_desktop_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(1280.dp, 800.dp)) {}
            }
        }
    }

    @Test fun desktop_dark() {
        captureRoboImage("login_content_desktop_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(1280.dp, 800.dp)) {}
            }
        }
    }
}
""",
                encoding="utf-8",
            )
            findings = scan_design_violations_scripts.scan(root)
        self.assertFalse(any(f["type"] == "preview_coverage" for f in findings))

    def test_scaffold_preview_coverage_creates_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui" / "LoginContent.kt"
            content.parent.mkdir(parents=True, exist_ok=True)
            content.write_text(
                """package com.example.feature.auth.ui

import androidx.compose.runtime.Composable

@Composable
fun LoginContent(
    state: LoginUiState,
    onIntent: (LoginIntent) -> Unit,
) {}
""",
                encoding="utf-8",
            )

            created = scaffold_preview_coverage_scripts.scaffold_preview_coverage(root)

            self.assertTrue(any(path.endswith("LoginContentPreview.kt") for path in created))
            self.assertTrue(any(path.endswith("LoginContentScreenshotTest.kt") for path in created))
            self.assertTrue(any(path.endswith("MultiDevicePreview.kt") for path in created))

    def test_clean_file_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = self._scan(
                tmp,
                "@Composable\nfun AuthContent(state: AuthUiState) {\n"
                "  val t = appTheme\n"
                "  Card {\n"
                "    AppText(text = state.title, style = AppTextStyle.BodyMedium)\n"
                "    Modifier.padding(t.spacing.lg)\n"
                "  }\n"
                "}\n",
            )
        self.assertEqual(findings, [])

    # ── CLI exit codes ────────────────────────────────────────────────────────

    def test_cli_exit_0_on_clean_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
                     / "scripts" / "scan_design_violations.py"),
                 tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0)

    def test_cli_exit_1_on_violations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Foo.kt").write_text("val c = Color(0xFF1A73E8)\n", encoding="utf-8")
            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
                     / "scripts" / "scan_design_violations.py"),
                 tmp],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 1)

    def test_cli_exit_2_on_missing_root(self) -> None:
        result = subprocess.run(
            ["python3",
             str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
                 / "scripts" / "scan_design_violations.py"),
             "/nonexistent/path/that/does/not/exist"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 2)

    def test_cli_json_output_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Foo.kt").write_text("val c = Color(0xFF1A73E8)\n", encoding="utf-8")
            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system"
                     / "scripts" / "scan_design_violations.py"),
                 tmp, "--json"],
                capture_output=True,
                text=True,
            )
        parsed = json.loads(result.stdout)
        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0)
        self.assertIn("type", parsed[0])
        self.assertIn("line", parsed[0])
        self.assertIn("file", parsed[0])


class LayoutConsistencyTests(unittest.TestCase):
    """Tests for scan_layout_consistency() in scan_design_violations.py."""

    def _make_ui_dir(self, tmp: str, feature: str = "auth") -> Path:
        ui_dir = Path(tmp) / "feature" / feature / "ui"
        ui_dir.mkdir(parents=True, exist_ok=True)
        return ui_dir

    def _write_content(self, ui_dir: Path, name: str, body: str) -> Path:
        path = ui_dir / name
        path.write_text(body, encoding="utf-8")
        return path

    def test_flat_screens_are_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ui = self._make_ui_dir(tmp)
            self._write_content(ui, "ListContent.kt", "fun ListContent() { Column { } }")
            self._write_content(ui, "DetailContent.kt", "fun DetailContent() { Column { } }")
            findings = scan_design_violations_scripts.scan_layout_consistency(Path(tmp))
        self.assertEqual(findings, [])

    def test_card_screens_are_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ui = self._make_ui_dir(tmp)
            self._write_content(ui, "ProfileContent.kt", "fun ProfileContent() { AppCard() { } }")
            self._write_content(ui, "SettingsContent.kt", "fun SettingsContent() { AppCard() { } }")
            findings = scan_design_violations_scripts.scan_layout_consistency(Path(tmp))
        self.assertEqual(findings, [])

    def test_mixed_card_and_flat_flags_minority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ui = self._make_ui_dir(tmp)
            self._write_content(ui, "ListContent.kt", "fun ListContent() { Column { } }")
            self._write_content(ui, "DetailContent.kt", "fun DetailContent() { Column { } }")
            self._write_content(ui, "ProfileContent.kt", "fun ProfileContent() { AppCard() { } }")
            findings = scan_design_violations_scripts.scan_layout_consistency(Path(tmp))
        types = [f["type"] for f in findings]
        self.assertIn("layout_inconsistency", types)
        # Only the minority (card) is flagged, not the majority (flat x2)
        flagged = [f["file"] for f in findings if f["type"] == "layout_inconsistency"]
        self.assertTrue(any("ProfileContent" in p for p in flagged))
        self.assertFalse(any("ListContent" in p for p in flagged))

    def test_tabbed_screen_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ui = self._make_ui_dir(tmp)
            self._write_content(ui, "OverviewContent.kt", "fun OverviewContent() { Column { TabRow() } }")
            self._write_content(ui, "ListContent.kt", "fun ListContent() { Column { } }")
            findings = scan_design_violations_scripts.scan_layout_consistency(Path(tmp))
        types = [f["type"] for f in findings]
        self.assertIn("layout_inconsistency", types)

    def test_single_content_file_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ui = self._make_ui_dir(tmp)
            self._write_content(ui, "AuthContent.kt", "fun AuthContent() { AppCard() { } }")
            findings = scan_design_violations_scripts.scan_layout_consistency(Path(tmp))
        self.assertEqual(findings, [])

    def test_different_features_checked_independently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth_ui = self._make_ui_dir(tmp, "auth")
            home_ui = self._make_ui_dir(tmp, "home")
            # auth uses flat — consistent within itself
            self._write_content(auth_ui, "LoginContent.kt", "fun LoginContent() { Column { } }")
            self._write_content(auth_ui, "RegisterContent.kt", "fun RegisterContent() { Column { } }")
            # home uses card — consistent within itself
            self._write_content(home_ui, "FeedContent.kt", "fun FeedContent() { AppCard() { } }")
            self._write_content(home_ui, "ProfileContent.kt", "fun ProfileContent() { AppCard() { } }")
            findings = scan_design_violations_scripts.scan_layout_consistency(Path(tmp))
        self.assertEqual(findings, [])


governance_scripts = load_module(
    "governance_check",
    REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "governance_check.py",
)


class GovernanceCheckTests(unittest.TestCase):
    def _project(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / ".kmm-skills").write_text(
            '{"skills_repo": "ronjunevaldoz/kmm-agent-skills", "version": "1.25.11"}',
            encoding="utf-8",
        )
        ui_src = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
        ui_src.mkdir(parents=True)
        (ui_src / "LoginContent.kt").write_text(
            "fun LoginContent() { Column { } }", encoding="utf-8"
        )
        (ui_src / "LoginContentPreview.kt").write_text(
            """package com.example.feature.auth.ui.previews

import androidx.compose.runtime.Composable

@MultiDevicePreview
@Composable
fun LoginContentPreview() { LoginContent() }
""",
            encoding="utf-8"
        )
        (ui_src.parent / "previews").mkdir(parents=True, exist_ok=True)
        (ui_src.parent / "previews" / "MultiDevicePreview.kt").write_text(
            """package com.example.feature.auth.ui.previews

import org.jetbrains.compose.ui.tooling.preview.Preview

@Preview(name = "Phone", widthDp = 360, heightDp = 640)
@Preview(name = "Tablet", widthDp = 673, heightDp = 841)
@Preview(name = "Desktop", widthDp = 1280, heightDp = 800)
annotation class MultiDevicePreview
""",
            encoding="utf-8"
        )
        jvm_previews = root / "feature" / "auth" / "ui" / "src" / "jvmTest" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui" / "previews"
        jvm_previews.mkdir(parents=True, exist_ok=True)
        (jvm_previews / "LoginContentScreenshotTest.kt").write_text(
            """package com.example.feature.auth.ui.previews

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.github.takahirom.roborazzi.captureRoboImage
import com.example.core.designsystem.theme.AppTheme
import kotlin.test.Test

class LoginContentScreenshotTest {
    @Test fun phone_light() {
        captureRoboImage("login_content_phone_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(360.dp, 640.dp)) {}
            }
        }
    }

    @Test fun phone_dark() {
        captureRoboImage("login_content_phone_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(360.dp, 640.dp)) {}
            }
        }
    }

    @Test fun tablet_light() {
        captureRoboImage("login_content_tablet_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(673.dp, 841.dp)) {}
            }
        }
    }

    @Test fun tablet_dark() {
        captureRoboImage("login_content_tablet_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(673.dp, 841.dp)) {}
            }
        }
    }

    @Test fun desktop_light() {
        captureRoboImage("login_content_desktop_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(1280.dp, 800.dp)) {}
            }
        }
    }

    @Test fun desktop_dark() {
        captureRoboImage("login_content_desktop_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(1280.dp, 800.dp)) {}
            }
        }
    }
}
""",
            encoding="utf-8"
        )
        return root

    def test_clean_project_returns_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            findings = (
                governance_scripts.run_scan_violations(root)
                + governance_scripts.run_audit_project(root)
            )
        self.assertEqual(findings, [])

    def test_hardcoded_color_is_high_severity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            (root / "feature" / "auth" / "ui" / "LoginContent.kt").write_text(
                "fun Foo() { Box(Modifier.background(Color(0xFFFF0000))) {} }",
                encoding="utf-8",
            )
            findings = governance_scripts.run_scan_violations(root)
        high = [f for f in findings if f["severity"] == "HIGH"]
        self.assertTrue(len(high) >= 1)

    def test_medium_finding_does_not_fail_on_high_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            ui = root / "feature" / "auth" / "ui" / "src" / "commonMain" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui"
            # layout inconsistency → warning → MEDIUM (audit_project does not flag this)
            (ui / "LoginContent.kt").write_text("fun LoginContent() { Column { } }", encoding="utf-8")
            (ui / "ProfileContent.kt").write_text("fun ProfileContent() { AppCard() { } }", encoding="utf-8")
            (ui / "ProfileContentPreview.kt").write_text(
                """package com.example.feature.auth.ui.previews

import androidx.compose.runtime.Composable

@MultiDevicePreview
@Composable
fun ProfileContentPreview() { ProfileContent() }
""",
                encoding="utf-8",
            )
            (ui.parent / "previews" / "MultiDevicePreview.kt").write_text(
                """package com.example.feature.auth.ui.previews

import org.jetbrains.compose.ui.tooling.preview.Preview

@Preview(name = "Phone", widthDp = 360, heightDp = 640)
@Preview(name = "Tablet", widthDp = 673, heightDp = 841)
@Preview(name = "Desktop", widthDp = 1280, heightDp = 800)
annotation class MultiDevicePreview
""",
                encoding="utf-8",
            )
            jvm_previews = root / "feature" / "auth" / "ui" / "src" / "jvmTest" / "kotlin" / "com" / "example" / "feature" / "auth" / "ui" / "previews"
            jvm_previews.mkdir(parents=True, exist_ok=True)
            (jvm_previews / "ProfileContentScreenshotTest.kt").write_text(
                """package com.example.feature.auth.ui.previews

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.github.takahirom.roborazzi.captureRoboImage
import com.example.core.designsystem.theme.AppTheme
import kotlin.test.Test

class ProfileContentScreenshotTest {
    @Test fun phone_light() {
        captureRoboImage("profile_content_phone_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(360.dp, 640.dp)) {}
            }
        }
    }

    @Test fun phone_dark() {
        captureRoboImage("profile_content_phone_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(360.dp, 640.dp)) {}
            }
        }
    }

    @Test fun tablet_light() {
        captureRoboImage("profile_content_tablet_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(673.dp, 841.dp)) {}
            }
        }
    }

    @Test fun tablet_dark() {
        captureRoboImage("profile_content_tablet_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(673.dp, 841.dp)) {}
            }
        }
    }

    @Test fun desktop_light() {
        captureRoboImage("profile_content_desktop_light.png") {
            AppTheme {
                Box(modifier = Modifier.size(1280.dp, 800.dp)) {}
            }
        }
    }

    @Test fun desktop_dark() {
        captureRoboImage("profile_content_desktop_dark.png") {
            AppTheme(darkTheme = true) {
                Box(modifier = Modifier.size(1280.dp, 800.dp)) {}
            }
        }
    }
}
""",
                encoding="utf-8",
            )
            findings = (
                governance_scripts.run_scan_violations(root)
                + governance_scripts.run_audit_project(root)
            )
        threshold = governance_scripts.SEVERITY_RANK["HIGH"]
        failing = [f for f in findings if governance_scripts.SEVERITY_RANK.get(f["severity"], 0) >= threshold]
        self.assertEqual(failing, [])

    def test_reads_kmm_skills_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".kmm-skills").write_text(
                '{"skills_repo": "ronjunevaldoz/kmm-agent-skills", "version": "1.24.1"}',
                encoding="utf-8",
            )
            version = governance_scripts.read_skills_version(root)
        self.assertEqual(version, "1.24.1")

    def test_missing_kmm_skills_file_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            version = governance_scripts.read_skills_version(Path(tmp))
        self.assertIsNone(version)

    def test_missing_kmm_skills_file_fails_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            (root / ".kmm-skills").unlink()
            findings = governance_scripts.validate_skills_version_pin(root)
        self.assertEqual(findings[0]["type"], "missing_version_pin")
        self.assertEqual(findings[0]["severity"], "HIGH")

    def test_branch_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            (root / ".kmm-skills").write_text(
                '{"skills_repo": "ronjunevaldoz/kmm-agent-skills", "version": "main"}',
                encoding="utf-8",
            )
            findings = governance_scripts.validate_skills_version_pin(root)
        self.assertEqual(findings[0]["type"], "mutable_version_pin")
        self.assertEqual(findings[0]["severity"], "HIGH")

    def test_tag_version_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            (root / ".kmm-skills").write_text(
                '{"skills_repo": "ronjunevaldoz/kmm-agent-skills", "version": "v1.25.11"}',
                encoding="utf-8",
            )
            findings = governance_scripts.validate_skills_version_pin(root)
        self.assertEqual(findings, [])

    def test_cli_exit_0_on_clean_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            script = REPO_ROOT / "skills/kotlin-multiplatform-audit/scripts/governance_check.py"
            result = subprocess.run(
                ["python3", str(script), str(root)],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0)

    def test_cli_exit_1_on_unpinned_skills_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            (root / ".kmm-skills").write_text(
                '{"skills_repo": "ronjunevaldoz/kmm-agent-skills", "version": "main"}',
                encoding="utf-8",
            )
            script = REPO_ROOT / "skills/kotlin-multiplatform-audit/scripts/governance_check.py"
            result = subprocess.run(
                ["python3", str(script), str(root)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)

    def test_cli_exit_2_on_missing_root(self) -> None:
        script = REPO_ROOT / "skills/kotlin-multiplatform-audit/scripts/governance_check.py"
        result = subprocess.run(
            ["python3", str(script), "/nonexistent/path/xyz"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)

    def test_cli_json_output_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            script = REPO_ROOT / "skills/kotlin-multiplatform-audit/scripts/governance_check.py"
            result = subprocess.run(
                ["python3", str(script), str(root), "--json"],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertIsInstance(parsed, list)


class HarvestProjectTests(unittest.TestCase):
    """Tests for --harvest mode and _detect_positive_patterns."""

    def test_harvest_returns_findings_and_lessons_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = audit_scripts.harvest_project(root)
            self.assertIn("project", result)
            self.assertIn("findings", result)
            self.assertIn("lessons", result)
            self.assertIsInstance(result["findings"], list)
            self.assertIsInstance(result["lessons"], list)

    def test_harvest_detects_local_app_dark_theme_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AppTheme.kt").write_text(
                "val LocalAppDarkTheme = compositionLocalOf<Boolean?> { null }\n"
                "fun isDark(): Boolean = LocalAppDarkTheme.current ?: isSystemInDarkTheme()\n",
                encoding="utf-8",
            )
            lessons = audit_scripts._detect_positive_patterns(root)
            patterns = [l["pattern"] for l in lessons]
            self.assertTrue(
                any("LocalAppDarkTheme" in p for p in patterns),
                f"Expected LocalAppDarkTheme lesson, got: {patterns}",
            )

    def test_harvest_detects_undo_window_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "FooViewModel.kt").write_text(
                "private const val UNDO_WINDOW_MS = 4500L\n"
                "private var undoJob: Job? = null\n",
                encoding="utf-8",
            )
            lessons = audit_scripts._detect_positive_patterns(root)
            patterns = [l["pattern"] for l in lessons]
            self.assertTrue(
                any("undo" in p.lower() for p in patterns),
                f"Expected undo-window lesson, got: {patterns}",
            )

    def test_harvest_detects_build_logic_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_logic = root / "build-logic" / "convention"
            build_logic.mkdir(parents=True)
            (build_logic / "build.gradle.kts").write_text("plugins { `kotlin-dsl` }", encoding="utf-8")
            lessons = audit_scripts._detect_positive_patterns(root)
            patterns = [l["pattern"] for l in lessons]
            self.assertTrue(
                any("build-logic" in p.lower() for p in patterns),
                f"Expected build-logic lesson, got: {patterns}",
            )

    def test_harvest_cli_outputs_json(self) -> None:
        import subprocess, json as _json
        with tempfile.TemporaryDirectory() as tmp:
            audit_script = REPO_ROOT / "skills" / "kotlin-multiplatform-audit" / "scripts" / "audit_project.py"
            result = subprocess.run(
                ["python3", str(audit_script), "--harvest", tmp],
                capture_output=True,
                text=True,
            )
            self.assertIn(result.returncode, (0, 1), "harvest should exit 0 or 1 only")
            parsed = _json.loads(result.stdout)
            self.assertIn("findings", parsed)
            self.assertIn("lessons", parsed)


if __name__ == "__main__":
    unittest.main()
