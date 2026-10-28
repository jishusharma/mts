"""Krown layer v0 detectors: pure functions of closed bars, no lookahead (a value at bar t uses bars <= t only).

Definitions: FORMULAS.md section 21. Numbers: params/krown_params.json (SOURCED with a ledger id, or OURS).
Descriptive only: no P&L, no live wiring, default OFF.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).parent


def load_params(path=None):
    with open(path or HERE / "params" / "krown_params.json", encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v["value"] for k, v in raw["params"].items()}


# ---- averages -------------------------------------------------------------------------------------------------

def sma(x, n):
    out = [None] * len(x)
    for t in range(n - 1, len(x)):
        out[t] = sum(x[t - n + 1:t + 1]) / n
    return out


def ema(x, n):
    """EMA seeded with the SMA of the first n values (OURS), alpha = 2/(n+1)."""
    out = [None] * len(x)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = sum(x[:n]) / n
    for t in range(n, len(x)):
        out[t] = out[t - 1] + a * (x[t] - out[t - 1])
    return out


def crosses(a, b):
    """'up' / 'down' at the first bar strictly on the other side of a-b; a tie bar is skipped; a None resets."""
    out = [None] * len(a)
    last = None
    for t in range(len(a)):
        if a[t] is None or b[t] is None:
            last = None
            continue
        d = a[t] - b[t]
        if d == 0:
            continue
        side = 1 if d > 0 else -1
        if last is not None and side != last:
            out[t] = "up" if side > 0 else "down"
        last = side
    return out


def leash(low, high, ema_line, n):
    """KR-M06: a run of >= n closes whose candle sits wholly above (below) the EMA ends at the first bar that touches it."""
    out = []
    run_l = run_s = 0
    for t in range(len(low)):
        e = ema_line[t]
        if e is None:
            run_l = run_s = 0
            continue
        if low[t] > e:
            run_l += 1
        else:
            if run_l >= n:
                out.append((t, "long", run_l))
            run_l = 0
        if high[t] < e:
            run_s += 1
        else:
            if run_s >= n:
                out.append((t, "short", run_s))
            run_s = 0
    return out


# ---- volume ---------------------------------------------------------------------------------------------------

def vol_ratio(v, n):
    """Volume over the mean of the n PRIOR bars (current excluded: OURS)."""
    out = [None] * len(v)
    for t in range(n, len(v)):
        m = sum(v[t - n:t]) / n
        out[t] = v[t] / m if m > 0 else None
    return out


def vol_ratio_slot(v, slots, m):
    """Same-slot baseline arm: mean of the same slot (index mod slots) over the previous m periods."""
    out = [None] * len(v)
    for t in range(slots * m, len(v)):
        base = sum(v[t - slots * j] for j in range(1, m + 1)) / m
        out[t] = v[t] / base if base > 0 else None
    return out


def vol_flags(ratio, mult, half):
    if ratio is None:
        return (False, False)
    return (ratio >= mult, ratio <= half)


# ---- volatility regime ----------------------------------------------------------------------------------------

def bbwp(c, basis, lookback, mult=2.0):
    """Bollinger band width percentile; FORMULAS.md 21.5. First value at t = basis-1+lookback."""
    n = len(c)
    bbw = [None] * n
    for t in range(basis - 1, n):
        w = c[t - basis + 1:t + 1]
        m = sum(w) / basis
        if m == 0:
            continue
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / basis)
        bbw[t] = 2 * mult * sd / m
    out = [None] * n
    for t in range(basis - 1 + lookback, n):
        prev = bbw[t - lookback:t]
        if bbw[t] is None or any(x is None for x in prev):
            continue
        out[t] = 100.0 * sum(1 for x in prev if x < bbw[t]) / lookback
    return out


def bbwp_regime(x, high, low):
    if x is None:
        return None
    if x >= high:
        return "expansion"
    if x <= low:
        return "compression"
    return "normal"


# ---- candles --------------------------------------------------------------------------------------------------

def engulfing(h, l, c, i):
    """KR-C06 strict: bull = trades below the prior low AND closes above the prior HIGH; bear mirrored."""
    if i < 1:
        return None
    if l[i] < l[i - 1] and c[i] > h[i - 1]:
        return "bull"
    if h[i] > h[i - 1] and c[i] < l[i - 1]:
        return "bear"
    return None


def is_hammer(o, h, l, c, p):
    r = h - l
    if r <= 0:
        return False
    return (min(o, c) - l) / r >= p["hammer_wick"] and (c - l) / r >= p["hammer_close_pos"]


def is_shooting_star(o, h, l, c, p):
    r = h - l
    if r <= 0:
        return False
    return (h - max(o, c)) / r >= p["hammer_wick"] and (h - c) / r >= p["hammer_close_pos"]


def is_doji(o, h, l, c, p):
    r = h - l
    return r > 0 and abs(c - o) / r <= p["doji_body"]


def three_crows(o, c, i):
    if i < 2:
        return False
    return all(c[j] < o[j] for j in (i - 2, i - 1, i)) and c[i] < c[i - 1] < c[i - 2]


def confirm_index(kind, h, l, c, i, horizon):
    """KR-C08: first close within `horizon` bars beyond the pattern's wick high (bull) or low (bear)."""
    for j in range(i + 1, min(i + horizon, len(c) - 1) + 1):
        if kind == "bull" and c[j] > h[i]:
            return j
        if kind == "bear" and c[j] < l[i]:
            return j
    return None


