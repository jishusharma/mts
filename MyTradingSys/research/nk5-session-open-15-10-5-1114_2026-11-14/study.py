"""nk5 session-open 15-10-5 study. See PRE_REG.md. STUDY_BUG=1 = deliberate look-ahead (test only)."""
import os, sys, json, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest")))
import fees  # noqa: E402  (single cost module, test_no_own_costs)
CACHE = r"F:\MTS\data_cache\binance"
SYMS = ["BTC","ETH","BNB","XRP","ADA","DOGE","SOL","LTC","LINK","TRX","EOS","XLM","ETC","DASH","ZEC","BCH","ATOM","NEO","IOTA","VET"]
SPLIT = pd.Timestamp("2024-01-01", tz="UTC")
ROWS = [("NY", "2h", 2), ("NY", "4h", 4), ("NY", "asia", None), ("UTC", "2h", 2), ("UTC", "4h", 4)]
FEE = round((fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 / 2) * 2e4, 6)  # bp round trip: taker 5 bp + 1 bp slippage per side = 12.0 (PRE_REG primary)
FEE_MAKER = FEE / 2  # bp: the pre-registered 6 bp maker-entry row (PRE_REG states the figure, not a split)


def bug():
    return os.environ.get("STUDY_BUG") == "1"


def load5(sym):
    a = np.load(os.path.join(CACHE, f"{sym}USDT_5m.npz"))["a"]
    idx = pd.to_datetime(a[:, 0].astype("int64"), unit="ms", utc=True)
    df = pd.DataFrame(a[:, 1:], index=idx, columns=list("ohlcv"))
    return df[~df.index.duplicated()].sort_index()


def resample(df5, rule):
    n = {"10min": 2, "15min": 3, "1h": 12, "1D": 288}[rule]
    g = df5.resample(rule, label="left", closed="left")
    out = g.agg({"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum"})
    cnt = g["c"].count()
    return out[cnt >= n].dropna()


def rsi(c, n):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def wma(x, n):
    w = np.arange(n, 0, -1, dtype=float)
    s = sum(w[k] * x.shift(k) for k in range(n))
    return s / w.sum()


def hm_state(c):
    """+1 buy (red<green), -1 sell, 0 none. green=EMA3(RSI9), red=WMA21(RSI9) [OURS reconstruction]."""
    r = rsi(c, 9)
    g = r.ewm(span=3, adjust=False).mean()
    red = wma(r, 21)
    s = pd.Series(0, index=c.index)
    s[red < g] = 1
    s[red > g] = -1
    s[red.isna() | g.isna()] = 0
    return s


