"""nkp1 tests. Causality checks FAIL under the deliberate look-ahead bugs (STUDY_BUG=1, PHASE_LAG=0): run
  STUDY_BUG=1 python -m pytest test_study.py   -> must report failures in test_ctx_future_bar / test_nk1 / test_nk5
  PHASE_LAG=0 python -m pytest test_study.py   -> must report a failure in test_phase_causal
test_*_detectable tests prove each checker can see its bug even when the env switch is off."""
import os, sys, glob
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phases as PH
import ctx as CX
import study as S


def rw_daily(n=6000, seed=1):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.03, n)))
    idx = pd.date_range("2010-01-01", periods=n, freq="D")
    return pd.DataFrame({"high": c * 1.02, "low": c * 0.98, "close": c}, index=idx)


def label_at(d, day, L=None):
    return PH.phase_daily(d, L=L).loc[day, "phase_id"]


def test_phase_causal():
    d = rw_daily()
    for day in pd.to_datetime(["2016-03-01", "2018-07-04", "2021-02-10", "2023-12-31"]):
        d2 = d.copy()
        d2.loc[d2.index >= day, ["high", "low", "close"]] *= 0.4  # crash from `day` on (own close changes)
        a = PH.phase_daily(d)
        b = PH.phase_daily(d2)
        cols = ["phase_id", "pos40", "rsi", "dd", "r10", "s50"]
        assert a.loc[day, cols].equals(b.loc[day, cols]) or np.allclose(a.loc[day, cols].astype(float), b.loc[day, cols].astype(float), equal_nan=True), \
            "label of day d changed when the close of day d changed: look-ahead"


def test_phase_leak_detectable():
    d = rw_daily()
    day = pd.Timestamp("2018-07-04")
    d2 = d.copy()
    d2.loc[d2.index >= day, ["high", "low", "close"]] *= 0.4
    a = PH.phase_daily(d, L=0)
    b = PH.phase_daily(d2, L=0)
    assert not np.allclose(a.loc[day, ["rsi", "dd", "r10"]].astype(float), b.loc[day, ["rsi", "dd", "r10"]].astype(float)), "lag 0 must leak"


def test_phase_hand_numbers():
    # FORMULAS s1 style: 14 equal rises -> RSI 100; drawdown 100,120,90 -> -25%
    c = pd.Series(np.arange(1, 17, dtype=float))
    assert PH.wilder_rsi(c, 14).iloc[14] == 100
    # one fall of 1 after 14 rises of 1: avg gain 13/14, avg loss 1/14 -> RS 13 -> RSI = 100-100/14
    c2 = pd.Series(list(np.arange(1, 16, dtype=float)) + [14.0])
    assert abs(PH.wilder_rsi(c2, 14).iloc[15] - (100 - 100 / (1 + 13))) < 1e-9
    d = pd.DataFrame({"high": [100, 120, 90], "low": [100, 120, 90], "close": [100, 120, 90.]}, index=pd.date_range("2020-01-01", periods=3))
    s = PH.state_table(d)
    assert abs(s.dd.iloc[-1] + 0.25) < 1e-12


def test_phase_first_match_and_allowed():
    assert PH.allowed_side(1, 0.2) == 1 and PH.allowed_side(2, 0.9) == -1 and PH.allowed_side(6, 0.1) == -1
    assert PH.allowed_side(4, 0.3) == 1 and PH.allowed_side(4, 0.7) == -1
    # a deep crash then bounce produces CAPITULATION that sticks 3 days
    n = 600
    c = np.r_[np.linspace(100, 400, 400), np.linspace(400, 180, 20), np.full(180, 180.0)]
    d = pd.DataFrame({"high": c * 1.01, "low": c * 0.99, "close": c}, index=pd.date_range("2015-01-01", periods=n))
    s = PH.state_table(d)
    assert (s.phase_id == 1).sum() >= 3


def synth5(days=160, seed=2, start="2024-01-01"):
    rng = np.random.default_rng(seed)
    n = days * 288
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.0015, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.0007, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.0007, n)))
    v = rng.uniform(50, 150, n)
    idx = pd.date_range(start, periods=n, freq="5min", tz="UTC")
    return pd.DataFrame({"o": o, "h": h, "l": l, "c": c, "v": v}, index=idx)


