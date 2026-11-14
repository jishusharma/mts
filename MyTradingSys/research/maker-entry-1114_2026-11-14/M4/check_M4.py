"""Adversarial checker for M4. Signal list (anchor, side, a1) comes from the original nk5_orig rule code (signal rule
is SOURCED, not the object of this check); ALL fill / stop / fee / net-R logic here is independent pure python on raw 1m."""
import os, sys, json, ctypes, time, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import nk5_orig as O
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception:
    pass
os.makedirs(r"F:\MTS\maker_slots", exist_ok=True)
slot = None
while slot is None:
    for i in range(4):
        try:
            os.mkdir(rf"F:\MTS\maker_slots\slot{i}"); slot = i; break
        except OSError:
            pass
    if slot is None:
        time.sleep(20)
print("slot", slot, flush=True)
MAKER, TAKER = 3e-4, 6e-4


def my_tick(m):
    v = np.unique(np.concatenate([m["o"], m["h"], m["l"], m["c"]]).round(10)); d = np.diff(v); d = d[d > 1e-9]
    return round(float(d.min()), 8)


def my_sim(sd, L, S, T_ms, E_ms, t, o, h, l, tick, life_ms=15 * 60000):
    """Own implementation. Only bars t>=T_ms (open of first bar after the signal bar)."""
    stop = L - sd * S
    i = int(np.searchsorted(t, T_ms)); end = T_ms + life_ms
    fill = None
    while i < len(t) and t[i] < end:
        stopped = (l[i] <= stop) if sd > 0 else (h[i] >= stop)
        thru = (l[i] <= L - tick) if sd > 0 else (h[i] >= L + tick)
        if thru:
            fill = i; break
        if stopped:
            return dict(filled=False, why="stop_first")
        i += 1
    if fill is None:
        return dict(filled=False, why="nothrough")
    j = fill
    while True:
        if j >= len(t):
            return dict(filled=True, decided=True, exit_beyond_data=True, net=np.nan, gross=np.nan, et="dataend")
        if t[j] >= E_ms:
            px, fee, et = o[j], TAKER, "time"; break
        if (l[j] <= stop) if sd > 0 else (h[j] >= stop):
            px, fee, et = stop, TAKER, "stop"; break
        j += 1
    gross = (px - L) * sd
    return dict(filled=True, net=(gross - (MAKER + fee) * L) / S, gross=gross / S, et=et)


rows = []
for s in O.SYMS:
    p = rf"F:\MTS\data_cache\binance_1m\{s}USDT_1m.npz"
    if not os.path.exists(p):
        continue
    z = np.load(p); t, o, h, l, c = (z[k] for k in ("t_ms", "o", "h", "l", "c"))
    tick = my_tick(dict(o=o, h=h, l=l, c=c))
    df5 = O.prep(O.load5(s)); C = O.coin_candidates(s, df5=df5); C = C[C.row == "NY-asia"]
    sg = O.signals(df5)
    for r in C.itertuples(index=False):
        sd = 1 if (r.sigL and r.phase in (1, 0)) else (-1 if (r.sigS and r.phase in (-1, 0)) else 0)
        if sd == 0:
            continue
        T = r.T; T_ms = float(T.value // 10**6)
        a1 = sg["atr1"].get(T.floor("1h") - pd.Timedelta(hours=1), np.nan)
        k = int(np.searchsorted(t, T_ms - 60000))
        if np.isnan(a1) or k >= len(t) or t[k] != T_ms - 60000:
            continue
        L = float(c[k]); S = max(0.005 * L, 0.6 * float(a1))
        E_ms = float((T.normalize() + pd.Timedelta(days=1, hours=8)).value // 10**6)
        if E_ms > t[-1]:
            continue
        x = my_sim(sd, L, S, T_ms, E_ms, t, o, h, l, tick)
        x.update(sym=s, T=T, sd=sd, L=L, S=S, a1=float(a1), E_ms=E_ms, tick=tick, gl=r.gl, gs=r.gs, S0=r.S)
        rows.append(x)
    print(s, len(rows), flush=True)
D = pd.DataFrame(rows)
V = D[D["T"] >= O.SPLIT]; Dv = D[D["T"] < O.SPLIT]


def summ(d):
    f = d[d.filled]
    return dict(n=len(d), filled=len(f), fill_rate=len(f) / len(d), net=float(f.net.mean()), gross=float(f.gross.mean()))


out = dict(VAL=summ(V), DEV=summ(Dv))
tk = np.where(V.sd > 0, V.gl, V.gs); out["taker_net_VAL"] = float(((tk - 12e-4) / V.S0).mean()); out["taker_n"] = len(V)
out["miss_reasons_VAL"] = V[~V.filled].why.value_counts().to_dict()
f = V[V.filled]; dd = f["T"].dt.normalize()
fd = f.groupby(dd).net.sum().sort_values(ascending=False)
out["ex_best5_mean_net"] = float(f[~dd.isin(fd.index[:5])].net.mean())
out["exit_types_VAL"] = f.et.value_counts().to_dict()
# (b) sample of 40 printed
rs = np.random.default_rng(11); samp = V.iloc[rs.permutation(len(V))[:40]]
out["sample_40"] = [dict(sym=r.sym, T=str(r.T), sd=int(r.sd), L=r.L, filled=bool(r.filled),
                         net=(round(r.net, 4) if r.filled else None), why=(None if r.filled else r.why)) for r in samp.itertuples()]
# (c) truncation: signals/phase/atr recomputed from 5m cut before T; fill decision from 1m cut at order-life end
bad_sig = bad_fill = n = 0
for s in sorted(set(samp.sym)):
    z = np.load(rf"F:\MTS\data_cache\binance_1m\{s}USDT_1m.npz"); t, o, h, l, c = (z[k] for k in ("t_ms", "o", "h", "l", "c"))
    df5 = O.prep(O.load5(s)); sgF = O.signals(df5)
    for r in samp[samp.sym == s].itertuples():
        T = r.T; T_ms = float(T.value // 10**6)
        sg2 = O.signals(O.prep(df5[df5.index < T]))
        a = O.signal_at(sg2, T)[:2]; b = O.signal_at(sgF, T)[:2]
        p2 = O.phase_for(sg2, T.normalize()); pF = O.phase_for(sgF, T.normalize())
        a2 = sg2["atr1"].get(T.floor("1h") - pd.Timedelta(hours=1), np.nan); aF = sgF["atr1"].get(T.floor("1h") - pd.Timedelta(hours=1), np.nan)
        n += 1
        if not (a == b and (p2 == pF or (np.isnan(p2) and np.isnan(pF))) and np.isclose(a2, aF)):
            bad_sig += 1
        cut = int(np.searchsorted(t, T_ms + 15 * 60000))
        x1 = my_sim(r.sd, r.L, r.S, T_ms, T_ms, t[:cut], o[:cut], h[:cut], l[:cut], r.tick)   # fill decision only
        if bool(x1["filled"]) != bool(r.filled):
            bad_fill += 1
out["truncation"] = dict(tests=n, signal_mismatch=bad_sig, fill_mismatch=bad_fill)
json.dump(out, open(os.path.join(HERE, "check_M4_out.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "sample_40"}, indent=1, default=str))
os.rmdir(rf"F:\MTS\maker_slots\slot{slot}")
