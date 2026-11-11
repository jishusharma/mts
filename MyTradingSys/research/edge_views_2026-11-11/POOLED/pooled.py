"""POOLED test: FLOW cascade long (flow_test.py) and TREND 4h Donchian 55/20 (trend.py) on ten coins. See PREREG.md. One run, no tuning."""
import glob, sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'backtest'))
from fees import BINANCE_TAKER  # shared cost source (T06): 2 x taker = 0.10 % round trip
FEE = BINANCE_TAKER * 2
HOUR = 3600_000; DAY = 24 * HOUR
R = "F:/MTS/data/tom_raw/"
COINS = {"BTC": "klines", "ETH": "klines_eth", **{s.upper(): "klines_" + s for s in "ada avax bnb doge link ltc sol xrp".split()}}
ms = lambda s: int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)
A_DEV_END, A_VAL_START = ms("2024-02-19"), ms("2024-03-20")
B_DEV_END, B_VAL_START = pd.Timestamp("2023-07-05 16:00"), pd.Timestamp("2023-08-04 20:00")


def load_1m(folder):
    fr = []
    for f in sorted(glob.glob(R + folder + "/*.csv")):
        d = pd.read_csv(f, header=None, usecols=range(6), names=["t", "o", "h", "l", "c", "v"], dtype=str)
        fr.append(d[d.t.str.fullmatch(r"\d+")].astype(float))
    d = pd.concat(fr).drop_duplicates("t").sort_values("t")
    d["t"] = np.where(d.t > 1e14, d.t / 1000, d.t).astype("int64")
    d.index = pd.to_datetime(d.t, unit="ms")
    return d


def bars(d, rule):
    b = d.resample(rule).agg({"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum"})
    b = b[d.c.resample(rule).count() > 0].copy()
    b["t"] = b.index.as_unit("ms").astype("int64")
    return b


def tstat(x):
    x = np.asarray(x, float); n = len(x)
    if n < 3 or x.std(ddof=1) == 0: return np.nan
    return x.mean() / (x.std(ddof=1) / np.sqrt(n))


# ---------------- Rule A ----------------
H = 24


def flow_coin(b):
    T, O, C, V = b.t.values, b.o.values, b.c.values, b.v.values; N = len(b)
    med = pd.Series(V).shift(1).rolling(720).median().values
    ret = C / O - 1; sig = []
    for i in range(720, N - 2):
        if V[i] > 3 * med[i] and ret[i] <= -0.03: sig.append(i + 1)
    skipped = 0; ev = []; busy = -1
    for e in sig:
        if e <= busy: continue
        if e + H - 1 >= N or T[e + H - 1] - T[e] != (H - 1) * HOUR or T[e] - T[e - 1] != HOUR: skipped += 1; continue
        busy = e + H - 1
        ev.append((T[e], C[e + H - 1] / O[e] - 1 - FEE))
    e = np.arange(721, N - H + 1)
    ok = (T[e + H - 1] - T[e] == (H - 1) * HOUR) & (T[e] - T[e - 1] == HOUR)
    e = e[ok]
    pool = (T[e], C[e + H - 1] / O[e] - 1 - FEE)
    return ev, pool, skipped


def period(t):
    return np.where(t < A_DEV_END, "DEV", np.where(t >= A_VAL_START, "VAL", "gap"))


def daymeans(t, x):
    d = t // DAY; u, inv = np.unique(d, return_inverse=True)
    return np.bincount(inv, weights=x) / np.bincount(inv)