# ---- swings, trend state ---------------------------------------------------------------------------------------

def swings(h, l, k):
    """Strict swings with k bars each side; (index, 'H'|'L', price, avail) with avail = index + k, ordered by index."""
    out = []
    for i in range(k, len(h) - k):
        around_h = h[i - k:i] + h[i + 1:i + k + 1]
        around_l = l[i - k:i] + l[i + 1:i + k + 1]
        if all(h[i] > x for x in around_h):
            out.append((i, "H", h[i], i + k))
        if all(l[i] < x for x in around_l):
            out.append((i, "L", l[i], i + k))
    return out


def _structural(highs, lows, tol):
    if len(highs) < 2 or len(lows) < 2:
        return "range"
    h1, h2 = highs[-2][1], highs[-1][1]
    l1, l2 = lows[-2][1], lows[-1][1]
    if h2 > h1 * (1 + tol) and l2 > l1 * (1 + tol):
        return "up"
    if h2 < h1 * (1 - tol) and l2 < l1 * (1 - tol):
        return "down"
    return "range"


def trend_state(h, l, c, k, tol):
    """KR-L10 state machine, FORMULAS.md 21.4. Per bar {state, dom_low, dom_high}."""
    n = len(c)
    by_avail = {}
    for s in swings(h, l, k):
        by_avail.setdefault(s[3], []).append(s)
    highs, lows = [], []
    state, dom_low, dom_high = "range", None, None
    out = []
    for t in range(n):
        changed = False
        for i, kind, price, _ in by_avail.get(t, []):
            (highs if kind == "H" else lows).append((i, price))
            changed = True
        if changed:
            s = _structural(highs, lows, tol)
            if state == "range":
                if s != "range":
                    state = s
            elif s != state:
                state, dom_low, dom_high = "range", None, None
            if state == "up" and len(highs) >= 2:
                dom_low = min(l[highs[-2][0]:highs[-1][0] + 1])
            elif state == "down" and len(lows) >= 2:
                dom_high = max(h[lows[-2][0]:lows[-1][0] + 1])
        if state == "up" and dom_low is not None and l[t] < dom_low and c[t] < dom_low:
            state, dom_low = "down", None
            dom_high = highs[-1][1] if highs else None
        elif state == "down" and dom_high is not None and h[t] > dom_high and c[t] > dom_high:
            state, dom_high = "up", None
            dom_low = lows[-1][1] if lows else None
        out.append({"state": state, "dom_low": dom_low, "dom_high": dom_high})
    return out


# ---- zones ----------------------------------------------------------------------------------------------------

def zone_bounds(kind, close, extreme):
    """KR-Z01: zone = [close, wick extreme] of the pivot bar."""
    return (min(close, extreme), max(close, extreme))


def zones_from(sw, h, l, c, ratio, t, p):
    """Ranked zones usable at bar t from the swing list `sw` (any superset of the swings known by t)."""
    cand = [s for s in sw if s[3] <= t and s[0] >= t - p["zone_lookback"]]
    zones = []
    for i, kind, ext, avail in cand:
        lo, hi = zone_bounds(kind, c[i], ext)
        turns = sum(1 for j, k2, e2, _ in cand if k2 == kind and lo <= e2 <= hi)
        r = ratio[i]
        heavy = r is not None and r >= p["vol_mult"]
        if turns < p["zone_min_turns"] and not heavy:
            continue
        touches = sum(1 for j in range(avail + 1, t + 1) if l[j] <= hi and h[j] >= lo)
        zones.append({"lo": lo, "hi": hi, "kind": kind, "pivot": i, "avail": avail, "turns": turns, "heavy": heavy,
                      "touches": touches, "mature": touches > p["zone_mature_tests"]})
    zones.sort(key=lambda z: (z["heavy"], z["turns"], z["avail"]), reverse=True)
    kept = []
    for z in zones:
        if any(q["kind"] == z["kind"] and q["lo"] <= z["hi"] and z["lo"] <= q["hi"] for q in kept):
            continue
        kept.append(z)
        if len(kept) >= p["zone_max"]:
            break
    return kept


