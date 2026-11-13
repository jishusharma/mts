"""Tests for the crowding-reversal core: PIT percentile flag, fade side, fee/funding netting, one-position rule."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import crowd as C  # noqa: E402


def test_flag_excludes_current_and_flags_extremes():
    x = list(np.linspace(0.0, 1.0, 100)) + [5.0, -5.0, 0.5]
    f = C.trailing_flag(x, 100)
    assert np.isnan(f[:100]).all()
    assert f[100] == 1.0 and f[101] == -1.0 and f[102] == 0.0
    # current value must not move its own threshold: a huge value is still flagged
    assert f[100] == 1.0


def test_fade_side_signal_a():
    n = 5
    cd = dict(fund_flag=np.array([1.0, -1.0, 0.0, np.nan, 1.0]), X=np.full(n, .05), ret3=np.full(n, .1),
              ratio_flag=np.zeros(n), oi_flag=np.zeros(n), fund_rate=np.ones(n))
    assert list(C.signal_side(cd, "a")) == [-1, 1, 0, 0, -1]
    # (c) needs price up for the positive extreme and down for the negative extreme
    cd["ret3"] = np.array([.1, .1, .1, .1, .01])
    assert list(C.signal_side(cd, "c")) == [-1, 0, 0, 0, 0]


def test_net_includes_fee_and_funding_sign():
    g = np.array([0.02])
    # short, price +2% -> -2%, minus funding collected? short receives positive funding
    assert abs(C.net(-1, g, np.array([0.001]))[0] - (-(0.02 - 0.001) - C.ROUND_TRIP_FEE)) < 1e-12
    assert abs(C.net(1, g, np.array([0.001]))[0] - ((0.02 - 0.001) - C.ROUND_TRIP_FEE)) < 1e-12
    assert C.ROUND_TRIP_FEE > 0


def _toy(n=400):
    t = np.arange(n, dtype=np.int64) * C.H4
    o = 100 + np.arange(n, dtype=float)
    fts = np.array([0, 8 * 3600 * 1000, 16 * 3600 * 1000, 24 * 3600 * 1000], dtype=np.int64)
    fr = np.array([0.0, 0.001, 0.001, 0.001])
    return dict(t=t, o=o, c=o, fts=fts, fund_cum=np.concatenate([[0.0], np.cumsum(fr)]),
                fund_flag=np.zeros(n), fund_rate=np.zeros(n), ratio_flag=np.zeros(n), oi_flag=np.zeros(n),
                ret3=np.zeros(n), X=np.full(n, .05))


def test_forward_arrays_funding_window_and_hold():
    cd = _toy()
    g, f, v = C.fwd_trade_arrays(cd, 1)
    # entry bar 0 (t=0) exit bar 6 (t=24h): prints with 0 < ts <= 24h = three prints of 0.001
    assert abs(f[0] - 0.003) < 1e-12
    assert abs(g[0] - (106 / 100 - 1)) < 1e-12
    assert v[0] and not v[len(v) - 1]


def test_one_position_per_coin_and_next_bar_entry():
    cd = _toy()
    cd["fund_flag"][10:20] = 1.0   # signal on consecutive bars
    ents, sides, *_ = C.select_trades(cd, "a", "4h", 1)
    assert ents[0] == 11 and sides[0] == -1          # entry at the NEXT bar open
    assert ents[1] - ents[0] >= 6                    # next trade only after the 1-day hold ends


def test_cluster_bootstrap_ci_brackets_mean():
    rng = np.random.default_rng(0)
    v = rng.normal(0.01, 0.02, 600)
    w = np.repeat(np.arange(60), 10)
    m, lo, hi, p = C.cluster_boot(v, w, B=500)
    assert lo < m < hi and p < 0.01
