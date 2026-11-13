"""python -m pytest test_study.py.  Under STUDY_BUG=1 (look-ahead) the causality and no-edge tests must FAIL (test_bug_is_caught)."""
import os
import subprocess
import sys
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S  # noqa: E402
import run as R  # noqa: E402

T0 = 1704067200000  # 2024-01-01 00:00 UTC, a Monday


def synth(days=60, seed=5, jump=0.02):
    """5m random walk with volume; big jumps at the 00:00, 13:30 and Sunday 23:00 bars so gap / candle events exist."""
    n = days * 288
    r = np.random.default_rng(seed)
    ret = r.normal(0, 0.002, n)
    idx = np.arange(n)
    ev = (idx % 288 == 0) | (idx % 288 == S.NY_BAR) | ((idx // 288 + 0) % 7 == 6) & (idx % 288 == S.SUN_BAR)
    ret[ev] += r.normal(0, jump, ev.sum())
    c = 100 * np.exp(np.cumsum(ret))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.0007, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.0007, n)))
    v = r.uniform(1, 10, n)
    grid = T0 + idx.astype(np.int64) * S.MS5
    return grid, o, h, l, c, v


# ------------------------------------------------------------------------------------------ deterministic semantics
def test_vwap_anchor_reset():
    tp = np.array([10.0, 12, 11, 20, 22])
    v = np.array([1.0, 1, 2, 1, 0])
    gid = np.array([0, 0, 0, 1, 1])
    out = S.vwap(tp, v, gid)
    assert out[0] == 10 and out[1] == 11 and abs(out[2] - (10 + 12 + 22) / 4) < 1e-12
    assert out[3] == 20 and out[4] == 20          # zero extra volume keeps the group's VWAP


def test_hm_state_is_state_not_cross():
    c = synth(30)[4]
    r, e, w = S.hm_lines(c)
    s = S.hm_state(c)
    ok = ~np.isnan(w)
    assert ((s == 1) == (ok & (w < np.minimum(r, e)))).all()
    assert ((s == -1) == (ok & (w > np.maximum(r, e)))).all()
    s50 = S.hm_state(c, True)
    assert ((s50 == 1) <= (s == 1)).all() and (r[s50 == 1] > 50).all() and (r[s50 == -1] < 50).all()
    assert (s != 0).mean() > 0.2 and (s == 0).mean() > 0.02          # a state, present most of the time, with neutral gaps


def test_sim_cases():
    o = np.array([100, 100, 99, 98, 97, 100, 101, 102.0])
    h = np.array([100.5, 100.5, 99.5, 98.5, 97.5, 100.5, 102, 103.0])
    l = np.array([99.5, 99.5, 98.0, 96.0, 96.5, 99.5, 100.5, 101.5])
    # long entry bar 1 (open 100), S=1 -> stop 99; bar 2 opens 99 (stop touched at the open, fill 99): R = -1
    g, held, ent = S.sim(o, h, l, np.array([1]), np.array([1]), np.array([1.0]), np.array([4]))
    assert abs(g[0] + 1) < 1e-12 and held[0] == 2 and ent[0] == 100
    # long entry bar 1, S=3 -> stop 97; bar 3 low 96 breaks it; bar 3 opens 98 > stop so fill 97: R = -1
    g, held, ent = S.sim(o, h, l, np.array([1]), np.array([1]), np.array([3.0]), np.array([4]))
    assert abs(g[0] + 1) < 1e-12 and held[0] == 3
    # gap through the stop: S=0.8 -> stop 99.2; bar 2 opens 99 < 99.2 -> fills at the open 99 (worse): R = -1.25
    g, held, _ = S.sim(o, h, l, np.array([1]), np.array([1]), np.array([0.8]), np.array([4]))
    assert abs(g[0] + 1.25) < 1e-12 and held[0] == 2
    # short entry bar 4 (open 97), S=2 -> stop 99; bar 5 high 100.5 breaks it and opens 100 > 99 -> fill 100: R = -1.5
    g, held, _ = S.sim(o, h, l, np.array([4]), np.array([-1]), np.array([2.0]), np.array([3]))
    assert abs(g[0] + 1.5) < 1e-12 and held[0] == 2
    # time exit: long entry bar 5 (open 100), S=5, tlen 2 -> exit at open of bar 7 (102): R = +0.4
    g, held, _ = S.sim(o, h, l, np.array([5]), np.array([1]), np.array([5.0]), np.array([2]))
    assert abs(g[0] - 0.4) < 1e-12 and held[0] == 2


