import io
import os
import sys
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_flow as FF
import flow as W

DAYMS = 86400000
T0 = 1640995200000  # 2022-01-01 UTC


def synth(n=900, beta=0.0, seed=3):
    rng = np.random.default_rng(seed)
    F = rng.normal(0, 100, n)
    ret = beta * F * 1e-4 + rng.normal(0, 0.02, n)
    ts = T0 + np.arange(n) * DAYMS
    return ts, F, ret


def mkzip(rows):
    """rows: (price, qty, maker) in the aggTrades column order, header-less."""
    buf = io.StringIO()
    for i, (p, q, m) in enumerate(rows):
        buf.write("%d,%s,%s,%d,%d,%d,%s,True\n" % (i, p, q, i, i, 1640995200000 + i, m))
    zb = io.BytesIO()
    with zipfile.ZipFile(zb, "w") as z:
        z.writestr("x.csv", buf.getvalue())
    return zb.getvalue()


def test_reduce_hand_numbers():
    raw = mkzip([(100000, 12, "False"),    # 1.2M buy, large 1M
                 (100000, 60, "True"),     # 6.0M sell, large 1M and 5M
                 (100000, 5, "False"),     # 0.5M buy, small
                 (100000, 10, "True")])    # 1.0M sell, exactly at the 1M cutoff
    r = FF.parse_zip(raw)
    assert r["n"] == 4
    assert abs(r["total"] - 8.7e6) < 1
    assert abs(r["buy1"] - 1.2e6) < 1 and abs(r["sell1"] - 7.0e6) < 1
    assert abs(r["buy5"]) < 1 and abs(r["sell5"] - 6.0e6) < 1
    assert r["n1"] == 3 and r["n5"] == 1


def test_parse_zip_skips_header_row():
    raw = mkzip([(100000, 12, "False")])
    hdr = "agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n"
    zb = io.BytesIO()
    with zipfile.ZipFile(zb, "w") as z:
        z.writestr("x.csv", hdr + zipfile.ZipFile(io.BytesIO(raw)).read("x.csv").decode())
    r = FF.parse_zip(zb.getvalue())
    assert r["n"] == 1 and abs(r["buy1"] - 1.2e6) < 1


def test_net_flow_bp_venues():
    sp = {"buy1": 3e6, "sell1": 1e6, "total": 1e9}
    fu = {"buy1": 0.0, "sell1": 4e6, "total": 3e9}
    assert abs(W.net_flow_bp(sp, fu, "1", "SPOT") - 20.0) < 1e-9
    assert abs(W.net_flow_bp(sp, fu, "1", "FUT") - (-4e6 / 3e9 * 1e4)) < 1e-9
    assert abs(W.net_flow_bp(sp, fu, "1", "ALL") - (-2e6 / 4e9 * 1e4)) < 1e-9
    assert np.isnan(W.net_flow_bp(sp, None, "1", "ALL"))


def test_quintile_assignment_hand():
    edges = W.quintile_edges(np.arange(100.0))          # 19.8, 39.6, 59.4, 79.2
    q = W.quint([0, 19.8, 19.81, 50, 79.3, 99], edges)
    assert list(q) == [0, 1, 1, 2, 4, 4] or list(q) == [0, 0, 1, 2, 4, 4]
    assert W.quint([1e9], edges)[0] == 4 and W.quint([-1e9], edges)[0] == 0


def test_spread_hand():
    F = np.arange(100.0)
    ret = np.where(F >= 80, 0.01, np.where(F < 20, -0.01, 0.0))
    st = W.spread_stats(F, ret, W.quintile_edges(F))
    assert abs(st["spread"] - 0.02) < 1e-12 and not st["underpowered"]
    fr = W.fee_rows(st, 0.0012)
    assert abs(fr["two_leg"] - (200 - 24)) < 1e-6 and abs(fr["long_q5"] - (100 - 12)) < 1e-6


def test_lead_signal_detected_and_null_not():
    ts, F, ret = synth(beta=4.0)                         # real lead
    edges = W.quintile_edges(F[:400])
    ph = np.array(["UP"] * 900)
    act = W.spread_stats(F[400:], ret[400:], edges)["spread"]
    dr = W.shuffle_placebo(F[400:], ret[400:], ph[400:], edges, ndraw=600)
    assert act > 0 and W.pct_of(act, dr) > 97.5
    ci = W.block_ci(ts[400:], F[400:], ret[400:], edges, nboot=2000)
    assert ci[0] > 0
    ts, F, ret = synth(beta=0.0, seed=9)                 # null: no lead
    edges = W.quintile_edges(F[:400])
    act = W.spread_stats(F[400:], ret[400:], edges)["spread"]
    dr = W.shuffle_placebo(F[400:], ret[400:], ph[400:], edges, ndraw=600)
    assert 1.0 < W.pct_of(act, dr) < 99.0
    lo, hi = W.block_ci(ts[400:], F[400:], ret[400:], edges, nboot=2000)
    assert lo < 0 < hi


def test_shuffle_stays_inside_phase():
    n = 600
    F = np.where(np.arange(n) % 2 == 0, 500.0, -500.0)    # constant inside each phase
    phase = np.where(np.arange(n) % 2 == 0, "UP", "DOWN")
    ret = np.random.default_rng(1).normal(0, 0.02, n)
    edges = np.array([-100.0, -50.0, 50.0, 100.0])
    act = W.spread_stats(F, ret, edges)["spread"]
    dr = W.shuffle_placebo(F, ret, phase, edges, ndraw=50)
    assert np.allclose(dr, act)                           # a within-phase shuffle cannot move anything
    mixed = W.shuffle_placebo(F, ret, np.array(["UP"] * n), edges, ndraw=50)
    assert not np.allclose(mixed, act)                    # a cross-phase shuffle does


def test_block_ci_deterministic_and_small_sample_nan():
    ts, F, ret = synth(n=300, beta=3.0, seed=5)
    edges = W.quintile_edges(F)
    assert W.block_ci(ts, F, ret, edges, nboot=300) == W.block_ci(ts, F, ret, edges, nboot=300)
    lo, hi = W.block_ci(ts[:10], F[:10], ret[:10], edges, nboot=300)
    assert np.isnan(lo) and np.isnan(hi)


def test_spearman_and_flow_dir(tmp_path):
    assert abs(W.spearman([1, 2, 3, 4, 5, 6], [2, 4, 6, 8, 10, 12]) - 1.0) < 1e-12
    assert abs(W.spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) + 1.0) < 1e-12
    d = tmp_path / "spot"
    d.mkdir()
    (d / "2022-01-01.json").write_text('{"n": 1, "total": 5.0}')
    (d / "bad.json").write_text("{")
    got = W.load_flow_dir(str(d))
    assert list(got) == ["2022-01-01"] and W.load_flow_dir(str(tmp_path / "missing")) == {}


def test_split_masks():
    ts = np.array([1704067200000 - DAYMS, 1704067200000, 1751328000000])   # 2023-12-31, 2024-01-01, 2025-07-01
    assert list(W.split_mask(ts, "DEV")) == [True, False, False]
    assert list(W.split_mask(ts, "VAL")) == [False, True, True]
    assert list(W.split_mask(ts, "RECENT")) == [False, False, True]
