"""Fetch Bybit v5 public linear USDT klines (no key): 1h (60) and 4h (240) for 20 perps, 2020-01-01 on (or first listing).
Cache (git-ignored): runtime_data/edge4-malkan-r03-r04-1113/<COIN>_<iv>.json, rows [open_ms, o, h, l, c, v] ascending,
closed bars only, de-duplicated.   python fetch_klines.py
"""
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-malkan-r03-r04-1113"))
# Same 20 USDT perps as the sibling edge4_rsi_4h_le12 study (fixed before any outcome, OURS).
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
START_MS = 1577836800000  # 2020-01-01 UTC
IV_MS = {"60": 3600000, "240": 14400000}


def clean_bars(rows, iv_ms, now_ms):
    """Ascending, one row per open time (last seen wins), only bars closed by now_ms (open + iv_ms <= now_ms)."""
    by_t = {}
    for r in rows:
        by_t[int(r[0])] = r
    return [by_t[t] for t in sorted(by_t) if t + iv_ms <= now_ms]


def find_gaps(rows, iv_ms):
    """[(open_ms before gap, open_ms after gap)] wherever consecutive bars are not exactly one interval apart."""
    return [(a[0], b[0]) for a, b in zip(rows, rows[1:]) if b[0] - a[0] != iv_ms]


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0 and "list" in d.get("result", {}):
                return d
            time.sleep(2 + 3 * k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError(u)


def fetch(sym, iv):
    now = int(time.time() * 1000)
    end = now
    rows = []
    while end > START_MS:
        d = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, end))
        lst = d["result"]["list"]
        if not lst:
            break
        rows += [[int(r[0])] + [float(x) for x in r[1:6]] for r in lst]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.12)
    return [r for r in clean_bars(rows, IV_MS[iv], now) if r[0] >= START_MS]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        for iv in IV_MS:
            p = os.path.join(OUT, "%s_%s.json" % (c, iv))
            if os.path.exists(p):
                continue
            rows = fetch(c, iv)
            json.dump(rows, open(p, "w"))
            print(c, iv, len(rows), rows[0][0] if rows else None, "gaps", len(find_gaps(rows, IV_MS[iv])), flush=True)
