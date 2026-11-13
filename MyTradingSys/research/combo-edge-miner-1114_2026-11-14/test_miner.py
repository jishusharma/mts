"""Tests for the combo edge miner. Expected numbers come from FORMULAS.md worked examples or hand arithmetic, not from miner.py.
The causality tests must FAIL under STUDY_BUG=1 (test_bug_flag_is_detected runs them in a subprocess with the flag on)."""
import os
import sys
import subprocess
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import miner as M  # noqa: E402
import run as R  # noqa: E402


# ---------------------------------------------------------------- indicator worked examples (FORMULAS.md)
def test_atr_plain_sma_s12():
    atr = M.atr_sma([10, 11, 12, 11], [9, 9, 10, 9], [9.5, 10.5, 11.5, 10], 3)
    assert abs(atr[3] - 2.1666667) < 1e-6 and np.isnan(atr[2])


def test_rsi_wilder_s1():
    assert abs(M.rsi_wilder([10, 12, 11, 14], 3)[3] - 83.33333) < 1e-4


TOY_H = [10, 11, 12, 11, 13, 14, 13, 12, 11, 12, 13, 15, 14, 13, 12, 11, 12, 14, 15, 14]
TOY_L = [8, 9, 10, 9, 10, 12, 11, 10, 9, 10, 11, 12, 12, 11, 10, 9, 10, 11, 13, 12]
TOY_C = [9, 10, 11, 10, 12, 13, 12, 11, 10, 11, 12, 14, 13, 12, 11, 10, 11, 13, 14, 13]


def test_adx_toy_s30():
    dip, dim, adx = M.adx_di(TOY_H, TOY_L, TOY_C, 3)
    assert abs(dip[3] - 33.333) < 1e-2 and abs(dim[3] - 16.667) < 1e-2
    assert abs(dip[4] - 47.619) < 1e-2 and abs(dim[4] - 9.524) < 1e-2
    assert abs(adx[5] - 58.586) < 1e-2 and abs(adx[6] - 47.301) < 1e-2


def test_pct_rank_point_in_time():
    x = np.array([1.0, 5, 3, 4, 2, 6])
    out = M.pct_rank(x, 3)
    assert abs(out[3] - 2 / 3) < 1e-9 and abs(out[5] - 1.0) < 1e-9 and np.isnan(out[2])


# ---------------------------------------------------------------- costs (FORMULAS s13, fees.py)
def test_cost_is_12bp_from_fees_module():
    assert abs(M.COST12 - 0.0012) < 1e-12 and abs(M.COST6 - 0.0006) < 1e-12


def test_net_r_formula_s13():
    sm = dict(ret=np.array([0.01]), risk=np.array([1.0]), fund=np.array([0.0004]))      # long, funding paid 0.0004
    assert abs(M.net_r(sm, np.array([0]), M.COST12)[0] - 0.0084) < 1e-9
    sm["fund"] = np.array([-0.0004])                                                    # short receives
    assert abs(M.net_r(sm, np.array([0]), M.COST12)[0] - 0.0092) < 1e-9


# ---------------------------------------------------------------- simulator
def flat(n=80):
    return dict(o=np.full(n, 100.0), h=np.full(n, 100.2), l=np.full(n, 99.8), c=np.full(n, 100.0), atr=np.full(n, 1.0))


def sim(a, d, kind, nb=1):
    return M.simulate(a["o"], a["h"], a["l"], a["c"], a["atr"], d, kind, nb)


def test_simulate_stop_target_time():
    a = flat()
    a["l"][6] = 97.0                       # long stop 100-2.5=97.5 hit in bar 6
    r, rk, xi, xt = sim(a, 1, "T3R")
    assert abs(r[4] - (-0.025)) < 1e-9 and xi[4] == 6 and abs(rk[4] - 0.025) < 1e-9
    a = flat()
    a["h"][8] = 108.0                      # long target 107.5 hit
    r = sim(a, 1, "T3R")[0]
    assert abs(r[4] - 0.075) < 1e-9
    r = sim(a, -1, "T3R")[0]               # short: high 108 > stop 102.5
    assert abs(r[4] - (-0.025)) < 1e-9
    r, _, xi, _ = sim(flat(), 1, "T3R")    # nothing hit: time exit at close of the 30th bar, flat price -> 0
    assert abs(r[10]) < 1e-12 and xi[10] == 10 + 1 + 29
    assert np.isnan(r[75]) and xi[75] == -1        # not resolved before data end


