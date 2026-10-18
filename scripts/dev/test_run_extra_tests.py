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


def test_study_folder_tests_are_discovered_without_an_entry(tmp_path):
    import subprocess
    (tmp_path / "scripts" / "dev").mkdir(parents=True)
    (tmp_path / "scripts" / "dev" / "run_all_tests.py").write_text('"test_named"' + NL, encoding="utf-8")
    for rel in ("MyTradingSys/research/s1/test_new.py", "MyTradingSys/research/s1/test_named.py",
                "MyTradingSys/research/archive/test_old.py", "MyTradingSys/backtest/test_elsewhere.py"):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("def test_x():" + NL + "    pass" + NL, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    assert rx.discovered(tmp_path) == ["MyTradingSys/research/s1/test_new.py"]


def test_failure_detail_empty_output_is_empty():
    assert rx.failure_detail("", "") == ""
    assert rx.failure_detail(None, None) == ""
