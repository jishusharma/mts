"""Fetch Binance SPOT 1d klines (public market data, data-api.binance.vision) for the 10 symbols into the ignored cache
runtime_data/wt-c30-10sym-1115/ (per-symbol daily trend gate needs 200 daily bars before 2024-01). 15m + BTC 1w/1M are copied from the
bb-retest-10sym-1115 cache (same fetch, 2023-10-01..2026-11-14 23:45)."""
import calendar, json, os, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "wt-c30-10sym-1115"))
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
API = "https://data-api.binance.vision/api/v3/klines"
END_MS = calendar.timegm((2026, 11, 15, 0, 0, 0)) * 1000
START = calendar.timegm((2022, 1, 1, 0, 0, 0)) * 1000


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(1 + 2 * k)
    raise RuntimeError(u)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for s in SYMS:
        rows, st = [], START
        while st < END_MS:
            lst = get("%s?symbol=%sUSDT&interval=1d&startTime=%d&endTime=%d&limit=1000" % (API, s, st, END_MS - 1))
            if not lst:
                break
            rows += [[int(r[0])] + [float(x) for x in r[1:6]] for r in lst]
            st = int(lst[-1][0]) + 1
            if len(lst) < 1000:
                break
        json.dump(rows, open(os.path.join(OUT, "%s_1d.json" % s), "w"))
        print(s, len(rows), flush=True)
