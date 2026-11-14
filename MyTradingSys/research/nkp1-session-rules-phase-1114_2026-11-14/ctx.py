"""Eight single-bucket context layers (spec s2). Every layer is a series with an AVAILABILITY time (when its value is
known); a lookup at time T takes the last value with avail <= T. STUDY_BUG=1 makes every layer available one period early
(look-ahead), used only by test_study.py. All cutoffs are fixed in PRE_REG.md and never changed after DEV is seen."""
import os
import numpy as np
import pandas as pd

H4, D1, F8 = 4 * 3600_000, 86400_000, 8 * 3600_000
LAYERS = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
LABELS = {
    "C1": ("4hRSI<=40", "4hRSI mid", "4hRSI>=60"),
    "C2": ("WT<=-53", "WT mid", "WT>=+53"),
    "C3": ("%B<0.10", "%B mid", "%B>0.90"),
    "C4": ("OI24h<=-3%", "OI flat", "OI24h>=+3%"),
    "C5": ("fund<0", "fund 0-0.03%", "fund>0.03%"),
    "C6": ("bull-div", "agree", "bear-div"),
    "C7": ("RVratio<0.7", "RV mid", "RVratio>1.3"),
    "C8": ("Asia", "EU", "US"),
}


def ms_idx(idx):
    return idx.as_unit('ns').asi8 // 10 ** 6


def ms_ts(ts):
    return int(ts.as_unit('ns').value // 10 ** 6)


def bug():
    return os.environ.get("STUDY_BUG") == "1"


def rsi_wilder(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def wavetrend(h, l, c, n1=10, n2=21):
    """LazyBear WaveTrend wt1 (FORMULAS s20.1): ap=(h+l+c)/3; esa=EMA(ap,n1); d=EMA(|ap-esa|,n1); ci=(ap-esa)/(0.015 d); wt1=EMA(ci,n2)."""
    ap = (h + l + c) / 3
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d.where(d > 1e-9 * ap.abs()))
    wt1 = ci.ewm(span=n2, adjust=False).mean()
    wt1.iloc[:200] = np.nan   # warm-up 200 bars (FORMULAS s20.2)
    return wt1


def resample(df5, rule, nmin):
    g = df5.resample(rule, label="left", closed="left")
    out = g.agg({"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum"})
    return out[g["c"].count() >= nmin].dropna()


class Ctx:
    """per-coin context lookup. df5: DataFrame o,h,l,c,v indexed by UTC time. spot1d/oi/fund optional (None = NO-DATA)."""

    def __init__(self, df5, spot1d=None, oi=None, fund=None):
        e = 1 if bug() else 0
        self.s = {}
        h4 = resample(df5, "4h", 40)
        r = rsi_wilder(h4.c, 14)
        ma = h4.c.rolling(20).mean()
        sd = h4.c.rolling(20).std(ddof=0)
        pb = (h4.c - (ma - 2 * sd)) / (4 * sd.where(sd > 0))
        t4 = ms_idx(h4.index)
        self.s["c1"] = (t4 + H4 - e * H4, r.to_numpy())
        self.s["c3"] = (t4 + H4 - e * H4, pb.to_numpy())
        d1 = resample(df5, "1D", 250)
        td = ms_idx(d1.index)
        wt = wavetrend(d1.h, d1.l, d1.c)
        self.s["c2"] = (td + D1 - e * D1, wt.to_numpy())
        lr = np.log(d1.c).diff()
        rv = lr.rolling(7).std() / lr.rolling(60).std()
        self.s["c7"] = (td + D1 - e * D1, rv.to_numpy())
        self.s["c6"] = (np.array([]), np.array([]))
        if spot1d is not None and len(spot1d):
            v = spot1d.v.where(spot1d.v > 0)
            delta = (2 * spot1d.tbv - spot1d.v) / v
            chg = spot1d.c / spot1d.o - 1
            code = np.where((chg < 0) & (delta > 0), 0.0, np.where((chg > 0) & (delta < 0), 2.0, 1.0))
            code[np.isnan(delta.to_numpy())] = np.nan
            self.s["c6"] = (spot1d.ts.to_numpy() + D1 - e * D1, code)
        self.s["c4"] = (np.array([]), np.array([]))
        if oi is not None and len(oi) > 1:
            ts = oi.ts.to_numpy()
            ch = oi.oi.to_numpy()[1:] / oi.oi.to_numpy()[:-1] - 1
            ok = (ts[1:] - ts[:-1]) == D1
            ch = np.where(ok, ch, np.nan)
            self.s["c4"] = (ts[1:] + 1 - e * D1, ch)
        self.s["c5"] = (np.array([]), np.array([]))
        if fund is not None and len(fund) >= 3:
            ts = fund.ts.to_numpy()
            m3 = fund.rate.rolling(3).mean().to_numpy()
            self.s["c5"] = (ts - e * F8, m3)
        self.first = {k: (int(v[0][0]) if len(v[0]) else None) for k, v in self.s.items()}

    def raw(self, key, T):
        a, v = self.s[key]
        if len(a) == 0:
            return np.full(len(T), np.nan)
        i = np.searchsorted(a, T, side="right") - 1
        out = np.where(i >= 0, v[np.clip(i, 0, len(v) - 1)], np.nan)
        # stale guard: a value older than 3 periods is not trusted (data gap)
        age = T - a[np.clip(i, 0, len(a) - 1)]
        lim = {"c1": 3 * H4, "c3": 3 * H4, "c2": 3 * D1, "c7": 3 * D1, "c6": 3 * D1, "c4": 3 * D1, "c5": 3 * F8}[key]
        return np.where(age <= lim + (D1 if bug() else 0), out, np.nan)

    def at(self, T):
        """T: array of ms. returns DataFrame raw values r1..r7 + buckets b1..b8 (0,1,2; -1 = NO-DATA)."""
        T = np.asarray(T, dtype=np.int64)
        o = {}
        r1, r2, r3, r4, r5, r6, r7 = (self.raw(k, T) for k in ("c1", "c2", "c3", "c4", "c5", "c6", "c7"))
        o.update(r1=r1, r2=r2, r3=r3, r4=r4, r5=r5, r7=r7)
        hr = (T // 3600_000) % 24
        b = {}
        b["b1"] = np.where(np.isnan(r1), -1, np.where(r1 <= 40, 0, np.where(r1 >= 60, 2, 1)))
        b["b2"] = np.where(np.isnan(r2), -1, np.where(r2 <= -53, 0, np.where(r2 >= 53, 2, 1)))
        b["b3"] = np.where(np.isnan(r3), -1, np.where(r3 < 0.10, 0, np.where(r3 > 0.90, 2, 1)))
        b["b4"] = np.where(np.isnan(r4), -1, np.where(r4 <= -0.03, 0, np.where(r4 >= 0.03, 2, 1)))
        b["b5"] = np.where(np.isnan(r5), -1, np.where(r5 < 0, 0, np.where(r5 > 0.0003, 2, 1)))
        b["b6"] = np.where(np.isnan(r6), -1, r6).astype(int)
        b["b7"] = np.where(np.isnan(r7), -1, np.where(r7 < 0.7, 0, np.where(r7 > 1.3, 2, 1)))
        b["b8"] = np.where(hr < 8, 0, np.where(hr < 16, 1, 2))
        o.update({k: np.asarray(v).astype(int) for k, v in b.items()})
        return pd.DataFrame(o)
