"""Fetch Bybit v5 public 1h linear klines + funding history for the pool; cache under runtime_data/<slug>/ (ignored)."""
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "runtime_data", "edge-extreme-confirm-template-1113")
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX"]
START_MS = 1577836800000  # 2020-01-01
HOUR = 3600000


def get(url):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mts-research"}), timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0:
                return d["result"]["list"]
        except Exception:
            pass
        time.sleep(1 + k)
    raise RuntimeError(url)


def klines(sym):
    rows, end = {}, int(time.time() * 1000)
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%sUSDT&interval=60&limit=1000&end=%d" % (sym, end))
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.05)
    return [rows[k] for k in sorted(rows) if k >= START_MS]


def funding(sym):
    rows, end = {}, int(time.time() * 1000)
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%sUSDT&limit=200&endTime=%d" % (sym, end))
        if not lst:
            break
        for r in lst:
            rows[int(r["fundingRateTimestamp"])] = float(r["fundingRate"])
        old = min(int(r["fundingRateTimestamp"]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.05)
    return [[k, rows[k]] for k in sorted(rows) if k >= START_MS]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        p = os.path.join(OUT, c + "_1h.json")
        if not os.path.exists(p):
            json.dump(klines(c), open(p, "w"))
        p2 = os.path.join(OUT, c + "_fund.json")
        if not os.path.exists(p2):
            json.dump(funding(c), open(p2, "w"))
        k = json.load(open(p))
        print(c, len(k), k[0][0] if k else None, len(json.load(open(p2))), flush=True)
