"""Tests for run_dev.py guard, loader and net R (card kurisko-dev-event-study). Expected values are hand-derived."""
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_dev as rd  # noqa: E402

FROZEN = "# PRE_REG\nFrozen: 5m:stoch:long, 5m:stoch:short\n"


def test_guard_refuses_changed_cell(tmp_path):
    with pytest.raises(rd.GuardError, match="differ from the frozen"):
        rd.guard(FROZEN, ["5m:stoch:long", "15m:stoch:long"], "abc", tmp_path / "r.json")


def test_guard_accepts_the_frozen_list(tmp_path):
    assert rd.guard(FROZEN, [], "abc", tmp_path / "r.json") == ["5m:stoch:long", "5m:stoch:short"]


def test_guard_refuses_changed_data_sha(tmp_path):
    f = tmp_path / "BTCUSDT-1m-2022-01.csv"
    f.write_bytes(b"1,2,3,4,5\n")
    good = hashlib.sha256(b"1,2,3,4,5\n").hexdigest()
    rd.guard(FROZEN, [], "abc", tmp_path / "r.json", [f], {f.name: good})
    with pytest.raises(rd.GuardError, match="data sha"):
        rd.guard(FROZEN, [], "abc", tmp_path / "r.json", [f], {f.name: "0" * 64})


def test_guard_refuses_second_run(tmp_path):
    r = tmp_path / "run_receipt.json"
    r.write_text("{}", encoding="utf-8")
    with pytest.raises(rd.GuardError, match="one run"):
        rd.guard(FROZEN, [], "abc", r)


def test_guard_refuses_uncommitted_pre_reg(tmp_path):
    with pytest.raises(rd.GuardError, match="not committed"):
        rd.guard(FROZEN, [], None, tmp_path / "r.json")


def test_guard_refuses_zero_frozen(tmp_path):
    with pytest.raises(rd.GuardError, match="0 cells"):
        rd.guard("**Frozen cells: 0 of 8 candidates.**", [], "abc", tmp_path / "r.json")


def test_loader_refuses_bars_after_dev(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("1719792000000,1,2,0.5,1.5,10\n", encoding="utf-8")   # 2024-07-01T00:00Z
    with pytest.raises(ValueError, match="2024-07-01"):
        rd.load_dev([f], check_sha=False)
    f.write_text("1719791940000,1,2,0.5,1.5,10\n", encoding="utf-8")   # 2024-06-30T23:59Z
    assert rd.load_dev([f], check_sha=False) == [(1719791940000, 2.0, 0.5, 1.5)]


def test_net_r_formulas13_hand_value():
    # FORMULAS 13 worked example: long 100 -> 101, fee 0.0010 + slip 0.0002, funding 0.0001 + 0.0003:
    # net = 0.01 - 0.0012 - 0.0004 = 0.0084; stop 0.5 % of entry -> 0.0084 / 0.005 = 1.68 R.
    assert rd.net_r("long", 100, 101, 0.005, 0.0012, [0.0001, 0.0003]) == pytest.approx(1.68)
    # short 100 -> 99 same records: net = 0.01 - 0.0012 + 0.0004 = 0.0092 -> 1.84 R
    assert rd.net_r("short", 100, 99, 0.005, 0.0012, [0.0001, 0.0003]) == pytest.approx(1.84)
