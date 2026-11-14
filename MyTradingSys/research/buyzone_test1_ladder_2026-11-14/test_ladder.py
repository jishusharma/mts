import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ladder as L


def walk(n, seed):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.03, n)))
    o = np.concatenate([[c[0]], c[:-1]]) * np.exp(rng.normal(0, 0.004, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.01, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.01, n)))
    ts = (np.arange(n) * 86400000 + 1451606400000).astype(np.int64)  # from 2016-01-01
    return ts, o, h, l, c


def hand_series():
    lows = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 16, 18, 19, 20, 19, 18, 17, 16, 15, 14, 13, 12,
            14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    l = np.array(lows, float)
    h = l + 2
    c = l + 1.5
    o = l + 1.0
    return o, h, l, c


def test_hl_break_first_close_is_bar30():
    o, h, l, c = hand_series()
    H = h[10:23].max()
    assert H == 22
    first = next(i for i in range(25, len(c)) if c[i] > H)
    assert first == 30
    atr = L.wilder_atr(h, l, c)
    cc, j, stop0 = L.find_signals(o, h, l, c, atr, L.wilder_rsi(c), "A")[0]
    assert cc == 30
    assert abs(stop0 - (12 - max(0.6 * atr[30], 0.06))) < 1e-9


def test_no_signal_when_second_low_not_higher():
    o, h, l, c = hand_series()
    l2 = l.copy()
    l2[22] = 9.0   # second low below the first -> not HL_BREAK
    h2, c2 = l2 + 2, l2 + 1.5
    assert L.find_signals(o, h2, l2, c2, L.wilder_atr(h2, l2, c2), L.wilder_rsi(c2), "A") == []


def test_break_before_pivot_known_does_not_count():
    o, h, l, c = hand_series()
    c2 = c.copy()
    c2[23] = 30.0   # closes far above H on bar j+1, before the pivot is known (j+3 = 25)
    h2 = np.maximum(h, c2)
    sig = L.find_signals(o, h2, l, c2, L.wilder_atr(h2, l, c2), L.wilder_rsi(c2), "A")
    assert all(s[0] >= 25 for s in sig)


def test_causality_by_truncation():
    for seed in range(4):
        ts, o, h, l, c = walk(3500, seed)
        for mode in ("A", "B"):
            full, _ = L.build_events("X", ts, o, h, l, c, mode)
            for cut in (2200, 3000):
                part, _ = L.build_events("X", ts, o, h, l, c, mode, n_avail=cut)
                ref = [e for e in full if e["x"] < cut]
                assert [(e["sig"], e["e"], e["x"]) for e in part] == [(e["sig"], e["e"], e["x"]) for e in ref]
                assert [e["phase"] for e in part] == [e["phase"] for e in ref]


def test_events_exist_on_walk():
    n = sum(len(L.build_events("X", *walk(3500, s), "A")[0]) for s in range(4))
    assert n > 10


def test_phase_causal_by_truncation():
    ts, o, h, l, c = walk(2000, 7)
    full = L.phases(h, l, c)
    part = L.phases(h[:1500], l[:1500], c[:1500])
    assert list(full[:1500]) == list(part)
    assert set(full[500:]) <= set(L.PHASES) | {""}


def flat(n=60):
    o = np.full(n, 100.0); h = np.full(n, 100.5); l = np.full(n, 99.5); c = np.full(n, 100.0)
    return o, h, l, c, np.full(n, 1.0)


