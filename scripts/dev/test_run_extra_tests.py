import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_extra_tests as rx

NL = chr(10)
PIPE = "        | "


def test_failure_detail_keeps_last_30_stdout_lines_indented():
    out = NL.join(f"line{i}" for i in range(100))
    rows = rx.failure_detail(out, "").split(NL)[1:]
    assert len(rows) == 30
    assert rows[0] == PIPE + "line70" and rows[-1] == PIPE + "line99"


def test_failure_detail_includes_stderr_tail_and_truncates_long_lines():
    d = rx.failure_detail("a", "b" * 500)
    assert d.endswith("b" * 300) and "b" * 301 not in d
    assert PIPE + "a" in d


def test_no_test_file_is_listed_twice():
    # 2026-10-16: two sessions registered the same ~70 s research test; every gate run (and both CI OSes) ran it twice
    dup = sorted({p for p in rx.EXTRA if rx.EXTRA.count(p) > 1})
    assert not dup, dup


def test_failure_detail_empty_output_is_empty():
    assert rx.failure_detail("", "") == ""
    assert rx.failure_detail(None, None) == ""
