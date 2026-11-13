"""run_1113.py - card adx-1d-through25-1113. Executes PRE_REG.md exactly; no search. Context study, no orders.
  python run_1113.py [--out REPORT.md]
ADX/DI re-implemented from FORMULAS.md section 30.1 (not imported from adx.py).
"""
import csv
import datetime
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
KL = os.path.join(ROOT, "market_data", "klines")
BTC_CSV = os.path.join(ROOT, "research", "btc_cycles_2026-11", "btc_daily.csv")
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "LTCUSDT")
N = 14
FEE = 0.0010
HOLDS = (3, 6, 12)
PRIMARY_H = 6
WARM = 100
SPLITS = (("DEV", "2020-01-01", "2024-06-30"), ("VALIDATION", "2024-07-01", "2025-06-30"),
          ("RECENT", "2025-07-01", "9999-12-31"))
DAY = 86400


def split_of(date):
    for name, lo, hi in SPLITS:
        if lo <= date <= hi:
            return name
    return None


# ---------------------------------------------------------------- data
def load(sym, now=None):
    rows = json.load(open(os.path.join(KL, "%s_1d_bybit.json" % sym)))
    now = time.time() if now is None else now
    bars = []
    for r in rows:
        if r[0] / 1000 + DAY > now:        # partial day
            continue
        bars.append({"d": datetime.datetime.fromtimestamp(r[0] / 1000, datetime.timezone.utc).strftime("%Y-%m-%d"),
                     "o": r[1], "h": r[2], "l": r[3], "c": r[4]})
    if sym == "BTCUSDT":
        first = bars[0]["d"]
        pre, prev = [], None
        for r in csv.DictReader(open(BTC_CSV, newline="")):
            if r["date"] < "2017-01-01" or r["date"] >= first:
                continue
            c = float(r["close"])
            pre.append({"d": r["date"], "o": prev if prev is not None else c, "h": float(r["high"]),
                        "l": float(r["low"]), "c": c})
            prev = c
        bars = pre + bars
    return bars


# ---------------------------------------------------------------- indicators (FORMULAS.md 30.1, 4)
def adx_di(h, l, c, n=N):
    """(dip, dim, adx); None until defined: DI from bar n, ADX from bar 2n-1."""
    m = len(c)
    dip, dim, adx = [None] * m, [None] * m, [None] * m
    if m <= n:
        return dip, dim, adx
    tr = [0.0] * m
    pdm = [0.0] * m
    mdm = [0.0] * m
    for i in range(1, m):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        pdm[i] = up if (up > dn and up > 0) else 0.0
        mdm[i] = dn if (dn > up and dn > 0) else 0.0
    st, sp, sm = sum(tr[1:n + 1]), sum(pdm[1:n + 1]), sum(mdm[1:n + 1])
    dx = [None] * m
    for i in range(n, m):
        if i > n:
            st = st - st / n + tr[i]
            sp = sp - sp / n + pdm[i]
            sm = sm - sm / n + mdm[i]
        dip[i] = 100 * sp / st if st else 0.0
        dim[i] = 100 * sm / st if st else 0.0
        s = dip[i] + dim[i]
        dx[i] = 100 * abs(dip[i] - dim[i]) / s if s else 0.0
    if m > 2 * n - 1:
        a = sum(dx[n:2 * n]) / n
        adx[2 * n - 1] = a
        for i in range(2 * n, m):
            a = (a * (n - 1) + dx[i]) / n
            adx[i] = a
    return dip, dim, adx


def ema(x, n):
    """EMA, alpha 2/(n+1), seeded by the SMA of the first n values (section 4)."""
    out = [None] * len(x)
    if len(x) < n:
        return out
    e = sum(x[:n]) / n
    out[n - 1] = e
    k = 2.0 / (n + 1)
    for i in range(n, len(x)):
        e = (x[i] - e) * k + e
        out[i] = e
    return out


def sma(x, n):
    return [None if i < n - 1 else sum(x[i - n + 1:i + 1]) / n for i in range(len(x))]


# ---------------------------------------------------------------- Rule A
def rule_a_events(dip, dim, adx, start=WARM):
    """[(i, side)] side +1 long / -1 short; signal at the close of bar i."""
    out = []
    for i in range(max(start, 1), len(adx)):
        if None in (adx[i], adx[i - 1], dip[i], dim[i]):
            continue
        if adx[i - 1] <= 25 < adx[i]:
            if dip[i] > dim[i]:
                out.append((i, 1))
            elif dim[i] > dip[i]:
                out.append((i, -1))
    return out


