"""Causal pivot candidates (PRE_REG.md in this folder). Every parameter is OURS. A candidate at bar i reads bars <= i only."""
import math
from collections import defaultdict

L = 3             # lookback bars (OURS)
ATR_N = 14        # FORMULAS.md section 12, length OURS
VOL_N = 20        # volume-spike mean window (OURS)
VOL_MULT = 2.0    # OURS
DELTA_FRAC = 0.2  # |delta|/volume (OURS)
LEVEL_ATR = 0.5   # location tolerance in ATR (OURS)
OI_LAG_MS = 300_000  # D2: OI stamp T usable by a bar closing at >= T + 5 min
DAY_MS = 86_400_000


def aggregate(rows, tf_min):
    """rows: dicts t(open ms), o,h,l,c,v,tb at 1m, sorted. Returns tf bars aligned to UTC multiples of tf_min; incomplete bars dropped."""
    step = tf_min * 60_000
    groups = defaultdict(list)
    for r in rows:
        groups[r["t"] - r["t"] % step].append(r)
    out = []
    for t0 in sorted(groups):
        g = groups[t0]
        if len(g) != tf_min:
            continue
        out.append({"t": t0, "close_ms": t0 + step, "o": g[0]["o"], "h": max(x["h"] for x in g), "l": min(x["l"] for x in g),
                    "c": g[-1]["c"], "v": sum(x["v"] for x in g), "tb": sum(x["tb"] for x in g)})
    return out


def atr(bars, i, n=ATR_N):
    """Plain SMA of True Range over the n bars ending at i (FORMULAS.md s12). None if i < n."""
    if i < n:
        return None
    s = 0.0
    for j in range(i - n + 1, i + 1):
        pc = bars[j - 1]["c"]
        s += max(bars[j]["h"] - bars[j]["l"], abs(bars[j]["h"] - pc), abs(bars[j]["l"] - pc))
    return s / n


def oi_at(oi, close_ms):
    """Latest OI row stamped <= close_ms - 5 min within 15 min; None if absent (NOT_IN_DATA, never 0)."""
    b = close_ms - OI_LAG_MS
    b -= b % 300_000
    for k in range(3):
        v = oi.get(b - k * 300_000)
        if v is not None:
            return v
    return None


def _slope(bars, oi, i):
    a, b = oi_at(oi, bars[i]["close_ms"]), oi_at(oi, bars[i - L]["close_ms"])
    return None if a is None or b is None else a - b


def _prev_sign(bars, oi, i):
    """Last non-zero OI slope sign at bars i, i-1, ... (up to 6 back); 0 if none (a flat stretch does not hide a flip)."""
    for j in range(i, max(i - 6, L) - 1, -1):
        s = _slope(bars, oi, j)
        if s is not None and s != 0:
            return _sgn(s)
    return 0


def _sgn(x):
    return (x > 0) - (x < 0)


def delta(bar):
    return 2 * bar["tb"] - bar["v"]


def prior_day_levels(bars, i):
    """(low, high) of the previous completed UTC day, from bars <= i. None if that day has no bars."""
    d = bars[i]["t"] // DAY_MS - 1
    lo = hi = None
    for j in range(i, -1, -1):
        dj = bars[j]["t"] // DAY_MS
        if dj < d:
            break
        if dj == d:
            lo = bars[j]["l"] if lo is None else min(lo, bars[j]["l"])
            hi = bars[j]["h"] if hi is None else max(hi, bars[j]["h"])
    return None if lo is None else (lo, hi)


def _fires(bars, oi, i):
    """Raw (name, side) pairs true at bar i using bars <= i."""
    move = _sgn(bars[i]["c"] - bars[i - L]["c"])
    out = []
    s_now = _slope(bars, oi, i)
    if s_now is not None and move != 0:
        if s_now != 0 and _prev_sign(bars, oi, i - 1) == -_sgn(s_now):
            out.append(("oi_flip", "BOTTOM" if move < 0 else "TOP"))
        if move > 0 and s_now < 0:
            out.append(("pv_oi_div", "TOP"))
        if move < 0 and s_now > 0:
            out.append(("pv_oi_div", "BOTTOM"))
    d = delta(bars[i])
    if move != 0 and bars[i]["v"] > 0 and _sgn(d) == -move and abs(d) / bars[i]["v"] >= DELTA_FRAC:
        out.append(("delta_sign", "BOTTOM" if d > 0 else "TOP"))
    if i >= VOL_N:
        mv = sum(bars[j]["v"] for j in range(i - VOL_N, i)) / VOL_N
        if mv > 0 and bars[i]["v"] >= VOL_MULT * mv and bars[i]["c"] != bars[i]["o"]:
            out.append(("vol_spike", "BOTTOM" if bars[i]["c"] < bars[i]["o"] else "TOP"))
    return out


