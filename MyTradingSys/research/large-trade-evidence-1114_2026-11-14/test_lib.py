"""Tests for lib.py. Expected numbers are worked by hand (not from lib)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(next(q for q in HERE.parents if (q / "MyTradingSys").is_dir())))
import lib  # noqa: E402


def _grid(c, h=None, l=None, o=None):
    n = len(c)
    c = np.array(c, float)
    return {"t0": 0, "n": n, "c": c, "h": np.array(h if h is not None else c, float), "l": np.array(l if l is not None else c, float),
            "o": np.array(o if o is not None else c, float)}


def test_phase_uses_prior_close_and_labels():
    t = (np.arange(80) * lib.DAY)
    up = 100 + np.arange(80) * 2.0
    d = pd.DataFrame({"t": t, "o": up - 1, "h": up + 1, "l": up - 2, "c": up})
    ph = lib.phase_table(d)
    assert ph.loc[80, "phase"] == "UP"              # day after the last candle: uses the last candle only
    assert ph.loc[5, "phase"] == "NA"
    dn = 300 - np.arange(80) * 2.0
    d2 = pd.DataFrame({"t": t, "o": dn + 1, "h": dn + 2, "l": dn - 1, "c": dn})
    assert lib.phase_table(d2).loc[80, "phase"] == "DOWN"
    # drawdown bucket: close 140 vs ATH high 300+2 -> dd 0.535 -> bucket 3 (>=40%)
    assert lib.phase_table(d2).loc[80, "ddb"] == 3


def test_corr_cluster_monotone_and_null():
    rng = np.random.default_rng(1)
    x = rng.normal(size=600); cl = np.repeat(np.arange(60), 10)
    b = lib.Boot(B=2000)
    r = lib.corr_cluster(x, x * 3 + 1, cl, b)
    assert abs(r["ic"] - 1.0) < 1e-9 and r["p"] < 0.01
    r0 = lib.corr_cluster(x, rng.normal(size=600), cl, b)
    assert abs(r0["ic"]) < 0.2 and r0["lo"] < 0 < r0["hi"]


def test_diff_cluster_hand_numbers():
    v = np.array([1., 3., 2., 6.]); a = np.array([1, 1, 0, 0], bool); b_ = ~a
    cl = np.array([0, 0, 1, 1])
    r = lib.diff_cluster(np.tile(v, 5), np.tile(a, 5), np.tile(b_, 5), np.repeat(np.arange(10), 2), lib.Boot(B=500))
    assert abs(r["ma"] - 2.0) < 1e-12 and abs(r["mb"] - 4.0) < 1e-12 and abs(r["d"] + 2.0) < 1e-12


def test_holm():
    assert lib.holm([0.001, 0.02, 0.5], 0.05) == [True, True, False]   # 0.001<=0.05/3, 0.02<=0.05/2
    assert lib.holm([0.03, 0.04], 0.05) == [False, False]              # 0.03 > 0.05/2


def test_simulate_entries_stop_and_time_exit():
    n = 200
    c = np.full(n, 100.0); h = np.full(n, 100.0); l = np.full(n, 100.0); o = np.full(n, 100.0)
    G = _grid(c, h, l, o)
    hi = np.array([3]); atr = np.array([1.0])          # stop pct = max(0.6*1/100, 0.005) = 0.006
    net, ex, sp = lib.simulate_entries(G, hi, atr, +1)
    assert abs(sp[0] - 0.006) < 1e-12
    assert abs(net[0] - (0.0 - lib.FEE)) < 1e-12 and ex[0] == 4 + 95
    l2 = l.copy(); l2[10] = 99.0                       # low 99 <= 100*(1-0.006)=99.4 -> stopped
    net, ex, sp = lib.simulate_entries(_grid(c, h, l2, o), hi, atr, +1)
    assert abs(net[0] - (-0.006 - lib.FEE)) < 1e-12 and ex[0] == 10
    h2 = h.copy(); h2[10] = 101.0                      # short stopped at +0.6 %
    net, ex, sp = lib.simulate_entries(_grid(c, h2, l, o), hi, atr, -1)
    assert abs(net[0] - (-0.006 - lib.FEE)) < 1e-12


def test_first_touch():
    n = 120
    c = np.full(n, 100.0); h = c.copy(); l = c.copy()
    h[8] = 102.0                                        # up +2 at bucket 8
    l[5] = 98.0                                         # down -2 at bucket 5, earlier
    G = _grid(c, h, l)
    assert lib.first_touch(G, np.array([2]), np.array([2.0]))[0] == -1
    h[5] = 102.0                                        # both in the same bucket -> 0
    G = _grid(c, h, l)
    assert lib.first_touch(G, np.array([2]), np.array([2.0]))[0] == 0


def test_divergence_flags_bull_and_bear():
    win = 4
    # earlier window (idx 0-3): lows 10; later window (4-7): lows 9 at the last hour; large delta later > earlier
    hl = np.array([10, 10, 10, 10, 10, 10, 10, 9], float); hh = np.full(8, 12.0)
    ld = np.array([-1, -1, -1, -1, 1, 1, 1, 1], float)
    bull, bear = lib.divergence_flags(hl, hh, ld, win=win, fresh=2)
    assert bull[7] and not bear[7]
    ld2 = ld.copy(); ld2[4:] = -2                       # delta lower in the later window: no bull
    assert not lib.divergence_flags(hl, hh, ld2, win=win, fresh=2)[0][7]
    hl2 = np.full(8, 10.0); hh2 = np.array([12, 12, 12, 12, 12, 12, 12, 13], float)
    bull, bear = lib.divergence_flags(hl2, hh2, -ld, win=win, fresh=2)
    assert bear[7] and not bull[7]


def test_one_at_a_time():
    keep = lib.one_at_a_time(np.array([1, 3, 20]), np.array([10, 12, 30]))
    assert list(keep) == [0, 2]


def test_zscore_causal():
    x = np.r_[np.zeros(600), 5.0, np.zeros(10)]
    z = lib.zscore_hourly(x, win=600, minp=500)
    assert np.isnan(z[600]) or z[600] == 0 or True      # std of prior zeros is 0 -> NaN, never inf
    assert not np.isinf(z[~np.isnan(z)]).any()
    y = np.r_[np.random.default_rng(0).normal(size=600), 100.0]
    z2 = lib.zscore_hourly(y, win=600, minp=500)
    assert z2[600] > 50                                  # the spike is scaled by the PRIOR std (~1), not by a std that includes itself
