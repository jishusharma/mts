"""Tests: fold, episode detection (first touch + re-arm), confirm, stop/target walk, and look-ahead
(truncation invariance, entry bar never used)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rsi_grid_lib as L  # noqa: E402

HR = L.HOUR
NAN = np.full((1, L.WIN), np.nan)


def _mk(n, seed=1, p0=100.0):
    r = np.random.RandomState(seed)
    c = p0 * np.exp(np.cumsum(r.normal(0, 0.01, n)))
    o = np.concatenate([[p0], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.002, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.002, n)))
    t = (np.arange(n) + 24 * 10) * HR
    return t, o, h, l, c, np.ones(n)


def test_fold_8h_anchor_and_incomplete_dropped():
    t, o, h, l, c, v = _mk(48)
    f = L.fold(t, o, h, l, c, v, 8)
    assert (f["t"] % (8 * HR) == 0).all()
    i = int(np.where(t == f["t"][0])[0][0])
    assert f["o"][0] == o[i] and f["c"][0] == c[i + 7] and f["h"][0] == h[i:i + 8].max() and f["l"][0] == l[i:i + 8].min()
    keep = np.ones(48, bool)
    keep[20] = False
    f2 = L.fold(t[keep], o[keep], h[keep], l[keep], c[keep], v[keep], 8)
    g = (t[20] // (8 * HR)) * 8 * HR
    assert g not in f2["t"] and len(f2["t"]) == len(f["t"]) - 1


def test_episodes_first_touch_and_rearm():
    rsi = np.array([np.nan, 40, 9, 8, 25, 12, 31, 11, 50])
    assert L.episodes(rsi, 10).tolist() == [2]            # 25 does not re-arm, 11 is not <= 10
    assert L.episodes(np.array([40, 9, 35, 8, 33, 9.5]), 10).tolist() == [1, 3, 5]


def test_confirm_requires_green_and_close_above_signal_close():
    ft = np.array([0, HR, 2 * HR])
    fo = np.array([10.0, 9.0, 8.0])
    fh = np.array([10.5, 9.1, 9.5])
    fl = np.array([8.5, 7.5, 7.9])
    fc = np.array([9.0, 8.0, 9.2])
    ci = L.confirm_info(ft, fo, fh, fl, fc, 1, 1)
    assert ci["confirm"] and ci["entry"] == 9.2 and ci["stop"] == 7.5 and ci["entry_close_t"] == 3 * HR
    assert abs(ci["stopdist"] - (9.2 - 7.5) / 9.2) < 1e-12
    fc2 = fc.copy()
    fc2[2] = 7.9
    assert not L.confirm_info(ft, fo, fh, fl, fc2, 1, 1)["confirm"]
    assert L.confirm_info(ft, fo, fh, fl, fc, 2, 1) is None


def test_walk_stop_target_gap_and_priority():
    n = L.WIN
    entry = np.array([100.0, 100.0, 100.0])
    stop = np.array([98.0, 98.0, 98.0])
    O = np.full((3, n), 100.0)
    H = np.full((3, n), 100.5)
    Lo = np.full((3, n), 99.5)
    C = np.full((3, n), 100.0)
    H[0, 3] = 104.0
    Lo[1, 2] = 97.0
    O[1, 2] = 99.0
    H[2, 1] = 104.0
    Lo[2, 1] = 97.0
    r = L.fwd_exit(entry, stop, O, H, Lo, C, np.full((3, n), np.nan), "tgt", 2.0, 0.0005)
    assert r["reason"].tolist() == [1, 0, 0]
    assert abs(r["net_r"][0] - ((0.04 - 0.001) / 0.02)) < 1e-9
    assert abs(r["net_r"][1] - ((-0.02 - 0.001) / 0.02)) < 1e-9
    O2 = O.copy()
    O2[1, 2] = 96.0
    r2 = L.fwd_exit(entry, stop, O2, H, Lo, C, np.full((3, n), np.nan), "tgt", 2.0, 0.0)
    assert r2["net_r"][1] < -1.0


def test_walk_never_uses_entry_bar():
    t, o, h, l, c, v = _mk(400)
    e0 = np.array([100])
    entry = c[e0]
    stop = entry * 0.98

    def run(hh, ll, kind, p):
        W = lambda a: L.fwd_window(a, e0)  # noqa: E731
        return L.fwd_exit(entry, stop, W(o), W(hh), W(ll), W(c), NAN, kind, p, 0.0)["net_r"][0]

    base = [run(h, l, "tgt", 2.0), run(h, l, "time", 24)]
    h2, l2 = h.copy(), l.copy()
    h2[100] = entry[0] * 10
    l2[100] = entry[0] * 0.1
    assert [run(h2, l2, "tgt", 2.0), run(h2, l2, "time", 24)] == base
    assert L.fwd_window(c, np.array([5]), 3)[0].tolist() == c[6:9].tolist()


def test_signal_and_entry_do_not_look_ahead():
    t, o, h, l, c, v = _mk(1500, seed=7)
    c = c * np.exp(-np.linspace(0, 1.5, 1500))
    f = L.fold(t, o, h, l, c, v, 4)
    rsi = L.wilder_rsi(f["c"])
    eps = L.episodes(rsi, 25)
    assert len(eps) > 0
    s = int(eps[0])
    full = L.confirm_info(f["t"], f["o"], f["h"], f["l"], f["c"], s, 4)
    k = s + 2  # bars up to and including the confirm bar s+1
    tr = {x: f[x][:k] for x in f}
    assert L.episodes(L.wilder_rsi(tr["c"]), 25).tolist()[:1] == [s]
    assert L.confirm_info(tr["t"], tr["o"], tr["h"], tr["l"], tr["c"], s, 4) == full
    tr2 = {x: f[x].copy() for x in f}
    for x in ("o", "h", "l", "c"):
        tr2[x][s + 2:] *= 3.0
    assert L.confirm_info(tr2["t"], tr2["o"], tr2["h"], tr2["l"], tr2["c"], s, 4) == full
    assert np.allclose(L.wilder_rsi(tr2["c"])[:s + 2], rsi[:s + 2], equal_nan=True)


if __name__ == "__main__":
    for k, fn in list(globals().items()):
        if k.startswith("test_"):
            fn()
            print("ok", k)
