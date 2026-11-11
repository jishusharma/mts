import json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pytest
import log_trade as L

GOOD = json.loads((Path(__file__).parent / "template.jsonl").read_text().splitlines()[0])


def test_repo_path_refused(monkeypatch):
    p = L.REPO_ROOT / "MyTradingSys" / "runtime" / "j.jsonl"
    with pytest.raises(SystemExit, match="REFUSED"):
        L.append_row(GOOD, str(p))
    assert not p.exists()
    monkeypatch.setenv("MTS_TRADE_JOURNAL", str(p))
    assert L.main(["--check-path"]) == 2


def test_nested_git_repo_refused(tmp_path):
    (tmp_path / ".git").mkdir()
    with pytest.raises(SystemExit, match="REFUSED"):
        L.append_row(GOOD, str(tmp_path / "x" / "j.jsonl"))


def test_valid_row_validates_and_appends(tmp_path):
    assert L.validate(GOOD) == []
    out = tmp_path / "j.jsonl"
    L.append_row(GOOD, str(out))
    L.append_row(GOOD, str(out))
    assert len(out.read_text().splitlines()) == 2


def test_missing_readings_rejected(tmp_path):
    bad = {k: v for k, v in GOOD.items() if k != "readings_entry"}
    assert L.validate(bad)
    assert L.validate(dict(GOOD, readings_entry={"home": 1}))
    with pytest.raises(SystemExit, match="REJECTED"):
        L.append_row(bad, str(tmp_path / "j.jsonl"))
    assert not (tmp_path / "j.jsonl").exists()


def test_bad_side_and_reading_value():
    assert L.validate(dict(GOOD, side="UP"))
    assert L.validate(dict(GOOD, readings_entry=dict(GOOD["readings_entry"], home=2)))


def test_cli_logs_one_line(tmp_path):
    out = tmp_path / "j.jsonl"
    env = dict(os.environ, MTS_TRADE_JOURNAL=str(out))
    r = subprocess.run([sys.executable, str(Path(L.__file__)), "--symbol", "BTCUSDT", "--side", "LONG", "--entry", "100",
                        "--stop", "98", "--reason", "t", "--readings-entry", "home=1,grid=0,adx15=1,adx1h=0,vfi15=1,wt30=1"],
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert json.loads(out.read_text())["symbol"] == "BTCUSDT"


def test_template_is_one_example_row():
    rows = (Path(__file__).parent / "template.jsonl").read_text().splitlines()
    assert len(rows) == 1 and json.loads(rows[0])["id"] == "EXAMPLE"
