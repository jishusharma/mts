"""Independent checker for M6 (own code; no import of study/maker_fill). Raw 1m -> signal -> maker fill -> net R."""
import json, os, random
from datetime import datetime, timezone
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
TICK = R["ticks"]; DAY = 86400000
START = {"BTCUSDT": 1583020800000, "ETHUSDT": 1614556800000, "SOLUSDT": 1633046400000}


def load(sym):
    z = np.load(r"F:\MTS\data_cache\binance_1m\%s_1m.npz" % sym)
    return {k: z[k] for k in ("t_ms", "o", "h", "l", "c")}


def day_slice(m, day0):
    a = np.searchsorted(m["t_ms"], day0); b = np.searchsorted(m["t_ms"], day0 + DAY)
    return {k: v[a:b] for k, v in m.items()}


def bars5(d, day0, lo_slot, hi_slot):
    out = []
    for s in range(lo_slot, hi_slot):
        m = (d["t_ms"] >= day0 + s * 300000) & (d["t_ms"] < day0 + (s + 1) * 300000)
        if m.any():
            out.append((s, d["o"][m][0], d["h"][m].max(), d["l"][m].min(), d["c"][m][-1]))
    return out


def signal(m, day0):
    d = day_slice(m, day0)
    eu = bars5(d, day0, 84, 162)
    if (78 - len(eu)) > 3:
        return None
    EL = min(b[3] for b in eu); EH = max(b[2] for b in eu)
    us = bars5(d, day0, 162, 240)
    sw = next((b for b in us if b[3] < EL), None)
    if sw is None:
        return None
    rc = next((b for b in us if sw[0] <= b[0] < sw[0] + 12 and b[4] > EL), None)
    if rc is None:
        return None
    S = min(b[3] for b in us if sw[0] <= b[0] <= rc[0])
    nxt = [b for b in us if b[0] == rc[0] + 1]
    if not nxt:
        return None
    e = nxt[0][1]; risk = e - S
    if risk <= 0 or risk / e < 0.0015 or not EH > e:
        return None
    return dict(EL=EL, EH=EH, S=S, j=rc[0], sig_close=day0 + (rc[0] + 1) * 300000)


def maker(m, sg, day0, tick):
    L, S, EH = sg["EL"], sg["S"], sg["EH"]
    if (L - S) / L < 0.0015:
        return ("miss_minrisk", 0.0, None)
    t0 = sg["sig_close"]; tend = day0 + 240 * 300000
    a = np.searchsorted(m["t_ms"], t0); b = np.searchsorted(m["t_ms"], min(t0 + 300000, tend))
    fill = None
    for i in range(a, b):
        if m["l"][i] <= L - tick - 1e-12:
            fill = i; break
    if fill is None:
        return ("miss_nofill", 0.0, None)
    risk = L - S; ex = None
    end_i = np.searchsorted(m["t_ms"], tend)
    for i in range(fill, end_i):
        if m["l"][i] <= S:
            ex = ("stop", S, 0.0006); break
        if m["h"][i] >= EH + tick - 1e-12:
            ex = ("target", EH, 0.0003); break
    if ex is None:
        ex = ("time", float(m["o"][end_i]), 0.0006)
    g = (ex[1] - L) / risk; net = g - (0.0003 + ex[2]) * L / risk
    return ("filled_" + ex[0], net, g)


def d0_of(date):
    return int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


