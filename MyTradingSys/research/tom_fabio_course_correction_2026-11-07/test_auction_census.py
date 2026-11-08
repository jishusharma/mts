"""Tests for auction_census.py (card auction-context-event-census-1108). Expected numbers hand-computed."""
import datetime as dt
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("auction_census", HERE / "auction_census.py")
ax = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ax)


def _b(h, l, c):
    return {"h": h, "l": l, "c": c}


def test_long_target_fee_net():
    # entry 100, stop 99 (dist 1 -> 100 bps of price), target 101. Bar 2 high 101.2 hits target. fee_r = 10 bps / 100 bps = 0.10
    r = ax.simulate(1, 100.0, 99.0, [_b(100.5, 99.5, 100.2), _b(101.2, 100.0, 101.0)], 24, rt_bps=10.0)
    assert r["outcome"] == "target" and r["gross_r"] == 1.0
    assert r["fee_r"] == pytest.approx(0.10) and r["net_r"] == pytest.approx(0.90)


def test_stop_wins_same_bar_tie_and_costs_fee():
    r = ax.simulate(1, 100.0, 99.0, [_b(101.5, 98.9, 100.0)], 24, rt_bps=10.0)
    assert r["outcome"] == "stop" and r["net_r"] == pytest.approx(-1.10)


def test_short_and_open_mark_to_market():
    # short entry 100, stop 101, nothing hit, last close 99.5 -> +0.5 R gross, fee 0.10
    r = ax.simulate(-1, 100.0, 101.0, [_b(100.4, 99.4, 99.5)], 24, rt_bps=10.0)
    assert r["outcome"] == "open" and r["gross_r"] == pytest.approx(0.5) and r["net_r"] == pytest.approx(0.4)


def test_wrong_side_stop_is_rejected():
    assert ax.simulate(1, 100.0, 100.5, [_b(101, 99, 100)], 24) is None


def test_fee_gate_tight_stop_flagged():
    # stop 5 bps away: fee_r = 10/5 = 2.0 R > gate
    r = ax.simulate(1, 100.0, 99.95, [_b(100.1, 99.99, 100.05)], 24, rt_bps=10.0)
    assert r["fee_r"] == pytest.approx(2.0) and r["fee_r"] > ax.MAX_FEE_R


def test_stats_gate_split():
    ok = {"sim": {"outcome": "target", "gross_r": 1.0, "fee_r": 0.1, "net_r": 0.9}}
    bad = {"sim": {"outcome": "stop", "gross_r": -1.0, "fee_r": 2.0, "net_r": -3.0}}
    s = ax.stats([ok, bad, {"sim": None}])
    assert s["n"] == 2 and s["gate"]["n"] == 1 and s["gate"]["net"] == pytest.approx(0.9) and s["all"]["net"] == pytest.approx(-1.05)


def test_daily_bias_known_next_day():
    day = lambda i: {"t": int(dt.datetime(2026, 1, 1, tzinfo=dt.UTC).timestamp() * 1000) + i * 86400000, "c": 100.0 + i}
    m = ax.daily_bias([day(i) for i in range(25)])
    d0 = dt.date(2026, 1, 1)
    assert d0 + dt.timedelta(days=19 + 1) in m and d0 + dt.timedelta(days=19) not in m
    assert m[d0 + dt.timedelta(days=25)][0] == "bull"
