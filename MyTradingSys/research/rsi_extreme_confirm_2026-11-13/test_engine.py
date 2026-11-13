import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E  # noqa: E402

HR = 3600000


def mk(n=60, price=100.0):
    t = np.arange(n) * HR
    o = np.full(n, price)
    return t, o, o + 0.5, o - 0.5, o.copy()


def run(side, stop, ex, t, o, h, l, c, rsi=None, s=3, fee=0.0):
    n = len(c)
    rsi = np.full(n, 40.0) if rsi is None else rsi
    return E.fwd_outcomes(side, stop, ex, [s], t, o, h, l, c, rsi, np.full(n, 1.0), np.zeros(n), fee)


def test_long_target_hit_2r():
    t, o, h, l, c = mk()
    h[7] = 102.5          # entry bar 5 open 100, stop pct1 = 99, R = 1, target 102
    r = run(1, "pct1", "tgt2r", t, o, h, l, c)
    assert r["valid"][0] and r["x"][0] == 7
    assert abs(r["net_r"][0] - 2.0) < 1e-9 and abs(r["net_pct"][0] - 0.02) < 1e-9


def test_stop_first_when_both_in_one_bar():
    t, o, h, l, c = mk()
    h[6] = 103.0
    l[6] = 98.0
    r = run(1, "pct1", "tgt2r", t, o, h, l, c)
    assert r["x"][0] == 6 and abs(r["net_r"][0] + 1.0) < 1e-9


def test_gap_through_stop_fills_at_open():
    t, o, h, l, c = mk()
    o[6], h[6], l[6], c[6] = 97.0, 97.5, 96.0, 96.5
    r = run(1, "pct1", "time24", t, o, h, l, c)
    assert abs(r["net_r"][0] + 3.0) < 1e-9


def test_rsi_exit_and_time_exit():
    t, o, h, l, c = mk()
    rsi = np.full(60, 40.0)
    rsi[9] = 55.0
    c[9] = 101.0
    r = run(1, "pct1", "rsi50", t, o, h, l, c, rsi=rsi)
    assert r["x"][0] == 9 and abs(r["net_r"][0] - 1.0) < 1e-9
    r2 = run(1, "pct1", "time24", t, o, h, l, c)
    assert r2["x"][0] == 5 + E.W - 1


def test_short_mirror_fee_and_funding():
    t, o, h, l, c = mk()
    l[7] = 97.5           # short entry 100, stop pct1 = 101, R = 1, target 98
    n = len(c)
    G = np.zeros(n)
    G[6:] = 0.001         # +0.001 settled during the hold: long pays, short receives
    atr, rsi = np.full(n, 1.0), np.full(n, 60.0)
    r = E.fwd_outcomes(-1, "pct1", "tgt2r", [3], t, o, h, l, c, rsi, atr, G, 0.0005)
    assert r["x"][0] == 7
    assert abs(r["net_pct"][0] - (0.02 - 0.001 + 0.001)) < 1e-9
    rl = E.fwd_outcomes(1, "pct1", "time24", [3], t, o, h, l, c, rsi, atr, G, 0.0)
    assert abs(rl["net_pct"][0] + 0.011) < 1e-9  # long stopped at -1% in bar 7, pays funding 0.001


def test_atr_stop_and_mae():
    t, o, h, l, c = mk()
    l[3] = 98.0           # setup low 98, atr 1.0, atr100 stop = 97, R = 3
    l[6] = 98.5           # adverse 1.5 from entry 100
    r = run(1, "atr100", "time24", t, o, h, l, c)
    assert abs(r["rpct"][0] - 0.03) < 1e-9
    assert abs(r["mae_r"][0] - 0.5) < 1e-9


def test_one_position_and_confirm_mask():
    keep = E.pick_one_position(np.array([12, 13, 32]), np.array([20, 21, 40]))
    assert list(keep) == [0, 2]
    c = np.array([1.0, 2.0, 1.5, 1.7])
    rsi, atr = np.full(4, 20.0), np.full(4, 1.0)
    assert list(E.confirm_mask(1, c, rsi, atr)) == [True, False, True, False]
    assert list(E.confirm_mask(-1, c, rsi, atr)) == [False, True, False, False]
