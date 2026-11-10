"""Line-for-line python port of MyTradingSys/tools/live_aid/pulse.js (read, grid, setup, foldK), the indicator maths it calls in
live_aid_indicators.js (rma, rsi, wavetrend, divergence) and the zone merge/ladder of level_registry.js.
Parity with the JS is proved in test_pulse_parity.py (node run on fixtures). No parameter is changed here: P is copied from pulse.js l.12.
Kline row = [openTime, o, h, l, c, volume, closeTime, quoteVol, trades, takerBuyBase]; a row shorter than 10 has no taker column (NaN)."""
import math

NAN = float("nan")
GRID = [("1m", 60000, "1m"), ("2m", 120000, "1m"), ("3m", 180000, "3m"), ("5m", 300000, "5m"), ("7m", 420000, "1m"), ("10m", 600000, "1m"),
        ("15m", 900000, "15m"), ("30m", 1800000, "30m"), ("1h", 3600000, "1h"), ("2h", 7200000, "2h"), ("4h", 14400000, "4h")]
P = {"rsiUp": 50, "rsiDn": 50, "cvdN": 10, "divW": 15, "wtWarm": 60, "minBars": 40, "lean": 0.25, "near": 0.0015,   # OURS (pulse.js l.12)
     "w": {"1m": 1, "2m": 1, "3m": 1, "5m": 1, "7m": 2, "10m": 2, "15m": 2, "30m": 2, "1h": 3, "2h": 3, "4h": 3},
     "lowTfs": ["1m", "2m", "3m", "5m", "7m", "10m", "15m"], "highTfs": ["1h", "2h", "4h"]}
DAY = 86400000
MERGE = 0.0015   # level_registry.js MERGE
NEAR_N = 3


def fin(x):
    return x is not None and not math.isnan(x) and not math.isinf(x)


def _num(r, i):
    """JS +r[i]: undefined -> NaN."""
    return float(r[i]) if len(r) > i and r[i] is not None else NAN


def foldK(k, ms):
    out, cur = [], None
    for r in (k or []):
        t = _num(r, 0)
        a = math.floor(t / DAY) * DAY
        b = a + math.floor((t - a) / ms) * ms
        if cur is None or cur[0] != b:
            cur = [b, _num(r, 1), _num(r, 2), _num(r, 3), _num(r, 4), _num(r, 5), b + ms - 1, 0, 0, _num(r, 9)]
            out.append(cur)
        else:
            cur[2] = max(cur[2], _num(r, 2))
            cur[3] = min(cur[3], _num(r, 3))
            cur[4] = _num(r, 4)
            cur[5] += _num(r, 5)
            cur[9] += _num(r, 9)
    return out


def rowsFor(TFK, tf):
    src = TFK.get(tf[2]) if TFK else None
    if not src:
        return None
    return src if tf[2] == tf[0] else foldK(src, tf[1])


