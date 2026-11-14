"""Tests for scripts/dev/nowin_codemod.py.

Mutation check:
    Copied scripts/dev/nowin_codemod.py to a scratch directory and mutated
    line 16 `reverse=True` -> `reverse=False` in `patch()`; re-running pytest
    failed `test_patch_multiple_calls_same_line_and_trailing_comma` with
    `AssertionError` at line 19 (`assert b[col:col + 1] == b")"`).
"""
import sys
from pathlib import Path

import pytest

SCRIPTS_DEV = Path(__file__).resolve().parents[5] / "scripts" / "dev"
if str(SCRIPTS_DEV) not in sys.path:
    sys.path.append(str(SCRIPTS_DEV))

import nowin_codemod  # noqa: E402


def test_patch_single_line_captured_and_idempotent(tmp_path):
    target = tmp_path / "sample.py"
    original = (
        "import subprocess\n"
        'subprocess.run(["echo", "hi"], capture_output=True)\n'
    )
    expected = (
        "import subprocess\n"
        'subprocess.run(["echo", "hi"], capture_output=True, '
        'creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))\n'
    )
    target.write_text(original, encoding="utf-8")

    hits_first = nowin_codemod.patch(target)
    assert hits_first == 1
    assert target.read_text(encoding="utf-8") == expected

    hits_second = nowin_codemod.patch(target)
    assert hits_second == 0
    assert target.read_text(encoding="utf-8") == expected


def test_patch_ignores_empty_and_uncaptured(tmp_path):
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("", encoding="utf-8")
    assert nowin_codemod.patch(empty_file) == 0
    assert empty_file.read_text(encoding="utf-8") == ""

    uncaptured_file = tmp_path / "uncaptured.py"
    uncaptured_src = (
        "import subprocess\n"
        'subprocess.run(["echo", "hi"])\n'
        'subprocess.run(["echo", "ok"], creationflags=0, capture_output=True)\n'
    )
    uncaptured_file.write_text(uncaptured_src, encoding="utf-8")
    assert nowin_codemod.patch(uncaptured_file) == 0
    assert uncaptured_file.read_text(encoding="utf-8") == uncaptured_src


def test_patch_multiline_closing_paren_alone(tmp_path):
    target = tmp_path / "multiline.py"
    original = (
        "import subprocess\n"
        "subprocess.check_output(\n"
        '    ["echo", "hi"],\n'
        ")\n"
    )
    expected = (
        "import subprocess\n"
        "subprocess.check_output(\n"
        '    ["echo", "hi"],\n'
        '    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),\n'
        ")\n"
    )
    target.write_text(original, encoding="utf-8")

    assert nowin_codemod.patch(target) == 1
    assert target.read_text(encoding="utf-8") == expected
    assert nowin_codemod.patch(target) == 0


def test_patch_multiple_calls_same_line_and_trailing_comma(tmp_path):
    target = tmp_path / "same_line.py"
    original = (
        "import subprocess\n"
        'a = subprocess.check_output(["x"],); '
        'b = subprocess.Popen(["y"], stdout=subprocess.PIPE)\n'
    )
    expected = (
        "import subprocess\n"
        'a = subprocess.check_output(["x"], '
        'creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)); '
        'b = subprocess.Popen(["y"], stdout=subprocess.PIPE, '
        'creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))\n'
    )
    target.write_text(original, encoding="utf-8")

    assert nowin_codemod.patch(target) == 2
    assert target.read_text(encoding="utf-8") == expected
    assert nowin_codemod.patch(target) == 0


def test_patch_utf8_prefix_before_call(tmp_path):
    target = tmp_path / "utf8_case.py"
    original = (
        "import subprocess\n"
        'msg = "αβγ"; subprocess.run(["x"], stderr=subprocess.PIPE)\n'
    )
    expected = (
        "import subprocess\n"
        'msg = "αβγ"; subprocess.run(["x"], stderr=subprocess.PIPE, '
        'creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))\n'
    )
    target.write_text(original, encoding="utf-8")

    assert nowin_codemod.patch(target) == 1
    assert target.read_text(encoding="utf-8") == expected
