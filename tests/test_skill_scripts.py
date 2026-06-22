from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


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


class AuditProjectTests(unittest.TestCase):
    def test_audit_project_finds_smells(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "feature" / "auth" / "ui"
            ui_dir.mkdir(parents=True)
            (ui_dir / "AuthViewModel.kt").write_text(
                """
                _state.value = _state.value.copy(isLoading = true)
                val flow = MutableSharedFlow<Int>(replay = 1)
                import foo.bar.data.SecretRepo
                """.strip(),
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

    def test_extract_reference_components_finds_all_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)
        self.assertIn("AppFoo.kt", refs)
        self.assertIn("AppBar.kt", refs)
        self.assertEqual(len(refs), 2)

    def test_extract_reference_components_body_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)
        self.assertIn("AppFoo", refs["AppFoo.kt"])

    def test_compare_status_missing_when_no_project_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            results = update_design_system_scripts.compare(root, skill_md)
        statuses = {r["file"]: r["status"] for r in results}
        self.assertEqual(statuses["AppFoo.kt"], "MISSING")
        self.assertEqual(statuses["AppBar.kt"], "MISSING")

    def test_compare_status_current_when_file_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = root / "SKILL.md"
            self._write_skill_md(skill_md, self._SKILL_MD_TEMPLATE)
            refs = update_design_system_scripts.extract_reference_components(skill_md)

            comp_dir = root / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            (comp_dir / "AppFoo.kt").write_text(refs["AppFoo.kt"], encoding="utf-8")

            results = update_design_system_scripts.compare(root, skill_md)
        foo = next(r for r in results if r["file"] == "AppFoo.kt")
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
        foo = next(r for r in results if r["file"] == "AppFoo.kt")
        self.assertEqual(foo["status"], "MODIFIED")

    def test_resolve_filename_normalises_name_without_extension(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("AppButton"),
            "AppButton.kt",
        )

    def test_resolve_filename_normalises_name_with_app_prefix(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("Button"),
            "AppButton.kt",
        )

    def test_resolve_filename_passthrough_for_kt_suffix(self) -> None:
        self.assertEqual(
            update_design_system_scripts._resolve_filename("AppButton.kt"),
            "AppButton.kt",
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
        self.assertTrue(str(result).endswith("components"))

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

            comp_dir = root / "core" / "designsystem" / "components"
            comp_dir.mkdir(parents=True)
            for filename, code in refs.items():
                (comp_dir / filename).write_text(code, encoding="utf-8")

            result = subprocess.run(
                ["python3",
                 str(REPO_ROOT / "skills" / "kotlin-multiplatform-design-system" / "scripts" / "update_design_system.py"),
                 str(root),
                 "--skill-root", str(skill_root)],
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
