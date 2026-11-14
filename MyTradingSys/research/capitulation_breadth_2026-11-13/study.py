"""Run the 12 pre-registered cells. Usage: python study.py  -> results.json + printed summary."""
import json, os, sys, time, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from breadth_lib import wilder_rsi, breadth, find_events, find_entry, fwd_stop2r
from fetch import OUT
from universe import build
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees
COST = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13
STEP = 4 * 3600 * 1000
VAL0 = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
rng = np.random.default_rng(20261113)


def load():
    coins = [c for _, c, _ in build()[:60]]
    data = {c: json.load(open(os.path.join(OUT, c + "_4h.json"))) for c in coins}
    now = int(time.time() * 1000)
    t0 = min(d[0][0] for d in data.values()); t1 = max(d[-1][0] for d in data.values())
    if t1 + STEP > now:
        t1 -= STEP  # drop still-forming bar
    ts = np.arange(t0, t1 + 1, STEP); n = len(ts)
    A = {k: np.full((len(coins), n), np.nan) for k in "OHLCV"}
    for i, c in enumerate(coins):
        for r in data[c]:
            if r[0] > t1:
                continue
            x = (r[0] - t0) // STEP
            A["O"][i, x], A["H"][i, x], A["L"][i, x], A["C"][i, x], A["V"][i, x] = r[1], r[2], r[3], r[4], r[5]
    return coins, ts, A


coins, ts, A = load()
O, H, L, C, V = A["O"], A["H"], A["L"], A["C"], A["V"]
n = len(ts); BT = coins.index("BTC")
RSI = np.full(C.shape, np.nan)
for i in range(len(coins)):
    ok = ~np.isnan(C[i]); idx = np.where(ok)[0]
    RSI[i, idx] = wilder_rsi(C[i, idx])
B = breadth(RSI, 25.0)
csum = np.cumsum(np.nan_to_num(V), axis=1)


def top10(j):
    w = csum[:, j] - csum[:, j - 180] if j >= 180 else csum[:, j]
    cand = np.where(~np.isnan(C[:, j]))[0]
    return cand[np.argsort(-w[cand])[:10]]


_t10 = {}


def t10(j):
    if j not in _t10:
        _t10[j] = top10(j)
    return _t10[j]


def lastclose(i, k, j):
    x = C[i, k]
    if not np.isnan(x):
        return x
    s = C[i, j:k + 1]; s = s[~np.isnan(s)]
    return s[-1]


def fwd_ret(basket, kind, j, wlen):
    """net return of one trade entered at close of bar j; None if the exit lies beyond the data."""
    if kind[0] == "hold":
        k = j + kind[1]
        if k > n - 1:
            return None
        pb = None
    else:
        if j + kind[1] > n - 1:
            return None
        wl = np.nanmin(L[BT, j - wlen + 1: j + 1])
        k, pb = fwd_stop2r(j, wl, O[BT], H[BT], L[BT], C[BT], cap=kind[1])
    if basket == "BTC":
        p = pb if pb is not None else C[BT, k]
        return p / C[BT, j] - 1 - COST
    return float(np.mean([lastclose(i, k, j) / C[i, j] - 1 - COST for i in t10(j)]))


def fwd_gross(basket, j, h):
    k = min(j + h, n - 1)
    if basket == "BTC":
        return C[BT, k] / C[BT, j] - 1
    return float(np.mean([lastclose(i, k, j) / C[i, j] - 1 for i in t10(j)]))


def fwd_mae(basket, j, h=42):
    k = min(j + h, n - 1)
    if basket == "BTC":
        return np.nanmin(L[BT, j + 1:k + 1]) / C[BT, j] - 1
    return float(np.mean([np.nanmin(L[i, j + 1:k + 1]) / C[i, j] - 1 for i in t10(j)]))