def a_net(bars, i, side, h):
    if i + h >= len(bars):
        return None
    return side * (bars[i + h]["c"] / bars[i + 1]["o"] - 1.0) - FEE


# ---------------------------------------------------------------- Rule B
def rule_b(bars, dip, dim, adx, e20, start=WARM):
    """-> (trades, state). trade = dict(side, k, e, net, d, notarget). Trade still open at data end is not counted."""
    n = len(bars)
    h = [b["h"] for b in bars]
    l = [b["l"] for b in bars]
    o = [b["o"] for b in bars]
    c = [b["c"] for b in bars]
    trades = []
    state = {"armed": None, "open": None}
    free = -1
    t = max(start, 21)
    while t < n:
        if t <= free or None in (adx[t], adx[t - 1], dip[t], dim[t], e20[t], e20[t - 1]) \
                or not (adx[t] > 30 and adx[t] > adx[t - 1]):
            t += 1
            continue
        side = 1 if dip[t] > dim[t] else -1 if dim[t] > dip[t] else 0
        if side == 0:
            t += 1
            continue
        if side == 1:
            touch = l[t] <= e20[t] and c[t - 1] > e20[t - 1]
        else:
            touch = h[t] >= e20[t] and c[t - 1] < e20[t - 1]
        if not touch:
            t += 1
            continue
        k = None
        for j in range(t + 1, min(t + 3, n - 1) + 1):
            if (side == 1 and h[j] > h[t]) or (side == -1 and l[j] < l[t]):
                k = j
                break
        if k is None:
            if t + 3 > n - 1:
                state["armed"] = {"side": side, "t": t}
            t += 1
            continue
        fill = max(o[k], h[t]) if side == 1 else min(o[k], l[t])
        stop = l[t] if side == 1 else h[t]
        if side == 1:
            tgt = max(h[t - 20:t])
            tgt = tgt if tgt > fill else None
        else:
            tgt = min(l[t - 20:t])
            tgt = tgt if tgt < fill else None
        ex, e = None, None
        for m in range(k, min(k + 12, n - 1) + 1):
            op = o[m]
            if m > k and ((side == 1 and op <= stop) or (side == -1 and op >= stop)):
                ex, e = op, m
                break
            if (side == 1 and l[m] <= stop) or (side == -1 and h[m] >= stop):
                ex, e = stop, m
                break
            if tgt is not None and ((side == 1 and h[m] >= tgt) or (side == -1 and l[m] <= tgt)):
                if m > k:
                    ex = max(op, tgt) if side == 1 else min(op, tgt)
                else:
                    ex = tgt
                e = m
                break
            if m == k + 12:
                ex, e = c[m], m
                break
        if e is None:
            state["open"] = {"side": side, "k": k, "t": t}
            break
        trades.append({"side": side, "k": k, "e": e, "d": e - k, "notarget": tgt is None,
                       "net": side * (ex / fill - 1.0) - FEE})
        free = e
        t = e + 1
    return trades, state


# ---------------------------------------------------------------- baselines
class Base:
    def __init__(self, bars):
        self.b = bars
        self.cache = {}

    def mean(self, kind, split, side, h):
        key = (kind, split, side, h)
        if key in self.cache:
            return self.cache[key]
        v = []
        for j in range(WARM, len(self.b)):
            if split_of(self.b[j]["d"]) != split:
                continue
            if kind == "A":
                r = a_net(self.b, j, side, h)
            else:
                r = None if j + h >= len(self.b) else side * (self.b[j + h]["c"] / self.b[j]["c"] - 1.0) - FEE
            if r is not None:
                v.append(r)
        self.cache[key] = sum(v) / len(v) if v else None
        return self.cache[key]


# ---------------------------------------------------------------- statistics
def boot(items, reps=10000, seed=1113):
    """items = [(month, excess)] -> (mean, lo, hi) cluster bootstrap over months; (mean,None,None) if < 5 events."""
    if not items:
        return None, None, None
    mean = sum(x for _, x in items) / len(items)
    if len(items) < 5:
        return mean, None, None
    g = {}
    for mo, x in items:
        s = g.setdefault(mo, [0.0, 0])
        s[0] += x
        s[1] += 1
    blocks = list(g.values())
    rnd = random.Random(seed)
    nb = len(blocks)
    res = []
    for _ in range(reps):
        sx = cnt = 0
        for _ in range(nb):
            b = blocks[rnd.randrange(nb)]
            sx += b[0]
            cnt += b[1]
        res.append(sx / cnt)
    res.sort()
    return mean, res[int(0.025 * reps)], res[int(0.975 * reps) - 1]


