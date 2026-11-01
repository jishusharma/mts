"""Fill <cache>/btc1m_recent.json: Binance SPOT BTCUSDT 1m klines as [open_ms, o, h, l, c, volume, taker_buy_base] from
data.binance.vision daily zips (public, no key) plus the REST API for the current UTC day. Public market data, never committed.
Usage: python fetch_1m.py <cache> [--from 2026-06-21]
"""
import io, json, os, sys, urllib.request, zipfile
from datetime import date, datetime, timedelta, timezone

CACHE = sys.argv[1]
FROM = date.fromisoformat(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else date(2026, 6, 21)
OUT = os.path.join(CACHE, "btc1m_recent.json")


def row(r):
    t = int(r[0])
    return [t // 1000 if t > 10 ** 14 else t,  # vision spot files stamp microseconds since 2025; the API stamps ms
            float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])]


def day(d):
    u = "https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1m/BTCUSDT-1m-%s.zip" % d.isoformat()
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(u, timeout=60).read()))
    txt = z.read(z.namelist()[0]).decode("utf-8")
    return [row(l.split(",")) for l in txt.splitlines() if l and not l.startswith("open_time")]


def today(d0):
    out, start = [], int(datetime(d0.year, d0.month, d0.day, tzinfo=timezone.utc).timestamp() * 1000)
    while True:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime=%d" % start
        rows = json.load(urllib.request.urlopen(u, timeout=60))
        if not rows:
            break
        out += [row(r) for r in rows]
        if len(rows) < 1000:
            break
        start = rows[-1][0] + 60000
    return out


def main():
    rows, d, last = [], FROM, datetime.now(timezone.utc).date()
    while d < last:
        try:
            rows += day(d)
        except Exception as e:  # a missing day is reported, not silently skipped
            print("missing", d, e)
        d += timedelta(days=1)
    rows += today(last)
    rows = [r for r in rows if r[0] + 60000 <= int(datetime.now(timezone.utc).timestamp() * 1000)]  # closed bars only
    json.dump(rows, open(OUT, "w", encoding="utf-8", newline="\n"))
    print("wrote %d rows %s .. %s" % (len(rows), datetime.fromtimestamp(rows[0][0] / 1000, timezone.utc),
                                      datetime.fromtimestamp(rows[-1][0] / 1000, timezone.utc)))


if __name__ == "__main__":
    main()
