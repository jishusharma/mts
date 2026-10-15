"""Fetch checksummed public daily/weekly history for the Krown studies (card krown-data-daily-majors).

Series (Binance spot, data.binance.vision monthly klines, each zip checked against its published .CHECKSUM):
  BTCUSDT 1d and 1w from 2017-08; ETHUSDT, BNBUSDT, SOLUSDT 1d from their listing month.
Coinbase BTC-USD daily candles from the public exchange API (no auth, 300 candles per page).

Output (never in git): <out>/<SYMBOL>_<interval>.csv, one merged, sorted, de-duplicated file per series, open_time in
milliseconds UTC. Committed instead: DATA_MANIFEST.csv (per source file: url, published SHA256, verified) and
DATA_COVERAGE.md (per series: first/last bar, count, gaps, SHA256 of the merged file).

Run: python MyTradingSys/research/krown_ta101_2026-10-13/tools/fetch_daily_majors.py --out F:/MTS/data/krown_daily
Only timestamps are inspected here (coverage and gaps); no price outcome is read.
DECISION (OURS): a dedicated script rather than adding --market spot to fetch_binance_archive.py, so the futures tool and its
default URL stay untouched.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

UA = {"User-Agent": "MTS-krown-data/1.0"}
BASE = "https://data.binance.vision/data/spot/monthly/klines"
COLS = ["open_time_ms", "open", "high", "low", "close", "volume", "close_time_ms", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote"]
SERIES = [("BTCUSDT", "1d", (2017, 8)), ("BTCUSDT", "1w", (2017, 8)), ("ETHUSDT", "1d", (2017, 8)),
          ("BNBUSDT", "1d", (2017, 11)), ("SOLUSDT", "1d", (2020, 8))]
STEP = {"1d": 86400_000, "1w": 7 * 86400_000}


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                raise SystemExit(f"HTTP 429 from {url}: stop, retry later")
        except Exception:
            pass
        time.sleep(2 ** i)
    raise SystemExit(f"giving up on {url}")


def months(start, end):
    y, m = start
    while (y, m) <= end:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def to_ms(v):
    v = int(v)
    return v // 1000 if v > 10 ** 14 else v  # spot archives switch to microseconds from 2025-01-01


def fetch_binance(sym, iv, first, last_month, manifest):
    rows = {}
    for y, m in months(first, last_month):
        stamp = f"{y}-{m:02d}"
        name = f"{sym}-{iv}-{stamp}.zip"
        url = f"{BASE}/{sym}/{iv}/{name}"
        chk = get(url + ".CHECKSUM")
        if chk is None:
            manifest.append([sym, iv, stamp, url, "", "", "MISSING_404"])
            continue
        want = chk.decode().split()[0].lower()
        z = get(url)
        have = hashlib.sha256(z).hexdigest()
        ok = have == want
        manifest.append([sym, iv, stamp, url, want, have, "OK" if ok else "CHECKSUM_MISMATCH"])
        if not ok:
            raise SystemExit(f"checksum mismatch {url}")
        with zipfile.ZipFile(io.BytesIO(z)) as zf:
            inner = zf.namelist()
            assert len(inner) == 1 and inner[0].endswith(".csv"), inner
            for line in zf.read(inner[0]).decode().splitlines():
                p = line.split(",")
                if not p or not p[0].isdigit():
                    continue
                t = to_ms(p[0])
                rows[t] = [t] + p[1:6] + [to_ms(p[6])] + p[7:11]
    return [rows[k] for k in sorted(rows)]


def fetch_coinbase(manifest):
    """Daily candles, newest first per page: [time_s, low, high, open, close, volume]."""
    rows = {}
    start = datetime(2015, 7, 20, tzinfo=timezone.utc)
    end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    cur = start
    while cur < end:
        nxt = min(cur.timestamp() + 299 * 86400, end.timestamp())
        url = ("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400"
               f"&start={datetime.fromtimestamp(cur.timestamp(), timezone.utc):%Y-%m-%dT%H:%M:%SZ}"
               f"&end={datetime.fromtimestamp(nxt, timezone.utc):%Y-%m-%dT%H:%M:%SZ}")
        body = get(url)
        if body is None:
            raise SystemExit("coinbase 404")
        data = json.loads(body)
        manifest.append(["BTC-USD", "1d", f"{cur:%Y-%m-%d}", url, "", hashlib.sha256(body).hexdigest(),
                         f"API_PAGE_{len(data)}"])
        for t, lo, hi, op, cl, vol in data:
            rows[int(t) * 1000] = [int(t) * 1000, op, hi, lo, cl, vol, int(t) * 1000 + 86400_000 - 1, "", "", "", ""]
        cur = datetime.fromtimestamp(nxt, timezone.utc)
        time.sleep(0.5)
    return [rows[k] for k in sorted(rows)]


def write_series(path, rows):
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        w.writerows(rows)
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coverage(rows, step):
    ts = [r[0] for r in rows]
    gaps = [(ts[i - 1], ts[i]) for i in range(1, len(ts)) if ts[i] - ts[i - 1] != step]
    return ts[0], ts[-1], len(ts), gaps


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--last-month", default="2026-09")
    ap.add_argument("--doc-dir", default=str(Path(__file__).resolve().parents[1]))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ly, lm = map(int, a.last_month.split("-"))
    manifest, cov = [], []
    for sym, iv, first in SERIES:
        rows = fetch_binance(sym, iv, first, (ly, lm), manifest)
        path = out / f"{sym}_{iv}.csv"
        sha = write_series(path, rows)
        f, l, n, gaps = coverage(rows, STEP[iv])
        cov.append([f"Binance spot {sym}", iv, iso(f), iso(l), n, len(gaps), gaps[:5], sha, str(path)])
        print(sym, iv, n, "bars", iso(f), iso(l), "gaps", len(gaps), flush=True)
    rows = fetch_coinbase(manifest)
    path = out / "COINBASE_BTC-USD_1d.csv"
    sha = write_series(path, rows)
    f, l, n, gaps = coverage(rows, STEP["1d"])
    cov.append(["Coinbase BTC-USD", "1d", iso(f), iso(l), n, len(gaps), gaps[:5], sha, str(path)])
    print("coinbase", n, "bars", iso(f), iso(l), "gaps", len(gaps), flush=True)
    doc = Path(a.doc_dir)
    with open(doc / "DATA_MANIFEST.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["series", "interval", "period", "url", "published_sha256", "computed_sha256", "status"])
        w.writerows(manifest)
    json.dump(cov, open(Path(a.out) / "coverage.json", "w"), indent=1)
    print("manifest rows", len(manifest))


if __name__ == "__main__":
    sys.exit(main())