def atr(df, n=14):
    pc = df.c.shift()
    tr = pd.concat([df.h - df.l, (df.h - pc).abs(), (df.l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx_phase(d):
    """phase for UTC day D from data to close of D-1: 1 UP, -1 DOWN, 0 RANGE, nan warmup."""
    h, l, c = d.h, d.l, d.c
    up = h.diff()
    dn = -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=d.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=d.index)
    a = atr(d, 14)
    pdi = 100 * pdm.ewm(alpha=1 / 14, adjust=False).mean() / a
    mdi = 100 * mdm.ewm(alpha=1 / 14, adjust=False).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi)
    adx = dx.ewm(alpha=1 / 14, adjust=False).mean()
    sma = c.rolling(20).mean()
    slope = sma - sma.shift(5)
    ph = pd.Series(0.0, index=d.index)
    ph[(adx >= 20) & (pdi > mdi) & (slope > 0)] = 1
    ph[(adx >= 20) & (mdi > pdi) & (slope < 0)] = -1
    ph[adx.isna() | slope.isna()] = np.nan
    return ph   # raw per-day-close state; label for day D = state at close of D-1 (see phase_for)


def phase_for(sg, d):
    """phase label for UTC day d: state at close of d-1. bug: uses d's own close (look-ahead)."""
    return sg["phase"].get(d if bug() else d - pd.Timedelta(days=1), np.nan)


def anchors(days, kind):
    ny = ZoneInfo("America/New_York")
    out = []
    for d in days:
        if kind == "UTC":
            out.append(pd.Timestamp(d.year, d.month, d.day, tz="UTC"))
        else:
            out.append(pd.Timestamp(d.year, d.month, d.day, 16, tz=ny).tz_convert("UTC"))
    return out


def prep(df5):
    grid = pd.date_range(df5.index[0], df5.index[-1], freq="5min", tz="UTC")
    df5 = df5.reindex(grid)
    df5[["o", "h", "l", "c"]] = df5[["o", "h", "l", "c"]].ffill()
    df5["v"] = df5["v"].fillna(0)
    return df5


def signals(df5):
    """indicator series; returns dict used by candidates()."""
    d1 = resample(df5, "1D")
    r15 = rsi(resample(df5, "15min").c, 14)
    return dict(d1=d1, phase=adx_phase(d1), lo4=r15.rolling(4).min(), hi4=r15.rolling(4).max(),
                hm10=hm_state(resample(df5, "10min").c), hm5=hm_state(df5.c), atr1=atr(resample(df5, "1h"), 14))


def signal_at(sg, T):
    """(sigL, sigS) at anchor T from bars closed at or before T. bug: reads 15m later (look-ahead)."""
    sh = pd.Timedelta(minutes=15) if bug() else pd.Timedelta(0)
    Tb = T + sh
    lo = sg["lo4"].get(Tb - pd.Timedelta(minutes=15), np.nan)
    hi = sg["hi4"].get(Tb - pd.Timedelta(minutes=15), np.nan)
    s10 = sg["hm10"].get(Tb - pd.Timedelta(minutes=10), 0)
    s5 = sg["hm5"].get(Tb - pd.Timedelta(minutes=5), 0)
    return bool(lo <= 35 and s10 == 1 and s5 == 1), bool(hi >= 65 and s10 == -1 and s5 == -1), lo


def coin_candidates(sym, df5=None, min_days=30):
    df5 = prep(load5(sym) if df5 is None else df5)
    sg = signals(df5)
    d1, phase = sg["d1"], sg["phase"]
    o5 = df5.o.to_numpy()
    h5 = df5.h.to_numpy()
    l5 = df5.l.to_numpy()
    t0 = df5.index[0]
    days = d1.index[d1.index >= d1.index[0] + pd.Timedelta(days=min_days)]
    recs = []
    five = pd.Timedelta(minutes=5)
    for kind in ("NY", "UTC"):
        for d, T in zip(days, anchors(days, kind)):
            if T < t0 or T > df5.index[-1] - pd.Timedelta(hours=14):
                continue
            ph = phase_for(sg, d)
            if np.isnan(ph):
                continue
            sigL, sigS, lo = signal_at(sg, T)
            a1 = sg["atr1"].get(T.floor("1h") - pd.Timedelta(hours=1), np.nan)
            i0 = int((T - t0) / five)
            if np.isnan(a1) or np.isnan(lo) or i0 >= len(o5):
                continue
            entry = o5[i0]
            S = max(0.005 * entry, 0.6 * a1)
            for k, hn, hh in ROWS:
                if k != kind:
                    continue
                E = T + pd.Timedelta(hours=hh) if hh else (T.normalize() + pd.Timedelta(days=1, hours=8))
                i1 = int((E - t0) / five)
                if i1 >= len(o5):
                    continue
                hi = h5[i0:i1].max()
                lw = l5[i0:i1].min()
                rl = -S if lw <= entry - S else o5[i1] - entry
                rs = -S if hi >= entry + S else entry - o5[i1]
                recs.append(dict(sym=sym, day=d, T=T, row=f"{kind}-{hn}", phase=ph, sigL=sigL, sigS=sigS,
                                 S=S / entry, gl=rl / entry, gs=rs / entry))
    return pd.DataFrame(recs)


def build(syms=SYMS):
    fr = []
    for s in syms:
        if not os.path.exists(os.path.join(CACHE, f"{s}USDT_5m.npz")):
            print("missing", s)
            continue
        fr.append(coin_candidates(s))
        print(s, len(fr[-1]), flush=True)
    return pd.concat(fr, ignore_index=True)


def trades(C, fee_bp, matched=True):
    fee = fee_bp / 1e4
    out = []
    for dirn, sig, g in ((1, "sigL", "gl"), (-1, "sigS", "gs")):
        m = C[sig]
        m = m & ((C.phase == dirn) | (C.phase == 0)) if matched else m & (C.phase == -dirn)
        t = C[m].copy()
        t["dir"] = dirn
        t["netR"] = (t[g] - fee) / t.S
        t["feeR"] = fee / t.S
        out.append(t)
    return pd.concat(out)


def pool(C, fee_bp):
    fee = fee_bp / 1e4
    out = []
    for dirn, g in ((1, "gl"), (-1, "gs")):
        t = C[(C.phase == dirn) | (C.phase == 0)].copy()
        t["dir"] = dirn
        t["netR"] = (t[g] - fee) / t.S
        out.append(t)
    return pd.concat(out)


def boot_ci(x, rng, n=2000):
    x = np.asarray(x)
    mm = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(n)])
    return np.percentile(mm, [2.5, 97.5]), (mm <= 0).mean()


