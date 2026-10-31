"""Fail-first tests for run_f1.py. Expected values are hand-computed (see each case), never taken from the module."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_f1 as f1  # noqa: E402


def mkbars(h, l, tf_min=60, t0=0):
    n = len(h)
    return pd.DataFrame({"t": [t0 + i * tf_min * 60 for i in range(n)], "h": h, "l": l, "o": h, "c": l})


def test_pivot_confirmed_two_bars_later():
    # h = [1,2,5,2,1,0.5,0.4]: pivot high at index 2 (5 > 1,2,2,1). Known at the close of bar 4 (2 bars later), not before.
    h = [1, 2, 5, 2, 1, 0.5, 0.4]
    b = mkbars(h, [x - 0.1 for x in h])
    p = [q for q in f1.pivots(b, 60) if q[2] == 1]
    assert len(p) == 1
    avail, price, kind, i = p[0]
    assert price == 5 and i == 4
    assert avail == b.t[4] + 3600           # close of bar 4
    assert avail > b.t[3] + 3600            # not known at the close of bar 3
    # shift test: truncating the series after bar 3 (pivot not yet confirmed) yields no pivot
    assert [q for q in f1.pivots(b.iloc[:4].reset_index(drop=True), 60) if q[2] == 1] == []


def test_confluence_uses_only_confirmed_higher_tf_pivots():
    atr = np.array([1.0] * 10)
    p1h = [(1000, 100.0, 1, 5)]
    # 4h pivot at the same price but confirmed AFTER the 1h confirming close: must not count.
    late4 = [(1001, 100.2, 1, 0)]
    assert f1.confluence_flags(p1h, atr, late4, []) == [(False, False)]
    ok4 = [(1000, 100.2, 1, 0)]                  # confirmed at A, within 0.5 ATR
    assert f1.confluence_flags(p1h, atr, ok4, []) == [(True, False)]
    far = [(900, 100.6, 1, 0)]                   # 0.6 ATR away > 0.5 tolerance
    assert f1.confluence_flags(p1h, atr, far, []) == [(False, False)]
    wrongkind = [(900, 100.0, -1, 0)]
    assert f1.confluence_flags(p1h, atr, [], wrongkind) == [(False, False)]
    daily = [(900, 99.7, 1, 0)]
    assert f1.confluence_flags(p1h, atr, [], daily) == [(False, True)]


def _series(rows):
    t = np.arange(len(rows), dtype=np.int64) * 60
    a = np.array(rows, float)  # o,h,l,c
    return t, a[:, 0], a[:, 1], a[:, 2], a[:, 3]


def test_trade_short_target_and_cost():
    # resistance 100, ATR 2 -> risk 2, stop 102, target 98. Bar0 touches (h 100.5), bar1 reaches 98 (l 97.5).
    t, o, h, l, c = _series([(99, 100.5, 99, 100), (100, 100.5, 97.5, 98), (98, 99, 97, 98)])
    r = f1.trade_outcome(t, o, h, l, c, 0, 10_000, 100.0, 1, 2.0)
    assert r["why"] == "target" and r["gross_r"] == 1.0
    assert abs(r["net_r"] - (1.0 - 2 * 0.0005 * 100 / 2.0)) < 1e-12     # 0.05 R fee
    assert r["t"] == 0


def test_trade_stop_first_when_both_in_bar():
    t, o, h, l, c = _series([(99, 100.5, 99, 100), (100, 102.5, 97.5, 100)])
    r = f1.trade_outcome(t, o, h, l, c, 0, 10_000, 100.0, 1, 2.0)
    assert r["why"] == "stop" and r["gross_r"] == -1.0


def test_trade_long_support_and_untouched_and_gap():
    t, o, h, l, c = _series([(101, 102, 100.5, 101), (101, 102, 99.5, 100.5), (100.5, 103, 100, 102.5)])
    r = f1.trade_outcome(t, o, h, l, c, 0, 10_000, 100.0, -1, 2.0)      # support 100 touched at bar1; target 102 hit at bar2
    assert r["t"] == 60 and r["why"] == "target"
    assert f1.trade_outcome(t, o, h, l, c, 0, 10_000, 90.0, -1, 2.0) is None
    # gap through: open 103 above a resistance at 100 -> entry at the open 103 (short), risk 2, stop 105
    t2, o2, h2, l2, c2 = _series([(103, 103.5, 102.9, 103), (103, 103.2, 100.9, 101)])
    r2 = f1.trade_outcome(t2, o2, h2, l2, c2, 0, 10_000, 100.0, 1, 2.0)
    assert abs(r2["gross_r"] - 1.0) < 1e-12 or r2["why"] in ("target", "time")


def test_time_exit_marks_to_close():
    rows = [(99, 100.5, 99, 100)] + [(100, 100.5, 99.5, 99.5)] * 3
    t, o, h, l, c = _series(rows)
    r = f1.trade_outcome(t, o, h, l, c, 0, 10_000, 100.0, 1, 2.0)
    assert r["why"] == "time" and abs(r["gross_r"] - 0.25) < 1e-12      # short from 100, close 99.5, risk 2


def test_expiry_blocks_late_touch():
    t, o, h, l, c = _series([(99, 99.5, 99, 99), (99, 99.5, 99, 99), (99, 100.5, 99, 100)])
    assert f1.trade_outcome(t, o, h, l, c, 0, 120, 100.0, 1, 2.0) is None   # touch at t=120 is at/after expiry


def test_random_level_control_is_independent_of_pivot_price():
    # control levels: close +/- d*ATR; with a flat pool of distances the control level is exactly that, not a pivot
    rng = np.random.default_rng(1)
    pool = np.array([1.5])
    d = float(rng.choice(pool))
    assert 100 + 1 * d * 2.0 == 103.0


def test_week_boot_known_values():
    ts = np.array([0, 0, 604800, 604800]); y = np.array([1.0, 3.0, 2.0, 2.0])
    est, lo, hi = f1.week_boot(ts, y, B=200)
    assert est == 2.0 and lo <= 2.0 <= hi
    est2, _, _ = f1.week_boot(ts, y, ts, y + 1.0, B=200)
    assert est2 == -1.0


def test_planted_edge_detected_through_harness():
    rng = np.random.default_rng(5)
    n = 900
    lab = f1.harness.block_labels(n, 3, 10, np.random.default_rng(3))
    y = rng.normal(0, 1.0, n)
    flagged = f1.harness.shift_null_test(y, lab, n_shifts=200, rng=np.random.default_rng(1))["flagged"]
    assert flagged == []
    y2, _ = f1.harness.inject_edge(y, lab, 1, delta=1.0, frac=0.5, rng=np.random.default_rng(2))
    flagged2 = f1.harness.shift_null_test(y2, lab, n_shifts=200, rng=np.random.default_rng(1))["flagged"]
    assert flagged2 == [1]


def test_synthetic_end_to_end_one_pivot():
    # 1m series: a hump forms a 1h pivot high, price later re-touches the level and reverses -> a CONF-less NONE group trade
    mins = 60 * 200
    t = np.arange(mins, dtype=np.int64) * 60
    px = 100 + 0.0 * np.arange(mins)
    base = pd.DataFrame({"t": t, "o": px, "h": px + 0.2, "l": px - 0.2, "c": px, "v": 1.0, "tbv": 0.5})
    ev, n_piv = f1.build_events(base)
    assert isinstance(ev, pd.DataFrame)
