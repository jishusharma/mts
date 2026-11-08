"""Public Binance spot klines (data-api.binance.vision, no key) -> CSV t,o,h,l,c,v. Usage:
  python fetch_klines.py <interval> <start YYYY-MM-DD> <end_exclusive YYYY-MM-DD> <out.csv>
Seal rule (backtest/splits.py): counts run only on PRE_DEV+DEV (end <= 2024-07-01). The 2026 fixture is the operator-points
recall check only (logged in research/holdout_reads.csv); no performance is measured on it."""
import csv, json, sys, time, urllib.request, datetime as dt

URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=%s&limit=1000&startTime=%d&endTime=%d"


def ms(d):
    return int(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def fetch(interval, start, end):
    s, e, out = ms(start), ms(end) - 1, []
    while s < e:
        rows = json.load(urllib.request.urlopen(URL % (interval, s, e), timeout=30))
        if not rows:
            break
        out += [(int(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
        s = int(rows[-1][0]) + 1
        time.sleep(0.2)
    return out


if __name__ == "__main__":
    iv, a, b, path = sys.argv[1:5]
    rows = fetch(iv, a, b)
    with open(path, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["t", "o", "h", "l", "c", "v"])
        w.writerows(rows)
    print(path, len(rows), rows[0][0], rows[-1][0])
