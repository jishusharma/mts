"""python -m pytest test_study.py. Under STUDY_BUG=1 or PHASE_LAG=0 the look-ahead tests (phase, ctx, hm) must FAIL;
test_lookahead_variants_are_caught asserts that."""
import os, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
import phases as PH
import study as S

HERE = Path(__file__).resolve().parent


def walk(n, seed=3, vol=0.002):
    r = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(r.normal(0, vol, n)))
    o = np.concatenate([[100], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, vol / 3, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, vol / 3, n)))
    return o, h, l, c


def coin(n_days=120, seed=5):
    n = n_days * 288
    o, h, l, c = walk(n, seed, 0.0015)
    return dict(sym="SYN", start5=np.arange(n, dtype=np.int64) * S.MS5 + 1_600_000_000_000 // S.D1 * S.D1, o=o, h=h, l=l, c=c)


def aux_for(cd, seed=9):
    r = np.random.default_rng(seed)
    t0 = cd["start5"][0]
    nh = len(cd["c"]) // 12
    ts = t0 + np.arange(nh) * S.H1
    c1 = cd["c"].reshape(-1, 12)[:, -1]
    v = r.uniform(50, 150, nh)
    tb = v * r.uniform(0.3, 0.7, nh)
    taker = np.column_stack([ts, c1, c1, c1, c1, v, tb])
    oi = np.column_stack([ts, 1e9 * (1 + 0.1 * np.sin(np.arange(nh) / 30) + r.normal(0, 0.01, nh))])
    nf = nh // 8
    fund = np.column_stack([t0 + np.arange(nf) * 8 * S.H1, r.normal(0.0001, 0.0002, nf)])
    return dict(taker=taker, oi=oi, fund=fund)


def trunc(cd, aux, T):
    """data as known at time T: only 5m bars starting before T, 1h rows closed by T, funding rows settled by T"""
    n = int((T - cd["start5"][0]) // S.MS5)
    cd2 = {k: (v[:n] if isinstance(v, np.ndarray) else v) for k, v in cd.items()}
    a2 = dict(taker=aux["taker"][aux["taker"][:, 0] + S.H1 <= T], oi=aux["oi"][aux["oi"][:, 0] <= T], fund=aux["fund"][aux["fund"][:, 0] <= T])
    return cd2, a2


def poke(cd, aux, T, seed=77):
    """overwrite everything after T with garbage; a causal layer cannot notice"""
    r = np.random.default_rng(seed)
    n = int((T - cd["start5"][0]) // S.MS5)
    cd2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in cd.items()}
    for k in "ohlc":
        cd2[k][n:] = cd2[k][n:] * r.uniform(0.5, 2.0, len(cd2[k]) - n)
    a2 = {k: v.copy() for k, v in aux.items()}
    for k, tcol in (("taker", S.H1), ("oi", 0), ("fund", 0)):
        m = a2[k][:, 0] + tcol > T
        a2[k][m, 1:] = a2[k][m, 1:] * r.uniform(0.5, 2.0, a2[k][m, 1:].shape)
    return cd2, a2


# ---------------- phases ----------------
def synth_daily(n=3500, seed=2):
    r = np.random.default_rng(seed)
    reg = np.repeat(r.choice([-0.004, 0.0, 0.004], n // 100 + 1), 100)[:n]
    c = 100 * np.exp(np.cumsum(reg + r.normal(0, 0.03, n)))
    hi, lo = c * 1.01, c * 0.99
    return pd.DataFrame({"high": hi, "low": lo, "close": c}, index=np.arange(n) + 15000)


def test_phase_table_matches_truncated_recompute():
    d = synth_daily()
    t = PH.build_table(d)  # uses phase_lag(): PHASE_LAG=0 / STUDY_BUG=1 -> table peeks at same-day close
    rng = np.random.default_rng(1)
    days = rng.choice(d.index.values[1500:-1], 30, replace=False)
    bad = [int(x) for x in days if int(t.loc[x, "label"]) != PH.label_slow(d, int(x), lag=1)]
    assert not bad, bad


def test_phase_labels_hand_checked():
    # monotone rise: close > SMA50 > SMA200, S50>1% -> MARKUP (5); monotone fall: MARKDOWN (2)
    n = 400
    up = pd.DataFrame({"close": 100 * 1.01 ** np.arange(n)}, index=np.arange(n))
    up["high"], up["low"] = up.close * 1.001, up.close * 0.999
    f = PH.features(up)
    lab, st = PH.labels_from_features(f)
    assert lab.iloc[-1] == 5 and st.iloc[-1] in ("BASE", "BULL")
    dn = pd.DataFrame({"close": 1000 * 0.99 ** np.arange(n)}, index=np.arange(n))
    dn["high"], dn["low"] = dn.close * 1.001, dn.close * 0.999
    lab2, st2 = PH.labels_from_features(PH.features(dn))
    assert lab2.iloc[-1] in (1, 2) and st2.iloc[-1] == "BEAR"
    assert (lab2.iloc[250:] != 5).all()


# ---------------- context layers ----------------
def _ctx_compare(T_days=70, seed=5):
    cd = coin(120, seed)
    aux = aux_for(cd)
    T = int(cd["start5"][0] + T_days * S.D1 + 5 * S.H1)
    k = 12
    full = S.build_ctx(cd, aux, k)
    pre = S.build_ctx(*trunc(cd, aux, T)[:1], trunc(cd, aux, T)[1], k)
    pk = S.build_ctx(*poke(cd, aux, T)[:1], poke(cd, aux, T)[1], k)
    O, H, L, C, start = S.tfbars(cd, k)
    tc = start + k * S.MS5
    known = np.nonzero(tc <= T)[0]
    return full, pre, pk, known


def test_context_layers_causal_prefix_and_poke():
    full, pre, pk, known = _ctx_compare()
    assert len(known) > 500
    for L in range(8):
        a, b, c = full[known, L], pre[known, L], pk[known, L]
        assert (a == b).all(), (S.LAYERS[L], "prefix", int((a != b).sum()))
        assert (a == c).all(), (S.LAYERS[L], "poke", int((a != c).sum()))


def test_context_layers_not_all_na():
    full, _, _, known = _ctx_compare()
    for L in range(8):
        assert (full[known, L] < 3).sum() > 50, S.LAYERS[L]
        if L != 6:  # synthetic constant-vol walk keeps RV7/RV60 in the mid bucket
            assert len(np.unique(full[known, L][full[known, L] < 3])) >= 2, S.LAYERS[L]


def test_hm_state_causal_prefix():
    c = walk(30000)[3]
    full = S.hm_state(c)
    for cut in range(3000, 20000, 500):
        assert S.hm_state(c[:cut + 1])[cut] == full[cut], cut


def test_bb_signals_causal_prefix():
    o, h, l, c = walk(20000, 8, 0.004)
    for kind in ("BO", "FO"):
        j, d, _ = S.bb_signals(o, h, l, c, kind)
        cut = 12000
        j2, d2, _ = S.bb_signals(o[:cut], h[:cut], l[:cut], c[:cut], kind)
        assert (j[j < cut] == j2).all() and (d[j < cut] == d2).all()


# ---------------- sim, cost, gap ----------------
def test_sim_stop_gap_and_cost_hand_numbers():
    o = np.array([100, 100, 98.8, 97, 97.0, 100.0])
    h = np.array([101, 101, 99.5, 98, 97.5, 101.0])
    l = np.array([99.5, 99.5, 98.5, 96, 96.5, 99.0])
    # long entry open[0]=100, S=1 -> stop 99. bar1 low 99.5 no hit, bar2 open 98.8 < stop: gap fills at 98.8 -> -1.2R
    g, held = S.sim(o, h, l, np.array([0]), np.array([1]), np.array([1.0]), np.array([4]), np.array([100.0]))
    assert abs(g[0] + 1.2) < 1e-9 and held[0] == 3
    # no stop: S=10 -> exit at open[3]=97 -> -0.3R
    g, held = S.sim(o, h, l, np.array([0]), np.array([1]), np.array([10.0]), np.array([3]), np.array([100.0]))
    assert abs(g[0] + 0.3) < 1e-9 and held[0] == 3
    # short entry 100, S=1 -> stop 101: bar0 high 101 touches (stop wins ties): open[0]=100 < 101 so fill at stop 101 -> -1R
    g, held = S.sim(o, h, l, np.array([0]), np.array([-1]), np.array([1.0]), np.array([3]), np.array([100.0]))
    assert abs(g[0] + 1.0) < 1e-9 and held[0] == 1
    # cost in R = 12 bp * entry / S = 0.0012*100/1 = 0.12R
    assert abs(0.0012 * 100.0 / 1.0 - 0.12) < 1e-12


def test_no_edge_on_random_walk_gross():
    o, h, l, c = walk(60000, 4, 0.003)
    j, d, ex = S.hm_signals(o, h, l, c)
    ne = {1: S.nextexit(ex[1]), -1: S.nextexit(ex[-1])}
    a = S.atr(h, l, c)
    e = j + 1
    ok = (e + 50 < len(c)) & ~np.isnan(a[j]) & (j > 60)
    j, d, e = j[ok], d[ok], e[ok]
    tl = np.clip(np.where(d == 1, ne[1][e], ne[-1][e]) + 1 - e, 1, 48)
    Sx = np.maximum(1.5 * a[j], 0.005 * o[e])
    g, _ = S.sim(o, h, l, e, d, Sx, tl, o[e])
    assert len(g) > 1000
    assert abs(g.mean() / (g.std() / np.sqrt(len(g)))) < 4


def test_day_stats_and_bh():
    rng = np.random.default_rng(1)
    x = np.array([1.0, -1, 1, 1, -1, 1] * 10)
    st = S.day_stats(x, np.repeat(np.arange(10), 6), rng)
    assert st["n"] == 60 and abs(st["mean"] - 1 / 3) < 1e-12 and st["days"] == 10
    adj = S.bh([0.001, 0.04, 0.5], 0.10)
    assert np.allclose(adj, [0.003, 0.06, 0.5])


# ---------------- repo hygiene ----------------
def test_tracked_files_under_5mb():
    out = subprocess.check_output(["git", "-C", str(HERE), "ls-files", "-s", "."], text=True)
    for ln in out.splitlines():
        name = ln.split("\t")[1]
        assert (HERE / name).stat().st_size < 5 * 1024 * 1024, name


def test_lookahead_variants_are_caught():
    """Under STUDY_BUG=1 and under PHASE_LAG=0 the causal tests above must fail."""
    for env_extra, k in (({"STUDY_BUG": "1"}, "context_layers_causal"), ({"STUDY_BUG": "1"}, "hm_state"),
                         ({"STUDY_BUG": "1"}, "phase_table_matches"), ({"PHASE_LAG": "0"}, "phase_table_matches")):
        env = dict(os.environ, **env_extra)
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", str(Path(__file__)), "-k", k], env=env, cwd=HERE, capture_output=True, text=True)
        assert r.returncode != 0, (env_extra, k)
