"""F-BT-14 one-shot repair: fill the naked-POC list for the days the Java writer was missing (it had no writer after
2026-08-28), using the FIXED volume-profile rule (F-BT-09: per-bar weights normalised to the bar volume), then mark
every POC visited that a later 1m bar traded through.

Mirrors MarketDataSnapshot.buildVp (prior-day profile, 1m bars of one UTC day, numBins = max(50, int(range/5)),
triangular weight around hlc3, floorKey bins) and NakedPocTracker.recordPoc / markVisitedByBars.
Never overwrites a day the tracker already has. Atomic write (temp file + replace). Dry run unless --apply.
Usage: python scripts/dev/backfill_naked_pocs.py --klines Dumps/backtest/raw/klines --file runtime_data/naked_pocs/BTCUSDT_naked_pocs.json [--apply]
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def load_day(path):
    bars = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            bars.append((int(r["open_time"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r["volume"])))
    return bars


def day_poc(bars):
    """POC of one day's 1m bars, the fixed buildVp rule. Returns None for no bars."""
    if not bars:
        return None
    lo = min(b[2] for b in bars)
    hi = max(b[1] for b in bars)
    rng = hi - lo
    nb = max(50, int(rng / 5))
    bs = rng / nb if rng > 0 else 1.0
    keys = [lo + i * bs for i in range(nb + 1)]
    prof = dict.fromkeys(keys, 0.0)

    def floorkey(p):
        i = bisect.bisect_right(keys, p) - 1
        return keys[i] if i >= 0 else keys[0]

    for _t, h, l, c, v in bars:
        tp = (h + l + c) / 3.0
        half = (h - l) / 2.0
        n = int(max(1, (h - l) / bs))
        ps = [l + i * (h - l) / n for i in range(n)]
        ws = [max(1.0 - abs(p - tp) / half, 0.0) if half > 0 else 0.0 for p in ps]
        s = sum(ws)
        if s > 0:
            for p, w in zip(ps, ws):
                prof[floorkey(p)] += v * w / s
        else:
            prof[floorkey(tp)] += v
    best = max(prof.values())
    return next(k for k in keys if prof[k] == best)  # first max, as the Java stream max over a TreeMap


def backfill(entries, days, today):
    """entries: list of {date, poc, visited}; days: {date_str: bars}. Returns (new entries, added dates, newly visited dates)."""
    have = {e["date"] for e in entries}
    out = [dict(e) for e in entries]
    added = []
    for d in sorted(days):
        if d in have or d >= today:
            continue
        p = day_poc(days[d])
        if p and p > 0:
            out.append({"date": d, "poc": round(p, 2), "visited": False})
            added.append(d)
    out.sort(key=lambda e: e["date"])
    visited = []
    for e in out:
        if e["visited"] or e["date"] >= today:
            continue
        after = int((dt.datetime.fromisoformat(e["date"]) + dt.timedelta(days=1)).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        for d in sorted(days):
            if any(b[0] >= after and b[2] <= e["poc"] <= b[1] for b in days[d]):
                e["visited"] = True
                visited.append(e["date"])
                break
    return out, added, visited


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--from-date", default="2026-08-29")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    days = {}
    for p in sorted(Path(a.klines).glob("BTCUSDT-1m-*.csv")):
        d = p.stem.replace("BTCUSDT-1m-", "")
        if d >= a.from_date:
            days[d] = load_day(p)
    entries = json.load(open(a.file, encoding="utf-8")) if os.path.exists(a.file) else []
    out, added, visited = backfill(entries, days, today)
    print("days read %d, added %s, newly visited %s" % (len(days), added, visited))
    print("naked after: %s" % [e["date"] + ":" + str(e["poc"]) for e in out if not e["visited"]])
    if a.apply:
        tmp = a.file + ".tmp"
        with open(tmp, "w", newline="\n", encoding="utf-8") as fh:
            json.dump(out[-90:], fh, indent=2)
        os.replace(tmp, a.file)
        print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
