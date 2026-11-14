"""Causality and mechanics tests for lib.py. Run: python -m pytest test_lib.py -q"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def _walk(n, seed=1):
    r = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(r.normal(0, .01, n)))
    return c * (1 + np.abs(r.normal(0, .004, n))), c * (1 - np.abs(r.normal(0, .004, n))), c


def test_pivot_level_known_only_from_confirmation_bar():
    h, l, _ = _walk(300)
    phs, _ = lib.pivots(h, l, 3)
    lv = lib.last_pivot_level(300, phs, h, 3)
    p = phs[5]
    assert lv[p + 3] == h[p]
    assert lv[p + 2] != h[p]


def test_future_data_does_not_change_past_levels():
    h, l, _ = _walk(400)
    a = lib.last_pivot_level(400, lib.pivots(h, l, 3)[0], h, 3)
    h2, l2 = h.copy(), l.copy()
    h2[300:] *= 1.5
    l2[300:] *= 0.5
    b = lib.last_pivot_level(400, lib.pivots(h2, l2, 3)[0], h2, 3)
    assert np.array_equal(a[:297], b[:297], equal_nan=True)


def test_phase_uses_previous_day_only():
    t = np.arange(0, 6) * lib.DAY
    dd = np.column_stack([t, np.ones(6), np.ones(6), np.ones(6), np.ones(6), np.ones(6)])
    ph = np.array([0, 1, 2, 3, 4, 5], np.int8)
    d4 = np.array([[3 * lib.DAY + 20 * 3600_000, 1, 1, 1, 1, 1]], float)  # last 4H bar of day 3
    assert lib.phase_for_4h(d4, dd, ph)[0] == 2  # day 2, never day 3


@pytest.mark.skipif(not os.path.exists(f"{lib.CACHE}/BTCUSDT_1d.npy"), reason="local kline cache absent (CI)")
def test_phase_series_ignores_future():
    a = np.load(f"{lib.CACHE}/BTCUSDT_1d.npy")[:-1]
    full = lib.phases(a)
    cut = lib.phases(a[:2500])
    assert np.array_equal(full[:2500], cut)


class _C:
    n = 200
    o = np.full(200, 100.0)
    h = np.full(200, 101.0)
    l = np.full(200, 99.5)
    c = np.full(200, 100.0)
    atr = np.full(200, 0.1)
    PL = np.full(200, 99.5)
    PH = np.full(200, 105.0)
    brk_up = np.zeros(200, bool)
    brk_dn = np.zeros(200, bool)


def test_stop_first_and_fee_in_R():
    co = _C()
    co.l = co.l.copy()
    co.l[11] = 98.0
    r = lib.simulate(co, 10, 1)  # pivot 99.5 minus max(0.06, 0.5) = stop 99.0, risk 1.0
    assert r["stopped"] and abs(r["gross_R"] + 1) < 1e-9
    assert abs(lib.net(r, 12) - (-1 - 12e-4 * 100 / 1.0)) < 1e-9


def test_opposite_signal_exit_planned_hold():
    co = _C()
    co.brk_dn = co.brk_dn.copy()
    co.brk_dn[15] = True
    r = lib.simulate(co, 10, 1)
    assert r["planned"] == 15 + 1 - 11 and not r["stopped"]


def test_divergence_available_only_after_confirmation():
    r = np.random.default_rng(3)
    n = 120
    c = 100 + np.cumsum(r.normal(0, 1, n))
    a = np.column_stack([np.arange(n) * lib.DAY * 7.0, c, c + 1, c - 1, c, np.ones(n)])
    b, _ = lib.divergence_times(a, 7 * lib.DAY)
    _, pls = lib.pivots(a[:, 2], a[:, 3], lib.KHTF)
    assert b.size == 0 or b.min() >= a[pls[1] + lib.KHTF, 0] + 7 * lib.DAY
