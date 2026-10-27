"""Noise units for the Tom v2 stop-width transfer rule (TOM_LAYER_V2_SPEC.md part B, section 11).

Reads 1m klines only (prices, no trade, no outcome). Window = the DAX dev window of HOLDOUT_CLEAN.json with its
dropped days removed; nothing from the DAX holdout (2026-04-11 on) is opened. BTC uses the same calendar window.

Noise unit N(tf) = median true range (FORMULAS.md section 12) of tf-minute bars, as a fraction of the bar's close.
A tf bar is kept only if all its 1m bars exist (no gap inside, previous bar adjacent).

  python -I scripts/dev/tom_noise_units.py --dax F:/MTS/data/dax_archive/klines --btc <klines_dir> \
      --split MyTradingSys/research/tom_transfer_2026-10-11/HOLDOUT_CLEAN.json
"""
import sys
sys.dont_write_bytecode = True
import argparse
import csv
import glob
import json
import os
from datetime import datetime, timezone, date, timedelta
from statistics import median
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")
TFS = (1, 5, 15, 60)


def true_ranges(bars):
    """bars: list of (high, low, close) in time order, all adjacent. TR per FORMULAS.md 12, i >= 1, as fraction of close."""
    out = []
    for i in range(1, len(bars)):
        h, l, c = bars[i]
        pc = bars[i - 1][2]
        out.append(max(h - l, abs(h - pc), abs(l - pc)) / c)
    return out


def aggregate(rows, tf):
    """rows: dict minute_ts_ms -> (o, h, l, c). Returns list of (bucket_ms, h, l, c) for complete tf-minute buckets."""
    step = tf * 60000
    buckets = {}
    for ts, (o, h, l, c) in rows.items():
        b = ts - ts % step
        cur = buckets.get(b)
        if cur is None:
            buckets[b] = [1, h, l, c, ts]
        else:
            cur[0] += 1
            cur[1] = max(cur[1], h)
            cur[2] = min(cur[2], l)
            if ts > cur[4]:
                cur[3], cur[4] = c, ts
    return [(b, v[1], v[2], v[3]) for b, v in sorted(buckets.items()) if v[0] == tf]


def tr_fracs(agg, tf, keep):
    """True range fractions for buckets whose previous bucket is adjacent and keep(bucket_ms) is true."""
    step = tf * 60000
    out = []
    for i in range(1, len(agg)):
        b, h, l, c = agg[i]
        pb, _, _, pc = agg[i - 1]
        if b - pb != step or not keep(b):
            continue
        out.append(max(h - l, abs(h - pc), abs(l - pc)) / c)
    return out


def min_stop_width(entry, n5, fees):
    """Minimum stop width gate for BTC replays (TOM_LAYER_V2_SPEC.md section 11.4).

    W_noise = 0.88 x N5 (SOURCED 0.88, TOM_LAYER_V2_SPEC.md 11.4; his 20-point stop, k0zm5NYn0IQ:22-24)
    W_fee = round-turn fee fraction / 0.25 (SOURCED 0.25 R, PROJECT_VISION.md:234)
    W_min = max(W_noise, W_fee) * entry
    """
    fee_rt = (fees["entry"] + fees["stop"]) if isinstance(fees, dict) else float(fees)
    return max(0.88 * n5, fee_rt / 0.25) * entry