def zones_at(h, l, c, v, t, p):
    sw = swings(h[:t + 1], l[:t + 1], p["zone_k"])
    return zones_from(sw, h, l, c, vol_ratio(v[:t + 1], p["vol_sma"]), t, p)


# ---- RSI, MACD ------------------------------------------------------------------------------------------------

def rsi(c, period):
    """Wilder RSI: first averages are the simple mean of the first `period` changes."""
    n = len(c)
    out = [None] * n
    if n <= period:
        return out
    gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, n)]
    losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, n)]
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period

    def val(ag, al):
        if al == 0:
            return 100.0 if ag > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + ag / al)

    out[period] = val(ag, al)
    for t in range(period + 1, n):
        ag = (ag * (period - 1) + gains[t - 1]) / period
        al = (al * (period - 1) + losses[t - 1]) / period
        out[t] = val(ag, al)
    return out


def rsi_zone(x, bull=60, bear=40):
    if x is None:
        return None
    if x > bull:
        return "bull"
    if x < bear:
        return "bear"
    return "range"


def macd(c, fast, slow, sig):
    ef, es = ema(c, fast), ema(c, slow)
    line = [None] * len(c)
    for t in range(len(c)):
        if ef[t] is not None and es[t] is not None:
            line[t] = ef[t] - es[t]
    start = slow - 1
    sg = [None] * len(c)
    valid = line[start:]
    se = ema(valid, sig) if len(valid) >= sig else [None] * len(valid)
    for j, x in enumerate(se):
        sg[start + j] = x
    return line, sg


def bear_divergence(h, l, rsi_line, k):
    """Bars (the later swing's avail) where a swing high is higher than the previous one but its RSI is lower."""
    highs = [s for s in swings(h, l, k) if s[1] == "H"]
    out = []
    for a, b in zip(highs, highs[1:]):
        ra, rb = rsi_line[a[0]], rsi_line[b[0]]
        if ra is None or rb is None:
            continue
        if b[2] > a[2] and rb < ra:
            out.append(b[3])
    return out


# ---- range, coil ----------------------------------------------------------------------------------------------

def range_state(h, l, c, t, p):
    """KR-R01 / R07, FORMULAS.md 21.8: range over the n PRIOR bars; None when absent or too wide."""
    n = p["range_n"]
    if t < n:
        return None
    top, bottom = max(h[t - n:t]), min(l[t - n:t])
    height = top - bottom
    mid = (top + bottom) / 2
    if height <= 0 or mid <= 0 or height / mid > p["range_width_max"]:
        return None
    pos = (c[t] - bottom) / height
    edge = None
    if pos <= p["range_edge"] + 1e-9:
        edge = "low"
    elif pos >= 1 - p["range_edge"] - 1e-9:
        edge = "high"
    breakout = "up" if c[t] > top else ("down" if c[t] < bottom else None)
    return {"top": top, "bottom": bottom, "height": height, "position": pos, "edge": edge, "breakout": breakout}


def coil_score(h, l, t, recent, n):
    """Mean bar range of the last `recent` bars over the mean range of the n bars before them."""
    if t - recent - n + 1 < 0:
        return None
    a = sum(h[j] - l[j] for j in range(t - recent + 1, t + 1)) / recent
    b = sum(h[j] - l[j] for j in range(t - recent - n + 1, t - recent + 1)) / n
    return a / b if b > 0 else None


# ---- tops -----------------------------------------------------------------------------------------------------

def tops(candle, vol, volat, mom, window, need):
    """KR-P01: bars where >= `need` of the four signals sit inside the last `window` bars and the count was lower a bar earlier."""
    n = len(candle)

    def count(t):
        if t < 0:
            return 0
        lo = max(0, t - window + 1)
        return sum(1 for s in (candle, vol, volat, mom) if any(s[lo:t + 1]))

    return [t for t in range(n) if count(t) >= need and count(t - 1) < need]