def run_A():
    rng = np.random.default_rng(11); ev = {}; pools = {}; sk = {}
    for c, f in COINS.items():
        ev[c], pools[c], sk[c] = flow_coin(bars(load_1m(f), "1h")); print("A", c, len(ev[c]), flush=True)
    out = {"coin": [], "pooled": [], "skipped": sk}
    for per in ("DEV", "VAL"):
        T_all, X_all = [], []
        for c in COINS:
            t = np.array([a for a, _ in ev[c]], dtype="int64"); x = np.array([b for _, b in ev[c]], float)
            m = period(t) == per if len(t) else np.array([], bool)
            t, x = t[m], x[m]; T_all.append(t); X_all.append(x)
            out["coin"].append((per, c, len(x), 100 * x.mean() if len(x) else np.nan, tstat(x)))
        t = np.concatenate(T_all); x = np.concatenate(X_all)
        dm = daymeans(t, x)
        draws_day, draws_ev = [], []
        for _ in range(200):
            tt, xx = [], []
            for c, T_ in zip(COINS, T_all):
                n = len(T_)
                if n == 0: continue
                pt, px = pools[c]; pm = period(pt) == per
                idx = rng.integers(0, pm.sum(), n); tt.append(pt[pm][idx]); xx.append(px[pm][idx])
            tt = np.concatenate(tt); xx = np.concatenate(xx)
            draws_day.append(daymeans(tt, xx).mean()); draws_ev.append(xx.mean())
        draws_day, draws_ev = np.array(draws_day), np.array(draws_ev)
        out["pooled"].append(dict(per=per, n_ev=len(x), ev_mean=100 * x.mean(), n_days=len(dm), day_mean=100 * dm.mean(),
            day_t=tstat(dm), pct_day=100 * np.mean(draws_day < dm.mean()), p95_day=100 * np.percentile(draws_day, 95),
            pct_ev=100 * np.mean(draws_ev < x.mean()), p95_ev=100 * np.percentile(draws_ev, 95),
            win=100 * (x > 0).mean(), placebo_mean_day=100 * draws_day.mean()))
    return out


# ---------------- Rule B ----------------
def donchian(df, N, X):  # copied unchanged from TREND/trend.py (same tuples)
    o, h, l, c = [df[k].values for k in 'ohlc']; n = len(c); tr = []; pos = 0
    hi = pd.Series(h).shift(1).rolling(N).max().values; lo = pd.Series(l).shift(1).rolling(N).min().values
    xh = pd.Series(h).shift(1).rolling(X).max().values; xl = pd.Series(l).shift(1).rolling(X).min().values
    i = max(N, X)
    while i < n - 1:
        if pos == 0:
            s = 1 if c[i] > hi[i] else (-1 if c[i] < lo[i] else 0)
            if s: pos = s; e = i + 1; ep = o[e]; stop = xl[i] if s == 1 else xh[i]; risk = abs(ep - stop) / ep
        else:
            if (pos == 1 and c[i] < xl[i]) or (pos == -1 and c[i] > xh[i]):
                tr.append((pos, e, i + 1, pos * (o[i + 1] / ep - 1) - FEE, risk)); pos = 0; continue
        i += 1
    if pos: tr.append((pos, e, n - 1, pos * (c[n - 1] / ep - 1) - FEE, risk))
    return tr


def placebo_B(df, tr, rng, draws=200):
    c = df.c.values; o = df.o.values; n = len(c); dirs = np.array([t[0] for t in tr]); hold = np.array([t[2] - t[1] for t in tr]); out = []
    for _ in range(draws):
        hs = rng.choice(hold, len(tr)); st = np.array([rng.integers(1, max(2, n - 1 - h)) for h in hs]); en = np.minimum(st + hs, n - 1)
        out.append(np.mean(dirs * (c[en] / o[st] - 1) - FEE))
    return np.array(out)


def monthly(trs):
    if not trs: return np.array([])
    s = pd.Series([x for _, x in trs], index=pd.DatetimeIndex([t for t, _ in trs]))
    return s.groupby(s.index.to_period("M")).mean().values


def run_B():
    rng = np.random.default_rng(1); rows = []; pooled_in = {}
    for c, f in COINS.items():
        h4 = bars(load_1m(f), "4h")[["o", "h", "l", "c"]]; print("B", c, len(h4), flush=True)
        for per, sd in (("DEV", h4[h4.index <= B_DEV_END]), ("VAL", h4[h4.index >= B_VAL_START])):
            if len(sd) < 100: continue
            tr = donchian(sd, 55, 20); bh = sd.c.iloc[-1] / sd.o.iloc[0] - 1
            for side, f_ in (("ALL", lambda t: True), ("long", lambda t: t[0] == 1), ("short", lambda t: t[0] == -1)):
                sub = [t for t in tr if f_(t)]; x = np.array([t[3] for t in sub])
                pl = placebo_B(sd, sub, rng) if sub else np.array([])
                comp = np.prod(1 + x) - 1 if len(x) else 0.0
                rows.append(dict(per=per, coin=c, side=side, n=len(x), mean=100 * x.mean() if len(x) else np.nan, t=tstat(x),
                                 win=100 * (x > 0).mean() if len(x) else np.nan, pct=100 * np.mean(pl < x.mean()) if len(x) else np.nan,
                                 comp=100 * comp, bh=100 * bh, span=f"{sd.index[0].date()}..{sd.index[-1].date()}"))
                pooled_in.setdefault((per, side), []).append((len(x), x, pl, [(sd.index[t[2]], t[3]) for t in sub]))
    pooled = []
    for (per, side), L in pooled_in.items():
        n = sum(a[0] for a in L); x = np.concatenate([a[1] for a in L]); mt = [z for a in L for z in a[3]]
        mo = monthly(mt); pdraw = sum(a[0] * a[2] for a in L if a[0]) / n
        pooled.append(dict(per=per, side=side, n=n, mean=100 * x.mean(), win=100 * (x > 0).mean(), months=len(mo), month_mean=100 * mo.mean(),
                           t_month=tstat(mo), pct=100 * np.mean(pdraw < x.mean()), p95=100 * np.percentile(pdraw, 95),
                           placebo_mean=100 * pdraw.mean(), t_trade=tstat(x)))
    return rows, pooled


