"""Tests for nkp2-levels-phase-1114. Run: python -m pytest test_study.py -q
Look-ahead tests MUST FAIL under STUDY_BUG=1 (phase / pivots use the same day's close), PHASE_LAG=0 (same-day phase), STUDY_BUG=2 (HTF context from the bar containing the signal bar).
These tests compute labels, signals and context only: no trade outcome is computed here."""
import os, sys, subprocess, copy
from pathlib import Path
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mts_phase as mp
import ctxlib as cx
import nkcore as nk

DAY = 86400000
needs_data = pytest.mark.skipif(not (nk.SPOT / "BTCUSDT_15m.npz").exists() or not mp.PHASE_CSV.exists(), reason="data cache not present")


def btc_daily():
    return mp.load_btc_daily()


@needs_data
def test_phase_lag_causal():
    """label for day D from data truncated at D-1 equals the full-series label; PHASE_LAG=0 cannot be reproduced from D-1 data -> FAILS."""
    d, h, l, c = btc_daily()
    dl, lab, st, F = mp.day_labels(d, h, l, c)
    rng = np.random.default_rng(5)
    days = rng.choice(np.flatnonzero(d > d[0] + 1600), 25, replace=False)
    for k in days:
        day = int(d[k])
        m = d <= day - 1  # only data through the previous close
        got = mp.label_for_day(d[m], h[m], l[m], c[m], day)
        full = int(lab[np.searchsorted(dl, day)]) if day in set(dl.tolist()) else 0
        assert got == full, (day, got, full)


@needs_data
def test_phase_csv_matches_recompute_30_days():
    """verify_phase: 30 random csv days equal an independent recomputation from truncated data (lag 1)."""
    d, h, l, c = btc_daily()
    m_csv = mp.read_phase_csv()
    rng = np.random.default_rng(11)
    days = rng.choice(sorted(m_csv), 30, replace=False)
    for day in days:
        m = d <= day - 1
        assert mp.label_for_day(d[m], h[m], l[m], c[m], int(day), lag=1) == m_csv[int(day)], int(day)


