"""Hand-fixture tests of the PRE_REG trade simulator in study.py (no market data, CI-safe).

Every expected number is computed by hand from PRE_REG s.1-2, not from study.py:
  net_R = (sgn*(exit-entry) - 0.0007*entry - 0.0007*exit - sgn*fund_sum*entry) / R, R = |entry - stop|, target = entry +- 2 R,
  stop first when one 1m bar holds both, a bar that opens beyond the stop fills at its open, time stop at the close of the
  1m bar ending entry + 24 h (= the 1440th bar from the entry bar), entry = open of the 1m bar opening at T + 60 s.
`test_planted_bug_is_caught` re-runs the same fixture on four deliberately broken simulators (target first, no gap fill,
24 h + 1 bar, funding sign not flipped for a short); every one must fail at least one fixture check.
`STUDY_UNDER_TEST=<path>` points the whole file at another copy of study.py (used once to record a planted-bug failure).
"""
import importlib.util
import os
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent


def _load():
    p = Path(os.environ.get("STUDY_UNDER_TEST", HERE / "study.py"))
    spec = importlib.util.spec_from_file_location("study_under_test", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = _load()


def bars(rows):
    a = np.array(rows, float)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3]      # o, h, l, c


def flat(n, px=100.0):
    return [(px, px + 0.2, px - 0.2, px)] * n


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- fixture checks, parameterised by the simulator under test
def chk_target(sim, settle):
    o, h, l, c = bars([(100, 100.5, 99.5, 100.2), (100.2, 102.5, 100.1, 102.0)])
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "target" and t["idx"] == 1 and close(t["exit"], 102.0), t
    assert close(settle("long", t["entry"], 99.0, t["exit"], 0.0)[0], 2 - 0.07 - 0.0714)          # 1.8586


def chk_stop_first_long(sim, settle):
    o, h, l, c = bars([(100, 103, 98.5, 101)])         # one bar holds the stop (<= 99) and the target (>= 102)
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "stop" and t["idx"] == 0 and close(t["exit"], 99.0), t
    assert close(settle("long", t["entry"], 99.0, t["exit"], 0.0)[0], -1 - 0.07 - 0.0693)         # -1.1393


def chk_stop_first_short(sim, settle):
    o, h, l, c = bars([(100, 101.5, 97.0, 99)])        # holds the short stop (>= 101) and the target (<= 98)
    t = sim("short", 101.0, o, h, l, c)
    assert t["kind"] == "stop" and close(t["exit"], 101.0), t
    assert close(settle("short", t["entry"], 101.0, t["exit"], 0.0)[0], -1 - 0.07 - 0.0707)       # -1.1407


def chk_gap_long(sim, settle):
    o, h, l, c = bars([(100, 100.4, 99.6, 100.1), (98.0, 98.5, 97.0, 97.5)])      # bar 1 opens below the stop 99
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "stop" and t["idx"] == 1 and close(t["exit"], 98.0), t         # fill at the open, not at 99
    assert close(settle("long", t["entry"], 99.0, t["exit"], 0.0)[0], -2 - 0.07 - 0.0686)         # -2.1386


def chk_gap_short(sim, settle):
    o, h, l, c = bars([(100, 100.4, 99.6, 99.9), (102.0, 103.0, 101.5, 102.5)])   # bar 1 opens above the short stop 101
    t = sim("short", 101.0, o, h, l, c)
    assert t["kind"] == "stop" and t["idx"] == 1 and close(t["exit"], 102.0), t
    assert close(settle("short", t["entry"], 101.0, t["exit"], 0.0)[0], -2 - 0.07 - 0.0714)       # -2.1414


def chk_target_short(sim, settle):
    o, h, l, c = bars([(100, 100.2, 99.0, 99.2), (99.2, 99.3, 97.9, 98.5)])
    t = sim("short", 101.0, o, h, l, c)
    assert t["kind"] == "target" and t["idx"] == 1 and close(t["exit"], 98.0), t
    assert close(settle("short", t["entry"], 101.0, t["exit"], 0.0)[0], 2 - 0.07 - 0.0686)        # 1.8614


def chk_target_gap_fills_at_target(sim, settle):
    o, h, l, c = bars([(100, 100.2, 99.8, 100), (103.0, 104.0, 102.5, 103.5)])    # opens above the 102 target
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "target" and close(t["exit"], 102.0), t                            # PRE_REG: target price, not the open


