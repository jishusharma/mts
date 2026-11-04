"""Level-approach study (card level-approach-study-daily-last-lower-hi): approaches to the daily last lower high and the
prior-day high, classified near_miss / wick_back / close_then_fail / accepted per TF, DEV only. PRE_REG.md is the spec.

Run: python level_approach.py [--klines F:/MTS/data/tom_raw/klines]
Refuses to run unless PRE_REG.md ends with a FROZEN_UTC line; reads BTCUSDT 1m 2022-01..2024-06 only (loader refuses any bar
at/after 2024-07-01). Output: events.csv, tables.csv, RESULT.md (aggregates only, no account data).
"""
import argparse
import hashlib
import sys
from collections import namedtuple
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EPS, K, FWD, LB = 0.001, 3, 12, 10               # OURS: arm line 0.1 % under level, 3 confirm closes, 12-bar forward, 10-day lower-low lookback
TFS = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}
CUTOFF_MS = int(np.datetime64("2024-07-01T00:00", "ms").astype("int64"))
SPLIT_MS = int(np.datetime64("2023-07-01T00:00", "ms").astype("int64"))   # dev half A < split <= half B
DAY_MS = 86_400_000
MIN_N = 30
Event = namedtuple("Event", "idx cls n_close")


def require_frozen(path):
    txt = Path(path).read_text(encoding="utf-8")
    last = [ln for ln in txt.splitlines() if ln.strip()][-1] if txt.strip() else ""
    if not last.startswith("FROZEN_UTC:"):
        raise SystemExit("PRE_REG.md is not frozen (last line must be FROZEN_UTC: ...); refusing to run")
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def daily_levels(H, L, lb=LB):
    """Per day i (known at its open): prior-day high H[i-1]; last lower high = max high from the latest lower-low day j<=i-1
    (L[j] < min(L[j-lb:j])) through i-1. NaN when no lower low yet, or when it equals the prior-day high (duplicate)."""
    n = len(H)
    pdh = np.full(n, np.nan)
    lh = np.full(n, np.nan)
    ll_day = -1
    for i in range(1, n):
        j = i - 1
        if j >= lb and L[j] < L[j - lb:j].min():
            ll_day = j
        pdh[i] = H[i - 1]
        if ll_day >= 0:
            v = H[ll_day:i].max()
            lh[i] = np.nan if v == pdh[i] else v
    return pdh, lh


def classify_approaches(h, c, level, eps=EPS, k=K):
    """Walk bars; per level an approach is armed after a close under level*(1-eps). First bar with high >= that line is the event:
    near_miss (high < level), wick_back (high >= level, close < level), else a through-close resolved over the next k closes:
    close_then_fail (n_close = which later close fell back under) or accepted. Unresolved (< k bars left) are dropped."""
    out = []
    armed = False
    prev = np.nan
    n = len(h)
    for i in range(n):
        lv = level[i]
        if np.isnan(lv):
            armed, prev = False, np.nan
            continue
        if lv != prev:
            armed, prev = False, lv
        thr = lv * (1 - eps)
        if not armed:
            if c[i] < thr:
                armed = True
            continue
        if h[i] < thr:
            continue
        armed = False
        if c[i] <= lv:
            out.append(Event(i, "wick_back" if h[i] >= lv else "near_miss", 0))
            continue
        if i + k >= n:
            continue
        fail = next((j for j in range(1, k + 1) if c[i + j] < lv), 0)
        out.append(Event(i, "close_then_fail" if fail else "accepted", fail))
    return out


def load_klines(paths, cutoff_ms=CUTOFF_MS):
    import pandas as pd
    df = pd.concat([pd.read_csv(p, usecols=["open_time", "open", "high", "low", "close", "volume", "taker_buy_volume"]) for p in paths],
                   ignore_index=True)
    df = df[df.open_time < cutoff_ms].sort_values("open_time").drop_duplicates("open_time").reset_index(drop=True)
    if len(df) and df.open_time.iloc[-1] >= cutoff_ms:
        raise SystemExit("loader read a bar at/after the DEV cutoff")
    return df


def resample(df, m):
    g = df.groupby(df.open_time // (m * 60_000))
    r = g.agg(t=("open_time", "first"), h=("high", "max"), l=("low", "min"), c=("close", "last"), v=("volume", "sum"),
              tb=("taker_buy_volume", "sum"), cnt=("open_time", "size"))
    return r[r.cnt == m].reset_index(drop=True)


def rsi(c, n=14):
    import pandas as pd
    d = pd.Series(c).diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).to_numpy()