def sgn(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def rma(values, n):
    out, s, cnt, prev = [NAN] * len(values), 0.0, 0, NAN
    for i, v in enumerate(values):
        if not fin(v):
            continue
        if cnt < n:
            s += v
            cnt += 1
            if cnt == n:
                prev = s / n
                out[i] = prev
        else:
            prev = (prev * (n - 1) + v) / n
            out[i] = prev
    return out


def sma(values, n):
    out = [NAN] * len(values)
    for i in range(n - 1, len(values)):
        w = values[i - n + 1:i + 1]
        if all(fin(x) for x in w):
            out[i] = sum(w) / n
    return out


def rsi(closes, n=14):
    g, l = [NAN], [NAN]
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        g.append(d if d > 0 else 0)
        l.append(-d if d < 0 else 0)
    ag, al = rma(g, n), rma(l, n)
    out = []
    for a, b in zip(ag, al):
        if not fin(a) or not fin(b):
            out.append(NAN)
        elif b == 0:
            out.append(50 if a == 0 else 100)
        else:
            out.append(100 - 100 / (1 + a / b))
    return out


def wavetrend(times, highs, lows, closes, tfMs, warmup=200):
    n = len(closes)
    a1, a2 = 2 / 11, 2 / 22
    esa = dev = tci = None
    since, prevT = 0, None
    raw, keep = [NAN] * n, [False] * n
    for i in range(n):
        if prevT is not None and times[i] - prevT != tfMs:
            esa = dev = tci = None
            since = 0
        prevT = times[i]
        if not fin(highs[i]) or not fin(lows[i]) or not fin(closes[i]):
            esa = dev = tci = None
            since = 0
            continue
        ap = (highs[i] + lows[i] + closes[i]) / 3
        esa = ap if esa is None else a1 * ap + (1 - a1) * esa
        x = abs(ap - esa)
        dev = x if dev is None else a1 * x + (1 - a1) * dev
        if dev <= 1e-9 * abs(ap):
            tci = None
            since = 0
            continue
        ci = (ap - esa) / (0.015 * dev)
        tci = ci if tci is None else a2 * ci + (1 - a2) * tci
        since += 1
        raw[i] = tci
        keep[i] = since >= warmup
    w2 = sma(raw, 4)
    wt1, wt2, ev, last = [], [], [], 0
    for i in range(n):
        wt1.append(raw[i] if keep[i] else NAN)
        wt2.append(w2[i] if keep[i] else NAN)
        if not fin(wt1[i]) or not fin(wt2[i]):
            ev.append(0)
            last = 0
            continue
        side = (wt1[i] > wt2[i]) - (wt1[i] < wt2[i])
        ev.append(side if side != 0 and last != 0 and side != last else 0)
        if side != 0:
            last = side
    return {"wt1": wt1, "wt2": wt2, "event": ev}


def divergence(price, ind, w=15):
    n = len(price)
    if n < 2 * w or len(ind) != n:
        return None
    p1, p2, i1, i2 = price[n - 2 * w:n - w], price[n - w:], ind[n - 2 * w:n - w], ind[n - w:]
    if not all(fin(x) for a in (p1, p2, i1, i2) for x in a):
        return None
    if min(p2) < min(p1) and min(i2) > min(i1):
        return 1
    if max(p2) > max(p1) and max(i2) < max(i1):
        return -1
    return 0


def read(k, ms):
    if not k or len(k) < P["minBars"]:
        return None
    t, h, l, c, cum, s, okCvd = [], [], [], [], [], 0.0, True
    for r in k:
        t.append(_num(r, 0))
        h.append(_num(r, 2))
        l.append(_num(r, 3))
        c.append(_num(r, 4))
        v, b = _num(r, 5), _num(r, 9)
        if not fin(v) or not fin(b):
            okCvd = False
        else:
            s += 2 * b - v
        cum.append(s)
    n = len(c) - 1
    rs, w = rsi(c, 14), wavetrend(t, h, l, c, ms, P["wtWarm"])
    rv, a, b2 = rs[n], w["wt1"][n], w["wt2"][n]
    cv = cum[n] - cum[max(0, n - P["cvdN"])] if okCvd else NAN
    div = {"rsi": divergence(c, rs, P["divW"]), "wt": divergence(c, w["wt1"], P["divW"]), "cvd": divergence(c, cum, P["divW"]) if okCvd else None}
    v = {"rsi": None if not fin(rv) else 1 if rv > P["rsiUp"] else -1 if rv < P["rsiDn"] else 0,
         "wt": sgn(a - b2) if fin(a) and fin(b2) else None, "cvd": sgn(cv) if fin(cv) else None}
    dsum = (div["rsi"] or 0) + (div["wt"] or 0) + (div["cvd"] or 0)
    score = (v["rsi"] or 0) + (v["wt"] or 0) + (v["cvd"] or 0) + 2 * dsum
    return {"rsi": rv, "wt1": a, "wt2": b2, "cvd": cv, "v": v, "div": div, "dsum": dsum, "score": score,
            "bias": 1 if score >= 2 else -1 if score <= -2 else 0}


def grid(TFK):
    rows = []
    for tf in GRID:
        rows.append({"tf": tf[0], "ms": tf[1], "r": read(rowsFor(TFK, tf), tf[1])})
    num = den = hiNum = hiDen = 0
    for x in rows:
        if not x["r"]:
            continue
        wt = P["w"][x["tf"]]
        sc = max(-7, min(7, x["r"]["score"])) / 7
        num += wt * sc
        den += wt
        if x["tf"] in P["highTfs"]:
            hiNum += sc
            hiDen += 1
    lean = num / den if den else NAN
    hi = hiNum / hiDen if hiDen else NAN
    d = "NO DATA" if not fin(lean) else "UP" if lean >= P["lean"] else "DOWN" if lean <= -P["lean"] else "MIXED"
    return {"rows": rows, "lean": lean, "hi": hi, "dir": d, "n": sum(1 for x in rows if x["r"])}


def setup(g, ladder, px, homeDir):
    if not g or not (px > 0) or not ladder:
        return None

    def near(z):
        return bool(z) and abs(px / z["price"] - 1) <= P["near"]
    cand = [z for z in (ladder.get("at"), (ladder.get("above") or [None])[0], (ladder.get("below") or [None])[0]) if near(z)]
    cand.sort(key=lambda z: abs(px - z["price"]))
    res = sup = cand[0] if cand else None
    names = {"rsi": "RSI", "wt": "WaveTrend", "cvd": "CVD"}

    def divs(sd):
        out = []
        for x in g["rows"]:
            if not x["r"] or x["tf"] not in P["lowTfs"]:
                continue
            for key in ("rsi", "wt", "cvd"):
                if x["r"]["div"][key] == sd:
                    out.append(x["tf"] + " " + names[key])
        return out
    hi = g["hi"] if "hi" in g and g["hi"] is not None else NAN
    tries = []
    if res:
        tries.append({"side": "SHORT", "z": res, "sd": -1, "big": (fin(hi) and hi < 0) or homeDir == "SHORT"})
    if sup:
        tries.append({"side": "LONG", "z": sup, "sd": 1, "big": (fin(hi) and hi > 0) or homeDir == "LONG"})
    for q in tries:
        d = divs(q["sd"])
        if q["big"] and d:
            word = "bearish" if q["sd"] < 0 else "bullish"
            return {"side": q["side"], "level": q["z"]["price"], "name": q["z"].get("name"), "divs": d,
                    "why": ["at " + str(q["z"].get("name")), "big picture " + ("down" if q["sd"] < 0 else "up"),
                            word + " divergence " + ", ".join(d[:3]) + (" +" + str(len(d) - 3) if len(d) > 3 else "")]}
    return None


# ---- level_registry.js: merge + ladder (items need price, label) ----
def _rnd1(x):
    return math.floor(x * 10 + 0.5) / 10


def merge(items, tol=None):
    tol = MERGE if tol is None else tol
    s = sorted((x for x in (items or []) if x and fin(x.get("price")) and x["price"] > 0), key=lambda a: a["price"])
    zs = []
    for it in s:
        z = zs[-1] if zs else None
        if z and it["price"] / z["lo"] - 1 <= tol:
            z["hi"] = it["price"]
            z["items"].append(it)
        else:
            zs.append({"lo": it["price"], "hi": it["price"], "items": [it]})
    out = []
    for z in zs:
        kinds = []
        for i in z["items"]:
            if i["label"] not in kinds:
                kinds.append(i["label"])
        out.append({"lo": z["lo"], "hi": z["hi"], "price": _rnd1((z["lo"] + z["hi"]) / 2), "label": "Cluster" if len(kinds) > 1 else z["items"][0]["label"],
                    "n": len(z["items"]), "items": z["items"]})
    return out


def ladder(zones, px, n=None):
    n = n or NEAR_N
    up, dn, at = [], [], None
    for z in (zones or []):
        if z["lo"] <= px <= z["hi"]:
            at = z
        elif z["lo"] > px:
            up.append(z)
        else:
            dn.append(z)
    up.sort(key=lambda z: z["lo"])
    dn.sort(key=lambda z: -z["hi"])
    return {"above": up[:n], "below": dn[:n], "at": at}
