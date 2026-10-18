"""Tests for count_events.py / select_cells.py (card wavetrend-prereg-counts). Run: python -m pytest <this file>.

Expected values are derived by hand from ATLAS_STUDY_SPEC.md s2, not from the code under test.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import count_events as ce  # noqa: E402

spec = importlib.util.spec_from_file_location("select_cells", HERE / "select_cells.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def _walk(n, seed=7):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    h = c * (1 + np.abs(rng.normal(0, 0.003, n)))
    l = c * (1 - np.abs(rng.normal(0, 0.003, n)))
    return {"O": c.copy(), "H": h, "L": l, "C": c, "V": np.ones(n)}


def _events(B):
    wt1, wt2 = ce.wt_series(B)
    cross = ce.ev_cross(wt1, wt2)
    a1, a2, a4 = ce.ev_A(wt1, 53, 3)
    c1, c2 = ce.ev_C(B, wt1, 2, 20, 53)
    return {"A1": a1, "A2": a2, "A3": ce.ev_A3(wt1, cross, 53), "A4": a4, "B1": ce.ev_B1(wt1),
            "B2": ce.ev_B2(wt1, 5), "C1": c1, "C2": c2}


def test_future_spike_changes_no_past_event():
    """Events dated <= T are identical with and without a huge spike planted after T (no look-ahead; pivots confirm at p+k)."""
    n, T = 1500, 1200
    B = _walk(n)
    base = _events({k: v.copy() for k, v in B.items()})
    S = {k: v.copy() for k, v in B.items()}
    S["H"][T + 1:T + 3] *= 5.0
    S["C"][T + 1:T + 3] *= 4.0
    S["L"][T + 1:T + 3] *= 0.2
    spiked = _events(S)
    total = 0
    for name in base:
        a = [e for e in base[name] if e[0] <= T]
        b = [e for e in spiked[name] if e[0] <= T]
        total += len(a)
        assert a == b, name
    assert total > 20, "series too quiet to test anything"


def test_pivot_confirmed_k_bars_after_pivot():
    x = np.array([1, 2, 3, 9, 4, 3, 2, 1, 2], float)
    assert ce.pivots(x, 2, True) == [(3, 5)]           # peak at index 3 is known only at index 5
    assert ce.pivots(-x, 2, False) == [(3, 5)]


def test_A1_episode_and_A2_once():
    wt = np.full(40, 0.0)
    wt[10:20] = [50, 54, 58, 61, 60, 59, 58, 57, 56, 52]      # enters at 11, turns at 15 (60<61 is bar 14: 60 < 61)
    a1, a2, a4 = ce.ev_A(wt, 53, 3)
    assert a1 == [(11, 1)]
    assert a2 == [(14, 1)]                                     # first fall below previous value while still >= 53
    assert a4 == [(19, 1)]                                     # back under 53 at bar 19


def test_A1_flicker_reentry_is_not_a_new_arrival():
    wt = np.full(40, 0.0)
    wt[10:12] = [54, 55]       # arrival at 10 (R=3 outside bars before)
    wt[12:14] = [50, 50]       # 2 bars outside
    wt[14:16] = [54, 56]       # re-entry after 2 < R=3: no new A1
    a1, _, _ = ce.ev_A(wt, 53, 3)
    assert a1 == [(10, 1)]


def test_B2_centre_test_vs_cross():
    wt = np.array([20, 10, 3, 4, 12, 9, 2, -3, -9, -12.0])
    # first: from + side, touches |wt|<=5 at idx 2,3, leaves + at idx 4 -> B2 side +1; second touch 6-7 then leaves negative = cross, not B2
    assert ce.ev_B2(wt, 5) == [(4, 1)]


def test_selection_floor_and_caps():
    rows = []
    for tf, d in (("5m", 900), ("15m", 800), ("1h", 120)):
        rows.append(dict(tf=tf, event="A1_L53", var="ALL", bin="all", events=str(d), event_days=str(d), side_up="1", side_lo="1", mde_d="0"))
        for v in ("trend", "htf", "vol", "part"):
            rows.append(dict(tf=tf, event="A1_L53", var=v, bin="b", events=str(d // 3), event_days=str(d // 3 + 100 if tf != "1h" else 100),
                             side_up="1", side_lo="1", mde_d="0"))
    ch = sc.select(rows)
    assert all(r["tf"] != "1h" for r in ch)               # base 120 < FLOOR: TF dropped
    assert len(ch) == 2                                    # per-event cap 2
    assert len({(r["tf"], r["var"]) for r in ch}) == 2
