package GROUP_ID.designsystem.detekt

import io.gitlab.arturbosch.detekt.api.BaseRule
import io.gitlab.arturbosch.detekt.api.Finding
import io.gitlab.arturbosch.detekt.test.lint
import java.nio.file.Files

fun BaseRule.lintAt(relativePath: String, content: String): List<Finding> {
    val root = Files.createTempDirectory("detekt-rule-test")
    val file = root.resolve(relativePath)
    Files.createDirectories(file.parent)
    Files.writeString(file, content)
    return try {
        lint(file)
    } finally {
        root.toFile().deleteRecursively()
    }
}
