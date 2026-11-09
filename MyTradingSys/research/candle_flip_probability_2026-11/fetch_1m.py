"""Fetch BTCUSDT 1m spot klines (public data-api.binance.vision) 2024-01-01T00:00Z -> now into btcusdt_1m.csv.gz.
Columns: open_time_ms,open,high,low,close,volume. Closed bars only. 8 parallel requests, 1000 bars each."""
import csv, gzip, json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT = Path(__file__).resolve().parent / "klines_1m_cache.csv.gz"
START = 1704067200000  # 2024-01-01T00:00Z
URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime=%d"


def get(t):
    for i in range(8):
        try:
            with urllib.request.urlopen(URL % t, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(1 + i)
    raise SystemExit("fetch failed at %d" % t)


def main():
    now = int(time.time() * 1000)
    starts = list(range(START, now - 60000, 60000 * 1000))
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for n, r in enumerate(ex.map(get, starts)):
            rows.extend((k[0], k[1], k[2], k[3], k[4], k[5]) for k in r if k[6] < now)
            if n % 100 == 0:
                print(n, len(starts), len(rows), flush=True)
    rows.sort()
    assert len({r[0] for r in rows}) == len(rows)
    with gzip.open(OUT, "wt", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["open_time_ms", "open", "high", "low", "close", "volume"])
        w.writerows(rows)
    print("rows", len(rows), "first", rows[0][0], "last", rows[-1][0])


if __name__ == "__main__":
    main()
