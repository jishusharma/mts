"""Fetch Binance SPOT klines (public market data, data-api.binance.vision) into the ignored cache runtime_data/bb-retest-10sym-1115/.
15m for the 10 symbols from 2023-10-01 (warm-up for BB/ATR/session history) to 2026-11-14 23:59 UTC; 1d/1w/1M of BTCUSDT from listing (regime context)."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "bb-retest-10sym-1115"))
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
API = "https://data-api.binance.vision/api/v3/klines"
END_MS = 1763164800000  # 2025-11-15 00:00 UTC placeholder replaced below
END_MS = int(__import__("calendar").timegm((2026, 11, 15, 0, 0, 0)) * 1000)   # exclusive: last bar 2026-11-14 23:45
START_15M = int(__import__("calendar").timegm((2023, 10, 1, 0, 0, 0)) * 1000)


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(1 + 2 * k)
    raise RuntimeError(u)


def fetch(sym, iv, start):
    p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
    if os.path.exists(p):
        return sym, iv, -1
    rows = []
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
    jobs = [(s, "15m", START_15M) for s in SYMS] + [("BTC", iv, 0) for iv in ("1d", "1w", "1M")]
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(lambda a: fetch(*a), jobs):
            print(*r, flush=True)