def chk_entry_bar_can_stop(sim, settle):
    o, h, l, c = bars([(100, 100.1, 98.9, 99.5)])
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "stop" and t["idx"] == 0 and close(t["exit"], 99.0), t


def chk_time_stop(sim, settle):
    rows = flat(1440)
    rows[1439] = (100.0, 100.9, 99.9, 100.8)            # last bar of the 24 h window closes at 100.8, inside stop/target
    rows += [(100.8, 100.9, 90.0, 91.0)]                # bar 1441 would hit the stop: it is outside the window
    o, h, l, c = bars(rows)
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "time" and t["idx"] == 1439 and close(t["exit"], 100.8) and not t["cut"], t
    assert close(settle("long", t["entry"], 99.0, t["exit"], 0.0)[0], 0.8 - 0.07 - 0.07056)       # 0.65944


def chk_stop_on_last_window_bar(sim, settle):
    rows = flat(1440)
    rows[1439] = (100.0, 100.0, 98.0, 98.5)             # the 1440th bar still counts
    o, h, l, c = bars(rows)
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "stop" and t["idx"] == 1439 and close(t["exit"], 99.0), t


def chk_cut_window(sim, settle):
    o, h, l, c = bars(flat(300) + [(100.0, 100.3, 99.9, 100.25)])
    t = sim("long", 99.0, o, h, l, c)
    assert t["kind"] == "time" and t["cut"] is True and close(t["exit"], 100.25) and t["idx"] == 300, t


def chk_entry_beyond_stop(sim, settle):
    assert sim("long", 99.0, *bars([(98.5, 99.0, 98.0, 98.7)])) is None
    assert sim("long", 99.0, *bars([(99.0, 99.5, 98.0, 99.1)])) is None                      # entry == stop: R = 0, skipped
    assert sim("short", 101.0, *bars([(101.5, 102.0, 101.0, 101.2)])) is None
    assert sim("short", 101.0, *bars([(101.0, 101.5, 100.0, 100.2)])) is None


def chk_cost_in_r(sim, settle):
    # flat trade (exit == entry): cost = 14 bp of price / R. 50,000 with R = 1,000 -> 70 / 1000 = 0.07 R; R = 2,000 -> 0.035 R
    assert close(settle("long", 50000.0, 49000.0, 50000.0, 0.0)[0], -0.07, 1e-12)
    assert close(settle("long", 50000.0, 48000.0, 50000.0, 0.0)[0], -0.035, 1e-12)
    assert close(settle("short", 50000.0, 51000.0, 50000.0, 0.0)[0], -0.07, 1e-12)
    # 7 bp on entry AND 7 bp on exit: exit at 51,000 long, R 1,000: (1000 - 35 - 35.7) / 1000 = 0.9293
    assert close(settle("long", 50000.0, 49000.0, 51000.0, 0.0)[0], (1000 - 35 - 35.7) / 1000, 1e-12)


def chk_funding_sign(sim, settle):
    base_l = settle("long", 100.0, 99.0, 100.0, 0.0)[0]                                        # -0.14
    assert close(base_l, -0.14)
    assert close(settle("long", 100.0, 99.0, 100.0, 0.0001)[0], -0.15)                          # long pays a positive rate
    assert close(settle("long", 100.0, 99.0, 100.0, -0.0001)[0], -0.13)                         # long receives a negative rate
    assert close(settle("short", 100.0, 101.0, 100.0, 0.0001)[0], -0.13)                        # short receives a positive rate
    assert close(settle("short", 100.0, 101.0, 100.0, -0.0001)[0], -0.15)                       # short pays a negative rate
    assert close(settle("long", 100.0, 98.0, 100.0, 0.0003)[0], (-0.14 - 0.03) / 2)             # two settlements, R = 2


CHECKS = [chk_target, chk_stop_first_long, chk_stop_first_short, chk_gap_long, chk_gap_short, chk_target_short,
          chk_target_gap_fills_at_target, chk_entry_bar_can_stop, chk_time_stop, chk_stop_on_last_window_bar, chk_cut_window,
          chk_entry_beyond_stop, chk_cost_in_r, chk_funding_sign]


def failures(sim, settle):
    bad = []
    for ck in CHECKS:
        try:
            ck(sim, settle)
        except (AssertionError, TypeError, KeyError, IndexError):
            bad.append(ck.__name__)
    return bad


@pytest.mark.parametrize("ck", CHECKS, ids=[c.__name__ for c in CHECKS])
def test_real_simulator(ck):
    ck(S.simulate, S.settle)


