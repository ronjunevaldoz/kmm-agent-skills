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
import re
import sys
from pathlib import Path

# 40 official shadcn/ui components with their canonical Awake filenames
OFFICIAL_SHADCN_COMPONENTS = [
    # Inputs & Controls
    ("Button", "inputs", ["ShadcnButton.kt", "Button.kt"], "ButtonPage.kt"),
    ("ButtonGroup", "inputs", ["ShadcnButtonGroup.kt", "ButtonGroup.kt"], "ButtonGroupPage.kt"),
    ("Checkbox", "inputs", ["ShadcnCheckbox.kt", "Checkbox.kt"], "CheckboxPage.kt"),
    ("Combobox", "inputs", ["ShadcnCombobox.kt", "Combobox.kt"], "ComboboxPage.kt"),
    ("Field", "inputs", ["ShadcnField.kt", "Field.kt"], "FieldPage.kt"),
    ("Input", "inputs", ["ShadcnInput.kt", "TextField.kt"], "TextFieldPage.kt"),
    ("InputGroup", "inputs", ["ShadcnInputGroup.kt", "InputGroup.kt"], "InputGroupPage.kt"),
    ("InputOTP", "inputs", ["ShadcnInputOtp.kt", "InputOtp.kt"], "InputOtpPage.kt"),
    ("RadioGroup", "inputs", ["ShadcnRadioGroup.kt", "RadioGroup.kt"], "RadioGroupPage.kt"),
    ("RangeSlider", "inputs", ["ShadcnRangeSlider.kt", "RangeSlider.kt"], "RangeSliderPage.kt"),
    ("Select", "inputs", ["ShadcnSelect.kt", "Select.kt"], "SelectPage.kt"),
    ("Slider", "inputs", ["ShadcnSlider.kt", "Slider.kt"], "SliderPage.kt"),
    ("Switch", "inputs", ["ShadcnSwitch.kt", "Switch.kt"], "SwitchPage.kt"),
    ("Textarea", "inputs", ["ShadcnTextarea.kt", "Textarea.kt"], "TextareaPage.kt"),
    ("Toggle", "inputs", ["ShadcnToggle.kt", "Toggle.kt"], "TogglePage.kt"),
    ("ToggleGroup", "inputs", ["ShadcnToggleGroup.kt", "ToggleGroup.kt"], "ToggleGroupPage.kt"),
    # Feedback & Status
    ("Alert", "status", ["ShadcnAlert.kt", "Alert.kt"], "AlertPage.kt"),
    ("Avatar", "status", ["ShadcnAvatar.kt", "Avatar.kt"], "AvatarPage.kt"),
    ("Badge", "status", ["ShadcnBadge.kt", "Badge.kt"], "BadgePage.kt"),
    ("Empty", "status", ["ShadcnEmpty.kt", "Empty.kt"], "EmptyPage.kt"),
    ("Kbd", "status", ["ShadcnKbd.kt", "Kbd.kt"], "KbdPage.kt"),
    ("Progress", "status", ["ShadcnProgress.kt", "Progress.kt"], "ProgressPage.kt"),
    ("Skeleton", "status", ["ShadcnSkeleton.kt", "Skeleton.kt"], "SkeletonPage.kt"),
    ("Spinner", "status", ["ShadcnSpinner.kt", "Spinner.kt"], "SpinnerPage.kt"),
    ("Toast", "status", ["ShadcnToast.kt", "Toast.kt"], "ToastPage.kt"),
    # Navigation & Overlays
    ("Breadcrumb", "navigation", ["ShadcnBreadcrumb.kt", "Breadcrumb.kt"], "BreadcrumbPage.kt"),
    ("Dialog", "overlay", ["ShadcnDialog.kt", "Dialog.kt"], "DialogPage.kt"),
    ("DropdownMenu", "overlay", ["ShadcnDropdownMenu.kt", "DropdownMenu.kt"], "DropdownMenuPage.kt"),
    ("Popover", "overlay", ["ShadcnPopover.kt", "Popover.kt"], "PopoverPage.kt"),
    ("Sheet", "overlay", ["ShadcnSheet.kt", "Sheet.kt"], "SheetPage.kt"),
    ("Tabs", "navigation", ["ShadcnTabs.kt", "Tabs.kt"], "TabsPage.kt"),
    ("Tooltip", "overlay", ["ShadcnTooltip.kt", "Tooltip.kt"], "TooltipPage.kt"),
    # Layout & Data
    ("Accordion", "layout", ["ShadcnAccordion.kt", "Accordion.kt"], "AccordionPage.kt"),
    ("AspectRatio", "layout", ["ShadcnAspectRatio.kt", "AspectRatio.kt"], "AspectRatioPage.kt"),
    ("Card", "layout", ["ShadcnCard.kt", "Card.kt"], "CardPage.kt"),
    ("Collapsible", "layout", ["ShadcnCollapsible.kt", "Collapsible.kt"], "CollapsiblePage.kt"),
    ("Resizable", "layout", ["ShadcnResizable.kt", "Resizable.kt"], "ResizablePage.kt"),
    ("Separator", "layout", ["ShadcnSeparator.kt", "Separator.kt"], "SeparatorPage.kt"),
    ("Sidebar", "layout", ["ShadcnSidebar.kt", "Sidebar.kt"], "SidebarPage.kt"),
    ("Table", "layout", ["ShadcnTable.kt", "Table.kt"], "TablePage.kt"),
]

