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


# ---- census-5m-15m-7y-session-ladder-1109 -------------------------------------------------------------------------
def _ev(hour, direction, bias, verdict="FAST_REJECTION"):
    t = int(dt.datetime(2024, 3, 5, hour, 0, tzinfo=dt.UTC).timestamp() * 1000)
    return {"t": t, "dir": direction, "verdict": verdict, "ladder": bias, "session": ax.session_of(t)}


def test_session_block_and_ladder_gate():
    # a 5m event outside london/ny, or against the ladder, is excluded by the session+ladder gate
    asia_with = _ev(3, -1, "bearish")
    ny_against = _ev(15, 1, "bearish")
    ny_with = _ev(15, -1, "rally_in_macro_bear")
    london_neutral = _ev(9, 1, "neutral")
    evs = [asia_with, ny_against, ny_with, london_neutral]
    assert ax.gated(evs, "session+ladder") == [ny_with]
    assert ax.gated(evs, "session") == [ny_against, ny_with, london_neutral]
    assert ax.gated(evs, "ladder") == [asia_with, ny_with]
    assert ax.gated(evs, "none") == evs


def test_node_exit_be_and_half_at_poc():
    # long entry 100, stop 99 (1R = 1). Nodes 100.8 (too close, < 1R) and 103; POC 101.5 -> half off there.
    # bar 1 tags POC (+1.5R on half) and +1R (BE). bar 2 comes back to 100: BE stop, 0 R on the rest.
    fut = [_b(101.6, 100.2, 101.4), _b(101.0, 99.9, 100.1)]
    r = ax.simulate_node(1, 100.0, 99.0, fut, 32, [100.8, 103.0], 101.5)
    assert r["exit"] == "stop" and r["be"] and r["part"]
    assert r["gross_r"] == pytest.approx(0.75) and r["target_r"] == pytest.approx(3.0)
    assert ax.simulate_node(1, 100.0, 99.0, fut, 32, [100.8], None) is None   # no node >= 1R: no trade


def test_ladder_map_uses_only_closed_days():
    days = [{"t": ax.ms(2024, 1, 1) + k * 86400000, "o": 100 + k, "h": 101 + k, "l": 99 + k, "c": 100.5 + k, "v": 1.0}
            for k in range(60)]
    m1 = ax.ladder_map(days)
    days2 = [dict(d) for d in days]
    days2[45]["c"], days2[45]["h"], days2[45]["l"] = 10.0, 101 + 45, 9.0          # crash on day 45
    m2 = ax.ladder_map(days2)
    d45 = ax.day_of(days[45]["t"])
    assert all(m1[d] == m2[d] for d in m1 if d <= d45)                          # day 45's own bar never leaks into its bias