def test_simulate_stop_gap_fills_at_open():
    a = flat()
    a["o"][6] = 95.0
    a["l"][6] = 94.0
    r = sim(a, 1, "T3R")[0]
    assert abs(r[4] - (-0.05)) < 1e-9       # worse of stop (97.5) and open (95)


def test_simulate_ride_exits_next_open():
    a = flat(60)
    a["c"][20] = 99.0                       # prior-10-bar low is 99.8, close 99 < it -> exit at open of bar 21
    a["o"][21] = 99.5
    r, _, xi, xt = sim(a, 1, "RIDE")
    assert abs(r[5] - (-0.005)) < 1e-9 and xi[5] == 20 and xt[5] == 21


def test_simulate_trail_locks_profit():
    n = 60
    a = flat(n)
    for j in range(2, 12):
        a["o"][j] = a["c"][j - 1]
        a["c"][j] = 100 + 1.0 * (j - 1)     # steady climb to 110
        a["h"][j] = a["c"][j] + 0.2
        a["l"][j] = a["o"][j] - 0.2
    a["o"][12:], a["c"][12:], a["h"][12:], a["l"][12:] = 105.0, 105.0, 105.2, 104.8
    r = sim(a, 1, "TRAIL")[0]
    assert r[0] > 0.0                        # trail exit above entry (best close 110 - 3*1 = 107 > 100)


def test_greedy_non_overlap():
    idx = np.array([1, 2, 5, 6, 9, 10])
    xg = np.array([4, 4, 7, 7, 12, 12])
    assert M.greedy(idx, xg).tolist() == [1, 5, 9]


def test_cluster_stats_hand():
    m, se, g = M.cluster_stats(np.array([1.0, 3, -1, -3]), np.array([1, 1, 2, 2]))
    assert abs(m) < 1e-12 and g == 2 and abs(se - 2.0) < 1e-9


def test_bh_adjust():
    q = M.bh_qvalues([0.001, 0.2], 2)
    assert abs(q[0] - 0.002) < 1e-12 and abs(q[1] - 0.2) < 1e-12
    assert abs(M.bh_qvalues([0.01], 100)[0] - 1.0) < 1e-12      # family size m enters


# ---------------------------------------------------------------- synthetic world for causality and planted edge
def make_world(n_days=1000, seed=3, plant=False):
    rng = np.random.default_rng(seed)
    t0 = M.day_num(2018, 6, 1) * 86400000
    data = {}
    for sym in ("BTC", "AAA"):
        n = n_days * 6
        ret = rng.normal(0, 0.012, n) + 0.0001
        c = 100 * np.exp(np.cumsum(ret))
        if plant and sym == "AAA":
            # planted ground truth: after a close above the prior 20-day high (126 bars), drift +1.5% per 4h bar for 6 bars
            ret = rng.normal(0, 0.012, n)
            c = np.empty(n)
            c[0] = 100.0
            left = 0
            for i in range(1, n):
                r = ret[i] + (0.015 if left > 0 else 0.0)
                left = max(left - 1, 0)
                c[i] = c[i - 1] * np.exp(r)
                if i > 125 and c[i] > c[i - 126:i].max() and left == 0:
                    left = 6
        o = np.r_[c[0], c[:-1]]
        sp = np.abs(rng.normal(0, 0.004, n)) * c
        h, l = np.maximum(o, c) + sp, np.minimum(o, c) - sp
        v = rng.uniform(100, 200, n)
        tbv = v * rng.uniform(0.4, 0.6, n)
        ts = (t0 + np.arange(n) * 4 * 3600000).astype(np.int64)
        s4 = dict(ts=ts, o=o, h=h, l=l, c=c, v=v, tbv=tbv)
        d = {k2: [] for k2 in ("ts", "o", "h", "l", "c", "v", "tbv")}
        for j in range(n_days):
            sl = slice(j * 6, j * 6 + 6)
            d["ts"].append(ts[j * 6])
            d["o"].append(o[sl][0])
            d["h"].append(h[sl].max())
            d["l"].append(l[sl].min())
            d["c"].append(c[sl][-1])
            d["v"].append(v[sl].sum())
            d["tbv"].append(tbv[sl].sum())
        s1 = {k2: np.array(v2) for k2, v2 in d.items()}
        s1["ts"] = s1["ts"].astype(np.int64)
        oi = (s1["ts"] + 86400000 - 1, 1000 * np.exp(np.cumsum(rng.normal(0, 0.03, n_days))))
        fts = ts[::2]
        fund = (fts.astype(np.int64), rng.normal(0.0001, 0.0002, len(fts)))
        data[sym] = dict(spot=s4, d1=s1, oi=oi, fund=fund)
    cd = np.arange(M.day_num(2018, 5, 1), M.day_num(2018, 6, 1) + n_days + 5)
    data["cycle"] = (cd.astype(np.int64), rng.uniform(-0.3, 0.6, len(cd)))
    return data


