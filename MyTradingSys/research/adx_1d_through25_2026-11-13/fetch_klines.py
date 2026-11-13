"""Fetch daily USDT-linear klines from Bybit public API (no key). Output is ignored by git (MyTradingSys/market_data/klines/*.json).
  python fetch_klines.py BTCUSDT ETHUSDT ...      rows [start_ms, o, h, l, c, v], ascending, one file per symbol
"""
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "market_data", "klines")


def fetch(sym):
    rows, end = {}, None
    while True:
        url = "https://api.bybit.com/v5/market/kline?category=linear&symbol=%s&interval=D&limit=1000" % sym
        if end:
            url += "&end=%d" % end
        d = json.load(urllib.request.urlopen(url, timeout=30))["result"]["list"]
        if not d:
            break
        for r in d:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        nxt = min(int(r[0]) for r in d) - 1
        if end is not None and nxt >= end:
            break
        end = nxt
        if len(d) < 1000:
            break
        time.sleep(0.2)
    return [rows[k] for k in sorted(rows)]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for s in sys.argv[1:]:
        r = fetch(s)
        json.dump(r, open(os.path.join(OUT, "%s_1d_bybit.json" % s), "w"))
        import datetime
        print(s, len(r), datetime.datetime.utcfromtimestamp(r[0][0] / 1000).date(), datetime.datetime.utcfromtimestamp(r[-1][0] / 1000).date())
