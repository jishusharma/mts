"""Tests for nkp4. The look-ahead tests must FAIL under STUDY_BUG=1 (and PHASE_LAG=0): run
`STUDY_BUG=1 python -m pytest test_nkp4_study.py` to see red. test_bug_is_detected proves the detectors detect."""
import os, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nkp4_phases as PH, nkp4_study as ST, nkp4_stats as SS

M15, H1, D1 = ST.M15, ST.H1, ST.D1
T0 = 1_600_000_000_000 // D1 * D1


def synth(days=130, seed=1):
    rng = np.random.default_rng(seed)
    n = days * 96
    ts = T0 + np.arange(n, dtype=np.int64) * M15
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.004, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.003, n)); l = np.minimum(o, c) * (1 - rng.uniform(0, 0.003, n))
    D = dict(ts=ts, o=o, h=h, l=l, c=c, v=rng.uniform(1, 2, n))
    nh = days * 24
    hts = T0 + np.arange(nh, dtype=np.int64) * H1
    hc = c[3::4][:nh]; v = rng.uniform(100, 200, nh)
    aux = dict(h1=dict(ts=hts, c=hc, v=v, tb=v * rng.uniform(0.3, 0.7, nh)),
               oi=dict(ts=hts, oi=1e6 * np.exp(np.cumsum(rng.normal(0, 0.01, nh)))),
               fund=dict(ts=T0 + np.arange(days * 3, dtype=np.int64) * 8 * H1, fr=rng.normal(0.0001, 0.0003, days * 3)))
    return D, aux


def poke(D, aux, i):
    """Replace everything that is NOT yet known at the close of 15m bar i by wild values."""
    tc = D["ts"][i] + M15
    D2 = {k: v.copy() for k, v in D.items()}
    fut = D2["ts"] > D["ts"][i]
    for k in ("o", "h", "l", "c", "v"):
        D2[k][fut] = D2[k][fut] * 5.0 + 3.0
    a2 = {k: {kk: vv.copy() for kk, vv in v.items()} for k, v in aux.items()}
    m = a2["h1"]["ts"] > tc - H1
    for k in ("c", "v", "tb"):
        a2["h1"][k][m] = a2["h1"][k][m] * 7.0 + 1.0
    a2["oi"]["oi"][a2["oi"]["ts"] > tc] *= 3.0
    a2["fund"]["fr"][a2["fund"]["ts"] > tc] += 0.01
    return D2, a2


def count_changed_layers(seed=1):
    D, aux = synth(seed=seed)
    base = ST.context(D, aux)
    nk_l, nk_s, _ = ST.nk_layers(D)
    changed = set(); nk_changed = 0
    for i in (6000, 6003, 7777, 8101, 9000, 9500):
        D2, a2 = poke(D, aux, i)
        c2 = ST.context(D2, a2)
        for li in range(8):
            if c2[li, i] != base[li, i]:
                changed.add(li)
        l2, s2, _ = ST.nk_layers(D2)
        nk_changed += int((l2[:, i] != nk_l[:, i]).sum() + (s2[:, i] != nk_s[:, i]).sum())
    return changed, nk_changed


def test_context_layers_use_no_future_bars():
    changed, nk_changed = count_changed_layers()
    assert not changed, f"context layers {sorted(changed)} read future data"
    assert nk_changed == 0


def test_every_context_layer_has_data_in_synth():
    D, aux = synth()
    ctx = ST.context(D, aux)
    for li in range(8):
        assert (ctx[li] >= 0).any(), ST.LAYERS[li]


def test_phase_label_ignores_same_day_close():
    daily, _ = PH.load_btc_daily()
    base = PH.phase_table(daily)["label"]
    rng = np.random.default_rng(3)
    days = base.loc["2019-06-01":"2026-10-01"].dropna().index
    for d in rng.choice(days, 40, replace=False):
        for mult in (0.55, 1.7):
            d2 = daily.copy()
            d2.loc[d, ["high", "low", "close"]] = d2.loc[d, ["high", "low", "close"]] * mult
            lab = PH.phase_table(d2).loc[d, "label"]
            assert lab == base.loc[d], f"phase at {pd.Timestamp(d).date()} changed when same-day close changed (mult {mult})"