def cut_world(w, cut_ms):
    cd, cv = w["cycle"]
    keep = cd < cut_ms // 86400000
    out = {"cycle": (cd[keep], cv[keep])}
    for s in ("BTC", "AAA"):
        x = w[s]
        s4 = {k: v[x["spot"]["ts"] + 4 * 3600000 <= cut_ms] for k, v in x["spot"].items()}
        s1 = {k: v[x["d1"]["ts"] + 86400000 <= cut_ms] for k, v in x["d1"].items()}
        oi = (x["oi"][0][x["oi"][0] <= cut_ms], x["oi"][1][x["oi"][0] <= cut_ms])
        fu = (x["fund"][0][x["fund"][0] <= cut_ms], x["fund"][1][x["fund"][0] <= cut_ms])
        out[s] = dict(spot=s4, d1=s1, oi=oi, fund=fu)
    return out


def as_tf(w, tf):
    """build_frame reads the tf bars from data[sym]['spot']; for the daily frame that is the daily bar set."""
    if tf == "4h":
        return w
    return {k: (dict(v, spot=v["d1"]) if isinstance(v, dict) and "d1" in v else v) for k, v in w.items()}


def frames_equal(a, b, ncoin):
    for ci in range(ncoin):
        n = b.end[ci] - b.start[ci]
        for key in ("L", "S"):
            x = getattr(a, key)[:, a.start[ci]:a.start[ci] + n]
            y = getattr(b, key)[:, b.start[ci]:b.end[ci]]
            if not np.array_equal(x, y):
                return False, key
        pa = a.phase[a.start[ci]:a.start[ci] + n - 1]
        pb = b.phase[b.start[ci]:b.end[ci] - 1]
        if not np.array_equal(np.nan_to_num(pa, nan=9), np.nan_to_num(pb, nan=9)):
            return False, "phase"
    return True, ""


@pytest.mark.parametrize("tf", ["4h", "1d"])
def test_causality(tf):
    """Features and phase labels at bars before the cut must not change when later data is removed (fails under STUDY_BUG=1)."""
    w = make_world(700)
    full = M.build_frame(tf, ["BTC", "AAA"], data=as_tf(w, tf))
    t0 = w["BTC"]["spot"]["ts"][0]
    for cut_bar in (410 * 6 + 2, 520 * 6 + 3, 630 * 6 + 5):
        cut = int(t0 + cut_bar * 4 * 3600000)
        part = M.build_frame(tf, ["BTC", "AAA"], data=as_tf(cut_world(w, cut), tf))
        ok, what = frames_equal(full, part, 2)
        assert ok, f"{what} uses data after the cut"


def test_bug_flag_is_detected():
    env = dict(os.environ, STUDY_BUG="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", f"{__file__}::test_causality"],
                       env=env, capture_output=True, text=True, cwd=HERE)
    assert r.returncode != 0, "the causality test did not fail with look-ahead switched on"