def summarize(rows):
    n = len(rows)
    if n == 0:
        return {"n": 0}
    m, lo, hi = boot([(r["month"], r["ex"]) for r in rows])
    return {"n": n, "net": sum(r["net"] for r in rows) / n, "ex": m, "lo": lo, "hi": hi,
            "win": sum(1 for r in rows if r["net"] > 0) / n}


# ---------------------------------------------------------------- study
def study():
    data = {}
    for s in SYMS:
        bars = load(s)
        h = [b["h"] for b in bars]
        l = [b["l"] for b in bars]
        c = [b["c"] for b in bars]
        dip, dim, adx = adx_di(h, l, c)
        data[s] = {"bars": bars, "dip": dip, "dim": dim, "adx": adx, "e20": ema(c, 20), "sma200": sma(c, 200),
                   "base": Base(bars)}
    A = {h: [] for h in HOLDS}
    B = []
    cur = {}
    for s, d in data.items():
        bars = d["bars"]
        ev = rule_a_events(d["dip"], d["dim"], d["adx"])
        for i, side in ev:
            sp = split_of(bars[i]["d"])
            if sp is None:
                continue
            for h in HOLDS:
                r = a_net(bars, i, side, h)
                if r is None:
                    continue
                bm = d["base"].mean("A", sp, side, h)
                A[h].append({"sym": s, "split": sp, "side": side, "net": r, "ex": r - bm, "month": bars[i]["d"][:7]})
        trades, st = rule_b(bars, d["dip"], d["dim"], d["adx"], d["e20"])
        for t in trades:
            sp = split_of(bars[t["k"]]["d"])
            if sp is None:
                continue
            bm = d["base"].mean("B", sp, t["side"], t["d"])
            if bm is None:
                continue
            B.append({"sym": s, "split": sp, "side": t["side"], "net": t["net"], "ex": t["net"] - bm,
                      "month": bars[t["k"]]["d"][:7], "notarget": t["notarget"], "d": t["d"]})
        last = len(bars) - 1
        al = ev[-1] if ev else None
        cur[s] = {"date": bars[last]["d"], "adx": d["adx"][last], "dip": d["dip"][last], "dim": d["dim"][last],
                  "a_last": None if al is None else (bars[al[0]]["d"], al[1], last - al[0]),
                  "b_state": st,
                  "b_filter": bool(d["adx"][last] > 30 and d["adx"][last] > d["adx"][last - 1])}
    mix = {}
    for name, _, _ in SPLITS:
        up = tot = 0
        for d in data.values():
            for j in range(WARM, len(d["bars"])):
                if d["sma200"][j] is None or split_of(d["bars"][j]["d"]) != name:
                    continue
                tot += 1
                up += d["bars"][j]["c"] > d["sma200"][j]
        mix[name] = (up / tot if tot else None, tot)
    bars = [b for b in load("BTCUSDT") if b["d"] >= "2017-01-01"]
    dip, dim, adx = adx_di([b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars])
    repro = sum(1 for i, sd in rule_a_events(dip, dim, adx, start=2) if sd == 1)
    return data, A, B, cur, mix, repro


def pct(x, d=2):
    return "-" if x is None else "%+.*f%%" % (d, x * 100)


def cellstr(s):
    if s["n"] == 0:
        return "n=0"
    t = "n=%d net %s ex %s" % (s["n"], pct(s["net"]), pct(s["ex"]))
    if s.get("lo") is not None:
        t += " [%s,%s]" % (pct(s["lo"], 1), pct(s["hi"], 1))
    return t + " win %.0f%%" % (s["win"] * 100) + (" U" if s["n"] < 30 else "")


def table(rows):
    L = ["| symbol side | DEV | VALIDATION | RECENT |", "|---|---|---|---|"]
    for s in SYMS:
        for sd in (1, -1):
            L.append("| %s %s | %s |" % (s[:-4], "long" if sd == 1 else "short", " | ".join(
                cellstr(summarize([r for r in rows if r["sym"] == s and r["side"] == sd and r["split"] == sp[0]]))
                for sp in SPLITS)))
    for lab, f in (("POOLED long", lambda r: r["side"] == 1), ("POOLED short", lambda r: r["side"] == -1),
                   ("POOLED both", lambda r: True)):
        L.append("| **%s** | %s |" % (lab, " | ".join(
            cellstr(summarize([r for r in rows if f(r) and r["split"] == sp[0]])) for sp in SPLITS)))
    return L


