#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0
""":"
exec python3 "$0" "$@"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# The 40 core shadcn/ui components
OFFICIAL_SHADCN_COMPONENTS = [
    # Inputs & Controls
    ("Button", "inputs", "Button.kt", "ButtonPage.kt"),
    ("ButtonGroup", "inputs", "ButtonGroup.kt", "ButtonGroupPage.kt"),
    ("Checkbox", "inputs", "Checkbox.kt", "CheckboxPage.kt"),
    ("Combobox", "inputs", "Combobox.kt", "ComboboxPage.kt"),
    ("Field", "inputs", "Field.kt", "FieldPage.kt"),
    ("Input", "inputs", "TextField.kt", "TextFieldPage.kt"),
    ("InputGroup", "inputs", "InputGroup.kt", "InputGroupPage.kt"),
    ("InputOTP", "inputs", "InputOtp.kt", "InputOtpPage.kt"),
    ("RadioGroup", "inputs", "RadioGroup.kt", "RadioGroupPage.kt"),
    ("RangeSlider", "inputs", "RangeSlider.kt", "RangeSliderPage.kt"),
    ("Select", "inputs", "Select.kt", "SelectPage.kt"),
    ("Slider", "inputs", "Slider.kt", "SliderPage.kt"),
    ("Switch", "inputs", "Switch.kt", "SwitchPage.kt"),
    ("Textarea", "inputs", "Textarea.kt", "TextareaPage.kt"),
    ("Toggle", "inputs", "Toggle.kt", "TogglePage.kt"),
    ("ToggleGroup", "inputs", "ToggleGroup.kt", "ToggleGroupPage.kt"),
    # Feedback & Status
    ("Alert", "status", "Alert.kt", "AlertPage.kt"),
    ("Avatar", "status", "Avatar.kt", "AvatarPage.kt"),
    ("Badge", "status", "Badge.kt", "BadgePage.kt"),
    ("Empty", "status", "Empty.kt", "EmptyPage.kt"),
    ("Kbd", "status", "Kbd.kt", "KbdPage.kt"),
    ("Progress", "status", "Progress.kt", "ProgressPage.kt"),
    ("Skeleton", "status", "Skeleton.kt", "SkeletonPage.kt"),
    ("Spinner", "status", "Spinner.kt", "SpinnerPage.kt"),
    ("Toast", "status", "Toast.kt", "ToastPage.kt"),
    # Navigation & Overlays
    ("Breadcrumb", "navigation", "Breadcrumb.kt", "BreadcrumbPage.kt"),
    ("Dialog", "overlay", "Dialog.kt", "DialogPage.kt"),
    ("DropdownMenu", "overlay", "DropdownMenu.kt", "DropdownMenuPage.kt"),
    ("Popover", "overlay", "Popover.kt", "PopoverPage.kt"),
    ("Sheet", "overlay", "Sheet.kt", "SheetPage.kt"),
    ("Tabs", "navigation", "Tabs.kt", "TabsPage.kt"),
    ("Tooltip", "overlay", "Tooltip.kt", "TooltipPage.kt"),
    # Layout & Data
    ("Accordion", "layout", "Accordion.kt", "AccordionPage.kt"),
    ("AspectRatio", "layout", "AspectRatio.kt", "AspectRatioPage.kt"),
    ("Card", "layout", "Card.kt", "CardPage.kt"),
    ("Collapsible", "layout", "Collapsible.kt", "CollapsiblePage.kt"),
    ("Resizable", "layout", "Resizable.kt", "ResizablePage.kt"),
    ("Separator", "layout", "Separator.kt", "SeparatorPage.kt"),
    ("Sidebar", "layout", "Sidebar.kt", "SidebarPage.kt"),
    ("Table", "layout", "Table.kt", "TablePage.kt"),
]

IGNORED_DIRS = {".git", ".gradle", "build", ".idea", ".vscode", ".claude", "node_modules", ".system_generated"}


def audit_shadcn_parity(project_root: Path) -> dict:
    project_root = project_root.resolve()
    
    # 1. Build fast file index in one single pass (under 50ms)
    existing_kt_files = set()
    existing_png_files = set()

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for file in files:
            if file.endswith(".kt"):
                existing_kt_files.add(file)
            elif file.endswith(".png"):
                existing_png_files.add(file.lower())

    results = []

    # Check components, pages, and previews
    for name, category, comp_file, page_file in OFFICIAL_SHADCN_COMPONENTS:
        has_comp = comp_file in existing_kt_files
        has_page = page_file in existing_kt_files

        # Check visual preview baselines
        preview_name = name.lower()
        has_preview = any(preview_name in f for f in existing_png_files)

        results.append({
            "name": name,
            "category": category,
            "has_comp": has_comp,
            "has_page": has_page,
            "has_preview": has_preview,
            "is_complete": has_comp and has_page,
        })

    total = len(results)
    implemented_comps = sum(1 for r in results if r["has_comp"])
    showcase_pages = sum(1 for r in results if r["has_page"])
    visual_previews = sum(1 for r in results if r["has_preview"])
    complete_count = sum(1 for r in results if r["is_complete"])

    return {
        "results": results,
        "total": total,
        "implemented_comps": implemented_comps,
        "showcase_pages": showcase_pages,
        "visual_previews": visual_previews,
        "complete_count": complete_count,
        "parity_percentage": (complete_count / total) * 100.0,
    }


def print_scorecard(summary: dict) -> None:
    print(f"\n📊 Shadcn / UI Compose Parity Scorecard")
    print(f"{'=' * 75}")
    print(f"{'Component':<18} | {'Category':<12} | {'Component':<10} | {'Showcase':<10} | {'Visual Test':<10}")
    print(f"{'-' * 18}-+-{'-' * 12}-+-{'-' * 10}-+-{'-' * 10}-+-{'-' * 10}")

    for r in summary["results"]:
        comp_status = "✅ Done" if r["has_comp"] else "❌ Missing"
        page_status = "✅ Done" if r["has_page"] else "❌ Missing"
        preview_status = "📸 Yes" if r["has_preview"] else "⏳ None"
        print(f"{r['name']:<18} | {r['category']:<12} | {comp_status:<10} | {page_status:<10} | {preview_status:<10}")

    print(f"{'=' * 75}")
    print(f"🎯 Total Tracked Components : {summary['total']}")
    print(f"📦 Implemented Components  : {summary['implemented_comps']}/{summary['total']} ({(summary['implemented_comps']/summary['total'])*100:.1f}%)")
    print(f"🖥️ Interactive Pages        : {summary['showcase_pages']}/{summary['total']} ({(summary['showcase_pages']/summary['total'])*100:.1f}%)")
    print(f"📸 Visual Baseline Assets   : {summary['visual_previews']}/{summary['total']} ({(summary['visual_previews']/summary['total'])*100:.1f}%)")
    print(f"⭐ Complete (Comp + Page)   : {summary['complete_count']}/{summary['total']} ({summary['parity_percentage']:.1f}%)\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated Shadcn/UI Compose parity auditor")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    args = parser.parse_args()

    summary = audit_shadcn_parity(args.project)
    print_scorecard(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