def test_phase_label_uses_prior_close_only():
    w = make_world(450)
    ts, c = w["BTC"]["d1"]["ts"], w["BTC"]["d1"]["c"]
    tab = M.phase_table(ts, c, bug=False)
    d = int(len(c) * 0.8)
    tab2 = M.phase_table(ts[:d + 1], c[:d + 1], bug=False)
    assert tab2[0][d] == tab[0][d]
    a, b = tab2[1][d], tab[1][d]
    assert (np.isnan(a) and np.isnan(b)) or a == b
    # the label for day D is keyed D = (day of close) + 1: a bar on day D never sees the close of day D
    assert tab[0][d] == ts[d] // M.DAY + 1


# ---------------------------------------------------------------- planted edge: the miner finds it, and the same search on no-edge data does not
def best_t(plant):
    R.MIN_N = 30
    w = make_world(1200, seed=5, plant=plant)
    fr = M.build_frame("4h", ["BTC", "AAA"], data=w)
    brk = M.FIDX["BRK20"]
    allc = R.combos()
    cl = [c for c in allc if brk in c][:40] + [c for c in allc if brk not in c][:40]
    cells, _ = R.dev_search(fr, lambda s: None, cl)
    ts_ = [c["mean12"] / c["se12"] for c in cells if c["se12"] > 0]
    return max(ts_) if ts_ else 0.0


def test_planted_edge_found_and_null_quiet():
    t_plant = best_t(True)
    t_null = best_t(False)
    assert t_plant > 4.0, t_plant
    assert t_null < t_plant


# ---------------------------------------------------------------- independent scalar reference for the vectorised simulator
def naive(o, h, l, c, atr, s, d, kind, nb):
    """Bar-by-bar reference written from PRE_REG 'Trade management' (not from miner.simulate)."""
    n = len(c)
    H = {"T3R": 30, "TRAIL": 60, "RIDE": 60}[kind] * nb
    e = s + 1
    entry = o[e]
    S = max(2.5 * atr[s], 0.02 * entry)
    if not np.isfinite(S):
        return None
    stop = entry - d * S
    tgt = entry + d * 3 * S
    best, armed = entry, False
    for k in range(H):
        j = e + k
        if j >= n:
            return None
        adverse, favour = (l[j], h[j]) if d > 0 else (h[j], l[j])
        if d * (stop - adverse) >= 0:
            fill = stop if d * (o[j] - stop) >= 0 else o[j]
            return d * (fill - entry) / entry, j
        if kind == "T3R" and d * (favour - tgt) >= 0:
            return d * (tgt - entry) / entry, j
        if kind == "RIDE":
            lo = min(l[max(0, j - 10 * nb):j]) if d > 0 else max(h[max(0, j - 10 * nb):j])
            if j >= 10 * nb and d * (lo - c[j]) >= 0 and j + 1 < n:
                return d * (o[j + 1] - entry) / entry, j
        if k == H - 1:
            return d * (c[j] - entry) / entry, j
        if kind == "TRAIL":
            best = max(best, c[j]) if d > 0 else min(best, c[j])
            armed = armed or d * (c[j] - entry) >= S
            if armed and np.isfinite(atr[j]):
                cand = best - d * 3 * atr[j]
                stop = max(stop, cand) if d > 0 else min(stop, cand)
    return None


@pytest.mark.parametrize("kind", ["T3R", "TRAIL", "RIDE"])
@pytest.mark.parametrize("d", [1, -1])
def test_simulate_matches_naive_reference(kind, d):
    rng = np.random.default_rng(11)
    n = 700
    c = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.03, n)))
    o = np.r_[c[0], c[:-1]] * np.exp(rng.normal(0, 0.005, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.01, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.01, n)))
    atr = M.atr_sma(h, l, c, 14)
    r, rk, xi, xt = M.simulate(o, h, l, c, atr, d, kind, 1)
    bad = 0
    for s in range(20, n - 2):
        ref = naive(o, h, l, c, atr, s, d, kind, 1)
        if ref is None:
            assert xi[s] == -1 and np.isnan(r[s])
            continue
        assert abs(r[s] - ref[0]) < 1e-9 and xi[s] == ref[1], (s, r[s], ref)