def verdict(rows, mix, other_holds=None):
    val = summarize([r for r in rows if r["split"] == "VALIDATION"])
    rec = summarize([r for r in rows if r["split"] == "RECENT"])
    if val["n"] < 30:
        return "UNDERPOWERED (VALIDATION n=%d < 30)" % val["n"]
    reasons = []
    if not (val["lo"] is not None and val["lo"] > 0):
        reasons.append("VALIDATION excess CI lower bound %s not > 0" % pct(val["lo"], 2))
    if other_holds is not None and not all(x is not None and x > 0 for x in other_holds):
        reasons.append("h=3/h=12 excess not both > 0")
    share = mix["VALIDATION"][0]
    if share is not None and (share > 0.85 or share < 0.15):
        reasons.append("VALIDATION ONE-REGIME")
    if rec["n"] >= 10 and rec["ex"] < 0:
        reasons.append("RECENT contradicts (mean excess %s, n=%d)" % (pct(rec["ex"]), rec["n"]))
    elif rec["n"] >= 5 and rec.get("hi") is not None and rec["hi"] < 0:
        reasons.append("RECENT CI upper bound < 0")
    return "FAIL: " + "; ".join(reasons) if reasons else "PASS"


def report(out):
    data, A, B, cur, mix, repro = study()
    L = ["# REPORT adx 1d through 25 + Holy Grail (card adx-1d-through25-1113)", ""]
    L.append("Regime mix (close above/below own 200d SMA, pooled 5 symbols): " + "; ".join(
        "%s %s (n=%d)" % (k, "-" if v[0] is None else "%.0f%% bull / %.0f%% bear" % (v[0] * 100, (1 - v[0]) * 100), v[1])
        for k, v in mix.items()) + ".")
    L.append("PRE_REG.md fixes every rule (committed before any outcome). Fee 10 bps RT. CI = 95% cluster bootstrap over "
             "calendar months (10,000, seed 1113), overlapping events kept. ex = excess vs same-symbol/split/side "
             "unconditional baseline. U = n<30. Data: Bybit 1d, BTC back-filled from csv before 2020-03-25; last closed bar 2026-11-12.")
    L.append("Reproduction check: BTC csv through-25 longs since 2017 = %d (source study 34 +-4): %s." % (
        repro, "OK" if abs(repro - 34) <= 4 else "NOT MATCHING"))
    L.append("")
    hv = {h: summarize([r for r in A[h] if r["split"] == "VALIDATION"]) for h in HOLDS}
    va = verdict(A[PRIMARY_H], mix, [hv[3].get("ex"), hv[12].get("ex")])
    vb = verdict(B, mix)
    L += ["## Verdicts", "| Rule | Verdict | VALIDATION pooled |", "|---|---|---|",
          "| A: 1d ADX through 25, hold 6 (primary) | **%s** | %s |" % (
              va, cellstr(summarize([r for r in A[PRIMARY_H] if r["split"] == "VALIDATION"]))),
          "| B: Holy Grail (EMA20, stop/target/12d) | **%s** | %s |" % (
              vb, cellstr(summarize([r for r in B if r["split"] == "VALIDATION"]))), ""]
    L += ["## Rule A, hold %d days (primary)" % PRIMARY_H] + table(A[PRIMARY_H]) + [""]
    L += ["## Rule A robustness, pooled both sides", "| hold | DEV | VALIDATION | RECENT |", "|---|---|---|---|"]
    for h in HOLDS:
        L.append("| %d | %s |" % (h, " | ".join(
            cellstr(summarize([r for r in A[h] if r["split"] == sp[0]])) for sp in SPLITS)))
    L += ["", "## Rule B (Holy Grail), one exit rule"] + table(B)
    L.append("Rule B trades with no target available: %d of %d (stop/time exit only)." % (
        sum(1 for r in B if r["notarget"]), len(B)))
    L += ["", "## Current state (last closed bar)"]
    for s, c in cur.items():
        a = c["a_last"]
        astr = ("last A signal %s %s, %d d ago%s" % (a[0], "long" if a[1] == 1 else "short", a[2],
                                                      " (6d hold still open)" if a[2] < 6 else "")) if a else "no A signal"
        bs = c["b_state"]
        bset = ("setup ARMED " + ("long" if bs["armed"]["side"] == 1 else "short")) if bs["armed"] else \
            "trade OPEN" if bs["open"] else "no B setup"
        L.append("- %s %s: ADX %.1f +DI %.1f -DI %.1f; A: %s; B filter %s, %s" % (
            s[:-4], c["date"], c["adx"], c["dip"], c["dim"], astr, "ON" if c["b_filter"] else "off", bset))
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump({"A_val": {str(h): hv[h] for h in HOLDS}, "verdict_A": va, "verdict_B": vb, "repro": repro},
              open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    out = os.path.join(HERE, "REPORT.md")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    report(out)
