"""Core-rule tests for study.py (setup detection, stop-first, net R, DST window)."""
import sys
import datetime as dt
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study  # noqa: E402


def test_setup_needs_two_consecutive_inside_closes():
    assert study.find_setup([False, True, False, True, True], skip=False) == 4
    assert study.find_setup([False, True, False, True], skip=False) is None


def test_skip_first30_ignores_block_zero():
    # blocks 0 and 1 inside: valid without skip, not with skip (pair must start at block >= 1)
    assert study.find_setup([True, True, False, False], skip=False) == 1
    assert study.find_setup([True, True, False, False], skip=True) is None
    assert study.find_setup([False, True, True], skip=True) == 2


def test_stop_first_when_bar_touches_both():
    H = np.array([100.0, 100.0, 103.0]); L = np.array([100.0, 100.0, 90.0]); C = np.array([100.0, 100.0, 95.0])
    # short entered at bar 0: stop 102, target 91: bar 2 touches both -> stop
    ex, kind, reach_any, reach_bs = study.sim_trade(-1, 0, 91.0, 102.0, H, L, C)
    assert kind == "stop" and ex == 102.0 and reach_any is True and reach_bs is False


def test_target_and_time_exit_and_net_r():
    H = np.array([100.0, 100.5, 100.2]); L = np.array([100.0, 99.0, 98.0]); C = np.array([100.0, 99.5, 98.5])
    ex, kind, ra, rb = study.sim_trade(-1, 0, 98.5, 101.0, H, L, C)
    assert kind == "target" and ex == 98.5 and ra and rb
    r = study.net_r(-1, 100.0, 98.5, 101.0)       # gross +1.5 / risk 1.0 = 1.5, minus cost/risk
    assert abs(r - (0.015 - study.COST_RT) / 0.01) < 1e-9
    ex, kind, _, _ = study.sim_trade(1, 0, 110.0, 90.0, H, L, C)
    assert kind == "time" and ex == 98.5


def test_ny_window_dst_rule():
    s, e = study.ac.ny_session_window(dt.date(2024, 7, 10))
    assert (e - s) == 390 * 60_000 and dt.datetime.fromtimestamp(s / 1000, dt.timezone.utc).hour == 13
    s, e = study.ac.ny_session_window(dt.date(2024, 12, 10))
    assert dt.datetime.fromtimestamp(s / 1000, dt.timezone.utc).hour == 14


def test_bh_selects_small_p():
    assert list(study.bh(np.array([0.001, 0.5, 0.9]), 0.10)) == [True, False, False]
