"""Causality tests. Pass on real code; fail under STUDY_BUG=1 (look-ahead)."""
import numpy as np, pandas as pd
import study


def synth(days=120, seed=3):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=days * 288, freq="5min", tz="UTC")
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, len(idx))))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * 1.0005
    l = np.minimum(o, c) * 0.9995
    return pd.DataFrame(dict(o=o, h=h, l=l, c=c, v=1.0), index=idx)


def _vals(df5, T, day):
    sg = study.signals(df5)
    sgL, sgS, lo = study.signal_at(sg, T)
    s10 = sg["hm10"].get(T - pd.Timedelta(minutes=10), np.nan)
    sh = pd.Timedelta(minutes=15) if study.bug() else pd.Timedelta(0)
    return (sg["lo4"].get(T + sh - pd.Timedelta(minutes=15), np.nan), sg["hm10"].get(T + sh - pd.Timedelta(minutes=10), np.nan),
            sg["hm5"].get(T + sh - pd.Timedelta(minutes=5), np.nan), study.phase_for(sg, day))


def test_truncation_does_not_change_signal_or_phase():
    df = synth()
    bad = 0
    for k in range(40, 110, 5):
        day = pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(days=k)
        for T in (day, day + pd.Timedelta(hours=21)):
            full = _vals(df, T, day)
            part = _vals(df[df.index < T], T, day)   # only bars opened before T (closed by T)
            for a, b in zip(full, part):
                same = (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-9
                bad += (not same)
    assert bad == 0, f"{bad} look-ahead differences"


def test_nyasia_is_only_row_and_anchored_at_ny_close():
    C = study.coin_candidates("SYN", df5=synth())
    assert set(C.row) == {"NY-asia"}
    assert len(C) > 50
    assert all(t.hour in (20, 21) for t in C["T"])


def test_rsi_known_value():
    c = pd.Series([44, 44.34, 44.09, 44.15, 43.61, 43.44, 43.03, 43.52, 43.13, 42.66, 42.82, 42.52, 43.23, 43.43, 43.28, 43.9])
    r = study.rsi(c, 14).iloc[-1]
    assert 55 < r < 75


def test_bh_monotone():
    q = study.bh([0.01, 0.04, 0.03, 0.5])
    assert q[0] <= 0.04 and q[3] == 0.5
