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


def test_extra_is_loaded_from_the_tsv_data_file():
    # a registration must be a smoke-gate data edit (extra_tests.tsv), not an edit of run_extra_tests.py (full gate, 570-690 s)
    tsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra_tests.tsv")
    lines = [ln.strip() for ln in open(tsv, encoding="utf-8").read().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    assert lines and rx.EXTRA == lines
    assert len(set(lines)) == len(lines)


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


def test_only_picks_the_named_subset_in_list_order_and_refuses_a_typo():
    # GATE_SPEED D6: the smoke gate runs `run_extra_tests.py --only <subset>`
    tests = ["a/test_1.py", "b/test_2.py", "c/test_3.py"]
    assert rx.pick([], tests) == tests
    assert rx.pick(["--only", "c/test_3.py", "a/test_1.py"], tests) == ["a/test_1.py", "c/test_3.py"]
    assert rx.pick(["--only"], tests) == []
    try:
        rx.pick(["--only", "a/test_9.py"], tests)
    except SystemExit as e:
        assert "a/test_9.py" in str(e)
    else:
        raise AssertionError("a name that is not an extra test must stop the step")


def test_child_env_lets_a_test_in_a_subfolder_import_a_repo_root_package(tmp_path, monkeypatch):
    # 2026-11-05: a test run from its own folder failed with ModuleNotFoundError: No module named 'MyTradingSys'
    (tmp_path / "rootpkg").mkdir()
    (tmp_path / "rootpkg" / "__init__.py").write_text("VALUE = 7" + NL, encoding="utf-8", newline=NL)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "test_imp.py").write_text("from rootpkg import VALUE" + NL + "def test_it():" + NL + "    assert VALUE == 7" + NL,
                                                  encoding="utf-8", newline=NL)
    monkeypatch.setattr(rx, "REPO", tmp_path)
    monkeypatch.setenv("PYTHONPATH", "keepfirst")
    assert rx.child_env()["PYTHONPATH"] == os.pathsep.join(["keepfirst", str(tmp_path)])
    ok, tail = rx.run_one("sub/test_imp.py", tmp_path / "bt")
    assert ok, tail


def test_a_hung_file_is_killed_at_the_timeout_and_fails(tmp_path, monkeypatch):
    (tmp_path / "test_hang.py").write_text("import time" + NL + "def test_h():" + NL + "    time.sleep(60)" + NL, encoding="utf-8", newline=NL)
    monkeypatch.setattr(rx, "REPO", tmp_path)
    ok, tail = rx.run_one("test_hang.py", tmp_path / "bt", timeout=3)
    assert not ok and "timed out after 3s" in tail


def test_a_child_that_dies_with_no_output_is_run_once_more(tmp_path, monkeypatch):
    mark = tmp_path / "mark"
    src = NL.join(["import os", f"m = {str(mark)!r}", "if not os.path.exists(m):", "    open(m, 'w').close()", "    os._exit(3)", ""])
    (tmp_path / "conftest.py").write_text(src, encoding="utf-8", newline=NL)
    (tmp_path / "test_ok.py").write_text("def test_a():" + NL + "    pass" + NL, encoding="utf-8", newline=NL)
    monkeypatch.setattr(rx, "REPO", tmp_path)
    ok, tail = rx.run_one("test_ok.py", tmp_path / "bt")
    assert ok and "1 passed" in tail



def test_slowest_first_keeps_every_file_once_and_leads_with_the_slow_ones():
    rels = ["a.py", "scripts/dev/test_lab_query.py", "b.py", "scripts/dev/test_planted_error_trial.py"]
    out = rx.slowest_first(rels)
    assert sorted(out) == sorted(rels)
    assert out[:2] == ["scripts/dev/test_planted_error_trial.py", "scripts/dev/test_lab_query.py"]
    assert out[2:] == ["a.py", "b.py"]


