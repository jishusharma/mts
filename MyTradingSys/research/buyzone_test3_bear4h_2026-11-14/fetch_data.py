"""Fetch Binance spot 4h klines (public, no key) and Bybit linear funding history (public, no key) into host caches
OUTSIDE the repo. Daily klines come from the Test 1 fetcher (buyzone_test1_ladder_2026-11-14/fetch_spot.py).
  python fetch_data.py
Cache root: $MTS_DATA_CACHE_ROOT or C:/Users/e-ngineers/MTS_data_cache. Never committed (repo is public).
"""
import json
import os
import time
import urllib.request

UNIVERSE = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM",
            "ETC", "XLM", "BCH", "NEO", "UNI", "NEAR", "FIL", "ALGO", "VET"]
ROOT = os.environ.get("MTS_DATA_CACHE_ROOT", "C:/Users/e-ngineers/MTS_data_cache")
D1 = os.path.join(ROOT, "binance_spot_1d")
H4 = os.path.join(ROOT, "binance_spot_4h")
FUND = os.path.join(ROOT, "bybit_funding")
KL = "https://data-api.binance.vision/api/v3/klines"
FR = "https://api.bybit.com/v5/market/funding/history"


def get(url):
    return json.load(urllib.request.urlopen(url, timeout=30))


def fetch_4h(sym):
    rows, start = [], 0
    while True:
        d = get("%s?symbol=%s&interval=4h&limit=1000&startTime=%d" % (KL, sym, start))
        if not d:
            break
        rows += [[int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in d]
        start = int(d[-1][0]) + 1
        if len(d) < 1000:
            break
        time.sleep(0.15)
    return rows


def fetch_funding(sym):
    """[[settlement_ts_ms, rate], ...] ascending. Empty list if the symbol has no Bybit linear history."""
    out, end = {}, int(time.time() * 1000)
    while True:
        d = get("%s?category=linear&symbol=%s&limit=200&endTime=%d" % (FR, sym, end))
        lst = d.get("result", {}).get("list", [])
        if not lst:
            break
        for r in lst:
            out[int(r["fundingRateTimestamp"])] = float(r["fundingRate"])
        nxt = min(int(r["fundingRateTimestamp"]) for r in lst) - 1
        if nxt >= end or len(lst) < 200:
            break
        end = nxt
        time.sleep(0.12)
    return sorted([k, v] for k, v in out.items())


if __name__ == "__main__":
    for d in (H4, FUND):
        os.makedirs(d, exist_ok=True)
    for c in UNIVERSE:
        r = fetch_4h(c + "USDT")
        json.dump(r, open(os.path.join(H4, c + "USDT.json"), "w"))
        f = fetch_funding(c + "USDT")
        json.dump(f, open(os.path.join(FUND, c + "USDT.json"), "w"))
        print(c, "4h bars", len(r), "funding rows", len(f), "first funding", f[0][0] if f else None)
