"""Fetch public Binance spot klines (4h, 1d, 3d, 1w) for the 20-coin universe into a local cache OUTSIDE the repo.
Public market data only. Output: <CACHE>/<SYM>_<tf>.npy (cols: open_time_ms, o, h, l, c, v). Never commit the cache."""
import json
import os
import sys
import time
import urllib.request

import numpy as np

CACHE = os.environ.get("BZ2_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test2")
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "LTC", "TRX", "LINK", "XLM", "DOGE",
         "ETC", "DASH", "ZEC", "NEO", "IOTA", "VET", "ATOM", "EOS", "BCH", "QTUM"]
TFS = ["4h", "1d", "3d", "1w"]
START = int(np.datetime64("2017-08-01", "ms").astype("int64"))
BASES = ["https://api.binance.com", "https://data-api.binance.vision"]


def get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(1 + i)
    raise RuntimeError(url)


def fetch(sym, tf):
    out, t = [], START
    while True:
        rows = get(f"{BASES[0]}/api/v3/klines?symbol={sym}&interval={tf}&startTime={t}&limit=1000")
        if not rows:
            break
        out += [[r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in rows]
        t = rows[-1][0] + 1
        if len(rows) < 1000:
            break
    return np.array(out)


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    for c in COINS:
        for tf in TFS:
            p = f"{CACHE}/{c}USDT_{tf}.npy"
            if os.path.exists(p):
                continue
            a = fetch(c + "USDT", tf)
            np.save(p, a)
            print(c, tf, len(a), np.datetime64(int(a[0, 0]), "ms") if len(a) else "-", flush=True)