def test_sim_exit_time_and_stop():
    o, h, l, c, atr = flat()
    assert L.sim_exit(o, h, l, c, atr, 10, 90.0) == (39, 100.0)          # time exit at close of bar e+29
    l2 = l.copy(); l2[15] = 98.0
    assert L.sim_exit(o, h, l2, c, atr, 10, 99.0) == (15, 99.0)          # initial stop
    o3 = o.copy(); o3[15] = 85.0; l3 = l.copy(); l3[15] = 84.0
    assert L.sim_exit(o3, h, l3, c, atr, 10, 99.0) == (15, 85.0)         # gap through the stop: exit at the open
    o4, h4, l4, c4 = o.copy(), h.copy(), l.copy(), c.copy()
    o4[12:] = 120.0; h4[12:] = 121.0; l4[12:] = 119.5; c4[12:] = 120.0   # run to ~121; trail = 121 - 2 = 119
    l4[16] = 117.0
    assert L.sim_exit(o4, h4, l4, c4, atr, 10, 90.0) == (16, 119.0)      # trailing exit at the level
    assert L.sim_exit(o[:30], h[:30], l[:30], c[:30], atr[:30], 10, 90.0) is None   # still open at data end


def test_trailing_uses_only_prior_bars():
    o, h, l, c, atr = flat()
    o[13:] = 120.0; l[13:] = 119.5; h[13:] = 120.5; c[13:] = 120.0
    h[13] = 130.0; l[13] = 105.0   # bar 13 spikes up AND trades down to 105; trail from bars before 13 is 100.5-2=98.5
    r = L.sim_exit(o, h, l, c, atr, 10, 90.0)
    assert r[0] != 13              # the 130 high of bar 13 itself must not raise bar 13's level
    l[14] = 127.0                  # bar 14: trail = 130 - 2 = 128 > low 127 -> exit at 128 (open 120 gapped below -> open)
    r = L.sim_exit(o, h, l, c, atr, 10, 90.0)
    assert r == (14, 120.0)


def test_table_matches_sim_exit():
    ts, o, h, l, c = walk(1200, 3)
    tab = L.PlaceboTable({"X": (ts, o, h, l, c)})
    atr = L.wilder_atr(h, l, c)
    rng = np.random.default_rng(0)
    for e in rng.integers(450, 1150, 40):
        rr = 0.04
        stop0 = o[e] * (1 - rr)
        res = L.sim_exit(o, h, l, c, atr, int(e), stop0)
        g = tab.gross(np.array([[e]]), np.array([[rr]]))[0, 0]
        if res is None:
            assert np.isnan(g)
        else:
            assert abs(g - (res[1] / o[e] - 1)) < 1e-12


def test_placebo_percentile_not_extreme_for_random_events():
    ts, o, h, l, c = walk(3000, 11)
    tab = L.PlaceboTable({"X": (ts, o, h, l, c)})
    ph = L.phases(h, l, c)
    rng = np.random.default_rng(5)
    elig = [e for e in range(L.WARM + 1, 2900) if ph[e - 1] == "UP"]
    pcts = []
    atr = L.wilder_atr(h, l, c)
    for _ in range(6):
        es = rng.choice(elig, 25, replace=False)
        evs = []
        for e in es:
            rr = 0.05
            res = L.sim_exit(o, h, l, c, atr, int(e), o[e] * (1 - rr))
            if res:
                evs.append(dict(coin="X", phase="UP", r=rr, gross=res[1] / o[e] - 1, ts=int(ts[e])))
        act = np.mean([L.R_of(x["gross"], x["r"], 0.0012) for x in evs])
        d = L.placebo(tab, evs, "ALL", 0.0012, ndraw=400)
        pcts.append((d <= act).mean())
    assert 0.0 < np.mean(pcts) < 1.0 and sum(0.02 < p < 0.98 for p in pcts) >= 4


def test_block_ci_constant_and_wide():
    ts = (np.arange(200) * 86400000).astype(np.int64)
    lo, hi = L.block_ci(ts, np.full(200, 0.5))
    assert abs(lo - 0.5) < 1e-12 and abs(hi - 0.5) < 1e-12
    rng = np.random.default_rng(1)
    R = rng.normal(0, 1, 200)
    lo, hi = L.block_ci(ts, R)
    assert lo < R.mean() < hi


def test_fee_in_R():
    assert abs(L.R_of(0.10, 0.05, 0.0012) - (0.10 - 0.0012) / 0.05) < 1e-12
