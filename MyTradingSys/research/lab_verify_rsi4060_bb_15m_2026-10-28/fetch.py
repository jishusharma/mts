"""Fetch BTCUSDT 15m klines from data-api.binance.vision (public market data, pre-approved), paginate
backward ~365 days, write to klines_15m.csv in this folder. SOURCED data (Binance spot).
"""
import csv
import json
import os
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "klines_15m.csv")
INTERVAL_MS = 15 * 60 * 1000
DAYS = 400
LIMIT = 1000


def get(url, tries=3):
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5)


def main():
    end_ms = None
    all_rows = {}
    target_start = None
    n_calls = 0
    while True:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit={LIMIT}"
        if end_ms is not None:
            url += f"&endTime={end_ms}"
        rows = get(url)
        n_calls += 1
        if not rows:
            break
        for r in rows:
            all_rows[r[0]] = r
        oldest = rows[0][0]
        if target_start is None:
            # first call: now we know "now"; set target_start = now - DAYS
            newest = rows[-1][0]
            target_start = newest - DAYS * 86_400_000
        end_ms = oldest - 1
        if oldest <= target_start or len(rows) < LIMIT:
            break
        time.sleep(0.15)
    ts = sorted(all_rows)
    with open(OUT, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["open_time_ms", "open", "high", "low", "close", "volume"])
        for t in ts:
            r = all_rows[t]
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5]])
    print(f"calls={n_calls} rows={len(ts)} first={ts[0]} last={ts[-1]}")


if __name__ == "__main__":
    main()