@needs_data
def test_bar_phase_matches_truncated_btc():
    """phase attached to 1h bars equals the label recomputed from BTC daily data truncated before the bar's day. FAILS under STUDY_BUG=1."""
    d, h, l, c = btc_daily()
    pdays, plab = mp.phase_table_for_study()
    t1 = (np.arange(60) * 37 + 40000) * 3600000 + int(1.55e12) // 3600000 * 3600000
    ph = nk.phase_for_bars(t1, pdays, plab)
    for t, p in zip(t1, ph):
        day = int(t // DAY)
        m = d <= day - 1
        assert mp.label_for_day(d[m], h[m], l[m], c[m], day, lag=1) == p, (day, p)


def _cut_raw(raw, cut):
    r = {k: (v[raw["t"] < cut] if k in "tohlcv" and len(k) == 1 else v) for k, v in raw.items()}
    return r


def _slice_raw(coin="BTC", cut_day_offset=300, span_days=900):
    raw = nk.load_raw(coin)
    t = raw["t"]
    end = (t[-1] // DAY - cut_day_offset) * DAY  # cut at a UTC midnight
    start = end - span_days * DAY
    m = (t >= start) & (t < end + 120 * DAY)
    r = {k: raw[k][m] for k in "t o h l c v".split()}
    for k in ("kl", "fund", "oi"):
        if k in raw:
            r[k] = {x: y for x, y in raw[k].items()}
    return r, int(end)


def _poke(r, cut, f=7.0):
    p = copy.deepcopy(r)
    m = p["t"] >= cut
    for k in "o h l c".split():
        p[k] = np.where(m, p[k] * f, p[k])
    p["v"] = np.where(m, p["v"] * 5.0, p["v"])
    if "kl" in p:
        mm = p["kl"]["ts"] >= cut
        for k in ("o", "h", "l", "c", "v", "tbv"):
            p["kl"][k] = np.where(mm, p["kl"][k] * (9.0 if k != "tbv" else 0.0), p["kl"][k])
    if "fund" in p:
        mm = p["fund"]["ts"] > cut
        p["fund"]["rate"] = np.where(mm, 0.005, p["fund"]["rate"])
    if "oi" in p:
        mm = p["oi"]["ts"] >= cut
        p["oi"]["oi_value"] = np.where(mm, p["oi"]["oi_value"] * 9.0, p["oi"]["oi_value"])
    return p


@needs_data
@pytest.mark.parametrize("li", range(8))
def test_context_layer_ignores_future_bars(li):
    """future-bar poke: corrupting every bar at/after the cut must not change any context bucket of 1h bars closed by the cut. C1-C3 FAIL under STUDY_BUG=2."""
    r, cut = _slice_raw()
    cut += 22 * 3600000  # cut INSIDE the 4h and daily bars: a bar-in-progress leak shows up here
    name = cx.LAYERS[li]
    base = cx.compute_context(r)
    ok = base["t1"] + cx.H1 <= cut
    assert ok.sum() > 1000
    a = base["ctx"][li][ok]
    if (a >= 0).sum() == 0 and li in (3, 4, 5):
        pytest.skip(f"{name}: no data for BTC in the slice")
    for f in (7.0, 1 / 7.0):  # a spike up and a crash down after the cut
        b = cx.compute_context(_poke(r, cut, f))["ctx"][li][ok]
        assert (a == b).all(), f"{name} x{f:.2f}: {(a != b).sum()} buckets changed by future bars"


@needs_data
def test_signals_truncation_invariant():
    """signals and breakout events computed on data cut at a UTC midnight equal the full-data ones before the cut. FAILS under STUDY_BUG=1 (same-day pivots)."""
    r, cut = _slice_raw()
    cut += 10 * 3600000  # cut inside a UTC day: its daily bar is incomplete in the truncated data
    pdays, plab = mp.phase_table_for_study()
    Df = nk.prep("BTC", pdays, plab, raw=r)
    Dc = nk.prep("BTC", pdays, plab, raw=_cut_raw(r, cut))
    nc = len(Dc["t"])
    assert (Df["t"][:nc] == Dc["t"]).all()
    # levels / validity / phase / context of every bar up to the cut (including the cut day) must not depend on later data
    assert (Df["valid"][:nc] == Dc["valid"][:nc]).all()
    okv = Df["valid"][:nc]
    for k in nk.LEVELS:
        assert np.allclose(Df["lv"][k][:nc][okv], Dc["lv"][k][:nc][okv])
    lim = nc - nk.K_RET - nk.NK3_BARS - 8
    assert lim > 5000
    for d in (1, -1):
        for rule in ("NK2-core", "NK2-deep"):
            sf = nk.nk2_signals(Df, d, nk.NK2_TRIG[rule][d])[0]
            sc = nk.nk2_signals(Dc, d, nk.NK2_TRIG[rule][d])[0]
            assert (sf[sf < lim] == sc[sc < lim]).all(), (rule, d)
    ef = [(e["type"], e["s"], e["d"]) for e in nk.nk3_events(Df) if e["s"] < lim]
    ec = [(e["type"], e["s"], e["d"]) for e in nk.nk3_events(Dc) if e["s"] < lim]
    assert ef == ec
    assert (Df["ph"][:lim] == Dc["ph"][:lim]).all()
    assert (Df["ctx"][:, :lim] == Dc["ctx"][:, :lim]).all()


def _bars(o, h, l, c):
    n = len(o)
    return dict(n=n, o=np.array(o, float), h=np.array(h, float), l=np.array(l, float), c=np.array(c, float))


def test_exit_sim_close_vs_intraday_and_ties():
    # long entry 100, stop 99, target 102. bar0 trades through the stop intraday but closes above it.
    D = _bars([100, 100.0, 100], [100.5, 100.2, 103], [98.5, 99.6, 99.8], [100.1, 100.0, 102.5])
    px, k = nk.exit_sim(D, 0, 1, 100.0, 99.0, 102.0, "close", True)
    assert (px, k) == (102.0, 2)  # close basis ignores the wick; target touched on bar 2
    px, k = nk.exit_sim(D, 0, 1, 100.0, 99.0, 102.0, "intraday", True)
    assert (px, k) == (99.0, 0)  # intraday stop touched on bar 0
    # gap through the stop fills at the worse open (intraday) / at the close (close basis)
    G = _bars([100, 97.0], [100.2, 97.5], [99.5, 96.0], [100.0, 96.5])
    assert nk.exit_sim(G, 0, 1, 100.0, 99.0, 105.0, "intraday", True) == (97.0, 1)
    assert nk.exit_sim(G, 0, 1, 100.0, 99.0, 105.0, "close", True) == (96.5, 1)
    # same bar stop and target: stop wins
    S = _bars([100.0], [103.0], [98.0], [98.5])
    assert nk.exit_sim(S, 0, 1, 100.0, 99.0, 102.0, "close", True)[0] == 98.5
    # target not allowed on the fill bar for limit entries
    T = _bars([100.0, 100.0], [103.0, 100.5], [99.8, 99.9], [100.2, 100.1])
    px, k = nk.exit_sim(T, 0, 1, 100.0, 99.0, 102.0, "close", False)
    assert k == 1 and px == 100.1


def test_fee_formula_by_hand():
    T = dict(e=np.array([100.0]), x=np.array([101.0]), df=np.array([0.01]))
    # dist = 1.0; fee = 0.0006 * (100 + 101) = 0.1206 per unit -> 0.1206 R at 12 bp; 0.0603 R at 6 bp
    assert abs(nk.fee_r(T, 12.0)[0] - 0.1206) < 1e-12
    assert abs(nk.fee_r(T, 6.0)[0] - 0.0603) < 1e-12


def test_pivot_formulas_by_hand():
    p = nk.pivots(np.array([110.0]), np.array([90.0]), np.array([100.0]))
    # P=100; R1=2P-L=110; S1=2P-H=90; R2=P+(H-L)=120; S2=P-(H-L)=80; R3=H+2(P-L)=130; S3=L-2(H-P)=70
    assert [float(p[k][0]) for k in ("P", "R1", "S1", "R2", "S2", "R3", "S3")] == [100, 110, 90, 120, 80, 130, 70]


def test_cell_selection_rules_on_synthetic():
    import study
    rng = np.random.default_rng(1)
    n = 6000
    X = dict(coin=np.zeros(n, np.int16), t=(rng.integers(0, 1500, n) * DAY).astype(np.int64) + 1546300800000, ph=np.full(n, 5, np.int8), d=np.ones(n, np.int8), lvl=np.zeros(n, np.int8),
             ctx=rng.integers(0, 3, (n, 8)).astype(np.int8), g=rng.normal(0.0, 1.0, n), df=np.full(n, 0.01), e=np.full(n, 100.0), x=np.full(n, 100.0))
    X["g"] = X["g"] + (X["ctx"][:, 0] == 0) * 0.6 + (X["ctx"][:, 1] == 1) * 0.5  # layers 0 and 1 carry real edge
    X["t"] = np.minimum(X["t"], study.SPLIT - 1)
    T = {(r, study.REG_BASIS[r], "taker"): X for r in study.nk.RULES}
    share = {p: 0.2 for p in range(1, 7)}
    share[1] = 0.02  # below the 5% floor
    kept, scored, nodata = study.select_cells(T, share)
    for r in study.nk.RULES:
        layers = [c["layer"] for c in kept[r]]
        assert len(layers) == len(set(layers)) <= 3  # one cell per layer, top 3
        assert all(c["phase_id"] != 1 for c in kept[r])
        assert all(c["n"] >= 150 and c["days"] >= 40 and c["score"] > 0 for c in kept[r])
        assert "C1_rsi4h" in layers and "C2_wt1d" in layers  # the planted edge is found
    assert all(s["phase_id"] != 1 for s in scored)


def test_repo_files_under_5mb():
    out = subprocess.run(["git", "-C", str(HERE), "ls-files", "-s", "."], capture_output=True, text=True).stdout.splitlines()
    for ln in out:
        path = ln.split("\t")[1]
        assert (HERE / path).stat().st_size < 5 * 1024 * 1024, path
    for f in HERE.iterdir():
        if f.is_file():
            assert f.stat().st_size < 5 * 1024 * 1024, f