def candidates(bars, oi, start=0):
    """Onset-only candidates for every bar i >= start. Dict: i, name, side, atr, location, context."""
    res = []
    first = max(start, ATR_N + 1, L + 1)
    prev = set(_fires(bars, oi, first - 1)) if first - 1 > L else set()
    for i in range(first, len(bars)):
        now = set(_fires(bars, oi, i))
        a = atr(bars, i)
        for name, side in sorted(now - prev):
            if a is None or a <= 0:
                continue
            lv = prior_day_levels(bars, i)
            if lv is None:
                loc = "NOT_IN_DATA"
            elif side == "BOTTOM":
                loc = "AT_LEVEL" if bars[i]["l"] <= lv[0] + LEVEL_ATR * a else "OTHER"
            else:
                loc = "AT_LEVEL" if bars[i]["h"] >= lv[1] - LEVEL_ATR * a else "OTHER"
            n4 = TF_BARS_4H.get(_tf_min(bars), 48)
            if i < n4:
                ctx = "NOT_IN_DATA"
            else:
                r4 = bars[i]["c"] - bars[i - n4]["c"]
                ctx = "WITH" if (side == "BOTTOM" and r4 < 0) or (side == "TOP" and r4 > 0) else "AGAINST"
            res.append({"i": i, "name": name, "side": side, "atr": a, "location": loc, "context": ctx})
        prev = now
    return res


TF_BARS_4H = {5: 48, 15: 16}


def _tf_min(bars):
    return (bars[1]["t"] - bars[0]["t"]) // 60_000


def swing_label(bars, j):
    """OUTCOME annotation only. Strict 5-bar pivot at j, known at the close of bar j+2: 'low', 'high' or None."""
    if j < 2 or j + 2 >= len(bars):
        return None
    w = bars[j - 2:j + 3]
    lo = [b["l"] for b in w]
    hi = [b["h"] for b in w]
    if lo[2] < min(lo[:2]) and lo[2] < min(lo[3:]):
        return "low"
    if hi[2] > max(hi[:2]) and hi[2] > max(hi[3:]):
        return "high"
    return None


def outcome(bars, i, a, side, k=1.0, H=24, last_idx=None):
    """Reversal before continuation. Entry E = open of bar i+1; barriers E +- k*a. Returns HIT/MISS/AMBIGUOUS/TIMEOUT/CENSORED."""
    last = len(bars) - 1 if last_idx is None else last_idx
    if i + H > last:
        return "CENSORED"
    e = bars[i + 1]["o"]
    up, dn = e + k * a, e - k * a
    rev, cont = (up, dn) if side == "BOTTOM" else (dn, up)
    for j in range(i + 1, i + H + 1):
        b = bars[j]
        r = b["h"] >= rev if side == "BOTTOM" else b["l"] <= rev
        c = b["l"] <= cont if side == "BOTTOM" else b["h"] >= cont
        if r and c:
            return "AMBIGUOUS"
        if r:
            return "HIT"
        if c:
            return "MISS"
    return "TIMEOUT"


def cluster_p_se(pairs):
    """pairs: (day, hit 0/1). Ratio estimator: P = sum h / n, SE = sqrt(sum_d (h_d - P n_d)^2) / n."""
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan")
    hd, nd = defaultdict(float), defaultdict(int)
    for d, h in pairs:
        hd[d] += h
        nd[d] += 1
    p = sum(hd.values()) / n
    return p, math.sqrt(sum((hd[d] - p * nd[d]) ** 2 for d in nd)) / n
