from __future__ import annotations

import importlib.util
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
                "## When to Use This Skill\n\n**Trigger keywords:** example.\n",
                encoding="utf-8",
            )

            findings = audit_repo_scripts.audit_skills_repo(root)

            self.assertFalse(any("missing markers" in f for f in findings))


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


if __name__ == "__main__":
    unittest.main()
