package GROUP_ID.designsystem.detekt

import io.gitlab.arturbosch.detekt.test.lint
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ComponentRegistryRuleTest {

    private fun rule() = ComponentRegistryRule(io.gitlab.arturbosch.detekt.api.Config.empty)

    @Test fun `flags reimplemented Button built from raw primitives`() {
        val findings = rule().lintAt("feature/auth/ui/AuthButton.kt", """
            import androidx.compose.runtime.Composable
            @Composable
            fun MyButton(label: String) {
                Button(onClick = {}) { Text(label) }
            }
        """.trimIndent())
        assertEquals(1, findings.size)
        assertTrue(findings[0].message.contains("AppButton"))
    }

    @Test fun `flags reimplemented Card built from raw primitives`() {
        val findings = rule().lintAt("feature/home/ui/ProductCard.kt", """
            import androidx.compose.runtime.Composable
            @Composable
            fun ProductCard(title: String) {
                Card { Text(title) }
            }
        """.trimIndent())
        assertEquals(1, findings.size)
    }

    @Test fun `does not flag AppButton in design system`() {
        val findings = rule().lintAt("core/designsystem/components/AppButton.kt", """
            import androidx.compose.runtime.Composable
            @Composable
            fun AppButton(label: String) {}
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }

    @Test fun `does not flag Preview composable`() {
        val findings = rule().lintAt("core/designsystem/previews/AppButtonPreview.kt", """
            import androidx.compose.runtime.Composable
            @Composable
            fun AppButtonPreview() {}
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }

    @Test fun `does not flag a wrapper that composes the design system component`() {
        val findings = rule().lintAt("feature/home/ui/ProductCard.kt", """
            import androidx.compose.runtime.Composable
            @Composable
            fun ProductCard(title: String) {
                AppCard { AppText(title) }
            }
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }

    @Test fun `does not flag a zero-parameter composable`() {
        val findings = rule().lintAt("feature/home/ui/WelcomeCard.kt", """
            import androidx.compose.runtime.Composable
            @Composable
            fun WelcomeCard() {
                Card { Text("Welcome") }
            }
        """.trimIndent())
        assertTrue(findings.isEmpty())
    }
}