def synth_ctx_inputs(df5):
    d = df5.resample("1D").agg({"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum"})
    ts = CX.ms_idx(d.index)
    rng = np.random.default_rng(3)
    spot = pd.DataFrame({"ts": ts, "o": d.o.values, "h": d.h.values, "l": d.l.values, "c": d.c.values, "v": d.v.values, "tbv": d.v.values * rng.uniform(0.3, 0.7, len(d))})
    oi = pd.DataFrame({"ts": ts + 86400000 - 1, "oi": 1e6 * np.exp(np.cumsum(rng.normal(0, 0.03, len(d))))})
    ft = np.arange(ts[0], ts[-1] + 86400000, 8 * 3600000)
    fund = pd.DataFrame({"ts": ft, "rate": rng.normal(0.0001, 0.0004, len(ft))})
    return spot, oi, fund


def ctx_row(df5, spot, oi, fund, T):
    c = CX.Ctx(df5, spot, oi, fund)
    return c.at([T]).iloc[0]


def truncated(df5, spot, oi, fund, T):
    t = pd.Timestamp(T, unit="ms", tz="UTC")
    return (df5[df5.index < t], spot[spot.ts + 86400000 <= T], oi[oi.ts < T], fund[fund.ts <= T])


def check_ctx_causal(T_list):
    df5 = synth5(days=520, start="2023-01-01")   # > 200 daily bars so the WaveTrend warm-up (FORMULAS s20.2) is over at T
    spot, oi, fund = synth_ctx_inputs(df5)
    cf = CX.Ctx(df5, spot, oi, fund)
    bad = []
    for T in T_list:
        full = cf.at([T]).iloc[0]
        tr = ctx_row(*truncated(df5, spot, oi, fund, T), T)
        for k in full.index:
            a, b = full[k], tr[k]
            if not (a == b or (a != a and b != b)):
                bad.append((T, k, a, b))
    return bad


T_LIST = [int(pd.Timestamp(x, tz="UTC").timestamp() * 1000) for x in ["2024-03-10 00:00", "2024-03-10 13:30", "2024-04-02 20:00", "2024-05-01 08:05", "2024-05-20 21:00"]]


def test_ctx_future_bar():
    """all 8 layers: value at T must not change when every bar/row not yet available at T is removed."""
    bad = check_ctx_causal(T_LIST)
    assert not bad, f"look-ahead in context layers: {bad[:3]}"


def test_ctx_leak_detectable(monkeypatch):
    monkeypatch.setenv("STUDY_BUG", "1")
    bad = check_ctx_causal(T_LIST)
    assert {k for _, k, _, _ in bad} >= {"r1", "r2", "r3", "r4", "r5", "r7", "b6"}, "bug must be visible on every available layer"


def run_nk1(df5, with_bug=False):
    a = np.column_stack([CX.ms_idx(df5.index), df5.o, df5.h, df5.l, df5.c, df5.v]).astype(float)
    sig, _ = S.nk1_coin("X", a, val_pool=False)
    d = pd.DataFrame(sig)
    return d


def test_nk1(monkeypatch):
    df5 = synth5(days=400, seed=5)
    d = run_nk1(df5)
    assert len(d) > 200
    m = (d.ret / d.Rf).mean()
    assert m < 0.1, f"random walk must show no gross edge, got {m}"
    monkeypatch.setenv("STUDY_BUG", "1")
    dbug = run_nk1(df5)
    assert (dbug.ret / dbug.Rf).mean() > m + 0.15, "look-ahead entry must create a visible fake edge"
    monkeypatch.delenv("STUDY_BUG")


def nk5_diag(df5, cut):
    d = pd.DataFrame(S.nk5_coin("X", df5))
    d = d[d.anchor_ms <= cut]
    return d[["variant", "anchor_ms", "side", "d_lo", "d_hi", "d_s10", "d_s5"]].reset_index(drop=True)


def test_nk5(monkeypatch):
    df5 = synth5(days=140, seed=7)
    cut_ts = pd.Timestamp("2024-03-01", tz="UTC")
    cut = int(cut_ts.timestamp() * 1000)
    df5b = df5.copy()
    m = df5b.index >= cut_ts
    df5b.loc[m, ["o", "h", "l", "c"]] *= 1.3
    a = nk5_diag(df5, cut)
    b = nk5_diag(df5b, cut)
    assert len(a) > 20
    pd.testing.assert_frame_equal(a, b)  # signal inputs at every anchor <= cut do not depend on bars from the cut onward
    monkeypatch.setenv("STUDY_BUG", "1")
    a2, b2 = nk5_diag(df5, cut), nk5_diag(df5b, cut)
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(a2, b2)
    monkeypatch.delenv("STUDY_BUG")


def test_files_under_5mb():
    for f in glob.glob(str(HERE / "*")):
        assert os.path.getsize(f) < 5 * 1024 * 1024, f
