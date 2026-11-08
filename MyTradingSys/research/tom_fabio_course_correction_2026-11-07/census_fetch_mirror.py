"""Fetch BTCUSDT 5m klines from data.binance.vision (public mirror) into per-month .npy-free JSON rows.

Source order: futures/um monthly (2020-01 on; the mirror has no earlier um 5m monthly file, probed 2026-11-09),
spot monthly for 2019-01..2019-12 (warm-up for the weekly/monthly ladder + first window months). Current month: futures/um daily files.
Row = [t_ms, o, h, l, c, v, taker_buy_v]; delta is derived downstream as 2*taker_buy_v - v (taker buy minus taker sell).
Usage: python census_fetch_mirror.py <cache_dir> [last_day YYYY-MM-DD]
"""
import csv, datetime as dt, io, json, sys, urllib.request, zipfile
from pathlib import Path

BASE = "https://data.binance.vision/data"


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mts-census"}), timeout=60) as r:
            return r.read()
    except Exception:
        return None


def parse(z):
    rows = []
    with zipfile.ZipFile(io.BytesIO(z)) as zf:
        for name in zf.namelist():
            for r in csv.reader(io.TextIOWrapper(zf.open(name))):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t > 10 ** 14:  # microseconds (spot files from 2025)
                    t //= 1000
                rows.append([t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])])
    return rows


def main(cache, last_day):
    cache = Path(cache); cache.mkdir(parents=True, exist_ok=True)
    last = dt.date.fromisoformat(last_day)
    y, m = 2019, 1
    while (y, m) <= (last.year, last.month):
        out = cache / f"{y}-{m:02d}.json"
        if not out.exists():
            ym = f"{y}-{m:02d}"
            src, z = None, None
            if y >= 2020:
                z = get(f"{BASE}/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-{ym}.zip"); src = "um"
            if z is None and (y, m) < (last.year, last.month):
                z = get(f"{BASE}/spot/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-{ym}.zip"); src = "spot"
            rows = parse(z) if z else []
            if z is None:  # current month: daily um files
                src = "um-daily"
                d = dt.date(y, m, 1)
                while d.month == m and d <= last:
                    z = get(f"{BASE}/futures/um/daily/klines/BTCUSDT/5m/BTCUSDT-5m-{d.isoformat()}.zip")
                    if z: rows += parse(z)
                    d += dt.timedelta(days=1)
            json.dump({"src": src, "rows": rows}, open(out, "w"))
            print(ym, src, len(rows), flush=True)
        m += 1
        if m == 13: y, m = y + 1, 1


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "2026-11-08")