# ---------------------------------------------------------------- planted bugs: the fixture must notice each one
def _sim_target_first(side, stop, o, h, l, c):
    """Planted bug: when a bar holds both, the target wins."""
    o, h, l, c = (np.asarray(x, float)[:S.HOLD_BARS] for x in (o, h, l, c))
    entry = float(o[0])
    if side == "long":
        if entry <= stop:
            return None
        r = entry - stop; target = entry + 2 * r; hs, ht = l <= stop, h >= target
    else:
        if entry >= stop:
            return None
        r = stop - entry; target = entry - 2 * r; hs, ht = h >= stop, l <= target
    for k in range(len(o)):
        if ht[k]:
            return dict(kind="target", exit=target, idx=k, entry=entry, R=r, cut=False)
        if hs[k]:
            return dict(kind="stop", exit=stop, idx=k, entry=entry, R=r, cut=False)
    return dict(kind="time", exit=float(c[-1]), idx=len(c) - 1, entry=entry, R=r, cut=len(o) < S.HOLD_BARS)


def _sim_no_gap_fill(side, stop, o, h, l, c):
    """Planted bug: a gap through the stop still fills at the stop price."""
    t = S.simulate(side, stop, o, h, l, c)
    if t is not None and t["kind"] == "stop":
        t = dict(t, exit=stop)
    return t


def _sim_hold_plus_one(side, stop, o, h, l, c):
    """Planted bug: the 24 h window is 1441 bars."""
    saved = S.HOLD_BARS
    S.HOLD_BARS = saved + 1
    try:
        return S.simulate(side, stop, o, h, l, c)
    finally:
        S.HOLD_BARS = saved


def _settle_short_funding_unflipped(side, entry, stop, exit_px, fund_sum):
    """Planted bug: a short pays a positive rate like a long."""
    sgn = 1 if side == "long" else -1
    r = abs(entry - stop)
    return (sgn * (exit_px - entry) - 0.0007 * entry - 0.0007 * exit_px - fund_sum * entry) / r, r


PLANTED = [("target_first", _sim_target_first, S.settle), ("no_gap_fill", _sim_no_gap_fill, S.settle),
           ("hold_1441", _sim_hold_plus_one, S.settle), ("short_funding_unflipped", S.simulate, _settle_short_funding_unflipped)]


@pytest.mark.parametrize("name,sim,settle", PLANTED, ids=[p[0] for p in PLANTED])
def test_planted_bug_is_caught(name, sim, settle):
    assert failures(S.simulate, S.settle) == []
    bad = failures(sim, settle)
    assert bad, f"planted bug {name} passed every fixture check: the fixture cannot see it"


def test_planted_target_first_fails_the_stop_first_checks_specifically():
    bad = failures(_sim_target_first, S.settle)
    assert "chk_stop_first_long" in bad and "chk_stop_first_short" in bad


# ---------------------------------------------------------------- entry bar and funding window
def test_entry_index_is_the_bar_opening_at_T_plus_60s():
    ot = np.arange(0, 20 * 60_000, 60_000, dtype=np.int64)
    T = 5 * 60_000
    assert S.entry_index(ot, T) == 6                           # never the bar that opens at T (index 5)
    assert S.entry_index(ot, 19 * 60_000) == -1                # T + 60 s = bar 20 does not exist
    ot2 = np.delete(ot, 6)
    assert S.entry_index(ot2, T) == -1                         # missing entry bar: no trade, never the next bar


def test_funding_window_boundaries():
    ft = np.array([1000, 5000, 9000, 13000], np.int64)
    fr = np.array([0.1, 0.2, 0.4, 0.8])
    assert close(S.funding_sum(ft, fr, 1001, 9001), 0.2 + 0.4)             # 1000 is before the entry, 9000 inside
    assert close(S.funding_sum(ft, fr, 1000, 9000), 0.1 + 0.2)             # entry open == settlement counts; exit_end == settlement does not
    assert close(S.funding_sum(ft, fr, 2000, 4000), 0.0)                   # no settlement inside
    assert close(S.funding_sum(ft, fr, 0, 14000), 1.5)


def test_funding_enters_net_r_through_the_window():
    ft = np.array([1000], np.int64); fr = np.array([0.0002])
    inside = S.settle("long", 100.0, 99.0, 100.0, S.funding_sum(ft, fr, 500, 1500))[0]
    outside = S.settle("long", 100.0, 99.0, 100.0, S.funding_sum(ft, fr, 1500, 2500))[0]
    assert close(outside, -0.14) and close(inside, -0.14 - 0.02)
