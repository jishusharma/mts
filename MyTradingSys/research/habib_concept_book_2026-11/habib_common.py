"""Shared helpers for the Habib concept book (2026-11): Binance public klines, relative volume, body class, prior-day levels.

Public market data only (data-api.binance.vision; api.binance.com is not reachable from every host). No keys, no orders.
All thresholds are OURS unless a comment says SOURCED (see HABIB_CONCEPT_BOOK.md section 6).
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

sys.dont_write_bytecode = True
BASE = "https://data-api.binance.vision/api/v3/klines"
TF_MS = {"1m": 60_000, "30m": 1_800_000, "1h": 3_600_000, "4h": 14_400_000, "12h": 43_200_000, "1d": 86_400_000}
DAY = 86_400_000

# ---- OURS thresholds (Habib's own number is not public: imbalance_qriptal_2026-10-16/README.md:39)
VOL_LOOKBACK = 50      # OURS: median of the prior 50 bars of the same timeframe (imb.py, same convention)
REL_VOL_K = 2.0        # OURS: "volume anomaly" = volume >= 2.0 x that median
SMALL_BODY = 0.30      # OURS: body <= 30 % of range = small (trapped traders)
LARGE_BODY = 0.70      # OURS: body >= 70 % of range = large (strength, never fade)
WICKLESS = 0.05        # OURS: a side wick <= 5 % of range = wickless
TOL_RANGE = 0.004      # OURS (imb.py TOL_RANGE): level inside candle range +-0.4 %
TOL_MID = 0.0025       # OURS (imb.py TOL_MID): level equals open or midpoint +-0.25 %


def utc(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def ms_of(dt):
    return int(dt.timestamp() * 1000)


def fetch_klines(interval, start_ms, end_ms, symbol="BTCUSDT", retries=4):
    """All klines with open time in [start_ms, end_ms). Rows: [open_ms, o, h, l, c, v] as floats."""
    out, cur = [], start_ms
    while cur < end_ms:
        url = f"{BASE}?symbol={symbol}&interval={interval}&startTime={cur}&endTime={end_ms - 1}&limit=1000"
        for a in range(retries):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    rows = json.loads(r.read())
                break
            except Exception:
                if a == retries - 1:
                    raise
                time.sleep(1.5 * (a + 1))
        if not rows:
            break
        for k in rows:
            out.append([int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])])
        nxt = int(rows[-1][0]) + TF_MS[interval]
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.05)
    return [r for r in out if start_ms <= r[0] < end_ms]


def rel_volume(rows, n=VOL_LOOKBACK):
    """v[i] / median(v[i-n..i-1]); None until n prior bars exist."""
    out = []
    for i, r in enumerate(rows):
        if i < n:
            out.append(None)
            continue
        w = sorted(x[5] for x in rows[i - n:i])
        med = (w[n // 2 - 1] + w[n // 2]) / 2 if n % 2 == 0 else w[n // 2]
        out.append(r[5] / med if med > 0 else None)
    return out


def body_frac(r):
    rng = r[2] - r[3]
    return abs(r[4] - r[1]) / rng if rng > 0 else None


def body_class(r):
    b = body_frac(r)
    if b is None:
        return "flat"
    return "small" if b <= SMALL_BODY else "large" if b >= LARGE_BODY else "mid"


def wicks(r):
    """(upper, lower) wick as a fraction of range."""
    rng = r[2] - r[3]
    if rng <= 0:
        return (0.0, 0.0)
    return ((r[2] - max(r[1], r[4])) / rng, (min(r[1], r[4]) - r[3]) / rng)


def wick_label(r):
    u, l = wicks(r)
    if u <= WICKLESS and l <= WICKLESS:
        return "wickless"
    if u <= WICKLESS:
        return "wickless-top"
    if l <= WICKLESS:
        return "wickless-bottom"
    return "wick-both"


def value_area(bars1m, bin_=50.0, share=0.7):
    """Port of tf_strip.js valueArea (typical price (h+l+c)/3 into 50 USD bins, 70 %). -> dict(val, vah, poc) or None."""
    b, tot = {}, 0.0
    for k in bars1m:
        h, l, c, v = k[2], k[3], k[4], k[5]
        if v <= 0:
            continue
        i = int(((h + l + c) / 3) // bin_)
        b[i] = b.get(i, 0.0) + v
        tot += v
    if not b:
        return None
    keys = list(b)
    poc = keys[0]
    for i in keys:
        if b[i] > b[poc] or (b[i] == b[poc] and i < poc):
            poc = i
    lo = hi = poc
    acc = b[poc]
    mn, mx = min(keys), max(keys)
    while acc < share * tot and (lo > mn or hi < mx):
        up = b.get(hi + 1, 0.0) if hi < mx else -1
        dn = b.get(lo - 1, 0.0) if lo > mn else -1
        if up >= dn:
            hi += 1
            acc += max(up, 0)
        else:
            lo -= 1
            acc += max(dn, 0)
    return {"val": lo * bin_, "vah": (hi + 1) * bin_, "poc": poc * bin_}


def prior_day_levels(bars1m, now_ms):
    """Port of tf_strip.js levels() prior-day part: needs >= 1380 one-minute bars in the prior UTC day (fail closed)."""
    d0 = now_ms - (now_ms % DAY)
    p0 = d0 - DAY
    prior = [k for k in bars1m if p0 <= k[0] < d0]
    if len(prior) < 1380:
        return {}
    va = value_area(prior)
    out = {"Prior day high": max(k[2] for k in prior), "Prior day low": min(k[3] for k in prior),
           "Prior day close": prior[-1][4]}
    if va:
        out.update({"Prior VAH": va["vah"], "Prior VAL": va["val"], "Prior POC": va["poc"]})
    return out


def week_month_levels(bars1m, now_ms):
    """Weekly open (Mon 00:00Z), prior-week high/low, monthly open. From 1m bars; absent when the bar is missing."""
    t = utc(now_ms)
    mon = ms_of(t.replace(hour=0, minute=0, second=0, microsecond=0)) - t.weekday() * DAY
    out = {}
    m0 = ms_of(t.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    first = {k[0]: k for k in bars1m}
    if mon in first:
        out["Weekly open"] = first[mon][1]
    if m0 in first:
        out["Monthly open"] = first[m0][1]
    pw = [k for k in bars1m if mon - 7 * DAY <= k[0] < mon]
    if len(pw) >= 7 * 1440 - 60:
        out["Prior week high"] = max(k[2] for k in pw)
        out["Prior week low"] = min(k[3] for k in pw)
    return out


def nearest_level(price, levels, tol=0.003):
    """Closest named level within tol (fraction of price) -> (name, level, pct_distance) or None."""
    best = None
    for n, v in levels.items():
        d = abs(v - price) / price
        if d <= tol and (best is None or d < best[2]):
            best = (n, v, d)
    return best


def imbalance_flags(rows, k=REL_VOL_K):
    """Per candle: dict(rv, body, bclass, wick) for candles with rel volume >= k, else None."""
    rv = rel_volume(rows)
    out = []
    for r, x in zip(rows, rv):
        if x is not None and x >= k:
            out.append({"rv": x, "body": body_frac(r), "bclass": body_class(r), "wick": wick_label(r)})
        else:
            out.append(None)
    return out
