"""Tests for prob_tables.py (RSI deep-buy Phase 1 Steps D-E). Synthetic data only; expected numbers are hand counts or
textbook values, never taken from the module."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prob_tables as pt  # noqa: E402


def test_wilson_matches_textbook_values():
    # Wilson 95% (z=1.96) hand-computed: 5/10 -> 0.2366..0.7634 ; 0/10 -> 0..0.2775 ; 10/10 -> 0.7225..1
    lo, hi = pt.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=5e-4) and hi == pytest.approx(0.7634, abs=5e-4)
    lo, hi = pt.wilson(0, 10)
    assert lo == pytest.approx(0.0, abs=1e-9) and hi == pytest.approx(0.2775, abs=5e-4)
    lo, hi = pt.wilson(10, 10)
    assert lo == pytest.approx(0.7225, abs=5e-4) and hi == pytest.approx(1.0, abs=1e-9)
    assert all(np.isnan(v) for v in pt.wilson(0, 0))


def _wid(n_win, w):
    return np.repeat(np.arange(n_win), w)


def test_visits_numbered_with_hysteresis_and_window_reset():
    # window 0: dips to 20 at idx 2, hovers at 22 (below 23 re-arm) and 20 again (same visit), re-arms at 24, dips again at idx 7 -> visit 2
    # window 1 (new window): counting restarts, first dip at idx 12 is visit 1
    r = np.array([30, 30, 20, 22, 20, 21, 24, 19, 30, 30,
                  30, 30, 18, 30, 30, 30, 30, 30, 30, 30], dtype=float)
    wid = _wid(2, 10)
    idx, vn = pt.visit_events(r, wid, 20.0, 3.0)
    assert idx.tolist() == [2, 7, 12]
    assert vn.tolist() == [1, 2, 1]


def test_deeper_share_equals_hand_count():
    # 4 windows of 10 bars; each has one visit to L=20 at idx 1 of the window; later minimum in the window: 19, 17, 20.5(no), 14
    rows = []
    for m in (19, 17, 25, 14):
        w = [40, 20, m, 30, 30, 30, 30, 30, 30, 30]
        rows += w
    r = np.array(rows, dtype=float)
    wid = _wid(4, 10)
    idx, vn = pt.visit_events(r, wid, 20.0, 3.0)
    assert idx.tolist() == [1, 11, 21, 31]
    sm = pt.suffix_min_after(r, wid)
    for d, hand in ((1, 3), (2, 2), (3, 2), (5, 1)):     # hand count of m <= 20-d: {19,17,14}, {17,14}, {17,14}, {14}
        k = int((sm[idx] <= 20.0 - d).sum())
        assert k == hand, d


def test_rsi_race_bounce_vs_new_low():
    # entry 20. A: dips to 18 then rises to 24 (min 18, +5 off min -> 23 reached) -> bounce, but first falls only 2 (d=3 not hit).
    # B: falls to 16 (>=3 below 20) before any 5-point rise -> fail. C: never resolves -> nan.
    A = [20, 19, 18, 21, 24]
    B = [20, 19, 16, 25, 30]
    C = [20, 20, 21, 20, 21]
    r = np.array(A + B + C, dtype=float)
    wid = _wid(3, 5)
    ev = np.array([0, 5, 10])
    out = pt.rsi_race(r, ev, wid, b=5.0, d=3.0)
    assert out[0] == 1.0 and out[1] == 0.0 and np.isnan(out[2])


def test_survival_never_rises_and_matches_hand_km():
    # hit times: 2 events at t=1, 1 at t=3, 1 censored at 2, 2 never hit with full horizon 4
    first = np.array([1, 1, 3, np.inf, np.inf, np.inf])
    avail = np.array([4, 4, 4, 2, 4, 4])
    grid = (1, 2, 3, 4)
    s = pt.km_survival(first, avail, grid)
    # t=1: at risk 6, dead 2 -> 4/6 ; t=2: at risk 4 (one censored at 2 is still at risk at 2), dead 0 ;
    # t=3: at risk 3, dead 1 -> *2/3 ; t=4: at risk 2, dead 0
    assert s[0] == pytest.approx(4 / 6)
    assert s[1] == pytest.approx(4 / 6)
    assert s[2] == pytest.approx(4 / 6 * 2 / 3)
    assert s[3] == pytest.approx(4 / 6 * 2 / 3)
    assert all(s[i] >= s[i + 1] for i in range(len(s) - 1))


def test_event_at_t_unchanged_when_later_bars_change():
    rng = np.random.default_rng(3)
    r = 50 + 20 * np.sin(np.arange(200) / 5.0) + rng.normal(0, 1, 200)
    wid = _wid(4, 50)
    idx1, vn1 = pt.visit_events(r, wid, 35.0, 3.0)
    t = 120
    r2 = r.copy()
    r2[t + 1:] = rng.uniform(0, 100, len(r) - t - 1)
    idx2, vn2 = pt.visit_events(r2, wid, 35.0, 3.0)
    a = [(i, v) for i, v in zip(idx1, vn1) if i <= t]
    b = [(i, v) for i, v in zip(idx2, vn2) if i <= t]
    assert a == b and len(a) > 0


def test_dev_pass_refuses_bar_at_or_after_cutoff():
    ok = {"open_time": np.array([pt.CUTOFF_MS - 60_000])}
    pt.assert_dev(ok)
    with pytest.raises(ValueError):
        pt.assert_dev({"open_time": np.array([pt.CUTOFF_MS])})
    with pytest.raises(ValueError):
        pt.assert_val({"open_time": np.array([pt.HOLDOUT_MS])})
    pt.assert_val({"open_time": np.array([pt.HOLDOUT_MS - 60_000])})


def test_price_outcomes_fill_next_open_fee_and_mae():
    # event at bar 0: fill = open[1]=100; H=2 exit = open[3]=101 -> gross +1% > 0.10% fee ; MAE = min low bars 1..2 = 98 -> -2%
    o = np.array([100, 100, 100, 101, 101.0])
    lo = np.array([99, 99.5, 98, 100, 100.0])
    ret, mae = pt.price_outcomes(o, lo, np.array([0]), 2)
    assert ret[0] == pytest.approx(0.01)
    assert mae[0] == pytest.approx(98 / 100 - 1)
    ret2, _ = pt.price_outcomes(o, lo, np.array([3]), 2)
    assert np.isnan(ret2[0])
