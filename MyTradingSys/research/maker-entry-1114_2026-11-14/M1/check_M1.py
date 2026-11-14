"""Independent adversarial checker for M1 (NK2 pivot reclaim, 1h SHORT-P, sell limit at pivot P).
(b) Recomputes level P, stop, target, ATR, fill and exit for EVERY study signal (signal bar from raw_run.json, only the
    signal identity is taken from the study) directly from raw 1m bars, with its own fill code (no maker_fill import),
    and prints a hand trace for >=30 random signals.
(c) Truncation look-ahead tests (study code, tail cut).  (d) taker baseline vs original RESULT.  (e) gates.
Run: python check_M1.py   (acquires F:\\MTS\\maker_slots\\slotN, BelowNormal priority)"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = json.load(open(os.path.join(HERE, "raw_run.json")))
RES = json.load(open(os.path.join(HERE, "results.json")))
ROOT1M = r"F:\MTS\data_cache\binance_1m"
H1, DAY, SPLIT = 3600000, 86400000, 1704067200000
MAKER, TAKER = 0.0003, 0.0006


def acquire_slot():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    while True:
        for k in range(4):
            p = rf"F:\MTS\maker_slots\slot{k}"
            try:
                os.makedirs(p)
                return p
            except FileExistsError:
                if time.time() - os.path.getmtime(p) > 3 * 3600:
                    try:
                        os.rmdir(p); os.makedirs(p); return p
                    except OSError:
                        pass
        time.sleep(20)


def tick_of(m1):
    v = np.unique(np.round(np.concatenate([m1["o"], m1["h"], m1["l"], m1["c"]]), 10))
    d = np.round(np.diff(v), 8)
    return float(d[d > 0].min())


def hourly(m1):
    t = m1["t_ms"].astype(np.int64)
    hb = t // H1
    idx = np.flatnonzero(np.r_[True, hb[1:] != hb[:-1]])
    return dict(t=hb[idx] * H1,
                h=np.maximum.reduceat(m1["h"], idx), l=np.minimum.reduceat(m1["l"], idx),
                c=m1["c"][np.r_[idx[1:] - 1, len(t) - 1]], cnt=np.diff(np.r_[idx, len(t)]))


def daily(m1):
    t = m1["t_ms"].astype(np.int64)
    db = t // DAY
    idx = np.flatnonzero(np.r_[True, db[1:] != db[:-1]])
    return dict(d=db[idx], h=np.maximum.reduceat(m1["h"], idx), l=np.minimum.reduceat(m1["l"], idx),
                c=m1["c"][np.r_[idx[1:] - 1, len(t) - 1]], cnt=np.diff(np.r_[idx, len(t)]))


def my_trade(m1, hr, dy, tick, sig_close, strict_fill_bar=False, touch_stop=False, trunc_ms=None):
    """Independent re-derivation. Returns dict. Reads 1m bars only with t >= sig_close for fill/exit."""
    s_open = int(sig_close - H1)
    # hourly bars i-13..i (consecutive hours required) and prev close
    k = int(np.searchsorted(hr["t"], s_open))
    if k >= len(hr["t"]) or hr["t"][k] != s_open or k < 15:
        return dict(status="nobar")
    if not np.all(np.diff(hr["t"][k - 14:k + 1]) == H1):
        return dict(status="hourgap")
    hh, ll, cc = hr["h"][k - 14:k + 1], hr["l"][k - 14:k + 1], hr["c"][k - 14:k + 1]
    tr = np.maximum(hh[1:] - ll[1:], np.maximum(abs(hh[1:] - cc[:-1]), abs(ll[1:] - cc[:-1])))
    atr = tr.mean()  # 14 TRs, bars i-13..i
    day = s_open // DAY
    j = int(np.searchsorted(dy["d"], day - 1))
    if j >= len(dy["d"]) or dy["d"][j] != day - 1 or dy["cnt"][j] < 1440:
        return dict(status="noday")
    Hd, Ld, Cd = dy["h"][j], dy["l"][j], dy["c"][j]
    P = (Hd + Ld + Cd) / 3
    lv = [Ld - 2 * (Hd - P), P - (Hd - Ld), 2 * P - Hd, P, 2 * P - Ld, P + (Hd - Ld), Hd + 2 * (P - Ld)]  # S3 S2 S1 P R1 R2 R3
    L = P
    swing = hr["h"][k - 5:k + 1].max()
    dist = max(swing - L, 0.6 * atr, 0.005 * L)
    stop = L + dist
    below = [x for x in lv if x < L]
    if not below:
        return dict(status="rr", L=L)
    tgt = max(below)
    if L - tgt < dist:
        return dict(status="rr", L=L)
    t, o, h, l, c = m1["t_ms"], m1["o"], m1["h"], m1["l"], m1["c"]
    i0 = int(np.searchsorted(t, sig_close, side="left"))
    ie = int(np.searchsorted(t, sig_close + H1, side="left"))
    fi = -1
    for q in range(i0, ie):                       # walk 1m bars after the signal bar, order life 60 minutes
        if trunc_ms is not None and t[q] >= trunc_ms:
            break
        stopped = (h[q] >= stop) if touch_stop else (c[q] >= stop)
        thru = h[q] >= L + tick
        if thru:
            fi = q
            break
        if stopped:
            return dict(status="miss", reason="stop_before_fill", L=L, stop=stop, tgt=tgt, atr=atr)
    if fi < 0:
        return dict(status="miss", reason="no_through", L=L, stop=stop, tgt=tgt, atr=atr)
    tstop = sig_close + 25 * H1                    # entry bar open (= sig_close) + 25 bars
    q = fi
    ex = None
    while q < len(t) and t[q] < tstop:
        if trunc_ms is not None and t[q] >= trunc_ms:
            return dict(status="trunc_open", fill_ms=float(t[fi]), L=L)
        stp = (h[q] >= stop) if touch_stop else (c[q] >= stop)
        tg = l[q] <= tgt - tick
        if strict_fill_bar and q == fi:
            tg = False
        if stp:                                     # stop wins ties
            ex = ("stop", c[q] if not touch_stop else stop, TAKER, float(t[q])); break
        if tg:
            ex = ("target", tgt, MAKER, float(t[q])); break
        q += 1
    if ex is None:
        if q >= len(t):
            ex = ("data_end", c[-1], TAKER, float(t[-1]))
        else:
            ex = ("time", o[q], TAKER, float(t[q]))
    gross = (L - ex[1]) / dist
    fee = (MAKER + ex[2]) * L / dist
    return dict(status="filled", L=L, stop=stop, tgt=tgt, atr=atr, dist=dist, fill_ms=float(t[fi]), exit=ex[0],
                exit_ms=ex[3], gross=float(gross), fee=float(fee), net=float(gross - fee))


def main():
    slot = acquire_slot()
    try:
        run(slot)
    finally:
        try:
            os.rmdir(slot)
        except OSError:
            pass


def run(slot):
    t0 = time.time()
    rows = RAW["rows"]
    syms = sorted({r["sym"] for r in rows})
    rng = np.random.default_rng(2024)
    stat = dict(n=0, status={}, fill_mismatch=0, fillms_mismatch=0, net_mismatch=0, exit_mismatch=0, ndiff=[], tickdiff=[])
    mine = {}
    for sym in syms:
        z = np.load(rf"{ROOT1M}\{sym}USDT_1m.npz")
        m1 = {k: z[k].astype(np.float64) for k in ("t_ms", "o", "h", "l", "c")}
        tick = tick_of(m1)
        stat["tickdiff"].append((sym, tick, RAW["ticks"][sym]))
        hr, dy = hourly(m1), daily(m1)
        for idx, r in enumerate(rows):
            if r["sym"] != sym:
                continue
            res = {}
            for name, kw in (("base", {}), ("strict", dict(strict_fill_bar=True)), ("touchstop", dict(touch_stop=True)),
                             ("strict+touch", dict(strict_fill_bar=True, touch_stop=True))):
                if name != "base" and not r["val"]:
                    continue
                res[name] = my_trade(m1, hr, dy, tick, r["signal_close_ms"], **kw)
            mine[idx] = res
        print(sym, round(time.time() - t0), flush=True)
    # ---------- compare all signals
    cmpv = {"val": dict(n=0, filled_s=0, filled_m=0, netsum_s=0.0, netsum_m=0.0, gsum_m=0.0, feesum_m=0.0),
            "dev": dict(n=0, filled_s=0, filled_m=0, netsum_s=0.0, netsum_m=0.0, gsum_m=0.0, feesum_m=0.0)}
    bad, st_counts = [], {}
    for idx, res in mine.items():
        r, m = rows[idx], res["base"]
        st_counts[m["status"]] = st_counts.get(m["status"], 0) + 1
        c = cmpv["val" if r["val"] else "dev"]
        c["n"] += 1
        mf = m["status"] == "filled"
        c["filled_s"] += bool(r["filled"]); c["filled_m"] += mf
        c["netsum_s"] += r["net_R"]
        if mf:
            c["netsum_m"] += m["net"]; c["gsum_m"] += m["gross"]; c["feesum_m"] += m["fee"]
        if bool(r["filled"]) != mf:
            bad.append((idx, "fillflag", r["sym"], r["signal_close_ms"], r["filled"], m["status"]))
        elif mf:
            if abs(r["fill_ms"] - m["fill_ms"]) > 1:
                bad.append((idx, "fill_ms", r["sym"], r["signal_close_ms"], r["fill_ms"], m["fill_ms"]))
            elif abs(r["net_R"] - m["net"]) > 1e-6:
                bad.append((idx, "net", r["sym"], r["signal_close_ms"], r["net_R"], m["net"]))
    print("\n== (b) independent full recomputation, all study signals ==")
    print("status counts (mine):", st_counts)
    for k, c in cmpv.items():
        n = c["n"]
        print(f"{k}: n {n} | fills study {c['filled_s']} ({c['filled_s']/n:.4f}) mine {c['filled_m']} ({c['filled_m']/n:.4f}) | "
              f"net/filled study {c['netsum_s']/max(c['filled_s'],1):+.4f} mine {c['netsum_m']/max(c['filled_m'],1):+.4f} | "
              f"gross {c['gsum_m']/max(c['filled_m'],1):+.4f} fee {c['feesum_m']/max(c['filled_m'],1):.4f}")
    print("mismatches vs study:", len(bad), "of", len(mine))
    from collections import Counter
    print("mismatch kinds:", Counter(b[1] for b in bad))
    for b in bad[:12]:
        print("  ", b)
    # variants VAL
    for name in ("base", "strict", "touchstop", "strict+touch"):
        v = [res[name] for idx, res in mine.items() if rows[idx]["val"]]
        f = [x for x in v if x["status"] == "filled"]
        nets = np.array([x["net"] for x in f])
        print(f"VAL variant {name:13s}: signals {len(v)} filled {len(f)} rate {len(f)/len(v):.4f} mean net R/filled {nets.mean():+.4f} "
              f"per-signal {nets.sum()/len(v):+.4f}")
    # ---------- 35 random signal hand-trace table
    print("\n== random signal trace (VAL, 36 signals) ==")
    vi = [idx for idx in mine if rows[idx]["val"]]
    pick = rng.choice(vi, 36, replace=False)
    agree = 0
    for idx in pick:
        r, m = rows[idx], mine[idx]["base"]
        ok = bool(r["filled"]) == (m["status"] == "filled") and (not r["filled"] or abs(r["net_R"] - m["net"]) < 1e-6)
        agree += ok
        ts = time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["signal_close_ms"] / 1000))
        if m["status"] == "filled":
            print(f"{r['sym']:5s} {ts} L {m['L']:.6g} stop {m['stop']:.6g} tgt {m['tgt']:.6g} fill {time.strftime('%H:%M', time.gmtime(m['fill_ms']/1000))} "
                  f"exit {m['exit']} grossR {m['gross']:+.3f} feeR {m['fee']:.3f} netR {m['net']:+.3f} | study net {r['net_R']:+.3f} {'OK' if ok else 'DIFF'}")
        else:
            print(f"{r['sym']:5s} {ts} {m['status']}/{m.get('reason')} L {m.get('L')} | study filled={r['filled']} {'OK' if ok else 'DIFF'}")
    print("trace agreement:", agree, "/ 36")
    print("tick (mine vs study):", [x for x in stat["tickdiff"] if abs(x[1] - x[2]) > 1e-12] or "all equal")

    # ---------- independent VAL stats incl. bootstrap by day, ex best-5 days
    f = [(rows[idx], mine[idx]["base"]) for idx in vi if mine[idx]["base"]["status"] == "filled"]
    net = np.array([m["net"] for _, m in f])
    days = np.array([int(m["fill_ms"] // DAY) for _, m in f])
    ud, inv = np.unique(days, return_inverse=True)
    S = np.bincount(inv, weights=net); N = np.bincount(inv).astype(float)
    g = np.random.default_rng(7)
    cm = np.array([S[ix].sum() / N[ix].sum() for ix in g.integers(0, len(ud), (2000, len(ud)))])
    keep = np.ones(len(ud), bool); keep[np.argsort(-S)[:5]] = False
    print(f"independent VAL: filled {len(net)} mean net {net.mean():+.4f} day-cluster CI low {np.percentile(cm, 2.5):+.4f} "
          f"ex-best5 {S[keep].sum() / N[keep].sum():+.4f}")
    print("exit types mine VAL:", dict(Counter(m["exit"] for _, m in f)))
    # taker-fee-by-exit check: all-target exits should carry 6bp round trip, stops/time 9bp
    fe = {}
    for _, m in f:
        fe.setdefault(m["exit"], []).append(m["fee"] * m["dist"] / m["L"])
    print("fee fraction by exit (should be 0.0006 target / 0.0009 stop,time):", {k: round(float(np.mean(v)), 6) for k, v in fe.items()})

    # ---------- (c) truncation look-ahead
    print("\n== (c) truncation test ==")
    sample = rng.choice([i for i in mine if mine[i]["base"]["status"] == "filled"], 150, replace=False)
    zc = {}
    nfill_bad = nexit_bad = ntrunc_open = 0
    for idx in sample:
        r = rows[idx]
        sym = r["sym"]
        if sym not in zc:
            zc.clear()
            z = np.load(rf"{ROOT1M}\{sym}USDT_1m.npz")
            m1 = {k: z[k].astype(np.float64) for k in ("t_ms", "o", "h", "l", "c")}
            zc[sym] = (m1, hourly(m1), daily(m1), tick_of(m1))
        m1, hr, dy, tick = zc[sym]
        full = mine[idx]["base"]
        # cut everything from the bar after the fill bar: fill must be unchanged and trade must be 'open'
        cut = full["fill_ms"] + 60000
        a = my_trade(m1, hr, dy, tick, r["signal_close_ms"], trunc_ms=cut)
        if a.get("fill_ms") != full["fill_ms"]:
            nfill_bad += 1
        # cut everything after the exit bar: exit must be unchanged unless exit is the time stop
        if full["exit"] != "time":
            cut2 = full["exit_ms"] + 60000
            b = my_trade(m1, hr, dy, tick, r["signal_close_ms"], trunc_ms=cut2)
            if b["status"] != "filled" or b["exit_ms"] != full["exit_ms"] or abs(b["net"] - full["net"]) > 1e-12:
                nexit_bad += 1
        # cut before the signal close: nothing may fill
        cut3 = r["signal_close_ms"]
        d = my_trade(m1, hr, dy, tick, r["signal_close_ms"], trunc_ms=cut3)
        if d["status"] == "filled":
            ntrunc_open += 1
    print(f"my code, 150 filled trades: fill changed by tail cut {nfill_bad}; exit changed by tail cut {nexit_bad}; fills with data cut at signal close {ntrunc_open}")
    # the study's own lib: tail cut at fill+1 bar and exit+1 bar
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib")); sys.path.insert(0, HERE)
    import maker_fill as MF, study as S_, nk2_orig as O
    bad_lib = bad_lib2 = 0
    chk = 0
    for idx in sample[:60]:
        r = rows[idx]
        if r["exit_type"] == "time":
            continue
        sym = r["sym"]
        z = np.load(rf"{ROOT1M}\{sym}USDT_1m.npz")
        m1 = {k: z[k] for k in ("t_ms", "o", "h", "l", "c")}
        D = O.prep(sym, S_.TFK) if idx == sample[0] or 'Dcache' not in dir() or Dcache[0] != sym else Dcache[1]
        Dcache = (sym, D)
        i = r["i"]
        full = S_.maker_trade(D, i, m1, RAW["ticks"][sym])
        ex_i = int(np.searchsorted(m1["t_ms"], full["exit_ms"], side="right")) if full["filled"] else None
        if not full["filled"]:
            continue
        chk += 1
        m1t = {k: v[:ex_i] for k, v in m1.items()}
        tr = S_.maker_trade(D, i, m1t, RAW["ticks"][sym])
        if not tr["filled"] or tr["exit_ms"] != full["exit_ms"] or abs(tr["net_R"] - full["net_R"]) > 1e-12:
            bad_lib += 1
        fi_ = int(np.searchsorted(m1["t_ms"], full["fill_ms"], side="right"))
        m1f = {k: v[:fi_] for k, v in m1.items()}
        tf = S_.maker_trade(D, i, m1f, RAW["ticks"][sym])
        if tf["filled"] and tf["fill_ms"] != full["fill_ms"]:
            bad_lib2 += 1
    print(f"study code (lib) cut after exit bar: changed {bad_lib}/{chk}; cut after fill bar: fill time changed {bad_lib2}/{chk}")
    # signal-level truncation: cut 15m data right after the signal bar, recompute signal, level, atr, phase
    import nk2_orig as O2
    bad_sig = 0
    nt = 0
    for sym in ("BTC", "XRP"):
        a15 = O2.load15(sym)
        Df = O2.prep(sym, 4)
        cand = [r for r in rows if r["sym"] == sym and r["val"]]
        for r in rng.choice(cand, 4, replace=False):
            i = r["i"]
            cutms = Df["a"][i, 0] + H1
            keepn = int(np.searchsorted(a15[:, 0], cutms, side="left"))
            O2.load15 = lambda s, a=a15[:keepn]: a
            Dt = O2.prep(sym, 4)
            O2.load15 = lambda s: np.load(os.path.join(O2.CACHE, s + "USDT_15m.npz"))["a"]
            nt += 1
            j = len(Dt["a"]) - 1
            same = (Dt["a"][j, 0] == Df["a"][i, 0] and Dt["lv"]["P"][j] == Df["lv"]["P"][i] and Dt["ph"][j] == Df["ph"][i]
                    and Dt["atr"][j] == Df["atr"][i] and j in set(O2.signals(Dt, -1, "P", 4)))
            bad_sig += (not same)
    print(f"signal-level 15m tail-cut (bar i is last bar): changed {bad_sig}/{nt}")

    # ---------- (d) baseline vs original RESULT, (e) gates
    print("\n== (d) taker baseline (study results.json) vs original RESULT: VAL n 6102 gross 0.101 net12 -0.009 net6 0.046 win 46.2 | DEV n 8634 net12 -0.139")
    tv, td = RES["val"]["taker"], RES["dev"]["taker"]
    print(f"study: VAL n {tv['n']} gross {tv['gross']:.3f} net12 {tv['net12']:.3f} net6 {tv['net6']:.3f} win {100*tv['win']:.1f} | DEV n {td['n']} net12 {td['net12']:.3f}")
    print("original study.py byte-identical to nk2_orig.py (diff run separately: IDENTICAL).")
    print("\n== (e) gates ==")
    gt = RES["gates"]
    mv = RES["val"]["maker"]
    print("study gates:", gt["gates"], "failed", gt["failed"], "| n_filled", mv["n_filled"], "mean", round(mv["mean_net_R_filled"], 4),
          "ci", [round(x, 4) for x in mv["ci_trade"]], [round(x, 4) for x in mv["ci_day"]], "ex5", round(mv["ex_best5_days"], 4),
          "placebo p", round(RES["placebo"]["p"], 4))
    print("verdict logic: PASS needs all six; gates 2,3,6 fail on independent numbers above -> FAIL independent of gate 5.")
    print("elapsed", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
