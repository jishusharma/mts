"""Tests for depth_map.py (RSI deep-buy Phase 1 Steps A-C). Synthetic data only."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import depth_map as dm  # noqa: E402


def test_trough_ranking_exact_order():
    # planted troughs (value at index): 10->20, 25->15, 40->30, 55->10, 70->25, 85->35, 98->5 (edge: right side leaves the window, not confirmed)
    r = np.full(100, 60.0)
    for i, v in {10: 20, 25: 15, 40: 30, 55: 10, 70: 25, 85: 35, 98: 5}.items():
        r[i] = v
    out = dm.ranked_troughs(r[None, :], k=3, n=5)
    assert out.shape == (1, 5)
    assert out[0].tolist() == [10.0, 15.0, 20.0, 25.0, 30.0]


def test_trough_needs_full_neighbourhood_and_fewer_than_five_gives_nan():
    r = np.full(30, 60.0)
    r[10], r[20] = 12.0, 18.0
    out = dm.ranked_troughs(r[None, :], k=5, n=5)
    assert out[0, :2].tolist() == [12.0, 18.0]
    assert np.isnan(out[0, 2:]).all()


def test_hysteresis_wobble_is_one_visit_and_rise_then_dip_is_two():
    L, h = 30.0, 3.0
    wobble = np.array([[40, 31, 29, 31, 29, 30, 31, 29, 40]], dtype=float)    # never reaches 33 again
    assert dm.count_visits(wobble, L, h)[0] == 1
    two = np.array([[40, 31, 29, 31, 33, 29, 40, 40, 40]], dtype=float)       # rose to L+h=33, dipped again
    assert dm.count_visits(two, L, h)[0] == 2
    # a rise that stops 0.5 short of L+h does not re-arm
    short = np.array([[40, 29, 32.5, 29, 40, 40, 40, 40, 40]], dtype=float)
    assert dm.count_visits(short, L, h)[0] == 1


def test_running_record_has_no_lookahead():
    rng = np.random.default_rng(7)
    a = rng.uniform(10, 60, size=(3, 40))
    b = a.copy()
    b[:, 25:] = rng.uniform(1, 90, size=(3, 15))        # alter later bars
    ra, rb = dm.running_record_count(a), dm.running_record_count(b)
    assert np.array_equal(ra[:, :25], rb[:, :25])
    # records strictly lower: a flat run is not a new record
    flat = np.array([[50, 40, 40, 40, 30, 35, 30]], dtype=float)
    assert dm.running_record_count(flat)[0].tolist() == [1, 2, 2, 2, 3, 3, 3]


def test_p_touch_hand_computed_four_windows():
    # Hand computation (independent of depth_map.py), L=30, h=3, four windows of six bars:
    # W1 [40,35,29,33,28,40]: 29 visit1; 33>=L+h rearms; 28 visit2 -> min 28, 2 visits
    # W2 [40,31,30,31,29,31]: 30<=30 visit1; never back to 33 -> min 29, 1 visit
    # W3 [40,35,31.5,32,45,50]: min 31.5 > 30 untouched
    # W4 [50,45,40,38,36,34]: min 34 untouched
    R = np.array([[40, 35, 29, 33, 28, 40],
                  [40, 31, 30, 31, 29, 31],
                  [40, 35, 31.5, 32, 45, 50],
                  [50, 45, 40, 38, 36, 34]], dtype=float)
    t = dm.touch_stats(R, [28, 29, 30, 31], h=3.0)
    assert t[30]["n_windows"] == 4
    assert t[30]["p_touch"] == pytest.approx(2 / 4)
    assert t[30]["mean_visits_given_touched"] == pytest.approx(1.5)
    assert t[30]["p_2plus_given_touched"] == pytest.approx(0.5)
    assert t[29]["p_touch"] == pytest.approx(0.5)      # mins 28 and 29
    assert t[28]["p_touch"] == pytest.approx(0.25)     # only min 28
    assert t[31]["p_touch"] == pytest.approx(0.5)      # 31.5 > 31


def test_bar_at_or_after_cutoff_refused():
    ok = {"open_time": np.array([dm.CUTOFF_MS - 60_000], dtype="int64")}
    dm.assert_dev(ok)
    bad = {"open_time": np.array([dm.CUTOFF_MS - 60_000, dm.CUTOFF_MS], dtype="int64")}
    with pytest.raises(ValueError):
        dm.assert_dev(bad)


def test_rare_zone_line_is_monotone_in_q():
    rng = np.random.default_rng(3)
    mins = rng.uniform(5, 60, size=500)
    R = np.stack([np.r_[m, 70.0, 70.0] for m in mins])
    levels = list(range(5, 51))
    stats = dm.touch_stats(R, levels, h=3.0)
    ln = {q: dm.rare_line(stats, q) for q in (0.02, 0.05, 0.10, 0.20)}
    vals = [ln[q] for q in (0.02, 0.05, 0.10, 0.20)]
    assert all(v is not None for v in vals)
    assert vals == sorted(vals)
    # defined as the highest level whose P_touch < q
    for q, v in ln.items():
        assert stats[v]["p_touch"] < q
        nxt = v + 1
        if nxt in stats:
            assert stats[nxt]["p_touch"] >= q


def test_windows_built_only_from_complete_utc_groups():
    t0 = int(np.datetime64("2023-01-02T00:00", "ms").astype("int64"))     # a Monday
    n = 24 * 60 * 2
    t = t0 + np.arange(n) * 60_000
    keep = np.ones(n, bool)
    keep[100] = False                                                     # hole inside the first 4h window
    rsi = np.arange(n, dtype=float)
    M, starts = dm.window_matrix(t[keep], rsi[keep], tf_min=1, win_min=240)
    assert M.shape[1] == 240
    assert starts[0] == t0 + 240 * 60_000                                 # first 4h window dropped (incomplete)
