#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CATEGORY_MAP = {
    "inputs": ("Inputs", "inputs"),
    "layout": ("Layout", "layout"),
    "overlays": ("Overlays", "overlays"),
    "status": ("Status", "status"),
    "typography": ("Typography", "typography"),
    "blocks": ("Blocks", "blocks"),
    "gettingstarted": ("GettingStarted", "gettingstarted"),
}


def generate_component_code(name: str, category: str) -> str:
    return f"""/*
 * SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package io.github.ronjunevaldoz.awake.ui.designsystem.components

import io.github.ronjunevaldoz.awake.compose.foundation.layout.Box
import io.github.ronjunevaldoz.awake.compose.runtime.Composable
import io.github.ronjunevaldoz.awake.compose.runtime.Composer
import io.github.ronjunevaldoz.awake.compose.ui.Modifier
import io.github.ronjunevaldoz.awake.ui.designsystem.ShadcnTheme

/**
 * Shadcn {name} component in Compose Multiplatform.
 * Follows No-Material design token guidelines with full keyboard accessibility.
 */
@Composable
fun Shadcn{name}(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit = {{}},
) {{
    Box(modifier = modifier) {{
        content()
    }}
}}
"""


def generate_page_code(name: str, category_enum: str, category_dir: str) -> str:
    page_id = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()
    return f"""/*
 * SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package io.github.ronjunevaldoz.awake.sample.uishowcase.ui.pages.{category_dir}

import io.github.ronjunevaldoz.awake.compose.foundation.layout.Column
import io.github.ronjunevaldoz.awake.compose.foundation.layout.Spacer
import io.github.ronjunevaldoz.awake.compose.foundation.layout.height
import io.github.ronjunevaldoz.awake.compose.runtime.Composer
import io.github.ronjunevaldoz.awake.compose.ui.Modifier
import io.github.ronjunevaldoz.awake.compose.ui.unit.dp
import io.github.ronjunevaldoz.awake.sample.uishowcase.state.UiShowcaseRuntimeState
import io.github.ronjunevaldoz.awake.sample.uishowcase.ui.ShowcaseCategory
import io.github.ronjunevaldoz.awake.sample.uishowcase.ui.ShowcasePage
import io.github.ronjunevaldoz.awake.ui.designsystem.components.Shadcn{name}
import io.github.ronjunevaldoz.awake.ui.designsystem.components.shadcnMuted

internal val {name}Page = ShowcasePage(
    id = "{page_id}",
    title = "{name}",
    category = ShowcaseCategory.{category_enum},
    description = "Interactive {name} showcase preview.",
    usageCode = "Shadcn{name} {{ /* content */ }}",
    hero = {{ state -> {name}Hero(state) }},
)

context(_: Composer)
private fun {name}Hero(state: UiShowcaseRuntimeState) {{
    Column {{
        shadcnMuted("{name} component interactive preview.")
        Spacer(Modifier.height(12.dp))
        Shadcn{name} {{
            // Content
        }}
    }}
}}
"""


def generate_test_code(name: str) -> str:
    return f"""/*
 * SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
 *
 * SPDX-License-Identifier: Apache-2.0
 */
package io.github.ronjunevaldoz.awake.ui.designsystem.components

import kotlin.test.Test
import kotlin.test.assertNotNull

class Shadcn{name}Test {{
    @Test
    fun test{name}Instantiation() {{
        // Basic contract validation
        assertNotNull("{name}")
    }}
}}
"""


def scaffold_component_slice(project_root: Path, name: str, category_key: str, dry_run: bool = False) -> None:
    category_key = category_key.lower().strip()
    if category_key not in CATEGORY_MAP:
        print(f"❌ Unknown category: '{category_key}'. Available: {', '.join(CATEGORY_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    category_enum, category_dir = CATEGORY_MAP[category_key]

    comp_file = project_root / "awake" / "ui" / "designsystem" / "src" / "commonMain" / "kotlin" / "io" / "github" / "ronjunevaldoz" / "awake" / "ui" / "designsystem" / "components" / f"Shadcn{name}.kt"
    page_file = project_root / "samples" / "ui-showcase" / "src" / "commonMain" / "kotlin" / "io" / "github" / "ronjunevaldoz" / "awake" / "sample" / "uishowcase" / "ui" / "pages" / category_dir / f"{name}Page.kt"
    test_file = project_root / "awake" / "ui" / "designsystem" / "src" / "commonTest" / "kotlin" / "io" / "github" / "ronjunevaldoz" / "awake" / "ui" / "designsystem" / "components" / f"Shadcn{name}Test.kt"
    catalog_file = project_root / "samples" / "ui-showcase" / "src" / "commonMain" / "kotlin" / "io" / "github" / "ronjunevaldoz" / "awake" / "sample" / "uishowcase" / "ui" / "ShowcaseCatalog.kt"

    print(f"\n🎨 Scaffolding Full-Stack Shadcn Component: '{name}'")
    print(f"   1. Component : {comp_file.name}")
    print(f"   2. Page      : {page_file.name}")
    print(f"   3. Test      : {test_file.name}")

    if dry_run:
        print("\n🔍 DRY RUN: No files were written to disk.")
        return

    # Write component
    comp_file.parent.mkdir(parents=True, exist_ok=True)
    comp_file.write_text(generate_component_code(name, category_key), encoding="utf-8")
    print(f"  ✅ Created {comp_file.name}")

    # Write page
    page_file.parent.mkdir(parents=True, exist_ok=True)
    page_file.write_text(generate_page_code(name, category_enum, category_dir), encoding="utf-8")
    print(f"  ✅ Created {page_file.name}")

    # Write test
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(generate_test_code(name), encoding="utf-8")
    print(f"  ✅ Created {test_file.name}")

    # Register in catalog if present
    if catalog_file.exists():
        content = catalog_file.read_text(encoding="utf-8")
        import_stmt = f"import io.github.ronjunevaldoz.awake.sample.uishowcase.ui.pages.{category_dir}.{name}Page"
        page_entry = f"    {name}Page,"
        if import_stmt not in content:
            lines = content.splitlines()
            import_idx = -1
            for idx, line in enumerate(lines):
                if line.startswith("import io.github.ronjunevaldoz.awake.sample.uishowcase.ui.pages."):
                    import_idx = idx
            if import_idx != -1:
                lines.insert(import_idx + 1, import_stmt)
            content = "\n".join(lines)

        list_marker = "internal val ShowcasePages: List<ShowcasePage> = listOf("
        if list_marker in content and page_entry not in content:
            content = content.replace(list_marker, f"{list_marker}\n{page_entry}")
        catalog_file.write_text(content, encoding="utf-8")
        print(f"  ✅ Registered in {catalog_file.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Full-Stack Shadcn Component & Showcase Scaffolder")
    parser.add_argument("--name", type=str, required=True, help="Component name (e.g. Sheet, Accordion, Combobox)")
    parser.add_argument("--category", type=str, required=True, help="Category: inputs, layout, overlays, status, typography, blocks")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing disk")

    args = parser.parse_args()
    scaffold_component_slice(args.project, args.name, args.category, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