def d(t):
    return dt.datetime.fromtimestamp(ts[t] / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


KINDS = {"H12": ("hold", 12), "H42": ("hold", 42), "STOP2R": ("stop", 42)}
EV = {}
for T in (0.30, 0.50):
    out = []
    for t in find_events(B, T):
        j = find_entry(B, C[BT], t)
        hi = np.nanmax(H[BT, max(t - 180, 0):t])
        out.append(dict(t=t, j=j, B=float(B[t]), dd=float(C[BT, t] / hi - 1), val=bool(ts[t] >= VAL0)))
    EV[T] = out


def boot(x, nb=10000):
    x = np.asarray(x); m = x[rng.integers(0, len(x), (nb, len(x)))].mean(1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5), float((m <= 0).mean())


def yr(t):
    return dt.datetime.fromtimestamp(ts[t] / 1000, dt.timezone.utc).year


rows = []
valid_bars = [t for t in range(200, n - 43) if not np.isnan(C[BT, t])]
by_year = {}
for t in valid_bars:
    by_year.setdefault(yr(t), []).append(t)
for T in (0.30, 0.50):
    for bk in ("BTC", "TOP10"):
        for kn, kind in KINDS.items():
            tr = []
            for e in EV[T]:
                if e["j"] is None:
                    continue
                wl = e["j"] - e["t"] + 1
                r = fwd_ret(bk, kind, e["j"], wl)
                if r is None:
                    continue
                tr.append(dict(e=e, r=r, rb=fwd_ret(bk, kind, e["t"], 1), wl=wl))
            dev = [x["r"] for x in tr if not x["e"]["val"]]
            val = [x for x in tr if x["e"]["val"]]
            vr = np.array([x["r"] for x in val])
            row = dict(T=T, basket=bk, exit=kn, n_dev=len(dev), n_val=len(vr), dev_mean=float(np.mean(dev)) if dev else None,
                       n_events_val=sum(1 for e in EV[T] if e["val"]), n_events_dev=sum(1 for e in EV[T] if not e["val"]))
            if len(vr):
                lo, hi_, p1 = boot(vr)
                row.update(mean_val=float(vr.mean()), ci=[float(lo), float(hi_)], p_boot=p1, win=float((vr > 0).mean()),
                           worst=float(vr.min()), worst_date=d(val[int(vr.argmin())]["e"]["t"]))
                cnt = 0; N = 1000
                for _ in range(N):
                    s = []
                    for x in val:
                        pool = by_year.get(yr(x["e"]["j"]), valid_bars)
                        q = fwd_ret(bk, kind, int(pool[rng.integers(len(pool))]), x["wl"])
                        if q is not None:
                            s.append(q)
                    if s and np.mean(s) >= vr.mean():
                        cnt += 1
                row["plac_a_p"] = (1 + cnt) / (N + 1)
                pv = [x for x in val if x["rb"] is not None]
                if pv:
                    row["plac_b_event_mean"] = float(np.mean([x["rb"] for x in pv]))
                    row["plac_b_diff"] = float(np.mean([x["r"] for x in pv]) - row["plac_b_event_mean"])
            rows.append(row)
ps = [r.get("p_boot", 1.0) for r in rows]
order = np.argsort(ps); m = len(ps); kmax = 0
for rank, i in enumerate(order, 1):
    if ps[i] <= 0.10 * rank / m:
        kmax = rank
rej = set(int(i) for rank, i in enumerate(order, 1) if rank <= kmax)
for i, r in enumerate(rows):
    r["bh"] = i in rej
    if r["n_val"] < 12:
        r["verdict"] = "UNDERPOWERED"
    else:
        ok = (r["ci"][0] > 0 and r["mean_val"] > 0 and (r["dev_mean"] if r["dev_mean"] is not None else -1) > 0 and r["plac_a_p"] <= 0.05
              and (r.get("plac_b_diff") if r.get("plac_b_diff") is not None else -1) > 0 and r["bh"])
        r["verdict"] = "PASS" if ok else "FAIL"
tab = []
for T in (0.30, 0.50):
    for e in EV[T]:
        j = e["j"]; base = j if j is not None else e["t"]
        full = base + 42 <= n - 1
        tab.append(dict(T=T, date=d(e["t"]), B=e["B"], dd=e["dd"], entry=d(j) if j is not None else "no confirm", split="VAL" if e["val"] else "DEV",
                        btc2=fwd_gross("BTC", base, 12), btc7=fwd_gross("BTC", base, 42), top2=fwd_gross("TOP10", base, 12), top7=fwd_gross("TOP10", base, 42),
                        mae_btc=fwd_mae("BTC", base) if full else None, mae_top=fwd_mae("TOP10", base) if full else None, complete=full, tr=j is not None))
last = n - 1
today = dict(last_bar=d(last), B_last=float(B[last]), B_min_5d=float(np.nanmin(B[last - 29:last + 1])), B_max_5d=float(np.nanmax(B[last - 29:last + 1])),
             B_hist_pct=float((B[~np.isnan(B)] < B[last]).mean()), n_defined=int((~np.isnan(RSI[:, last])).sum()),
             events_last7d={str(T): [d(e["t"]) for e in EV[T] if e["t"] >= last - 42] for T in EV},
             B_tail=[round(float(x), 3) for x in B[-12:]], B_max_ever=float(np.nanmax(B)),
             B_min_last_day=float(np.nanmin(B[-6:])))
json.dump(dict(cells=rows, events=tab, today=today, n_bars=n, first=d(0), last=d(n - 1), universe=coins, n_events={str(T): len(EV[T]) for T in EV}),
          open(os.path.join(HERE, "results.json"), "w"), indent=1)
print(json.dumps(today)); print({T: len(EV[T]) for T in EV})
for r in rows:
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
