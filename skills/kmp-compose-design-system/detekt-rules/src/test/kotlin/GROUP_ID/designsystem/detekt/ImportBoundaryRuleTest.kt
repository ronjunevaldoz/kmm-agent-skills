package GROUP_ID.designsystem.detekt

import io.gitlab.arturbosch.detekt.test.lint
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ImportBoundaryRuleTest {

    private fun rule() = ImportBoundaryRule(io.gitlab.arturbosch.detekt.api.Config.empty)

    @Test fun `flags direct token import in feature ui`() {
        val findings = rule().lintAt("feature/auth/ui/AuthContent.kt", """
            import GROUP_ID.core.designsystem.tokens.AppColors
        """.trimIndent())
        assertEquals(1, findings.size)
        assertTrue(findings[0].message.contains("appTheme"))
    }

    @Test fun `flags spacing import in feature ui`() {
        val findings = rule().lintAt("feature/home/ui/HomeScreen.kt", """
            import GROUP_ID.core.designsystem.spacing.AppSpacing
        """.trimIndent())
        assertEquals(1, findings.size)
    }

    @Test fun `allows component import in feature ui`() {
        val findings = rule().lintAt("feature/auth/ui/AuthContent.kt", """
            import GROUP_ID.core.designsystem.components.AppButton
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }

    @Test fun `allows theme import in feature ui`() {
        val findings = rule().lintAt("feature/auth/ui/AuthContent.kt", """
            import GROUP_ID.core.designsystem.theme.AppTheme
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }

    @Test fun `does not flag token import outside feature ui`() {
        val findings = rule().lintAt("core/designsystem/theme/AppTheme.kt", """
            import GROUP_ID.core.designsystem.tokens.AppColors
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }
}