IGNORED_DIRS = {".git", ".gradle", "build", ".idea", ".vscode", ".claude", "node_modules", ".system_generated"}


def audit_shadcn_parity(project_root: Path) -> dict:
    project_root = project_root.resolve()

    # Fast indexed scan
    kt_files_by_name: dict[str, Path] = {}
    existing_png_files = set()

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for file in files:
            p = Path(root) / file
            if file.endswith(".kt"):
                kt_files_by_name[file] = p
            elif file.endswith(".png"):
                existing_png_files.add(file.lower())

    results = []

    for name, category, comp_candidates, page_file in OFFICIAL_SHADCN_COMPONENTS:
        has_comp = any(cand in kt_files_by_name for cand in comp_candidates)

        # Check if page is real or a placeholder stub
        has_page = False
        is_placeholder = False
        if page_file in kt_files_by_name:
            page_path = kt_files_by_name[page_file]
            try:
                page_content = page_path.read_text(encoding="utf-8")
                if "showcasePlaceholder(" in page_content or "ShowcaseStatus.Placeholder" in page_content:
                    is_placeholder = True
                    has_page = False
                else:
                    has_page = True
            except Exception:
                has_page = True

        preview_name = name.lower()
        has_preview = any(preview_name in f for f in existing_png_files)

        results.append({
            "name": name,
            "category": category,
            "has_comp": has_comp,
            "has_page": has_page,
            "is_placeholder": is_placeholder,
            "has_preview": has_preview,
            "is_complete": has_comp and has_page and has_preview,
        })

    total = len(results)
    implemented_comps = sum(1 for r in results if r["has_comp"])
    showcase_pages = sum(1 for r in results if r["has_page"])
    placeholders = sum(1 for r in results if r["is_placeholder"])
    visual_previews = sum(1 for r in results if r["has_preview"])
    complete_count = sum(1 for r in results if r["is_complete"])

    return {
        "results": results,
        "total": total,
        "implemented_comps": implemented_comps,
        "showcase_pages": showcase_pages,
        "placeholders": placeholders,
        "visual_previews": visual_previews,
        "complete_count": complete_count,
        "parity_percentage": (complete_count / total) * 100.0,
    }


def print_scorecard(summary: dict) -> None:
    print(f"\n📊 Deep Shadcn / UI Compose Parity Scorecard (Real Implementations)")
    print(f"{'=' * 80}")
    print(f"{'Component':<18} | {'Category':<12} | {'Component':<10} | {'Live Page':<12} | {'Visual Test':<10}")
    print(f"{'-' * 18}-+-{'-' * 12}-+-{'-' * 10}-+-{'-' * 12}-+-{'-' * 10}")

    for r in summary["results"]:
        comp_status = "✅ Built" if r["has_comp"] else "❌ Missing"
        page_status = "✅ Ready" if r["has_page"] else ("⚠️ Stub" if r["is_placeholder"] else "❌ None")
        preview_status = "📸 Verified" if r["has_preview"] else "⏳ None"
        print(f"{r['name']:<18} | {r['category']:<12} | {comp_status:<10} | {page_status:<12} | {preview_status:<10}")

    print(f"{'=' * 80}")
    print(f"🎯 Total Tracked Components : {summary['total']}")
    print(f"📦 Design System Components : {summary['implemented_comps']}/{summary['total']} ({(summary['implemented_comps']/summary['total'])*100:.1f}%)")
    print(f"🖥️ Live Non-Stub Pages      : {summary['showcase_pages']}/{summary['total']} ({(summary['showcase_pages']/summary['total'])*100:.1f}%)")
    print(f"⚠️ Placeholder Stubs        : {summary['placeholders']}/{summary['total']} ({(summary['placeholders']/summary['total'])*100:.1f}%)")
    print(f"📸 Visual Baseline Assets   : {summary['visual_previews']}/{summary['total']} ({(summary['visual_previews']/summary['total'])*100:.1f}%)")
    print(f"⭐ Complete Parity (All 3)  : {summary['complete_count']}/{summary['total']} ({summary['parity_percentage']:.1f}%)\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deep Shadcn/UI Compose parity auditor")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root directory")
    args = parser.parse_args()

    summary = audit_shadcn_parity(args.project)
    print_scorecard(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
