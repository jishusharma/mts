"""Independent recompute of anticipation_map 8 cells from PRE_REG.md definitions only (OURS)."""
import glob, sys
import numpy as np
import pandas as pd

VAR = sys.argv[1] if len(sys.argv) > 1 else "A"  # A: price at t-60 = open of bar t-60; B: close of bar t-60
CUT = pd.Timestamp("2024-07-01")
K = pd.concat([pd.read_csv(f, usecols=["open_time", "open", "close", "volume", "taker_buy_volume"])
               for f in sorted(glob.glob("F:/MTS/data/tom_raw/klines/BTCUSDT-1m-202[2-4]-*.csv"))])
K["t"] = pd.to_datetime(K.open_time, unit="ms")
K = K[K.t < CUT].drop_duplicates("t").set_index("t").sort_index()
M = pd.concat([pd.read_csv(f, usecols=["create_time", "sum_open_interest"])
               for f in sorted(glob.glob("F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-202[2-4]-*.csv"))])
M["t"] = pd.to_datetime(M.create_time)
oi = M[M.t < CUT].drop_duplicates("t").set_index("t").sort_index().sum_open_interest
print("zero-OI rows", int((oi <= 0).sum()))
oi = oi[oi > 0]  # PRE_REG silent; zero OI = feed gap = missing
print("kline rows", len(K), "oi rows", len(oi))
cl, op = K.close, K.open
delta = 2 * K.taker_buy_volume - K.volume
full = K.reindex(pd.date_range(K.index.min(), K.index.max(), freq="1min"))
ok = full.close.notna().astype(int)
cnt = ok.rolling(120).sum()  # ending at bar index i covers [i-119, i]
rows = []
for t in pd.date_range("2022-01-01", "2024-07-01", freq="1h", inclusive="left"):
    a = t - pd.Timedelta(minutes=60)
    b = t + pd.Timedelta(minutes=60)
    last = b - pd.Timedelta(minutes=1)
    if last not in cnt.index or cnt[last] != 120:
        continue
    if a not in oi.index or t not in oi.index or b not in oi.index:
        continue
    p_a = full.open[a] if VAR == "A" else full.close[a]
    p_t = full.close[t - pd.Timedelta(minutes=1)]
    p_b = full.close[last]
    d = delta[a:t - pd.Timedelta(minutes=1)].sum()
    rows.append((t, p_a, p_t, p_b, oi[a], oi[t], oi[b], d))
E = pd.DataFrame(rows, columns=["t", "pa", "pt", "pb", "oa", "ot", "ob", "d"])
print("events (complete bars + OI)", len(E))
pc = E.pt / E.pa - 1
oc = E.ot / E.oa - 1
keep = (pc.abs() >= 0.001) & (oc.abs() >= 0.001)
E = E[keep].copy()
E["ps"] = np.sign(pc[keep]); E["os"] = np.sign(oc[keep])
E["dl"] = np.where(E.d > 0, "BUY", "SELL")
E["cont"] = np.sign(E.pb - E.pt) == E.ps
E["undone"] = np.where(E.ps > 0, E.pb < E.pa, E.pb > E.pa)
E["oik"] = np.sign(E.ob - E.ot) == E.os
print("events after FLAT drop", len(E))
for (ps, os_), g in E.groupby(["ps", "os"]):
    print(f"state price{'+' if ps>0 else '-'} OI{'+' if os_>0 else '-'}: {len(g)}")
    for dl in ("BUY", "SELL"):
        c = g[g.dl == dl]
        print(f"  {dl}: n={len(c)} share={len(c)/len(g)*100:.1f}% cont={c.cont.mean()*100:.1f}% "
              f"undone={c.undone.mean()*100:.1f}% oik={c.oik.mean()*100:.1f}%")