def regime(a, b, btc_d):
    r13 = btc_d.c.pct_change(91)
    r13 = r13[(r13.index >= a) & (r13.index < b)].resample("W").last().dropna()
    lab = np.where(r13 > .15, "bull", np.where(r13 < -.15, "bear", "range"))
    return " / ".join(f"{100 * np.mean(lab == k):.0f}% {k}" for k in ("bull", "bear", "range")) + f" ({len(lab)} weeks)"


if __name__ == "__main__":
    A = run_A(); Brows, Bpool = run_B()
    btc_d = load_1m("klines").resample("1D").agg({"c": "last"}).dropna()
    reg = {"A DEV": regime(pd.Timestamp("2022-01-01"), pd.Timestamp(A_DEV_END, unit="ms"), btc_d),
           "A VAL": regime(pd.Timestamp(A_VAL_START, unit="ms"), pd.Timestamp("2026-10-01"), btc_d),
           "B DEV": regime(pd.Timestamp("2022-01-01"), B_DEV_END, btc_d), "B VAL": regime(B_VAL_START, pd.Timestamp("2026-10-01"), btc_d)}
    f = lambda v, d=2: "" if v is None or v != v else f"{v:.{d}f}"
    o = ["# POOLED tables (generated by pooled.py; n on every row)\n", "## A. FLOW cascade long, 24 h, fee 10 bp\n",
         "| period | events n | per-event mean % | win % | days n | per-day mean % | per-day t | placebo per-day mean % | placebo pct (per-day) | placebo p95 % | placebo pct (per-event) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in A["pooled"]:
        o.append(f"| {p['per']} | {p['n_ev']} | {f(p['ev_mean'])} | {f(p['win'], 0)} | {p['n_days']} | {f(p['day_mean'])} | {f(p['day_t'])} | {f(p['placebo_mean_day'])} | {f(p['pct_day'], 0)} | {f(p['p95_day'])} | {f(p['pct_ev'], 0)} |")
    o += ["\nPer coin (events, one position at a time):\n", "| period | coin | n | mean net % | t |", "|---|---|---|---|---|"]
    o += [f"| {a} | {b} | {n} | {f(m)} | {f(t)} |" for a, b, n, m, t in A["coin"]]
    o.append(f"\nSkipped signals (gap in bars): {A['skipped']}\n")
    o += ["## B. TREND 4h Donchian 55/20, fee 10 bp\n", "Pooled (t on monthly pooled returns, month = exit month):\n",
          "| period | side | trades n | mean net %/trade | win % | months n | month mean % | t (monthly) | t (per trade) | placebo mean % | placebo pct | placebo p95 % |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in Bpool:
        o.append(f"| {p['per']} | {p['side']} | {p['n']} | {f(p['mean'])} | {f(p['win'], 0)} | {p['months']} | {f(p['month_mean'])} | {f(p['t_month'])} | {f(p['t_trade'])} | {f(p['placebo_mean'])} | {f(p['pct'], 0)} | {f(p['p95'])} |")
    o += ["\nPer coin:\n", "| period | coin | side | n | win % | mean net % | t | placebo pct | strategy compounded % | buy-and-hold % | span |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in Brows:
        o.append(f"| {r['per']} | {r['coin']} | {r['side']} | {r['n']} | {f(r['win'], 0)} | {f(r['mean'])} | {f(r['t'])} | {f(r['pct'], 0)} | {f(r['comp'], 1)} | {f(r['bh'], 1)} | {r['span']} |")
    o += ["\n## Regime mix (BTC 13-week return label, weeks)\n"] + [f"- {k}: {v}" for k, v in reg.items()]
    pathlib.Path(__file__).with_name("tables.md").write_text("\n".join(o), encoding="utf-8")
    print("\n".join(o))