def test_every_slow_first_file_is_a_registered_extra_test():
    assert set(rx.SLOW_FIRST) <= set(rx.EXTRA)


def test_default_jobs_never_below_the_old_four_and_capped(monkeypatch):
    monkeypatch.delenv("MTS_GATE_JOBS", raising=False)
    assert [rx.jobs(c) for c in (1, 2, 4, 8, 12, 32)] == [1, 2, 4, 4, 6, 8]
    monkeypatch.setenv("MTS_GATE_JOBS", "3")
    assert rx.jobs(12) == 3


def _mk(tmp_path, name, body):
    (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / name).write_text(body + NL, encoding="utf-8", newline=NL)


def test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single():
    slow = "scripts/dev/test_planted_error_trial.py"
    rels = ["a/test_1.py", slow, "a/test_2.py", "b/test_3.py", "a/test_4.py"]
    units = rx.plan_units(rels, group_max=2)
    assert units[0] == ("one", slow)
    assert ("group", "a", ["a/test_1.py", "a/test_2.py"]) in units
    assert ("one", "a/test_4.py") in units and ("one", "b/test_3.py") in units
    flat = [u[1] if u[0] == "one" else None for u in units]
    assert sorted(r for u in units for r in ([u[1]] if u[0] == "one" else u[2])) == sorted(rels)


def test_run_group_green_files_run_in_one_process(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "REPO", tmp_path)
    for n in ("t1", "t2", "t3"):
        _mk(tmp_path, f"d/test_{n}.py", "def test_a():\n    pass")
    calls = []
    real = rx.subprocess.run
    monkeypatch.setattr(rx.subprocess, "run", lambda *a, **k: (calls.append(a[0]), real(*a, **k))[1])
    res = rx.run_group([f"d/test_{n}.py" for n in ("t1", "t2", "t3")], tmp_path / "bt")
    assert len(calls) == 1 and all(ok for ok, _ in res.values()), res


def test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "REPO", tmp_path)
    _mk(tmp_path, "d/test_good.py", "def test_a():\n    pass")
    _mk(tmp_path, "d/test_bad.py", "def test_b():\n    assert 0")
    bad = rx.run_files(["d/test_good.py", "d/test_bad.py"], 2, tmp=str(tmp_path / "bt"), many=rx.run_group)
    assert bad == ["d/test_bad.py"]


def test_run_group_a_file_with_no_tests_fails_like_alone(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "REPO", tmp_path)
    _mk(tmp_path, "d/test_ok.py", "def test_a():\n    pass")
    _mk(tmp_path, "d/test_empty.py", "X = 1")
    bad = rx.run_files(["d/test_ok.py", "d/test_empty.py"], 2, tmp=str(tmp_path / "bt"), many=rx.run_group)
    assert bad == ["d/test_empty.py"]


def test_run_group_timeout_falls_back_to_per_file_with_the_same_ceiling(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "REPO", tmp_path)
    _mk(tmp_path, "d/test_fast.py", "def test_a():\n    pass")
    _mk(tmp_path, "d/test_hang.py", "import time\ndef test_h():\n    time.sleep(60)")
    res = rx.run_group(["d/test_fast.py", "d/test_hang.py"], tmp_path / "bt", timeout=4)
    assert res["d/test_fast.py"][0] and not res["d/test_hang.py"][0] and "timed out after 4s" in res["d/test_hang.py"][1]


def test_a_crashing_group_runner_falls_back_to_the_per_file_run(tmp_path):
    def boom(rels, bt):
        raise RuntimeError("x")
    seen = []
    bad = rx.run_files(["d/test_1.py", "d/test_2.py"], 2, one=lambda rel, bt: (seen.append(rel) or rel.endswith("1.py"), "t"),
                       tmp=str(tmp_path), many=boom)
    assert sorted(seen) == ["d/test_1.py", "d/test_2.py"] and bad == ["d/test_2.py"]
