"""Fetch Binance SPOT 4h and 1d klines (public market data, data-api.binance.vision) for 10 symbols, 2021-12-01 .. 2026-11-14 23:59 UTC,
into the ignored cache runtime_data/reclaim-10sym-1115/. 2021-12 is indicator warm-up only; trades only from 2024-01-01 (see PRE_REG.md)."""
import calendar
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "reclaim-10sym-1115"))
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
API = "https://data-api.binance.vision/api/v3/klines"
END_MS = int(calendar.timegm((2026, 11, 15, 0, 0, 0)) * 1000)  # exclusive
START_MS = int(calendar.timegm((2021, 12, 1, 0, 0, 0)) * 1000)


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(1 + 2 * k)
    raise RuntimeError(u)


def fetch(sym, iv, start0=START_MS):
    p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
    if os.path.exists(p):
        return sym, iv, -1
    rows, start = [], start0
    while start < END_MS:
        lst = get("%s?symbol=%sUSDT&interval=%s&startTime=%d&endTime=%d&limit=1000" % (API, sym, iv, start, END_MS - 1))
        if not lst:
            break
        rows += [[int(r[0])] + [float(x) for x in r[1:6]] for r in lst]
        start = int(lst[-1][0]) + 1
        if len(lst) < 1000:
            break
    json.dump(rows, open(p, "w"))
    return sym, iv, len(rows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    jobs = [(s, iv, START_MS) for s in SYMS for iv in ("4h", "1d")] + [("BTC", "1w", 0), ("BTC", "1M", 0)]
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(lambda a: fetch(*a), jobs):
            print(*r, flush=True)