def build_events(df):
    import pandas as pd
    day = df.open_time // DAY_MS
    d = df.groupby(day).agg(h=("high", "max"), l=("low", "min"), c=("close", "last"), cnt=("open_time", "size"))
    d = d[d.cnt == 1440]
    pdh, lh = daily_levels(d.h.to_numpy(), d.l.to_numpy())
    bbmid = d.c.rolling(20).mean().shift(1).to_numpy()
    dmap = {int(k): i for i, k in enumerate(d.index)}
    rows = []
    for tf, m in TFS.items():
        b = resample(df, m)
        di = np.array([dmap.get(int(x) // DAY_MS, -1) for x in b.t])
        ok = di >= 0
        delta = 2 * b.tb.to_numpy() - b.v.to_numpy()
        cvd = pd.Series(delta).rolling(FWD).sum().to_numpy()
        r = rsi(b.c.to_numpy())
        h, c, t = b.h.to_numpy(), b.c.to_numpy(), b.t.to_numpy()
        for kind, arr in (("pdh", pdh), ("lh", lh)):
            lvl = np.where(ok, arr[np.where(ok, di, 0)], np.nan)
            for e in classify_approaches(h, c, lvl):
                a = e.idx + (K if e.cls in ("close_then_fail", "accepted") else 0)
                if a + FWD >= len(c):
                    continue
                lv = lvl[e.idx]
                bm = bbmid[di[e.idx]]
                rows.append(dict(t=int(t[e.idx]), tf=tf, kind=kind, cls=e.cls, n_close=e.n_close, level=lv,
                                 rsi=r[e.idx], cvd12=cvd[e.idx], delta=delta[e.idx], above_bbmid=int(c[e.idx] >= bm) if bm == bm else -1,
                                 fwd=c[a + FWD] / c[a] - 1, brk=int(c[a + FWD] > lv), half="A" if t[e.idx] < SPLIT_MS else "B"))
    return pd.DataFrame(rows)


def wilson(p, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    w = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return cen - w, cen + w


def tables(ev):
    import pandas as pd
    base = []
    for (kind, cls, tf), g in ev.groupby(["kind", "cls", "tf"]):
        p = g.brk.mean()
        lo, hi = wilson(p, len(g))
        base.append(dict(kind=kind, cls=cls, tf=tf, n=len(g), nA=(g.half == "A").sum(), nB=(g.half == "B").sum(),
                         mean_fwd_pct=100 * g.fwd.mean(), median_fwd_pct=100 * g.fwd.median(), p_above_level=p, ci_lo=lo, ci_hi=hi))
    ev = ev.assign(f_rsi=(ev.rsi >= 50).astype(int), f_cvd=(ev.cvd12 > 0).astype(int))
    seq = []
    for (cls, tf), g in ev[ev.above_bbmid >= 0].groupby(["cls", "tf"]):
        for (a, b, c_), s in g.groupby(["f_rsi", "f_cvd", "above_bbmid"]):
            if len(s) < MIN_N:
                continue
            pa, pb = s[s.half == "A"].brk.mean(), s[s.half == "B"].brk.mean()
            lo, hi = wilson(s.brk.mean(), len(s))
            seq.append(dict(cls=cls, tf=tf, rsi_ge50=a, cvd12_pos=b, above_dbb_mid=c_, n=len(s), p_above_level=s.brk.mean(),
                            ci_lo=lo, ci_hi=hi, pA=pa, pB=pb, mean_fwd_pct=100 * s.fwd.mean()))
    return pd.DataFrame(base), pd.DataFrame(seq)


def main():
    import pandas as pd
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    a = ap.parse_args()
    sha = require_frozen(HERE / "PRE_REG.md")
    paths = sorted(Path(a.klines).glob("BTCUSDT-1m-202[234]-*.csv"))
    paths = [p for p in paths if p.stem[-7:] <= "2024-06"]
    df = load_klines(paths)
    ev = build_events(df)
    base, seq = tables(ev)
    ev.to_csv(HERE / "events.csv", index=False, lineterminator="\n")
    base.to_csv(HERE / "tables.csv", index=False, lineterminator="\n")
    seq.to_csv(HERE / "sequences.csv", index=False, lineterminator="\n")
    print(f"pre_reg_sha256 {sha}\nevents {len(ev)}")
    return ev, base, seq, sha


if __name__ == "__main__":
    main()