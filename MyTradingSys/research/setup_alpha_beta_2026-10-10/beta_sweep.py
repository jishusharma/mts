import sys, os, glob, csv, json
sys.dont_write_bytecode = True

ROOT = r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
K15 = os.path.join(ROOT, "Dumps", "backtest", "raw_15m", "klines")
K5  = os.path.join(ROOT, "Dumps", "backtest", "raw_5m", "klines")

def load15():
    bars = []
    for f in sorted(glob.glob(os.path.join(K15, "BTCUSDT-15m-*.csv"))):
        with open(f) as fh:
            for r in csv.reader(fh):
                if not r or r[0] == "open_time": continue
                v = float(r[5]); tb = float(r[9])
                bars.append({"t": int(r[0])//1000, "o": float(r[1]), "h": float(r[2]),
                             "l": float(r[3]), "c": float(r[4]), "v": v, "tb": tb})
    bars.sort(key=lambda b: b["t"])
    cvd = 0.0
    for b in bars:
        cvd += (b["tb"]*2 - b["v"])
        b["cvd"] = cvd
    return bars

def load5():
    out = {}
    for f in sorted(glob.glob(os.path.join(K5, "BTCUSDT-5m-*.csv"))):
        with open(f) as fh:
            for r in csv.reader(fh):
                if not r or r[0] == "open_time": continue
                out[int(r[0])//1000] = {"o": float(r[1]), "h": float(r[2]),
                                        "l": float(r[3]), "c": float(r[4])}
    return out

def day_key(t):
    return t // 86400

def mark_levels(bars):
    days = {}
    for i, b in enumerate(bars):
        days.setdefault(day_key(b["t"]), []).append(i)
    levels = {}
    for d, idxs in days.items():
        if d - 1 not in days: continue
        prev = days[d-1]
        hi = max(bars[i]["h"] for i in prev)
        lo = min(bars[i]["l"] for i in prev)
        levels[d] = {"pdh": hi, "pdl": lo}
        bucket = {}
        for i in prev:
            key = round(bars[i]["c"] / (hi*0.0005)) if hi else 0
            bucket.setdefault(key, []).append(bars[i]["c"])
        levels[d]["eq"] = [c for g in bucket.values() if len(g) >= 2 for c in g]
    return levels

def day_key(t):
    return t // 86400

def mark_levels(bars):
    days = {}
    for i, b in enumerate(bars):
        days.setdefault(day_key(b["t"]), []).append(i)
    levels = {}
    for d, idxs in days.items():
        if d - 1 not in days: continue
        prev = days[d-1]
        hi = max(bars[i]["h"] for i in prev)
        lo = min(bars[i]["l"] for i in prev)
        levels[d] = {"pdh": hi, "pdl": lo}
        bucket = {}
        for i in prev:
            key = round(bars[i]["c"] / (hi*0.0005)) if hi else 0
            bucket.setdefault(key, []).append(bars[i]["c"])
        levels[d]["eq"] = [c for g in bucket.values() if len(g) >= 2 for c in g]
    return levels

def find_sweeps(bars, levels, eq_tol=0.0005):
    evs = []
    for i in range(2, len(bars)):
        d = day_key(bars[i]["t"])
        if d not in levels: continue
        lv = levels[d]; b = bars[i]
        if b["h"] > lv["pdh"] and b["c"] < lv["pdh"]:
            evs.append({"i": i, "side": "short", "level": lv["pdh"], "kind": "pdh", "ext": b["h"]})
        if b["l"] < lv["pdl"] and b["c"] > lv["pdl"]:
            evs.append({"i": i, "side": "long", "level": lv["pdl"], "kind": "pdl", "ext": b["l"]})
        for c0 in lv.get("eq", []):
            if abs(c0-lv["pdh"]) <= lv["pdh"]*eq_tol or abs(c0-lv["pdl"]) <= lv["pdl"]*eq_tol:
                continue
            if b["h"] > c0 and b["c"] < c0:
                evs.append({"i": i, "side": "short", "level": c0, "kind": "eqh", "ext": b["h"]})
            if b["l"] < c0 and b["c"] > c0:
                evs.append({"i": i, "side": "long", "level": c0, "kind": "eql", "ext": b["l"]})
    return evs

