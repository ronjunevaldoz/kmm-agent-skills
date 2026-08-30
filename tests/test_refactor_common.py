# SPDX-FileCopyrightText: 2023-2026 Ron June Valdoz
#
# SPDX-License-Identifier: Apache-2.0

import re

from scripts.refactor_common import substitute_outside_string_literals


def test_skips_matches_inside_double_quoted_string():
    pattern = re.compile(r"\bOld\b")
    content = 'val x = "Old"\nclass Old\n'
    result = substitute_outside_string_literals(pattern, "New", content)
    assert result == 'val x = "Old"\nclass New\n'


def test_skips_matches_inside_triple_quoted_string():
    pattern = re.compile(r"\bOld\b")
    content = 'val x = """Old"""\nclass Old\n'
    result = substitute_outside_string_literals(pattern, "New", content)
    assert result == 'val x = """Old"""\nclass New\n'


def test_skips_matches_inside_char_literal():
    pattern = re.compile(r"\bO\b")
    content = "val c = 'O'\nval x = O\n"
    result = substitute_outside_string_literals(pattern, "N", content)
    assert result == "val c = 'O'\nval x = N\n"


def test_replaces_when_no_string_literals_present():
    pattern = re.compile(r"\bOld\b")
    content = "class Old(val x: Old)\n"
    result = substitute_outside_string_literals(pattern, "New", content)
    assert result == "class New(val x: New)\n"
