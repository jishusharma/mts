"""Fetch Binance spot daily klines (public, no key) into a host cache OUTSIDE the repo.
  python fetch_spot.py            fetches the PRE_REG universe
Cache dir: $MTS_DATA_CACHE or C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d. Never committed.
"""
import json
import os
import sys
import time
import urllib.request

UNIVERSE = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM",
            "ETC", "XLM", "BCH", "NEO", "UNI", "NEAR", "FIL", "ALGO", "VET"]
CACHE = os.environ.get("MTS_DATA_CACHE", "C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d")
BASE = "https://data-api.binance.vision/api/v3/klines"


def fetch(sym):
    rows, start = [], 0
    while True:
        url = "%s?symbol=%s&interval=1d&limit=1000&startTime=%d" % (BASE, sym, start)
        d = json.load(urllib.request.urlopen(url, timeout=30))
        if not d:
            break
        rows += [[int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in d]
        start = int(d[-1][0]) + 1
        if len(d) < 1000:
            break
        time.sleep(0.15)
    return rows


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    for c in UNIVERSE:
        r = fetch(c + "USDT")
        json.dump(r, open(os.path.join(CACHE, c + "USDT.json"), "w"))
        print(c, len(r))