def test_sim_long_hold_stages():
    n = 3000
    o = np.full(n, 100.0)
    h = np.full(n, 100.0)
    l = np.full(n, 100.0)
    l[1500] = 90.0
    g, held, _ = S.sim(o, h, l, np.array([10, 10]), np.array([1, 1]), np.array([5.0, 5.0]), np.array([2000, 1000]))
    assert g[0] == -1 and held[0] == 1491 and g[1] == 0 and held[1] == 1000


def test_cme_gap_proxy_alignment():
    G, o, h, l, c, v = synth(30, seed=2, jump=0.0)
    B = S.prep(G, o, h, l, c, v)
    # day 5 is Saturday 2024-01-06? day0 Monday: day 6 = Sunday. Friday = day 4; its 21:55 bar close is the reference.
    ev = S.b_events(B, "cme")
    assert (ev["q"] % 288 == S.SUN_BAR).all() and ((ev["q"] // 288) % 7 == 6).all()
    k = 0
    q = ev["q"][k]
    ref = (q // 288 - 2) * 288 + S.FRI_REF
    assert abs(ev["gap"][k] - (o[q] - c[ref]) / B["atrd5"][q - 1]) < 1e-12
    # reference bar is the 21:55-22:00 Friday bar
    assert ((G[ref] - T0) % 86400000) == (21 * 3600 + 55 * 60) * 1000 and ((G[ref] - T0) // 86400000) % 7 == 4
    assert ((G[q] - T0) % 86400000) == 23 * 3600 * 1000 and ((G[q] - T0) // 86400000) % 7 == 6


def test_outside_frac():
    hi, lo = np.array([105.0, 100.0]), np.array([95.0, 90.0])
    up, dn = np.array([100.0, 100.0]), np.array([97.0, 95.0])
    f = S._outside_frac(hi, lo, up, dn, np.array([1, -1]))
    assert abs(f[0] - 0.5) < 1e-12 and abs(f[1] - 0.5) < 1e-12


def test_phase_labels_trend_and_range():
    r = np.random.default_rng(1)
    nd = 200
    up = 100 * np.exp(np.cumsum(r.normal(0.01, 0.006, nd)))
    dn = 100 * np.exp(np.cumsum(r.normal(-0.01, 0.006, nd)))
    rg = 100 + r.normal(0, 0.5, nd)
    out = {}
    for name, d in (("up", up), ("dn", dn), ("rg", rg)):
        c5 = np.repeat(d, 288)
        h5, l5 = c5 * 1.002, c5 * 0.998
        ph = S.daily_phase(h5, l5, c5)
        assert len(ph) == nd + 1 and ph[0] == 0 and (ph[:41] == 0).all()
        out[name] = np.bincount(ph[60:], minlength=4) / len(ph[60:])
    assert out["up"][1] > 0.6 and out["dn"][2] > 0.6 and out["rg"][3] > 0.5


def test_phase_uses_prior_close_only():
    r = np.random.default_rng(4)
    nd = 120
    d = 100 * np.exp(np.cumsum(r.normal(0.003, 0.01, nd)))
    c5 = np.repeat(d, 288)
    full = S.daily_phase(c5 * 1.003, c5 * 0.997, c5)
    cut = 90
    part = S.daily_phase(c5[:cut * 288] * 1.003, c5[:cut * 288] * 0.997, c5[:cut * 288])
    assert (full[:cut + 1] == part).all()


def test_cycle_flag_uses_prior_close():
    ts = (np.arange(1600) + 17000) * 86400000
    close = np.concatenate([np.linspace(100, 200, 1450), np.full(150, 10.0)])
    day0, flag, full, sma = S.cycle_by_day(ts, close)
    assert flag[1399] == 0 and flag[1400] == 1          # first SMA exists after 1400 closes; index D = flag from close of D-1
    assert flag[1450] == 1                               # close of day 1449 (200) above the SMA: bull
    assert flag[1451] == 2                               # close of day 1450 (10) below the SMA: bear, known only from day 1451


def test_bh_and_stats():
    ok = R.bh([0.001, 0.01, 0.04, 0.2, 1.0])
    assert ok.tolist() == [True, True, False, False, False] or ok.tolist() == [True, True, True, False, False]
    # q=0.05, m=5: thresholds 0.01, 0.02, 0.03, 0.04, 0.05 -> p 0.001 yes, 0.01 yes, 0.04 > 0.03 no
    assert ok.tolist() == [True, True, False, False, False]
    x = np.array([1.0, -1.0, 2.0, -0.5])
    day = np.array([1, 1, 2, 2])
    st = R.stats(x, day, np.random.default_rng(1), 200)
    assert st["n"] == 4 and abs(st["mean"] - 0.375) < 1e-12 and st["days"] == 2


# ------------------------------------------------------------------------------------------ causality (fail under STUDY_BUG=1)
def test_primitives_prefix_causal():
    G, o, h, l, c, v = synth(40)
    full_hm = S.hm_state(c)
    full_h50 = S.hm_state(c, True)
    fu, fl = S.bollinger(c)
    for cut in range(3000, 11000, 97):
        assert (S.hm_state(c[:cut + 1])[cut] == full_hm[cut]) and (S.hm_state(c[:cut + 1], True)[cut] == full_h50[cut]), cut
        u, lo = S.bollinger(c[:cut + 1])
        assert u[cut] == fu[cut] and lo[cut] == fl[cut], cut


def _prefix_equal(sig_fn, G, o, h, l, c, v, cuts):
    Bf = S.prep(G, o, h, l, c, v)
    full = sig_fn(Bf)
    for cut in cuts:
        B = S.prep(G[:cut], o[:cut], h[:cut], l[:cut], c[:cut], v[:cut])
        part = sig_fn(B)
        ref = {x for x in full if x[0] <= cut - 1}
        assert part == ref, (cut, sorted(part ^ ref)[:5])


def test_a_signals_prefix_causal():
    G, o, h, l, c, v = synth(45, seed=8)
    cuts = list(range(288 * 20 + 7, 288 * 45 - 5, 211))

    def sig(B):
        out = set()
        for anchor in ("U", "N"):
            for frame in ("I", "P"):
                m, d = S.a_signals(B, anchor, frame, 0)
                out |= {(int(a), int(b), anchor, frame) for a, b in zip(m, d)}
        return out
    assert len(sig(S.prep(G, o, h, l, c, v))) > 200
    _prefix_equal(sig, G, o, h, l, c, v, cuts)


def test_b_signals_prefix_causal():
    G, o, h, l, c, v = synth(300, seed=11, jump=0.03)
    Bf = S.prep(G, o, h, l, c, v)

    def sig_for(B):
        out = set()
        for src in ("cme", "s0000", "s1330"):
            ev = S.b_events(B, src)
            for rule in ("st", "gp", "gd"):
                m, d, vw = S.b_signals(B, ev, 0.3, rule)
                out |= {(int(a), int(b), src, rule) for a, b in zip(m, d)}
        return out
    full = sig_for(Bf)
    rules = {x[3] for x in full}
    assert {"st", "gp"} <= rules and len(full) > 30, (len(full), rules)
    cuts = [288 * k + 17 for k in range(120, 299, 6)] + [288 * k + S.NY_BAR + 3 for k in range(130, 299, 9)]
    for cut in cuts:
        B = S.prep(G[:cut], o[:cut], h[:cut], l[:cut], c[:cut], v[:cut])
        ref = {x for x in full if x[0] <= cut - 1}
        part = {x for x in sig_for(B) if x[0] <= cut - 1}      # signals past the data end are clipped-window artefacts; finish() drops them
        assert part == ref, cut


def test_no_edge_on_random_walk():
    G, o, h, l, c, v = synth(700, seed=3, jump=0.0)
    B = S.prep(G, o, h, l, c, v)
    t = S.a_trades(B, "U", "I", 0)
    g = t["g"]
    assert len(g) > 3000, len(g)
    tstat = g.mean() / (g.std() / np.sqrt(len(g)))
    assert abs(tstat) < 4, tstat


def test_a_gross_planted_edge_is_detected():
    """Plant a real edge: after each entry the price drifts with the trade (30m trend persistence): the engine must see gross R > 0."""
    G, o, h, l, c, v = synth(200, seed=6, jump=0.0)
    B = S.prep(G, o, h, l, c, v)
    m, d = S.a_signals(B, "U", "I", 0)
    ret = np.diff(np.log(c), prepend=np.log(c[0]))
    for mm, dd in zip(m, d):                                   # tilt the 12 bars after every entry bar in its direction
        if mm + 14 < len(ret):
            ret[mm + 1: mm + 13] += dd * 0.0015
    c2 = 100 * np.exp(np.cumsum(ret))
    o2 = np.concatenate([[100.0], c2[:-1]])
    h2, l2 = np.maximum(o2, c2) * 1.0007, np.minimum(o2, c2) * 0.9993
    B2 = S.prep(G, o2, h2, l2, c2, v)
    t = S.a_trades(B2, "U", "I", 0)
    assert len(t["g"]) > 300 and t["g"].mean() > 0.02


def test_bug_is_caught():
    if os.environ.get("STUDY_BUG") == "1":
        pytest.skip("inner run")
    env = dict(os.environ, STUDY_BUG="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", os.path.join(HERE, "test_study.py"),
                        "-k", "primitives_prefix or a_signals_prefix or b_signals_prefix or no_edge"], env=env, cwd=HERE, capture_output=True, text=True)
    assert r.returncode != 0, r.stdout[-500:]
