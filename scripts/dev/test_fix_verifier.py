import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fix_verifier as V

LOG = (V.SEP + "aaaaaaaaaaaa" + V.FIELD + "Fix x" + V.FIELD + "Body\n\nResult: x works. Test: scripts/dev/test_x.py\n"
       + V.SEP + "bbbbbbbbbbbb" + V.FIELD + "No result line" + V.FIELD + "just text\n"
       + V.SEP + "cccccccccccc" + V.FIELD + "Fix y" + V.FIELD + "Result: y ok\n")


def test_only_commits_with_result_line_listed():
    cs = V.parse_log(LOG)
    assert [c["sha"] for c in cs] == ["aaaaaaaaa", "ccccccccc"]


def test_verified_when_named_test_passes_and_cannot_when_fails_or_unnamed(tmp_path):
    (tmp_path / "scripts" / "dev").mkdir(parents=True)
    (tmp_path / "scripts" / "dev" / "test_x.py").write_text("x")
    a, c = V.parse_log(LOG)
    assert V.verify(a, tmp_path, runner=lambda p: (True, ""))[0] == "VERIFIED"
    st, why = V.verify(a, tmp_path, runner=lambda p: (False, "1 failed"))
    assert st == "CANNOT-VERIFY" and "fails" in why
    assert V.verify(c, tmp_path) == ("CANNOT-VERIFY", "no test file named in commit or card")
    assert "not on disk" in V.verify(a, tmp_path / "empty")[1]
    assert "not run" in V.verify(a, tmp_path, run=False)[1]


def test_card_named_test_is_found(tmp_path):
    d = tmp_path / "MyTradingSys" / "system" / "tasks"
    d.mkdir(parents=True)
    (d / "k.json").write_text('{"tests": "tests/test_k.py"}')
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_k.py").write_text("x")
    c = {"sha": "s", "subject": "s", "result": "r", "body": "Result: r\ncard MyTradingSys/system/tasks/k.json"}
    assert V.verify(c, tmp_path, runner=lambda p: (True, ""))== ("VERIFIED", "tests/test_k.py")


def test_real_pytest_runner_passes_and_fails(tmp_path):
    (tmp_path / "test_ok.py").write_text("def test_a():\n    assert True\n")
    (tmp_path / "test_bad.py").write_text("def test_a():\n    assert False\n")
    assert V._pytest("test_ok.py", tmp_path)[0] is True
    assert V._pytest("test_bad.py", tmp_path)[0] is False


def test_table_one_row_per_fix():
    cs = V.parse_log(LOG)
    t = V.table([(cs[0], "VERIFIED", "p"), (cs[1], "CANNOT-VERIFY", "no")])
    assert t.count("\n") == 3 and "VERIFIED" in t