def n5(bars, asof=None, days=20):
    """Noise unit N5: median true range (FORMULAS.md section 12) of completed 5-minute bars
    of the trailing 20 UTC days as a fraction of close (TOM_LAYER_V2_SPEC.md section 11.4).
    Reuses true_ranges and aggregate. Timestamp cutoffs are instants: open+5m must
    be <= asof. A date includes that whole UTC day (cutoff = next midnight).
    """
    if isinstance(bars, list) and bars and len(bars[0]) == 3 and not hasattr(bars[0], "keys"):
        # Direct list of (high, low, close)
        if asof is not None:
            raise ValueError("asof requires timestamped bars")
        trs = true_ranges(bars)
        return median(trs) if trs else 0.0

    if asof is not None:
        if isinstance(asof, str):
            asof = date.fromisoformat(asof)
        if isinstance(asof, date) and not isinstance(asof, datetime):
            start_d = asof - timedelta(days=days - 1)
            lo_ms = int(datetime(start_d.year, start_d.month, start_d.day, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
            end_d = asof + timedelta(days=1)
            hi_ms = int(datetime(end_d.year, end_d.month, end_d.day, tzinfo=timezone.utc).timestamp() * 1000)
        else:
            if isinstance(asof, datetime):
                if asof.tzinfo is None or asof.utcoffset() is None:
                    raise ValueError("asof datetime requires an explicit timezone")
                hi_ms = int(asof.timestamp() * 1000)
            else:
                hi_ms = int(asof * 1000) if asof < 1e11 else int(asof)
            lo_ms = hi_ms - days * 86400 * 1000

        if isinstance(bars, dict):
            rows = {ts: val for ts, val in bars.items() if lo_ms <= ts < hi_ms}
        elif hasattr(bars, "idx") and hasattr(bars, "t0") and hasattr(bars, "o"):
            i_start = max(0, bars.idx(lo_ms))
            i_end = min(bars.n, bars.idx(hi_ms) + 1)
            rows = {bars.t0 + i * 60000: (bars.o[i], bars.h[i], bars.l[i], bars.c[i]) for i in range(i_start, i_end)
                    if lo_ms <= bars.t0 + i * 60000 < hi_ms}
        else:
            rows = {ts: val for ts, val in dict(bars).items() if lo_ms <= ts < hi_ms}
    else:
        if isinstance(bars, dict):
            rows = bars
        elif hasattr(bars, "idx") and hasattr(bars, "t0") and hasattr(bars, "o"):
            rows = {bars.t0 + i * 60000: (bars.o[i], bars.h[i], bars.l[i], bars.c[i]) for i in range(bars.n)}
        else:
            rows = dict(bars)

    agg = aggregate(rows, 5)
    step = 5 * 60000
    if asof is not None:
        agg = [bar for bar in agg if bar[0] + step <= hi_ms]
    trs = []
    chunk = []
    for i in range(len(agg)):
        if chunk and agg[i][0] - agg[i - 1][0] != step:
            if len(chunk) > 1:
                trs.extend(true_ranges(chunk))
            chunk = []
        chunk.append((agg[i][1], agg[i][2], agg[i][3]))
    if len(chunk) > 1:
        trs.extend(true_ranges(chunk))
    return median(trs) if trs else 0.0


def load(klines_dir, start, end, dropped):
    rows = {}
    lo = datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp() * 1000
    hi = datetime(end.year, end.month, end.day, 23, 59, tzinfo=timezone.utc).timestamp() * 1000
    for path in sorted(glob.glob(os.path.join(klines_dir, "*-1m-*.csv"))):
        ym = os.path.basename(path).split("-1m-")[1][:7]
        if not (start.strftime("%Y-%m") <= ym <= end.strftime("%Y-%m")):
            continue
        with open(path, newline="") as f:
            for r in csv.reader(f):
                if not r or not r[0].isdigit():
                    continue
                ts = int(r[0])
                if ts < lo or ts > hi:
                    continue
                d = datetime.fromtimestamp(ts / 1000, timezone.utc).date().isoformat()
                if d in dropped:
                    continue
                rows[ts] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]))
    return rows


def berlin_morning(ts):
    t = datetime.fromtimestamp(ts / 1000, timezone.utc).astimezone(BERLIN)
    return t.weekday() < 5 and 8 <= t.hour < 12


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dax", required=True)
    ap.add_argument("--btc", required=True)
    ap.add_argument("--split", required=True)
    a = ap.parse_args()
    with open(a.split) as f:
        hc = json.load(f)
    start, end = (date.fromisoformat(x) for x in hc["dev_window"])
    dropped = set(hc["dev_dropped_days"])
    assert end < date.fromisoformat(hc["holdout_window"][0])
    res = {"window": hc["dev_window"], "dropped_days": len(dropped), "unit": "median true range / close", "rows": []}
    for name, d in (("DAX", a.dax), ("BTC", a.btc)):
        rows = load(d, start, end, dropped)
        days = len({datetime.fromtimestamp(t / 1000, timezone.utc).date() for t in rows})
        for tf in TFS:
            agg = aggregate(rows, tf)
            for label, keep in (("berlin_08_12_weekdays", berlin_morning), ("all_hours", lambda b: True)):
                if name == "DAX" and label == "all_hours":
                    continue
                v = tr_fracs(agg, tf, keep)
                res["rows"].append({"market": name, "tf_min": tf, "window": label, "bars": len(v),
                                    "median_tr_pct": round(100 * median(v), 5), "days_loaded": days})
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
