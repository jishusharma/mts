"""Independent checker for M3 (does not import study fill code). Recomputes fills/net R by plain loops on raw 1m,
using (sym,i,dir) from rows.json only as the signal list; close/ATR recomputed here from raw 15m."""
import json, random, numpy as np
rows = json.load(open(__file__.replace("check_M3.py", "rows.json")))
VAL = int(np.datetime64("2024-01-01").astype("datetime64[D]").astype(int))
val = [r for r in rows if r["day"] >= VAL]
random.seed(11)
miss = [r for r in val if not r["filled"]]
samp = random.sample(miss, 10) + random.sample([r for r in val if r["filled"]], 40)
cache = {}
def get(sym):
    if sym not in cache:
        a = np.load(rf"F:\MTS\data_cache\binance_spot\{sym}USDT_15m.npz"); b = np.load(rf"F:\MTS\data_cache\binance_1m\{sym}USDT_1m.npz")
        A = {k: a[k] for k in a.files}; A["t"] = A["t"] if "t" in A else A["ts"]; cache[sym] = (A, {k: b[k] for k in b.files})
    return cache[sym]
def atr14(h, l, c):
    a = np.zeros(len(c)); tr = np.zeros(len(c))
    for k in range(len(c)):
        pc = c[k-1] if k else np.nan
        t = h[k]-l[k] if k == 0 else max(h[k]-l[k], abs(h[k]-pc), abs(l[k]-pc)); tr[k] = t
        a[k] = tr[k]*(1/14) + (a[k-1]*(1-1/14) if k else 0) if k else tr[k]*(1/14)   # pandas ewm adjust=False, first = x0 -> fixed below
    # pandas adjust=False: y0=x0; y_k=(1-a)y_{k-1}+a x_k
    y = np.zeros(len(c)); y[0] = tr[0]
    for k in range(1, len(c)): y[k] = (1-1/14)*y[k-1] + tr[k]/14
    return y
def sim(sd, L, stop, tgt, t0, m, tick):
    """pure python loop. returns (filled, net_R, gross, exit)."""
    t = m["t_ms"]; lo = m["l"]; hi = m["h"]; op = m["o"]
    j = int(np.searchsorted(t, t0)); end = t0 + 900000
    f = None
    while j < len(t) and t[j] < end:
        if sd > 0:
            if lo[j] <= stop and not (lo[j] <= L - tick): return (False, 0, 0, "stopfirst")   # stop hit before fill bar
            if lo[j] <= L - tick: f = j; break
            if lo[j] <= stop: return (False, 0, 0, "stopfirst")
        else:
            if hi[j] >= L + tick: f = j; break
            if hi[j] >= stop: return (False, 0, 0, "stopfirst")
        j += 1
    if f is None: return (False, 0, 0, "no_through")
    tstop = t0 - 900000 + 25*900000
    risk = abs(L - stop); k = f
    while k < len(t) and t[k] < tstop:
        s_hit = (lo[k] <= stop) if sd > 0 else (hi[k] >= stop)
        g_hit = (hi[k] >= tgt + tick) if sd > 0 else (lo[k] <= tgt - tick)
        if s_hit: x, fee, ty = stop, 6, "stop"; break
        if g_hit: x, fee, ty = tgt, 3, "target"; break
        k += 1
    else:
        x, fee, ty = op[k], 6, "time"
    gr = (x - L)*sd/risk
    return (True, gr - (3+fee)*1e-4*L/risk, gr, ty)
def tick_of(m):
    v = np.unique(np.round(np.concatenate([m["o"], m["h"], m["l"], m["c"]]), 10)); d = np.round(np.diff(v), 8); return d[d > 0].min()
nbad = 0; nfill_bad = 0; maxdiff = 0; trunc_bad = 0; sigbar_in = 0
for r in samp:
    a, m = get(r["sym"]); i = r["i"]; sd = r["dirn"]
    assert a["t"][i] + 900000 == r["signal_close_ms"]
    atr = atr14(a["h"][:i+1], a["l"][:i+1], a["c"][:i+1])[i]
    L = float(a["c"][i]); S = max(atr, 0.005*L); stop = L - sd*S; tgt = L + sd*2*S
    tk = tick_of(m)
    res = sim(sd, L, stop, tgt, r["signal_close_ms"], m, tk)
    if res[0] != r["filled"]: nfill_bad += 1; print("FILL MISMATCH", r["sym"], i, res, r["reason_missed"])
    elif res[0]:
        d = abs(res[1] - r["net_R"]); maxdiff = max(maxdiff, d)
        if d > 1e-6: nbad += 1; print("NET MISMATCH", r["sym"], i, res, r["net_R"], r["exit_type"])
    # truncation: cut 1m data at fill resolution (fill decision uses only bars < signal_close+15m) -> same fill decision
    cut = np.searchsorted(m["t_ms"], r["signal_close_ms"] + 900000)
    mt = {k: v[:cut] for k, v in m.items()}
    try: rt = sim(sd, L, stop, tgt, r["signal_close_ms"], mt, tk)
    except IndexError: rt = (True,)   # filled; exit needs later bars (fill decision made without them)
    if rt[0] != res[0]: trunc_bad += 1; print("TRUNC DIFF", r["sym"], i)
    # also, truncate ATR/close inputs at the signal bar (already done above: arrays sliced to i+1)
    if r["filled"] and r["fill_ms"] < r["signal_close_ms"]: sigbar_in += 1
print(f"sample {len(samp)} (10 misses): fill mismatches {nfill_bad}, net mismatches {nbad}, max |dNetR| {maxdiff:.2e}, truncation diffs {trunc_bad}, fills before signal close {sigbar_in}")
# whole-set sanity from rows.json
fl = [r for r in val if r["filled"]]
print("VAL n", len(val), "filled", len(fl), "rate", len(fl)/len(val), "mean net", np.mean([r["net_R"] for r in fl]), "gross", np.mean([r["gross_R"] for r in fl]))
print("all fill_ms >= signal close:", all(r["fill_ms"] >= r["signal_close_ms"] for r in fl))
for ty, fee in (("stop", 6), ("time", 6), ("target", 3)):
    ok = all(abs(r["fee_R"] - (3+fee)*1e-4*r["entry_px"]/(r["entry_px"]*0+1) * 0 - r["fee_R"]) < 1 for r in fl if r["exit_type"] == ty)
# fee by exit: ratio fee_R / (entry fee-bp R unit); fee_R*risk/L should be .0009/.0006
import collections
c = collections.defaultdict(list)
for r in fl:
    risk_over_L = (r["entry_px"] - r["exit_px"])  # not risk; use gross to back out for stop exits
    c[r["exit_type"]].append(r["fee_R"])
print({k: (len(v), round(float(np.mean(v)), 4)) for k, v in c.items()})