def main():
    rng = random.Random(11)
    ms = {s: load(s) for s in START}
    rows = R["rows"]
    val = [r for r in rows if r["split"] == "VAL"]
    samp = rng.sample(val, 40) + rng.sample([r for r in rows if r["split"] == "DEV"], 10)
    bad = 0
    for r in samp:
        day0 = d0_of(r["date"])
        sg = signal(ms[r["sym"]], day0)
        if sg is None:
            print("SIGNAL NOT REPRODUCED", r["sym"], r["date"]); bad += 1; continue
        k, net, g = maker(ms[r["sym"]], sg, day0, TICK[r["sym"]])
        ok = (k.startswith("filled") == r["filled"]) and (not r["filled"] or abs(net - r["mk_net"]) < 1e-6) \
            and abs(sg["EL"] - r["EL"]) < 1e-9 and abs(sg["S"] - r["S"]) < 1e-9 and sg["j"] == r["j"]
        bad += (not ok)
        print("OK  " if ok else "DIFF", r["sym"], r["date"], k, round(net, 4), "study:", r["filled"], r["exit"], round(r["mk_net"], 4))
    print("sample", len(samp), "diffs", bad)
    n = f = 0; nets = []; gs = []; kinds = {}
    for sym in START:
        m = ms[sym]; d = START[sym] - START[sym] % DAY; end = m["t_ms"][-1]
        while d < end:
            dt = datetime.fromtimestamp(d / 1000, timezone.utc)
            if dt.weekday() < 5 and dt.strftime("%Y-%m-%d") >= "2024-01-01":
                sg = signal(m, d)
                if sg:
                    n += 1; k, net, g = maker(m, sg, d, TICK[sym]); kinds[k] = kinds.get(k, 0) + 1
                    if k.startswith("filled"):
                        f += 1; nets.append(net); gs.append(g)
            d += DAY
    print("INDEP VAL signals", n, "filled", f, "rate", round(f / n, 4), "net/filled", round(float(np.mean(nets)), 4),
          "gross", round(float(np.mean(gs)), 4), kinds)
    print("STUDY VAL", R["VAL"]["n_signals"], R["VAL"]["n_filled"], R["VAL"]["mean_net_R_filled"])
    # truncation test
    tr_bad = 0; cnt = 0
    for r in samp[:30]:
        day0 = d0_of(r["date"]); m = ms[r["sym"]]; sg = signal(m, day0)
        if sg is None:
            continue
        cut = np.searchsorted(m["t_ms"], sg["sig_close"])
        mt = {k: v[:cut] for k, v in m.items()}
        d = day_slice(mt, day0); us = bars5(d, day0, 162, sg["j"] + 1); eu = bars5(d, day0, 84, 162)
        EL = min(b[3] for b in eu); sw = next(b for b in us if b[3] < EL)
        rc = next(b for b in us if b[0] >= sw[0] and b[4] > EL)
        S = min(b[3] for b in us if sw[0] <= b[0] <= rc[0])
        same_sig = (rc[0] == sg["j"] and S == sg["S"] and EL == sg["EL"])
        cut2 = np.searchsorted(m["t_ms"], sg["sig_close"] + 300000)
        mt2 = {k: v[:cut2] for k, v in m.items()}
        a = np.searchsorted(mt2["t_ms"], sg["sig_close"])
        f_tr = any(mt2["l"][i] <= sg["EL"] - TICK[r["sym"]] - 1e-12 for i in range(a, len(mt2["t_ms"]))) \
            and (sg["EL"] - sg["S"]) / sg["EL"] >= 0.0015
        k_full = maker(m, sg, day0, TICK[r["sym"]])[0].startswith("filled")
        cnt += 1
        if not (same_sig and f_tr == k_full):
            tr_bad += 1; print("TRUNC DIFF", r["sym"], r["date"], same_sig, f_tr, k_full)
    print("truncation tested", cnt, "diffs", tr_bad)

    def taker(sym, lo, hi):
        m = ms[sym]; d = START[sym] - START[sym] % DAY; out = []
        while d < m["t_ms"][-1]:
            dt = datetime.fromtimestamp(d / 1000, timezone.utc); ds = dt.strftime("%Y-%m-%d")
            if dt.weekday() < 5 and lo <= ds <= hi:
                sg = signal(m, d)
                if sg:
                    dd = day_slice(m, d); us = bars5(dd, d, 162, 240)
                    e = [b for b in us if b[0] == sg["j"] + 1][0][1]
                    risk = e - sg["S"]; xit = None
                    for b in us:
                        if b[0] < sg["j"] + 1:
                            continue
                        if b[3] <= sg["S"]:
                            xit = sg["S"]; break
                        if b[2] >= sg["EH"]:
                            xit = sg["EH"]; break
                    if xit is None:
                        xit = us[-1][4]
                    out.append((xit - e) / risk - 0.0005 * (e + xit) / risk)
            d += DAY
        return out
    for name, lo, hi in (("DEV", "2020-03-01", "2024-06-30"), ("VAL", "2024-07-01", "2025-06-30"),
                         ("RECENT", "2025-07-01", "2099-01-01")):
        x = sum((taker(s, lo, hi) for s in START), [])
        print("TAKER10", name, len(x), round(float(np.mean(x)), 4))


main()
