"""check_M2.py - independent adversarial check of M2. Own fill/exit/fee code (does NOT import maker_fill / study).
Signals only come from orig_lib (byte-identical copy of the original nk3 lib.py, verified by diff).
Run: python -I-less (needs path to orig_lib):  python check_M2.py [coins...]"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orig_lib as lib

CACHE = r"F:\MTS\data_cache\binance_spot"
M1 = r"F:\MTS\data_cache\binance_1m"
COINS = sys.argv[1:] or "BTC ETH BNB XRP ADA SOL DOGE LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
SPLIT = int(np.datetime64("2024-01-01").astype("datetime64[ms]").astype(np.int64))
HOUR = 3600000


def load15(coin):
    z = np.load(os.path.join(CACHE, f"{coin}USDT_15m.npz"))
    return [z["ts" if "ts" in z.files else "t"]] + [z[k] for k in "o h l c v".split()]


def own_tick(l):
    v = np.unique(np.round(l, 10))
    d = np.diff(v)
    d = d[d > 1e-12]
    return float(np.round(d.min(), 8))


def my_trade(sd, L, dist, t0, m, tick, touch_fills=False):
    """independent per-signal maker trade. sd=+1 long/-1 short. t0 = signal bar close (ms).
    returns None if missed else (gross_R, net_R, exit_type, fill_idx, exit_idx)."""
    t, o, h, l, c = m
    stop = L - sd * dist
    tgt = L + sd * 2.0 * dist
    a = np.searchsorted(t, t0)               # first 1m bar with open >= t0 (strictly after the signal bar)
    if a >= len(t) or t[a] != t0:
        return "nodata"
    fi = None
    for k in range(a, a + 60):               # order life: 60 one-minute bars
        if k >= len(t):
            return "nodata"
        thru = (l[k] <= L - tick) if sd > 0 else (h[k] >= L + tick)
        if touch_fills:
            thru = (l[k] <= L) if sd > 0 else (h[k] >= L)
        stp = (l[k] <= stop) if sd > 0 else (h[k] >= stop)
        if thru:
            fi = k
            break
        if stp:
            return None                       # cancelled
    if fi is None:
        return None
    t_time = t0 + 24 * HOUR + HOUR            # open of bar e+25 = close of bar e+24
    ts_idx = np.searchsorted(t, t_time)
    k = fi
    while True:
        if k >= ts_idx:
            if k >= len(t):
                px, typ = c[-1], "data_end"
            else:
                px, typ = o[k], "time"
            fee = 0.0006 + 0.0003
            break
        sh = (l[k] <= stop) if sd > 0 else (h[k] >= stop)
        th = (h[k] >= tgt + tick) if sd > 0 else (l[k] <= tgt - tick)
        if sh:                                # stop wins ties, also on the fill bar
            px, typ, fee = stop, "stop", 0.0006 + 0.0003
            break
        if th:
            px, typ, fee = tgt, "target", 0.0003 + 0.0003
            break
        k += 1
    gross = (px - L) * sd / dist
    net = gross - fee * L / dist
    return gross, net, typ, fi, k


def main():
    rows = []
    truncation_fail = 0
    trunc_checked = 0
    feat_checked = 0
    feat_fail = 0
    touch_rows = []
    fillbar_target = 0
    for coin in COINS:
        t, o, h, l, c, v = load15(coin)
        days, lab = lib.daily_phase_table(t, o, h, l, c, v)
        t, o, h, l, c, v = lib.resample(t, o, h, l, c, v, 4)
        ph = lib.phase_for_bars(t, days, lab)
        F = lib.features(t, o, h, l, c)
        S = [s for s in lib.signals(t, o, h, l, c, F, ph) if s["type"] == "B"]
        z = np.load(os.path.join(M1, f"{coin}USDT_1m.npz"))
        m = tuple(z[k].astype(float) for k in ("t_ms", "o", "h", "l", "c"))
        tick = own_tick(m[3])
        # --- taker baseline with the original sim, cooldown as original
        idx = np.array([s["e"] for s in S]); px = np.array([s["px"] for s in S]); d = np.array([s["dir"] for s in S])
        if not len(S):
            continue
        dist_t = lib.stop_dist(np.array([s["nat"] for s in S]), np.array([s["atr"] for s in S]), px)
        g, ex = lib.sim(o, h, l, c, idx, px, d, dist_t, "X1", np.zeros(len(S), bool))
        tk = {int(i): (float(a), int(b), float(p), float(q)) for i, a, b, p, q in zip(idx, g, ex, px, dist_t)}
        last = -1
        for s in sorted(S, key=lambda s: s["e"]):
            if not (s["fit"] == 1 and s["e"] > last):
                continue
            last = tk[s["e"]][1]
            gt, _, pxt, dt = tk[s["e"]]
            split = "VAL" if t[s["e"]] >= SPLIT else "DEV"
            sd = s["dir"]
            i = s["i"]
            L = float(F["H"][i] if sd == -1 else F["L"][i])
            nat = (h[i] - L) if sd == -1 else (L - l[i])
            dist = max(nat, 0.6 * s["atr"], 0.005 * L)
            t0 = float(t[s["e"]] + HOUR)
            r = my_trade(sd, L, dist, t0, m, tick)
            rt = my_trade(sd, L, dist, t0, m, tick, touch_fills=True)
            rows.append(dict(coin=coin, split=split, e=s["e"], t0=t0, tk_gross=gt, tk_net=gt - 0.0012 * pxt / dt,
                             r=r, rt=rt, L=L, sd=sd, dist=dist))
            # --- truncation look-ahead test (1m data cut right after the order life = 60 min after signal close)
            if split == "VAL" and (len(rows) % 3 == 0):
                cut = np.searchsorted(m[0], t0 + HOUR)
                mc = tuple(a_[:cut] for a_ in m)
                rc = my_trade(sd, L, dist, t0, mc, tick)
                full_fill = r is not None and r != "nodata"
                trunc_fill = rc is not None and rc != "nodata"
                trunc_checked += 1
                if full_fill != trunc_fill or (full_fill and r[3] != rc[3]):
                    truncation_fail += 1
            # --- feature truncation test: recompute features/phase on 15m data cut right after the signal bar
            if split == "VAL" and (len(rows) % 11 == 0):
                e = s["e"]
                full15 = load15(coin)
                n15 = int(np.searchsorted(full15[0], t[e] + HOUR))  # 15m bars up to the close of 1h bar e only
                tt, oo, hh, ll, cc, vv = [a_[:n15] for a_ in full15]
                dd, lb = lib.daily_phase_table(tt, oo, hh, ll, cc, vv)
                tt, oo, hh, ll, cc, vv = lib.resample(tt, oo, hh, ll, cc, vv, 4)
                # resample may drop alignment; locate bar e by time
                je = int(np.searchsorted(tt, t[e]))
                ph2 = lib.phase_for_bars(tt, dd, lb)
                F2 = lib.features(tt, oo, hh, ll, cc)
                feat_checked += 1
                same = (je < len(tt) and tt[je] == t[e] and ph2[je - 1] == ph[i]
                        and abs(F2["H"][je - 1] - F["H"][i]) < 1e-9 and abs(F2["L"][je - 1] - F["L"][i]) < 1e-9
                        and abs(F2["atr_prev"][je - 1] - F["atr_prev"][i]) < 1e-9 * max(1, abs(F["atr_prev"][i])))
                if not same:
                    feat_fail += 1
        print(coin, "done", flush=True)
    out = {}
    for sp in ("DEV", "VAL"):
        R = [x for x in rows if x["split"] == sp]
        n = len(R)
        fl = [x for x in R if isinstance(x["r"], tuple)]
        nodata = sum(1 for x in R if x["r"] == "nodata")
        net = np.array([x["r"][1] for x in fl]); gr = np.array([x["r"][0] for x in fl])
        out[sp] = dict(n=n, filled=len(fl), nodata=nodata, fill_rate=len(fl) / n, net_filled=float(net.mean()),
                       gross_filled=float(gr.mean()), per_signal=float(net.sum() / n),
                       taker_net_all=float(np.mean([x["tk_net"] for x in R])),
                       taker_gross_all=float(np.mean([x["tk_gross"] for x in R])),
                       adverse=float(np.mean([x["tk_gross"] for x in R if isinstance(x["r"], tuple)]) - np.mean([x["tk_gross"] for x in R])),
                       exit_types={k: sum(1 for x in fl if x["r"][2] == k) for k in ("stop", "target", "time", "data_end")},
                       fill_bar_target=sum(1 for x in fl if x["r"][2] == "target" and x["r"][3] == x["r"][4]))
        ft = [x for x in R if isinstance(x["rt"], tuple)]
        out[sp]["touch_variant"] = dict(fill_rate=len(ft) / n, net_filled=float(np.mean([x["rt"][1] for x in ft])))
        # stricter variant: fill bar cannot credit the target (target needs a later bar)
    # random sample of 30 signals dump for hand audit
    rng = np.random.default_rng(5)
    VR = [x for x in rows if x["split"] == "VAL"]
    samp = [VR[i] for i in rng.choice(len(VR), 30, replace=False)]
    out["sample30"] = [dict(coin=x["coin"], t0=int(x["t0"]), sd=x["sd"], L=x["L"], dist=x["dist"],
                            res=(None if x["r"] is None else (x["r"] if isinstance(x["r"], str) else
                                 [round(x["r"][0], 4), round(x["r"][1], 4), x["r"][2]]))) for x in samp]
    out["truncation"] = dict(fill_checked=trunc_checked, fill_fail=truncation_fail, feature_checked=feat_checked, feature_fail=feat_fail)
    json.dump(out, open(os.environ.get("CHK_OUT", os.path.join(HERE, "check_M2_out.json")), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "sample30"}, indent=1, default=float))


if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass
    main()
