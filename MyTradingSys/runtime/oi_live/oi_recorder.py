"""D2 OI recorder (collection-only, public USD-M data, no keys, no orders).
  one-shot (scheduled every 60 s): append one row to oi_1m.csv  [ts_ms,iso_utc,symbol,openInterest,source]
     source = /fapi/v1/openInterest (live OI). Binance openInterestHist has no 1m period (min 5m), so the
     1-minute series is the live endpoint; the 5m hist is appended too when a new 5m bucket exists.
  --backfill: last 30 days of openInterestHist period=5m -> oi_5m_30d.csv [ts_ms,iso_utc,symbol,sumOpenInterest,sumOpenInterestValue]
Fail closed: any fetch error writes nothing and exits 1."""
import argparse, csv, json, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://fapi.binance.com"
SYMBOL = "BTCUSDT"
DIR = Path(__file__).resolve().parent
F1 = DIR / "oi_1m.csv"
F5 = DIR / "oi_5m_30d.csv"


def _get(path, params):
    with urllib.request.urlopen(BASE + path + "?" + urllib.parse.urlencode(params), timeout=15) as r:
        return json.loads(r.read())


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path, header, rows):
    new = not path.exists()
    with open(path, "a", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(header)
        w.writerows(rows)


def last_ts(path):
    if not path.exists():
        return 0
    last = 0
    with open(path) as f:
        for line in f:
            p = line.split(",", 1)[0]
            if p.isdigit():
                last = int(p)
    return last


def hist_rows(end_ms=None, start_ms=None, limit=500):
    p = {"symbol": SYMBOL, "period": "5m", "limit": limit}
    if end_ms: p["endTime"] = end_ms
    if start_ms: p["startTime"] = start_ms
    return _get("/futures/data/openInterestHist", p)


def to5(r):
    return [int(r["timestamp"]), iso(int(r["timestamp"])), r["symbol"], r["sumOpenInterest"], r["sumOpenInterestValue"]]


def backfill():
    now = int(time.time() * 1000)
    start = now - 30 * 86400 * 1000
    got = {}
    end = now
    while end > start:
        rows = hist_rows(end_ms=end)
        if not rows:
            break
        for r in rows:
            if int(r["timestamp"]) >= start:
                got[int(r["timestamp"])] = r
        oldest = min(int(r["timestamp"]) for r in rows)
        if oldest >= end:
            break
        end = oldest - 1
        time.sleep(0.3)
    out = [to5(got[k]) for k in sorted(got)]
    tmp = F5.with_suffix(".tmp")
    with open(tmp, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["ts_ms", "iso_utc", "symbol", "sumOpenInterest", "sumOpenInterestValue"])
        w.writerows(out)
    tmp.replace(F5)
    print("backfill rows", len(out))


def once():
    d = _get("/fapi/v1/openInterest", {"symbol": SYMBOL})
    append(F1, ["ts_ms", "iso_utc", "symbol", "openInterest", "source"],
           [[int(d["time"]), iso(int(d["time"])), d["symbol"], d["openInterest"], "fapi/v1/openInterest"]])
    if F5.exists():
        rows = [r for r in hist_rows(limit=3) if int(r["timestamp"]) > last_ts(F5)]
        if rows:
            append(F5, [], [to5(r) for r in sorted(rows, key=lambda r: int(r["timestamp"]))])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true")
    a = ap.parse_args()
    try:
        backfill() if a.backfill else once()
    except Exception as e:
        print("OI recorder error:", e, file=sys.stderr)
        sys.exit(1)
