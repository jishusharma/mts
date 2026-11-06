"""Independent blind recompute of level_approach_prep U1/U2/U3 from PRE_REG.md definitions only."""
import glob, json, sys
import numpy as np, pandas as pd

CUT = pd.Timestamp("2024-07-01")
K = sorted(glob.glob("F:/MTS/data/tom_raw/klines/BTCUSDT-1m-202[234]-*.csv"))
df = pd.concat([pd.read_csv(f, usecols=range(11)) for f in K])
df["t"] = pd.to_datetime(df.open_time, unit="ms")
df = df[df.t < CUT].drop_duplicates("t").sort_values("t").set_index("t")
m = pd.concat([pd.read_csv(f, usecols=["create_time", "sum_open_interest"])
               for f in sorted(glob.glob("F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-202[234]-*.csv"))])
m["t"] = pd.to_datetime(m.create_time)
oi = m[m.t < CUT].drop_duplicates("t").set_index("t").sort_index().sum_open_interest
O, H, L, C, V, TB = (df[c].values for c in ["open", "high", "low", "close", "volume", "taker_buy_volume"])
idx = df.index
pos = {t: i for i, t in enumerate(idx)}
days = sorted(set(idx.normalize()))
print("rows", len(df), "first", idx[0], "last", idx[-1], "days", len(days), "oi rows", len(oi))

ZONE, BRK = 0.003, 0.001
rows = []
for d in days[1:]:
    p = d - pd.Timedelta(days=1)
    pm = df.loc[p:d - pd.Timedelta(minutes=1)]
    dm = df.loc[d:d + pd.Timedelta(hours=23, minutes=59)]
    if len(pm) == 0 or len(dm) == 0:
        continue
    i0 = pos[dm.index[0]]; i1 = pos[dm.index[-1]] + 1
    for side, lvl in (("H", pm.high.max()), ("L", pm.low.min())):
        s = 1 if side == "H" else -1
        op = O[i0]
        inzone = op >= lvl * (1 - ZONE) if side == "H" else op <= lvl * (1 + ZONE)
        if inzone:
            continue
        # approach t
        t = None
        for i in range(i0, i1):
            if (side == "H" and H[i] >= lvl * (1 - ZONE)) or (side == "L" and L[i] <= lvl * (1 + ZONE)):
                t = i; break
        # touch u
        u = None
        for i in range(i0, i1):
            if (side == "H" and H[i] >= lvl) or (side == "L" and L[i] <= lvl):
                u = i; break
        r = dict(day=d, side=side, lvl=lvl, t=t, u=u)
        if t is not None and t >= 2 and t + 63 < len(df):
            v = V[t-2:t+1].sum()
            ds = s * (2 * TB[t-2:t+1] - V[t-2:t+1]).sum() / v if v > 0 else 0
            ext = ((H[t+1:t+4].max() - C[t]) if side == "H" else (C[t] - L[t+1:t+4].min())) / C[t]
            ab = ds >= 0.3 and ext < 0.001
            ref = C[t + 3]
            rev = None; rev_alt = None
            for j in range(t + 4, t + 64):
                brk = (C[j] > lvl * (1 + BRK)) if side == "H" else (C[j] < lvl * (1 - BRK))
                back = (L[j] <= ref * 0.995) if side == "H" else (H[j] >= ref * 1.005)
                if rev is None:
                    if back: rev = True
                    elif brk: rev = False
                if rev_alt is None:
                    if brk: rev_alt = False
                    elif back: rev_alt = True
                if rev is not None and rev_alt is not None: break
            brkf = rev is False
            rev = bool(rev); rev_alt = bool(rev_alt)
            dist = (lvl - C[t]) / lvl * s * 1.0  # >0 below level (for H)
            bucket = "beyond" if dist < 0 else "0-0.1" if dist < 0.001 else "0.1-0.2" if dist < 0.002 else "0.2+"
            ts = idx[t]
            e = (ts + pd.Timedelta(minutes=4)).floor("5min")
            b = (ts - pd.Timedelta(minutes=7)).floor("5min")
            ch = np.nan
            if e in oi.index and b in oi.index:
                ch = oi[e] / oi[b] - 1
            oig = "NA" if np.isnan(ch) else "UP" if ch > 0.001 else "DOWN" if ch < -0.001 else "FLAT"
            r.update(brkf=brkf, ds=ds, ext=ext, ab=ab, rev=rev, rev_alt=rev_alt, bucket=bucket, oig=oig, valid_u1=True)
        else:
            r["valid_u1"] = False
        if u is not None and u + 60 <= len(df):
            cnt = 0
            ut = idx[u]
            w0 = ut - pd.Timedelta(minutes=15)
            win = df.loc[w0:ut - pd.Timedelta(minutes=1)]
            for tf in (1, 2, 3, 5):
                found = False
                g = win.resample(f"{tf}min", origin="epoch", label="left", closed="left")
                for st, gg in g:
                    if len(gg) != tf or st < w0 or st + pd.Timedelta(minutes=tf) > ut:
                        continue
                    hi, lo, o_, c_ = gg.high.max(), gg.low.min(), gg.open.iloc[0], gg.close.iloc[-1]
                    rg = hi - lo
                    if rg <= 0: continue
                    if side == "H":
                        ok = hi >= lvl * (1 - ZONE) and (hi - max(o_, c_)) / rg >= 0.5
                    else:
                        ok = lo <= lvl * (1 + ZONE) and (min(o_, c_) - lo) / rg >= 0.5
                    if ok: found = True; break
                cnt += found
            seg = C[u:u + 60]
            hold = not ((seg > lvl * (1 + BRK)).any() if side == "H" else (seg < lvl * (1 - BRK)).any())
            r.update(wc=cnt, hold=bool(hold), valid_u3=True)
        else:
            r["valid_u3"] = False
        rows.append(r)

R = pd.DataFrame(rows)
out = {}
out["levels_considered"] = len(R)
out["approaches_found"] = int(R.t.notna().sum())
out["approaches_u1_valid"] = int(R.valid_u1.sum())
out["touches_found"] = int(R.u.notna().sum())
out["touches_u3_valid"] = int(R.valid_u3.sum())
U = R[R.valid_u1.astype(bool)].copy()
A = U[U.ab.astype(bool)]; N = U[~U.ab.astype(bool)]
out["absorption_n"] = len(A)
for key, col in (("primary", "rev"), ("alt_break_first", "rev_alt")):
    ar = A[col].mean()
    buckets = A.bucket.value_counts(normalize=True)
    mt = 0.0; used = 0.0
    for b_, w in buckets.items():
        nb = N[N.bucket == b_]
        if len(nb):
            mt += w * nb[col].mean(); used += w
    out[key] = dict(abs_rate=ar, nonabs_raw=N[col].mean(), matched=mt / used if used else None, used_w=used, nonabs_n=len(N))
out["break_first"] = dict(abs=float(A.brkf.astype(bool).mean()), nonabs=float(N.brkf.astype(bool).mean()))
out["bucket_mix_abs"] = A.bucket.value_counts().to_dict()
out["u2"] = {k: dict(n=len(g), rev=g.rev.mean()) for k, g in A.groupby("oig")}
T = R[R.valid_u3.astype(bool)]
out["u3"] = {int(k): dict(n=len(g), hold=g.hold.mean()) for k, g in T.groupby("wc")}
out["u3_3plus"] = dict(n=int((T.wc >= 3).sum()), hold=float(T[T.wc >= 3].hold.mean()))
print(json.dumps(out, indent=1, default=float))