def test_phase_lag_zero_is_the_bug():
    daily, _ = PH.load_btc_daily()
    a = PH.phase_table(daily, lag=0)["label"]
    rng = np.random.default_rng(3)
    days = a.loc["2019-06-01":"2026-10-01"].dropna().index
    hit = 0
    for d in rng.choice(days, 40, replace=False):
        d2 = daily.copy(); d2.loc[d, ["high", "low", "close"]] *= 0.55
        hit += PH.phase_table(d2, lag=0).loc[d, "label"] != a.loc[d]
    assert hit > 0     # with PHASE_LAG=0 the label does depend on the same-day close


def test_bug_is_detected():
    code = ("import sys; sys.path.insert(0, r'%s'); import test_nkp4_study as T; ch, nk = T.count_changed_layers(); "
            "print(len(ch)); sys.exit(0 if len(ch) > 0 else 1)" % HERE)
    env = dict(os.environ, STUDY_BUG="1")
    r = subprocess.run([sys.executable, "-W", "ignore", "-c", code], env=env, capture_output=True, text=True)
    assert r.returncode == 0, "STUDY_BUG look-ahead was NOT detected by the layer poke test: " + r.stdout + r.stderr


def test_simulate_gap_and_priority():
    n = 60
    ts = T0 + np.arange(n, dtype=np.int64) * M15
    o = np.full(n, 100.0); h = np.full(n, 100.2); l = np.full(n, 99.8); c = np.full(n, 100.0)
    o[3] = 98.0; l[3] = 97.0; h[3] = 98.1; c[3] = 97.5            # gap through the stop at bar 3
    D = dict(ts=ts, o=o, h=h, l=l, c=c, v=np.ones(n))
    atr = np.full(n, 0.5)
    res, feeR, ex, _ = ST.simulate(D, atr, 1)
    # signal bar 1: entry open[2]=100, S=max(0.5, 0.5)=0.5, stop 99.5; bar 3 opens at 98 -> filled at 98 => -4R
    assert res[1] == pytest.approx(-4.0)
    assert feeR[1] == pytest.approx(1e-4 * 100 / 0.5)
    res_s, _, _, _ = ST.simulate(D, atr, -1)
    assert res_s[1] == pytest.approx(TGT := ST.TGT_R) or res_s[1] > 0   # short wins on the gap


def test_maker_fill_model_drops_unfilled():
    n = 60
    ts = T0 + np.arange(n, dtype=np.int64) * M15
    c = np.full(n, 100.0); o = c.copy(); h = c + 0.1; l = c - 0.1
    l[2] = 100.05   # bar i+1 never trades down to the limit at 100 -> long limit not filled (i=1)
    D = dict(ts=ts, o=o, h=h, l=l, c=c, v=np.ones(n))
    _, _, _, fill = ST.simulate(D, np.full(n, 0.5), 1, maker=True)
    assert not fill[1] and fill[5]


def test_cluster_and_bh():
    rng = np.random.default_rng(0)
    day = np.repeat(np.arange(100), 5); x = rng.normal(0.3, 1.0, 500)
    r = SS.cluster(day, x, rng)
    assert r["lo95"] < r["mean"] < r["hi95"] and r["p"] < 0.05
    q = SS.bh([0.001, 0.2, 0.04])
    assert q[0] <= q[2] <= q[1] and q.max() <= 1


def test_rule_family_size():
    assert len(ST.RULES) == 9 and len(ST.LAYERS) == 8 and len(PH.LABELS) == 6
    assert sum(len(v) for v in ST.BUCKETS.values()) == 24


def test_shared_phase_table_verified():
    assert PH.verify_phase(30, seed=5) == []


def test_files_under_5mb():
    root = HERE.parents[2]
    files = subprocess.check_output(["git", "-C", str(root), "ls-files", str(HERE)], text=True).split()
    for f in files:
        p = root / f
        if p.exists():
            assert p.stat().st_size < 5 * 1024 * 1024, f
