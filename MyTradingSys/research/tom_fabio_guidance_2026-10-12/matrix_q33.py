"""Q33 matrix runner. Spec: PRE_REG_Q33.md (frozen before the first run). Event study, fee-net, placebo + BH-FDR.
Usage: python matrix_q33.py [klines_dir] [out_dir]
"""
import sys, glob, csv, os, itertools
sys.dont_write_bytecode = True
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)
from MyTradingSys.backtest.fees import FEES_ALL_TAKER  # noqa: E402

KDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "Dumps", "backtest", "raw_1m_2022", "klines")
OUT = sys.argv[2] if len(sys.argv) > 2 else HERE
FEE = FEES_ALL_TAKER["entry"] + FEES_ALL_TAKER["timeout"]
RNG = np.random.default_rng(20261012)
HS = (1, 4, 16)
PRIMARY = 4
COOL = 4

# ---------- load 1m, build 15m ----------
rows = []
for f in sorted(glob.glob(os.path.join(KDIR, "*.csv"))):
    with open(f) as fh:
        r = csv.reader(fh); next(r)
        rows.extend(r)
a = np.array([[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])] for x in rows])
ts1, o1, h1, l1, c1, v1, tb1 = a.T
n1 = len(a) // 15 * 15
def r15(x, how):
    x = x[:n1].reshape(-1, 15)
    return {"o": x[:, 0], "c": x[:, -1], "h": x.max(1), "l": x.min(1), "s": x.sum(1)}[how]
