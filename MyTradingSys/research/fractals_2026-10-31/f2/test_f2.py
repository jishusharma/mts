"""Fail-first tests for hseries.py and run_f2.py. Expected values are hand-derived, never taken from the modules."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hseries  # noqa: E402
import run_f2 as f2  # noqa: E402


def test_lookup_uses_only_closed_bars():
    # avail = bar open + 3600. Event at the exact avail second sees that bar; one second earlier does not.
    avail = np.array([100, 200, 300])
    assert f2.lookup_idx(avail, np.array([199, 200, 201, 99, 1000])).tolist() == [0, 1, 1, -1, 2]


def test_h_series_ignores_the_future_and_matches_availability():
    rng = np.random.default_rng(5)
    n = 1000
    bo = np.arange(n, dtype=np.int64) * 3600
    c = 100 * np.exp(np.cumsum(rng.standard_normal(n) * 0.01))
    h = hseries.h_from_closes(bo, c)
    c2 = c.copy()
    c2[700:] = c2[700:] * np.exp(np.cumsum(rng.standard_normal(n - 700)))   # wreck every close from bar 700 on
    h2 = hseries.h_from_closes(bo, c2)
    assert np.array_equal(h[:700], h2[:700], equal_nan=True)                  # bars 0..699 unchanged
    assert h[699] == h2[699] and not np.isnan(h[699])
    assert h[700] != h2[700]                                                   # bar 700 itself does change
    # an event at the open of hour 700 (second 700*3600) may use H[699] (its bar closes exactly then), not H[700]
    avail = bo + 3600
    assert f2.lookup_idx(avail, np.array([700 * 3600]))[0] == 699
    assert f2.lookup_idx(avail, np.array([700 * 3600 - 1]))[0] == 698


def test_h_missing_hour_blanks_windows_that_contain_the_gap():
    n = 1200
    bo = np.arange(n, dtype=np.int64) * 3600
    keep = np.arange(n) != 600                     # hour 200 absent: the return after it is not a 1h return
    c = 100 * np.exp(np.cumsum(np.random.default_rng(6).standard_normal(n) * 0.01))
    h = hseries.h_from_closes(bo[keep], c[keep])
    pos = {int(t): i for i, t in enumerate(bo[keep])}
    gap_ret = pos[601 * 3600]                       # position of the first bar after the gap
    for i in range(len(h)):
        contains = i - 479 <= gap_ret <= i
        if contains:
            assert np.isnan(h[i])
    ok_pos = np.flatnonzero(~np.isnan(h))
    after = ok_pos[ok_pos >= gap_ret]
    assert after[0] - gap_ret == 480                  # first window clear of the gap is valid
    assert np.isnan(h[:480]).all()


def test_state_switches_counts_only_runs_of_24_hours():
    # kept (<0.45) 30h, removed 30h, kept 30h, removed 5h, kept 30h: runs >=24h are K30, R30, K30, K30 -> wait: the 5h blip
    # separates two kept runs in the raw sequence (5 runs), but only runs >= 24h count: K30, R30, K30, K30 = 4 runs -> 3.
    h = np.r_[np.full(30, 0.40), np.full(30, 0.60), np.full(30, 0.40), np.full(5, 0.60), np.full(30, 0.40)]
    avail = np.arange(len(h), dtype=np.int64) * 3600
    assert f2.state_switches(h, avail, "A", 0, 10 ** 12) == 3
    # a series that never switches has 0
    assert f2.state_switches(np.full(100, 0.5), np.arange(100, dtype=np.int64), "A", 0, 10 ** 9) == 0


def test_lift_is_kept_minus_removed():
    y = np.array([1.0, 3.0, -1.0, -3.0])
    kept = np.array([True, True, False, False])
    assert f2.lift(y, kept) == 2.0 - (-2.0)


def _synthetic(seed, plant):
    rng = np.random.default_rng(seed)
    nh = 6000
    h = np.repeat(rng.choice([0.40, 0.50, 0.60], size=nh // 200), 200).astype(float)   # 200-hour regimes
    ev = {}
    for L in ("RSI-DIV-MTF", "FADE"):
        idx = rng.integers(0, nh, 1500)
        y = rng.standard_normal(1500)
        if plant:
            y = y + plant * (h[idx] < 0.45)
        ev[L] = (y, idx)
    return ev, h


def test_circular_shift_family_wise_null_flags_planted_edge_only(monkeypatch):
    monkeypatch.setattr(f2, "NPERM", 200)
    valid = np.ones(6000, bool)
    for plant, expect_flag in ((0.0, False), (0.5, True)):
        ev, h = _synthetic(7, plant)
        rng = np.random.default_rng(1)
        c1, c3 = f2.run_nulls(ev, h, valid, rng)
        obs = f2.null_lifts(ev, h, None)
        thr = float(np.quantile(c3.max(axis=1), 0.95))
        flagged = [j for j in range(4) if obs[j] > thr]
        if expect_flag:
            assert 0 in flagged and 2 in flagged            # gate A on both layers carries the planted edge
            assert f2.pval(c1[:, 0], obs[0]) < 0.05
        else:
            assert flagged == []
        # the circular shift keeps the set of H values (it only rolls them)
    hr = h.copy()
    hr[valid] = np.roll(h[valid], 123)
    assert np.array_equal(np.sort(hr), np.sort(h)) and not np.array_equal(hr, h)
