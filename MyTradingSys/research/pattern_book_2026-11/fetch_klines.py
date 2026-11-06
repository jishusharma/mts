"""Fetch public BTCUSDT klines (spot) from data-api.binance.vision into data/BTCUSDT_<tf>.csv.

api.binance.com is unreachable from the desktop; data-api.binance.vision is the public mirror (market data only, no keys).
Usage: python fetch_klines.py            (defaults: 1h 2000 bars, 4h 2000 bars, 1d and 1w from 2017-08-17)
Columns: t (open time ms), o, h, l, c, v. The last row is the forming bar and is dropped (closed bars only).
"""
import csv
import json
import pathlib
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={tf}&limit=1000&endTime={end}"
START_MS = 1502928000000  # 2017-08-17 00:00 UTC (first Binance BTCUSDT bar)
PLAN = {"1h": 2000, "4h": 2000, "1d": None, "1w": None}  # None = back to START_MS


def get(tf, end_ms):
    req = urllib.request.Request(URL.format(tf=tf, end=end_ms), headers={"User-Agent": "mts-pattern-book"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def fetch(tf, want):
    rows, end = {}, int(time.time() * 1000)
    while True:
        page = get(tf, end)
        if not page:
            break
        for k in page:
            rows[int(k[0])] = [int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])]
        end = int(page[0][0]) - 1
        if (want and len(rows) >= want) or int(page[0][0]) <= START_MS or len(page) < 1000:
            break
    out = [rows[t] for t in sorted(rows)][:-1]  # drop the forming bar
    return out[-want:] if want else out


def main():
    DATA.mkdir(exist_ok=True)
    for tf, want in PLAN.items():
        rows = fetch(tf, want)
        with open(DATA / f"BTCUSDT_{tf}.csv", "w", newline="\n", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["t", "o", "h", "l", "c", "v"])
            w.writerows(rows)
        print(tf, len(rows), rows[0][0], rows[-1][0])


if __name__ == "__main__":
    sys.exit(main())
