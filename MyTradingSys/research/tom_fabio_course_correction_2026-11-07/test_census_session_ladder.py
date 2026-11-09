"""Tests for census_session_ladder.py (card census-5m-15m-7y-session-ladder-1109). Expected numbers hand-computed."""
import datetime as dt
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("csl", HERE / "census_session_ladder.py")
csl = importlib.util.module_from_spec(_s)
_s.loader.exec_module(csl)


def _b(h, l, c):
    return {"h": h, "l": l, "c": c}


def test_long_node_target_model_d_fee():
    # entry 100, stop 99 (dist 1, 100 bps), T1 102 (2R). Bar hits 102: one target leg, gross +2.
    legs = csl.run_trade(1, 100.0, 99.0, [_b(102.5, 100.0, 102.0)], "NODE", t1=102.0)
    assert legs == [(1.0, 102.0, "target")]
    g, nt, nd, kind = csl.score(1, 100.0, 99.0, legs)
    # model T: (5 entry + 5 exit + 2 slip) / 100 bps = 0.12 R; model D: (0 + 0 + 2) / 100 = 0.02 R
    assert g == pytest.approx(2.0) and nt == pytest.approx(1.88) and nd == pytest.approx(1.98) and kind == "target"


def test_stop_wins_tie_and_pays_taker_exit_in_model_d():
    legs = csl.run_trade(1, 100.0, 99.0, [_b(103.0, 98.9, 100.0)], "NODE", t1=102.0)
    assert legs == [(1.0, 99.0, "stop")]
    g, nt, nd, _ = csl.score(1, 100.0, 99.0, legs)
    assert g == -1.0 and nd == pytest.approx(-1.0 - 0.07) and nt == pytest.approx(-1.0 - 0.12)


def test_break_even_moves_only_after_the_bar_that_earned_it():
    # bar1 trades +1R (high 101) and its low 99.5 must NOT stop at entry yet; bar2 pulls back to 99.9 -> BE stop at 100
    legs = csl.run_trade(1, 100.0, 99.0, [_b(101.0, 99.5, 100.5), _b(100.6, 99.9, 100.0)], "NODE_BE", t1=105.0)
    assert legs == [(1.0, 100.0, "stop")]
    g, _, nd, _ = csl.score(1, 100.0, 99.0, legs)
    assert g == pytest.approx(0.0) and nd == pytest.approx(-0.07)


def test_half_off_at_t1_then_be_on_the_rest_short():
    # short entry 100, stop 101 (dist 1), T1 98 (2R), T2 96. bar1 hits 98 -> half off at +2R, stop to 100.
    # bar2 low 97 (no T2, T2 needs a later bar than T1 anyway), bar3 high 100.2 -> BE stop on the other half.
    fut = [_b(100.2, 97.9, 98.5), _b(99.0, 97.0, 98.0), _b(100.2, 98.0, 99.0)]
    legs = csl.run_trade(-1, 100.0, 101.0, fut, "HALF_BE", t1=98.0, t2=96.0)
    assert legs == [(0.5, 98.0, "target"), (0.5, 100.0, "stop")]
    g, _, nd, _ = csl.score(-1, 100.0, 101.0, legs)
    assert g == pytest.approx(1.0) and nd == pytest.approx(1.0 - (0.5 * 5 + 2) / 100)


def test_trail_follows_best_price_by_one_r():
    # long entry 100 stop 99; bar1 high 103 -> BE earned, trail = 103 - 1 = 102 from bar2; bar2 low 101.9 stops at 102
    legs = csl.run_trade(1, 100.0, 99.0, [_b(103.0, 100.0, 102.5), _b(102.4, 101.9, 102.0)], "TRAIL")
    assert legs == [(1.0, 102.0, "stop")]


def test_node_variant_without_node_is_skipped_but_1r_runs():
    assert csl.run_trade(1, 100.0, 99.0, [_b(101.5, 99.5, 101.0)], "NODE", t1=None) is None
    assert csl.run_trade(1, 100.0, 99.0, [_b(101.5, 99.5, 101.0)], "B1R") == [(1.0, 101.0, "target")]


def test_session_blocks_are_dst_aware():
    # 2026-07-01 13:30 UTC = 09:30 New York (EDT) -> NY; 2026-01-05 13:30 UTC = 08:30 EST -> OTHER, 14:30 UTC -> NY
    ms = lambda y, m, d, hh, mm: int(dt.datetime(y, m, d, hh, mm, tzinfo=dt.UTC).timestamp() * 1000)
    assert csl.session_of(ms(2026, 7, 1, 13, 30)) == "NY"
    assert csl.session_of(ms(2026, 1, 5, 13, 30)) == "OTHER"
    assert csl.session_of(ms(2026, 1, 5, 14, 30)) == "NY"
    assert csl.session_of(ms(2026, 1, 5, 8, 30)) == "LON"      # 09:30 CET
    assert csl.session_of(ms(2026, 1, 3, 8, 30)) == "OTHER"    # Saturday
