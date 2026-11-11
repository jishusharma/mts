import glob, os, numpy as np, pandas as pd
RAW = "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw/fundingRate"
K = "F:/MTS/edge_views_data/k1h"; OIDIR = "F:/MTS/data/binance_metrics"
import sys as _s, pathlib as _p; _s.path.insert(0, str(_p.Path(__file__).resolve().parents[3] / 'backtest'))
from fees import BINANCE_TAKER  # shared cost source (T06): 2 x taker = 0.10 % round trip
FEE = BINANCE_TAKER * 2; HOUR = 3600_000; DAY = 24 * HOUR
rng = np.random.default_rng(11)

def load_k():
    fr = []
    for f in sorted(glob.glob(K + "/BTCUSDT-1h-*.csv")):
        d = pd.read_csv(f, header=None, usecols=range(6), names=["t","o","h","l","c","v"], dtype=str)
        d = d[d.t.str.fullmatch(r"\d+")].astype(float); fr.append(d)
    d = pd.concat(fr).drop_duplicates("t").sort_values("t").reset_index(drop=True)
    d["t"] = np.where(d.t > 1e14, d.t / 1000, d.t).astype("int64")
    return d
def load_f():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(RAW + "/*.csv"))]).drop_duplicates("calc_time").sort_values("calc_time")
    return d.calc_time.values.astype("int64"), d.last_funding_rate.values.astype(float)
def load_oi():
    out = []
    for f in sorted(glob.glob(OIDIR + "/*.csv")):
        d = pd.read_csv(f, usecols=["create_time", "sum_open_interest"])
        d = d[d.create_time.str[14:16] == "00"]; out.append(d[d.create_time.str[17:19] == "00"])
    d = pd.concat(out)
    d["t"] = pd.to_datetime(d.create_time, utc=True).dt.as_unit("ms").astype("int64")
    return d.drop_duplicates("t").set_index("t").sum_open_interest

k = load_k(); T = k.t.values; O = k.o.values; C = k.c.values; V = k.v.values; N = len(k)
ft, fv = load_f(); ftf = ft // HOUR * HOUR
print('funding ts jitter ms:', sorted(set((ft % HOUR).tolist()))[:5])
assert (np.diff(T) == HOUR).all() or print("kline gaps:", (np.diff(T) != HOUR).sum())
idx_of = {t: i for i, t in enumerate(T)}

def fund_in_hold(i, H):   # settlements in (T[i], T[i+H-1]+1h]
    a, b = T[i], T[i + H - 1] + HOUR
    m = (ftf > a) & (ftf <= b); return fv[m].sum()

def signals_funding():
    sig = {}
    for j, t in enumerate(ft):
        if t < 1609459200000: continue
        w = fv[(ft >= t - 365 * DAY) & (ft < t)]
        if len(w) < 800: continue
        hi, lo = np.percentile(w, 95), np.percentile(w, 5)
        i = np.searchsorted(T, t // HOUR * HOUR)
        if i >= N: continue
        if fv[j] >= hi: sig[i] = -1
        elif fv[j] <= lo: sig[i] = 1
    return sig
def signals_cascade():
    s = pd.Series(V); med = s.shift(1).rolling(720).median().values
    ret = C / O - 1; sig = {}
    for i in range(720, N - 1):
        if V[i] > 3 * med[i]:
            if ret[i] <= -0.03: sig[i + 1] = 1
            elif ret[i] >= 0.03: sig[i + 1] = -1
    return sig
def signals_oi():
    oi = load_oi(); sig = {}
    for i in range(4, N - 1):
        t1, t0 = T[i] + HOUR, T[i - 3]    # OI at bar close vs 4h before that
        if t1 in oi.index and t0 in oi.index and oi[t0] > 0:
            if oi[t1] / oi[t0] - 1 <= -0.05 and C[i] / C[i - 4] - 1 < 0: sig[i + 1] = 1
    return sig

def run(name, sig, H, lo_i, hi_i):
    ent = sorted(i for i in sig if lo_i <= i and i + H - 1 < hi_i)
    sp = lo_i + int(0.6 * (hi_i - lo_i)); gap = 30 * 24
    rows = []; busy = -1
    for i in ent:
        if i <= busy: continue
        busy = i + H - 1
        s = sig[i]; g = s * (C[i + H - 1] / O[i] - 1)
        rows.append((i, s, g - FEE, g - FEE - s * fund_in_hold(i, H)))
    tr = pd.DataFrame(rows, columns=["i", "side", "net", "netf"])
    # long/short per-bar return arrays for placebo
    ok = np.arange(lo_i, hi_i - H + 1)
    rl = C[ok + H - 1] / O[ok] - 1
    out = []
    for split, (a, b) in {"DEV": (lo_i, sp), "VAL": (sp + gap, hi_i)}.items():
        for side in (1, -1, 0):
            t = tr[(tr.i >= a) & (tr.i < b)]
            if side: t = t[t.side == side]
            n = len(t)
            if n == 0: out.append((name, split, {1:"long",-1:"short",0:"both"}[side], 0, *[np.nan]*5)); continue
            x = t.net.values; mean = x.mean(); sd = x.std(ddof=1) if n > 1 else np.nan
            tstat = mean / (sd / np.sqrt(n)) if n > 1 and sd > 0 else np.nan
            pct = np.nan
            if side:
                pool = ok[(ok >= a) & (ok < b)]; pr = side * rl[pool - lo_i] - FEE
                dr = [pr[rng.integers(0, len(pr), n)].mean() for _ in range(200)]
                pct = 100 * np.mean(np.array(dr) < mean)
            out.append((name, split, {1:"long",-1:"short",0:"both"}[side], n, 100*(x>0).mean(), 100*mean, tstat, pct, 100*t.netf.mean()))
    return out

res = []
ms = lambda s: int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)
def lo(s): return int(np.searchsorted(T, ms(s)))
res += run("a_funding", signals_funding(), 72, lo("2021-01-01"), N)
res += run("b_cascade", signals_cascade(), 24, lo("2020-02-01"), N)
res += run("c_oi_flush", signals_oi(), 24, lo("2022-01-05"), lo("2026-01-01"))
df = pd.DataFrame(res, columns=["event","split","side","n","win%","mean_net%","t","placebo_pct","mean_net_incl_funding%"])
df.to_csv("results.csv", index=False)
print("span", pd.to_datetime(T[0], unit="ms"), pd.to_datetime(T[-1], unit="ms"), "bars", N)
for e, g in df.groupby("event", sort=False):
    print("\n###", e); g=g.drop(columns="event").round(3); print("| "+" | ".join(g.columns)+" |"); print("|"+"---|"*len(g.columns))
    for r in g.itertuples(index=False): print("| "+" | ".join(str(x) for x in r)+" |")