O, H, L, C = r15(o1, "o"), r15(h1, "h"), r15(l1, "l"), r15(c1, "c")
V, TB = r15(v1, "s"), r15(tb1, "s")
T0 = ts1[0]
N = len(C)
t_ms = T0 + np.arange(N) * 900000.0
DELTA = 2 * TB - V
day = ((t_ms - T0) // 86400000).astype(int)
tod = ((t_ms - T0) // 900000 % 96).astype(int)
print("bars15", N, "fee/rt", FEE)

def roll_mean(x, n):
    cs = np.cumsum(np.insert(x, 0, 0.0)); out = np.full(len(x), np.nan)
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out
def roll_sd(x, n):
    m = roll_mean(x, n); m2 = roll_mean(x * x, n)
    return np.sqrt(np.maximum(m2 - m * m, 0))
def atr(n):
    pc = np.r_[C[0], C[:-1]]
    tr = np.maximum(H - L, np.maximum(abs(H - pc), abs(L - pc)))
    out = np.full(N, np.nan); out[n - 1] = tr[:n].mean()
    for i in range(n, N):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out

SMA = roll_mean(C, 20); SD = roll_sd(C, 20)
UP, LO = SMA + 2 * SD, SMA - 2 * SD
ATR15 = atr(14)
BBW = (UP - LO) / SMA

# ---------- filters ----------
# F1
tp = (H + L + C) / 3
cumpv = np.cumsum(tp * V); cumv = np.cumsum(V)
first = np.r_[0, np.flatnonzero(np.diff(day)) + 1]
base_pv = np.zeros(N); base_v = np.zeros(N)
for s, e in zip(first, np.r_[first[1:], N]):
    base_pv[s:e] = cumpv[s - 1] if s else 0; base_v[s:e] = cumv[s - 1] if s else 0
VW = (cumpv - base_pv) / np.maximum(cumv - base_v, 1e-9)
f1a = np.sign(C - VW)
week = day // 7
nweek = week.max() + 1
poc = np.full(nweek, np.nan)
for w in range(nweek):
    m = week == w
    if m.sum() == 0: continue
    b = np.floor(np.log(tp[m]) / 0.001).astype(int)
    u, inv = np.unique(b, return_inverse=True)
    vol = np.bincount(inv, weights=V[m])
    poc[w] = np.exp((u[vol.argmax()] + 0.5) * 0.001)
wpoc = np.full(N, 0.0)
for w in range(2, nweek):
    wpoc[week == w] = np.sign(poc[w - 1] - poc[w - 2])
n4 = N // 16
C4 = C[:n4 * 16].reshape(-1, 16)[:, -1]
ema = np.zeros(n4); ema[0] = C4[0]
for i in range(1, n4): ema[i] = ema[i - 1] + (2 / 21) * (C4[i] - ema[i - 1])
slope4 = np.zeros(n4); slope4[6:] = np.sign(ema[6:] - ema[:-6])
idx4 = (np.arange(N) + 1) // 16 - 1
f1c = np.where(idx4 >= 6, slope4[np.clip(idx4, 0, n4 - 1)], 0.0)
votes = f1a + wpoc + f1c
F1 = np.where(votes >= 2, 1, np.where(votes <= -2, -1, 0))   # +1 UP, -1 DOWN, 0 MIXED
# F3
den = roll_mean(V, 2) * 2
cvd = np.where(den > 0, roll_mean(DELTA, 2) * 2 / np.maximum(den, 1e-9), 0)
cm, cs_ = roll_mean(cvd, 2880), roll_sd(cvd, 2880)
cz = (cvd - cm) / np.where(cs_ > 0, cs_, np.nan)
F3 = np.where(cz >= 1, 1, np.where(cz <= -1, -1, 0)); F3[np.isnan(cz)] = 99
# F2
d = np.diff(C, prepend=C[0]); gain = np.maximum(d, 0); loss = np.maximum(-d, 0)
ag = np.zeros(N); al = np.zeros(N); ag[13] = gain[1:14].mean(); al[13] = loss[1:14].mean()
for i in range(14, N):
    ag[i] = (ag[i - 1] * 13 + gain[i]) / 14; al[i] = (al[i - 1] * 13 + loss[i]) / 14
RSI = 100 - 100 / (1 + ag / np.maximum(al, 1e-12))
F2 = np.where(RSI < 40, -1, np.where(RSI > 60, 1, 0)); F2[:20] = 99
# F7
W = 672
pr = np.full(N, np.nan)
valid = ~np.isnan(BBW)
for s in range(W + 20, N, 20000):
    e = min(N, s + 20000)
    win = swv(BBW[s - W + 1:e], W)
    pr[s:e] = (win <= BBW[s:e, None]).mean(1) * 100
F7 = np.where(pr <= 20, -1, np.where(pr >= 80, 1, 0)); F7[np.isnan(pr)] = 99  # -1 squeeze, +1 expanded
# F8 relative volume
nd = N // 96
Vd = V[:nd * 96].reshape(nd, 96)
med = np.full_like(Vd, np.nan)
med[20:] = np.median(swv(Vd, 20, axis=0)[:-1], axis=-1) if nd > 20 else np.nan
RV = np.full(N, np.nan); RV[:nd * 96] = (Vd / med).reshape(-1)

# ---------- prior-day profile (LVN / HVN) ----------
ATR1H = np.full(N, np.nan)
a4 = atr(14)  # 15m atr; 1h approx = sqrt(4) * 15m atr (frozen convention; no separate 1h ATR build)
ATR1H = a4 * 2.0
bands = {}   # day -> list of (lo, hi, w)
hvns = {}    # day -> sorted np.array of HVN prices
d1 = ((ts1[:n1] - T0) // 86400000).astype(int)
cl1 = c1[:n1]; vo1 = v1[:n1]
for dd in range(1, d1.max() + 1):
    m = d1 == dd - 1
    if m.sum() < 1000: continue
    first_bar = np.flatnonzero(day == dd)
    if len(first_bar) == 0 or np.isnan(ATR1H[first_bar[0] - 1]): continue
    w = ATR1H[first_bar[0] - 1] / 10
    if w <= 0: continue
    lo_p = cl1[m].min()
    bi = np.floor((cl1[m] - lo_p) / w).astype(int)
    vol = np.bincount(bi, weights=vo1[m]).astype(float)
    sm = np.convolve(vol, np.ones(3) / 3, mode="same")
    ne = sm[sm > 0]
    if len(ne) < 5: continue
    med_ = np.median(ne)
    pk = [i for i in range(1, len(sm) - 1) if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= med_]
    hvns[dd] = lo_p + (np.array(pk) + 0.5) * w
    bl = []
    for p0, p1 in zip(pk[:-1], pk[1:]):
        seg = sm[p0 + 1:p1]
        lowm = seg <= 0.5 * med_
        i = 0
        while i < len(seg):
            if lowm[i]:
                j = i
                while j + 1 < len(seg) and lowm[j + 1]: j += 1
                bl.append((lo_p + (p0 + 1 + i) * w, lo_p + (p0 + 1 + j + 1) * w, w))
                i = j + 1
            else:
                i += 1
    bands[dd] = bl
print("days with profile", len(bands))

# ---------- events: arrays of (bar index t, move direction m) per variant ----------
EV = {}
def cool(items):
    out = []; last = {}
    for t, m in sorted(items):
        if t - last.get(m, -99) >= COOL:
            out.append((t, m)); last[m] = t
    return out
warm = 3000
# T1
ub = (C > UP) & (np.r_[False, C[:-1] <= UP[:-1]])
lb = (C < LO) & (np.r_[False, C[:-1] >= LO[:-1]])
t1 = [(t, 1) for t in np.flatnonzero(ub) if t >= warm] + [(t, -1) for t in np.flatnonzero(lb) if t >= warm]
t1 = cool(t1)
EV["T1_cont"] = (t1, +1); EV["T1_fade"] = (t1, -1)
# T2 / T2b
tr, rj = [], []
for dd, bl in bands.items():
    ids = np.flatnonzero(day == dd)
    if len(ids) == 0: continue
    for lo, hi, w in bl:
        for t in ids:
            if t < warm: continue
            if (C[t] > hi) and (C[t - 1] <= lo or (t >= 2 and C[t - 2] <= lo and lo < C[t - 1] <= hi)):
                tr.append((t, 1))
            elif (C[t] < lo) and (C[t - 1] >= hi or (t >= 2 and C[t - 2] >= hi and lo <= C[t - 1] < hi)):
                tr.append((t, -1))
            if H[t] >= lo + w and C[t] <= lo and C[t - 1] <= lo:
                rj.append((t, 1))      # approached from below, rejected back below
            if L[t] <= hi - w and C[t] >= hi and C[t - 1] >= hi:
                rj.append((t, -1))     # approached from above, rejected back above
EV["T2_cont"] = (cool(list(set(tr))), +1)
EV["T2b_fade"] = (cool(list(set(rj))), -1)
# T3 / T3b
hold, thru = [], []
for i in range(max(2, warm), N - 100):
    if L[i] > H[i - 2]:
        zlo, zhi, imp = H[i - 2], L[i], 1
    elif H[i] < L[i - 2]:
        zlo, zhi, imp = H[i], L[i - 2], -1
    else:
        continue
    tests = 0; inside = False
    for j in range(i + 1, min(i + 97, N - 1)):
        entered = (L[j] <= zhi) if imp == 1 else (H[j] >= zlo)
        failed = (C[j] < zlo) if imp == 1 else (C[j] > zhi)
        if failed: break
        if entered and not inside:
            tests += 1; inside = True
            if tests == 1: hold.append((j, -imp))      # m = approach direction = -impulse
            if tests == 2: thru.append((j, -imp)); break
        elif not entered:
            inside = False
EV["T3_hold"] = (cool(hold), -1)   # side = impulse = -m
EV["T3b_through"] = (cool(thru), +1)  # side = against impulse = m... approach dir
# T4
hi16 = np.full(N, np.nan); lo16 = np.full(N, np.nan)
rm = swv(H, 16).max(1); rn = swv(L, 16).min(1)
hi16[16:] = rm[:-1]; lo16[16:] = rn[:-1]   # prior 16 bars, excl. current
t4 = []
for t in range(max(warm, 17), N):
    dd = day[t]
    hv = hvns.get(dd)
    if hv is None or np.isnan(ATR15[t]): continue
    if C[t] > hi16[t] and F3[t] == 1:
        nxt = hv[hv > hi16[t]]
        if len(nxt) and nxt.min() - hi16[t] >= ATR15[t]: t4.append((t, 1))
    elif C[t] < lo16[t] and F3[t] == -1:
        nxt = hv[hv < lo16[t]]
        if len(nxt) and lo16[t] - nxt.max() >= ATR15[t]: t4.append((t, -1))
EV["T4_cont"] = (cool(t4), +1)

# ---------- evaluation ----------
SUP = (RV >= 1.5)
def rets(ts, side):
    out = {}
    for h in HS:
        ok = ts + 1 + h <= N - 1
        r = np.full(len(ts), np.nan)
        e = ts[ok] + 1
        r[ok] = side[ok] * (C[ts[ok] + h] / O[e] - 1) - FEE
        out[h] = r
    return out
allbars = np.arange(warm, N - 20)
def placebo_p(side, h, obs, n):
    ok = allbars + 1 + h <= N - 1
    pool = allbars[ok]
    rr = (C[pool + h] / O[pool + 1] - 1)
    draws = RNG.integers(0, len(pool), size=(1000, n))
    pm = (side * rr[draws]).mean(1) - FEE
    return float((pm >= obs).mean()), float(pm.mean())

filters = {"all": None}
for k in (1, -1, 0): filters[f"F1={k}"] = ("F1", k)
for k in (1, -1, 0): filters[f"F3={k}"] = ("F3", k)
for a_, b_ in itertools.product((1, -1, 0), repeat=2): filters[f"F1={a_}&F3={b_}"] = ("F1F3", (a_, b_))
for k in (-1, 0, 1): filters[f"F2={k}"] = ("F2", k)
for k in (-1, 0, 1): filters[f"F7={k}"] = ("F7", k)   # -1 squeeze, +1 expanded
filters["F8=supported"] = ("F8", 1); filters["F8=unsupported"] = ("F8", 0)

res = []
half = N // 2
for var, (evs, smode) in EV.items():
    if not evs: continue
    ts = np.array([e[0] for e in evs]); m = np.array([e[1] for e in evs], dtype=float)
    # side: cont +1 => m ; fade -1 => -m; T3_hold side=-m(=impulse); T3b side = m? (against impulse = m approach dir)
    side = m * smode
    for sd_name, sd in (("long", 1.0), ("short", -1.0)):
        sel_side = side == sd
        for fname, fdef in filters.items():
            if fdef is None: msk = sel_side
            else:
                kind, k = fdef
                if kind == "F1": msk = sel_side & (F1[ts] == k)
                elif kind == "F3": msk = sel_side & (F3[ts] == k)
                elif kind == "F1F3": msk = sel_side & (F1[ts] == k[0]) & (F3[ts] == k[1])
                elif kind == "F2": msk = sel_side & (F2[ts] == k)
                elif kind == "F7": msk = sel_side & (F7[ts] == k)
                elif kind == "F8":
                    agree = (np.sign(cvd[ts]) == m)
                    sup = (SUP[ts] & agree)
                    msk = sel_side & (sup if k == 1 else (RV[ts] < 1.0))
            tsel = ts[msk]
            n = int(len(tsel))
            row = dict(trigger=var, side=sd_name, filt=fname, n=n)
            if n < 20:
                row.update(status="n<20"); res.append(row); continue
            R = rets(tsel, np.full(n, sd))
            for h in HS:
                r = R[h]; r = r[~np.isnan(r)]
                row[f"mean_H{h}"] = float(r.mean()) if len(r) else np.nan
                row[f"hit_H{h}"] = float((r > 0).mean()) if len(r) else np.nan
            r4 = R[PRIMARY]; okm = ~np.isnan(r4)
            row["h1_mean"] = float(r4[okm & (tsel < half)].mean()) if (okm & (tsel < half)).sum() else np.nan
            row["h2_mean"] = float(r4[okm & (tsel >= half)].mean()) if (okm & (tsel >= half)).sum() else np.nan
            if n >= 300:
                p, pm = placebo_p(sd, PRIMARY, row[f"mean_H{PRIMARY}"], n)
                row.update(p=p, placebo_mean=pm, status="tested")
            else:
                row.update(status="underpowered")
            res.append(row)
print("cells", len(res))

# BH-FDR over tested
tested = [r for r in res if r.get("status") == "tested"]
ps = np.array([r["p"] for r in tested]); mtests = len(ps)
order = np.argsort(ps); q = np.empty(mtests); prev = 1.0
for rank, i in enumerate(order[::-1]):
    k = mtests - rank
    prev = min(prev, ps[i] * mtests / k); q[i] = prev
for r, qq in zip(tested, q):
    r["q"] = float(qq)
    r["survivor"] = bool(qq <= 0.05 and r[f"mean_H{PRIMARY}"] > 0 and r["h1_mean"] > 0 and r["h2_mean"] > 0)

cols = ["trigger", "side", "filt", "n", "status", "mean_H1", "mean_H4", "mean_H16", "hit_H4", "h1_mean", "h2_mean", "placebo_mean", "p", "q", "survivor"]
with open(os.path.join(OUT, "MATRIX_CELLS.csv"), "w", newline="\n") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in res:
        w.writerow([("%.6g" % r[c]) if isinstance(r.get(c), float) else r.get(c, "") for c in cols])
ev_counts = {k: len(v[0]) for k, v in EV.items()}
print("events", ev_counts)
surv = [r for r in tested if r["survivor"]]
print("tested", mtests, "survivors", len(surv))
for r in sorted(tested, key=lambda r: r["p"])[:12]:
    print(r["trigger"], r["side"], r["filt"], r["n"], "mean4=%.5f" % r["mean_H4"], "p=%.3f q=%.3f" % (r["p"], r["q"]), r["h1_mean"], r["h2_mean"])
import json
json.dump(dict(events=ev_counts, tested=mtests, underpowered=sum(1 for r in res if r.get("status") == "underpowered"),
               survivors=[{k: r[k] for k in ("trigger", "side", "filt", "n", "mean_H4", "p", "q")} for r in surv]),
          open(os.path.join(OUT, "MATRIX_SUMMARY.json"), "w"), indent=1)
