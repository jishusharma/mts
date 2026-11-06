"""Moving-average state per timeframe (display layer, gates nothing). Definition: MA_CONCEPTS.md section (c).

Klines are the Binance shape [openTime,o,h,l,c,vol,closeTime,...]; the last bar is the forming bar.
Every average is None when there are fewer closes than its length (fail closed, never a guess).
Labels: lengths 20/21/50/55/200 SOURCED (Krown KR-M01/M07, web bull-market band); alpha 2/(N+1) SOURCED maths;
EMA seed (mean of the first N closes), slope window 5 bars, flat band 0.5 ATR, pullback touch 0.25 ATR: OURS.
The JavaScript twin is MyTradingSys/tools/live_aid/ma_strip.js; test_spec_ma_state.py checks both agree.
CLI: python ma_state.py            -> one JSON row per timeframe from data-api.binance.vision
"""
import json
import sys
import urllib.request

TFS = ["5m", "15m", "1h", "4h", "1d", "1w", "1M"]
BASE = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT"
SLOPE_BARS = 5
FLAT_ATR = 0.5
TOUCH_ATR = 0.25
# name -> (kind, length)
AVGS = {"sma20": ("sma", 20), "ema21": ("ema", 21), "ema55": ("ema", 55),
        "sma50": ("sma", 50), "sma200": ("sma", 200), "ema200": ("ema", 200)}


def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v == v and v not in (float("inf"), float("-inf")) else None


def sma_series(closes, n):
    """Rolling simple mean; None until n closes exist."""
    out = [None] * len(closes)
    s = 0.0
    for i, c in enumerate(closes):
        s += c
        if i >= n:
            s -= closes[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def ema_series(closes, n):
    """EMA with alpha 2/(n+1), seeded with the mean of the first n closes (OURS); None before bar n."""
    out = [None] * len(closes)
    if len(closes) < n:
        return out
    a = 2.0 / (n + 1)
    e = sum(closes[:n]) / n
    out[n - 1] = e
    for i in range(n, len(closes)):
        e = e + a * (closes[i] - e)
        out[i] = e
    return out


def atr14(klines):
    """Mean true range of the 14 closed bars before the forming bar; None with fewer than 16 bars."""
    n = len(klines)
    if n < 16:
        return None
    tot = 0.0
    for i in range(n - 15, n - 1):
        h, l, pc = _f(klines[i][2]), _f(klines[i][3]), _f(klines[i - 1][4])
        if h is None or l is None or pc is None:
            return None
        tot += max(h - l, abs(h - pc), abs(l - pc))
    return tot / 14


def cross_state(fast, slow):
    """{state, barsSince} for two aligned series. state up/down = fast above/below slow at the last bar with both
    defined and unequal (a tie keeps the previous state); barsSince = bars since the last change of state, None if none."""
    state = None
    last_change = None
    for i in range(len(fast)):
        f, s = fast[i], slow[i]
        if f is None or s is None or f == s:
            continue
        cur = "up" if f > s else "down"
        if state is not None and cur != state:
            last_change = i
        state = cur
    if state is None:
        return {"state": None, "barsSince": None}
    n = len(fast)
    return {"state": state, "barsSince": None if last_change is None else n - 1 - last_change}


def _slope(series, atr):
    if atr is None or len(series) <= SLOPE_BARS:
        return None
    a, b = series[-1], series[-1 - SLOPE_BARS]
    if a is None or b is None:
        return None
    d = a - b
    return "up" if d > FLAT_ATR * atr else "down" if d < -FLAT_ATR * atr else "flat"


def _avg_row(series, price, atr):
    v = series[-1]
    if v is None or not v:
        return None
    return {"v": v, "side": "above" if price > v else "below" if price < v else None,
            "distPct": 100.0 * (price - v) / v, "distAtr": None if not atr else (price - v) / atr,
            "ratio": price / v, "slope": _slope(series, atr)}


def ma_row(tf, klines):
    """One state row, or None when the bars are unreadable or the forming bar is missing."""
    if not isinstance(klines, list) or len(klines) < 2:
        return None
    last = klines[-1]
    closes = [_f(k[4]) if isinstance(k, (list, tuple)) and len(k) > 4 else None for k in klines]
    h, l = _f(last[2]), _f(last[3])
    if any(c is None for c in closes) or h is None or l is None:
        return None
    price = closes[-1]
    atr = atr14(klines)
    ser = {}
    for name, (kind, n) in AVGS.items():
        ser[name] = (sma_series if kind == "sma" else ema_series)(closes, n)
    avgs = {name: _avg_row(ser[name], price, atr) for name in AVGS}
    c2155 = cross_state(ser["ema21"], ser["ema55"])
    c50200 = cross_state(ser["sma50"], ser["sma200"])
    e21, e55 = ser["ema21"][-1], ser["ema55"][-1]
    pb = None
    if None not in (e21, e55, atr) and atr > 0:
        sl55 = _slope(ser["ema55"], atr)
        if e21 > e55 and sl55 == "up" and l <= e21 + TOUCH_ATR * atr and price >= e55:
            pb = "up"
        elif e21 < e55 and sl55 == "down" and h >= e21 - TOUCH_ATR * atr and price <= e55:
            pb = "down"
    band = None
    s20, e21v = ser["sma20"][-1], e21
    if s20 is not None and e21v is not None:
        lo, hi = min(s20, e21v), max(s20, e21v)
        band = "above" if price > hi else "below" if price < lo else "inside"
    return {"tf": tf, "bars": len(klines), "price": price, "atr": atr, "avgs": avgs,
            "cross2155": c2155, "cross50200": c50200, "pullback": pb, "band": band}


def ma_state(klines_by_tf):
    """One JSON-able row per timeframe in TFS order; a timeframe without readable klines is None."""
    return [ma_row(tf, klines_by_tf.get(tf)) for tf in TFS]


def fetch(tf, limit=1000):
    with urllib.request.urlopen("%s&interval=%s&limit=%d" % (BASE, tf, limit), timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


if __name__ == "__main__":
    data = {}
    for t in TFS:
        try:
            data[t] = fetch(t)
        except Exception as e:  # unreachable feed: that row is None, said on stderr
            print("fetch %s failed: %s" % (t, e), file=sys.stderr)
    for row in ma_state(data):
        print(json.dumps(row))