def simulate(bars, m5, evs, use_cvd, max_hold=6):
    trades = []
    for e in evs:
        i = e["i"]; side = e["side"]; ext = e["ext"]
        if use_cvd and not cvd_diverges(bars, i, side): continue
        t0 = bars[i]["t"] + 900
        entry = None
        for k in range(t0, t0+1800, 300):
            b = m5.get(k)
            if not b: continue
            if side == "long" and b["c"] > bars[i]["h"]: entry = b["c"]; break
            if side == "short" and b["c"] < bars[i]["l"]: entry = b["c"]; break
        if entry is None: continue
        stop = ext - (entry-ext)*0.0 if side=="long" else ext
        stop = ext - abs(entry-ext)*0.1 if side=="long" else ext + abs(entry-ext)*0.1
        r = abs(entry-stop); target = entry + 1.5*r if side=="long" else entry - 1.5*r
        res = None
        for k in range(t0+1800, t0+1800+max_hold*1800, 300):
            b = m5.get(k)
            if not b: continue
            if side=="long":
                if b["l"] <= stop: res = -1.0; break
                if b["h"] >= target: res = 1.5; break
            else:
                if b["h"] >= stop: res = -1.0; break
                if b["l"] <= target: res = 1.5; break
        if res is None: res = 0.0
        trades.append(res - 0.001)
    return trades

def stats(tr):
    if not tr: return {"n": 0, "wr": 0.0, "avgR": 0.0, "netR": 0.0}
    w = sum(1 for t in tr if t > 0)
    return {"n": len(tr), "wr": w/len(tr), "avgR": sum(tr)/len(tr), "netR": sum(tr)}

def main():
    bars = load15(); m5 = load5(); levels = mark_levels(bars)
    evs = find_sweeps(bars, levels)
    evs_sess = [e for e in evs if in_session(bars[e["i"]]["t"])]
    out = {}
    out["all"] = stats(simulate(bars, m5, evs, False))
    out["all_cvd"] = stats(simulate(bars, m5, evs, True))
    out["sess"] = stats(simulate(bars, m5, evs_sess, False))
    out["sess_cvd"] = stats(simulate(bars, m5, evs_sess, True))
    print(json.dumps(out, indent=2))
    dst = os.path.join(ROOT, "MyTradingSys", "research", "setup_alpha_beta_2026-10-10", "BETA_RESULTS.md")
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Beta results (NO-SOURCE)\n\n")
        f.write("Liquidity sweep + CVD absorption event study, Binance BTCUSDT perp, 15m levels / 5m entry.\n")
        f.write("CVD = kline taker-buy volume proxy (T5_CVD_DEFINITION_2026-10-01.md). Fee 0.05%/side.\n")
        f.write("NO-SOURCE: setup numbers from a chatbot handoff, not a trader transcript.\n\n")
        f.write("| scope | CVD filter | n | win rate | avg R | net R |\n|---|---|---|---|---|---|\n")
        for k, name, cvd in (("all","all sessions",False),("all_cvd","all sessions",True),
                             ("sess","London/NY only",False),("sess_cvd","London/NY only",True)):
            s = out[k]
            f.write("| %s | %s | %d | %.1f%% | %.3f | %.2f |\n" % (name, "yes" if cvd else "no", s["n"], s["wr"]*100, s["avgR"], s["netR"]))
    return 0

def cvd_diverges(bars, i, side, look=8):
    j = max(0, i-look)
    seg = bars[j:i+1]
    if side == "short":
        return bars[i]["cvd"] < max(b["cvd"] for b in seg)
    return bars[i]["cvd"] > min(b["cvd"] for b in seg)

def in_session(t):
    h = (t % 86400) // 3600
    return 7 <= h < 21

if __name__ == "__main__":
    sys.exit(main())

def mark_levels(bars, tol=0.0005):
    days = {}
    for i, b in enumerate(bars):
        days.setdefault(day_key(b["t"]), []).append(i)
    levels = {}
    for d, idxs in days.items():
        if d-1 not in days: continue
        prev = days[d-1]
        hi = max(bars[i]["h"] for i in prev)
        lo = min(bars[i]["l"] for i in prev)
        sh = [bars[i]["h"] for i in prev if bars[i]["h"] >= bars[i-1]["h"] and bars[i]["h"] >= bars[i+1]["h"]]
        sl = [bars[i]["l"] for i in prev if bars[i]["l"] <= bars[i-1]["l"] and bars[i]["l"] <= bars[i+1]["l"]]
        def cluster(vals):
            vals = sorted(vals); out = []; used = [False]*len(vals)
            for a in range(len(vals)):
                if used[a]: continue
                used[a] = True; grp = [vals[a]]
                for b2 in range(a+1, len(vals)):
                    if not used[b2] and abs(vals[b2]-vals[a]) <= vals[a]*tol:
                        grp.append(vals[b2]); used[b2] = True
                if len(grp) >= 2: out.append(sum(grp)/len(grp))
            return out
        levels[d] = {"pdh": hi, "pdl": lo, "eq": cluster(sh) + cluster(sl)}
    return levels