def cluster_ci(df, rng, n=2000):
    g = df.groupby("day").netR.agg(["sum", "count"])
    s = g["sum"].to_numpy()
    c = g["count"].to_numpy()
    mm = np.empty(n)
    for i in range(n):
        j = rng.integers(0, len(g), len(g))
        mm[i] = s[j].sum() / c[j].sum()
    return np.percentile(mm, [2.5, 97.5]), (mm <= 0).mean()


def placebo_p(tr, P, rng, n=2000):
    real = tr.netR.mean()
    parts = []
    for (ph, d), k in tr.groupby(["phase", "dir"]).size().items():
        pv = P[(P.phase == ph) & (P.dir == d)].netR.to_numpy()
        if len(pv):
            parts.append((pv, k))
    draws = np.array([np.concatenate([pv[rng.integers(0, len(pv), k)] for pv, k in parts]).mean() for _ in range(n)])
    return (draws >= real).mean(), draws.mean()


def ex_best5(tr):
    d = tr.groupby("day").netR.sum().sort_values(ascending=False)
    keep = tr[~tr.day.isin(d.index[:5])]
    return keep.netR.mean() if len(keep) else np.nan


def bh(ps):
    ps = np.asarray(ps, dtype=float)
    o = np.argsort(ps)
    m = len(ps)
    q = np.empty(m)
    prev = 1.0
    for rank, i in zip(range(m, 0, -1), o[::-1]):
        prev = min(prev, ps[i] * m / rank)
        q[i] = prev
    return q


def evaluate(C, rng):
    res = []
    for period in ("DEV", "VAL"):
        Cp = C[C["T"] < SPLIT] if period == "DEV" else C[C["T"] >= SPLIT]
        for row in sorted(C.row.unique()):
            Cr = Cp[Cp.row == row]
            for fee_name, fee in (("12bp", FEE), ("6bp", FEE_MAKER)):
                for kind in ("matched", "control"):
                    tr = trades(Cr, fee, kind == "matched")
                    r = dict(period=period, row=row, fee=fee_name, kind=kind, n=len(tr))
                    if len(tr) >= 2:
                        r.update(win=(tr.netR > 0).mean(), mean=tr.netR.mean(), feeR=tr.feeR.mean(), medS=tr.S.median())
                        if period == "VAL" and kind == "matched" and len(tr) >= 10 and (fee_name == "12bp" or row == "NY-4h"):
                            (a, _), _p = boot_ci(tr.netR, rng)
                            (b, _), pc = cluster_ci(tr, rng)
                            pp, pm = placebo_p(tr, pool(Cr, fee), rng)
                            r.update(ci_trade=a, ci_day=b, p_cluster=pc, placebo_p=pp, placebo_mean=pm, ex5=ex_best5(tr))
                    res.append(r)
    return pd.DataFrame(res)


def regime_mix(C):
    d = C.drop_duplicates(["sym", "day"])
    out = {}
    for name, m in (("DEV", d["T"] < SPLIT), ("VAL", d["T"] >= SPLIT)):
        out[name] = d[m].phase.map({1: "UP", -1: "DOWN", 0: "RANGE"}).value_counts(normalize=True).round(3).to_dict()
    return out


if __name__ == "__main__":
    C = build()
    C.to_pickle(os.path.join(os.environ.get("TEMP", "."), "nk5_cands.pkl"))
    R = evaluate(C, np.random.default_rng(1))
    g = R[(R.period == "VAL") & (R.kind == "matched") & R.p_cluster.notna()].copy()
    g["q"] = bh(g.p_cluster.to_numpy())
    R = R.merge(g[["row", "fee", "q"]], on=["row", "fee"], how="left")
    R.to_csv("results.csv", index=False)
    pd.set_option("display.width", 250)
    print(R.to_string())
    print("regime mix", regime_mix(C))
