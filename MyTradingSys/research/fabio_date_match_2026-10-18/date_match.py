"""Date the Fabio NQ-202512 session by price-path match against Dukascopy USATECHIDXUSD BID 1m bars.

Report only. Pattern (offsets from the F6 entry level E, so CFD-vs-futures basis cancels):
  F6 long avg 24914.33 -> TP 25001.00 (+86.7 pt) within 40 min, stop 24883.50 (-30.8 pt) not hit before TP,
  then the F11-F14 range 25095-25110 (+181..+196 pt) within 120 min of entry.
  Source: FABIO_TRADE_LEDGER.csv:25-28 (F6), FABIO_TRADE_LEDGER.md:95. All thresholds below are SOURCED from those rows
  except TP_WINDOW_MIN/RANGE_WINDOW_MIN/tolerances (OURS, judgement).
Usage: python -I date_match.py [--raw F:/MTS/data/nq_raw]
"""
import argparse
import datetime as dt
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
from dax_data import HEADERS, URL, parse_bi5  # noqa: E402

INST = "USATECHIDXUSD"
TP_PT = 86.7            # SOURCED 25001.00 - 24914.33
STOP_PT = 30.8          # SOURCED 24914.33 - 24883.50
RANGE_LO, RANGE_HI = 181.0, 196.0   # SOURCED 25095-24914 .. 25110-24914 (md:95)
TP_WINDOW_MIN = 20      # OURS: ledger F6 entry ~15:45 chart, flat ~15:55; 40 min matched too many ordinary NQ days
MID_PT, MID_WINDOW_MIN = 155.0, 35   # F10 TP 25074.25 (+160) at ~16:07 chart, ~22 min after F6 entry (md ledger F10-m1); 155/35 are OURS
RANGE_WINDOW_MIN = 120  # OURS
RANGE_TOL = 50.0        # OURS: pts outside the band that decay the score to 0
WIN_LO, WIN_HI = 13 * 60, 15 * 60 + 15  # entry minute window UTC (chart 15:45 CET/CEST = 13:45/14:45 UTC, +- slack)


def best_match(bars, lo=WIN_LO, hi=WIN_HI):
    """bars: [(open_ms,o,h,l,c,v)] one UTC day. Returns (score 0..1, entry_ms, entry_price)."""
    if not bars:
        return 0.0, 0, 0.0
    day0 = bars[0][0] - bars[0][0] % 86400000
    best = (0.0, 0, 0.0)
    for i, b in enumerate(bars):
        m = (b[0] - day0) // 60000
        if not lo <= m <= hi:
            continue
        e = b[4]
        w40 = [x for x in bars[i + 1:] if x[0] <= b[0] + TP_WINDOW_MIN * 60000]
        tp_t = next((x[0] for x in w40 if x[2] - e >= TP_PT), None)
        c1 = 1.0 if tp_t is not None else 0.0
        if c1:
            c2 = 0.0 if any(x[3] - e <= -STOP_PT for x in w40 if x[0] <= tp_t) else 1.0
        else:
            c2 = 0.0
        w120 = [x for x in bars[i + 1:] if x[0] <= b[0] + RANGE_WINDOW_MIN * 60000]
        top = max((x[2] - e for x in w120), default=0.0)
        dist = 0.0 if RANGE_LO <= top <= RANGE_HI else min(abs(top - RANGE_LO), abs(top - RANGE_HI))
        c3 = max(0.0, 1.0 - dist / RANGE_TOL) if top >= TP_PT else 0.0
        mid = any(x[2] - e >= MID_PT for x in bars[i + 1:] if x[0] <= b[0] + MID_WINDOW_MIN * 60000)
        c4 = 1.0 if mid else 0.0
        s = (c1 + c2 + c3 + c4) / 4 if c1 else 0.0
        if s > best[0] + 1e-12:
            best = (s, b[0], e)
    return best


def verdict(ranked):
    """ranked: [(score, day)] sorted desc."""
    if not ranked or ranked[0][0] <= 0:
        return "NOT_IN_DATA"
    if ranked[0][0] >= 0.99 and (len(ranked) < 2 or ranked[0][0] - ranked[1][0] >= 0.1):
        return "MATCH"
    return "AMBIGUOUS"


def fetch_day(day, raw):
    f = raw / f"{day:%Y-%m-%d}.bi5"
    if f.exists():
        return f.read_bytes()
    url = URL.format(inst=INST, y=day.year, m0=day.month - 1, d=day.day, side="BID")
    for attempt in range(6):
        time.sleep(0.7)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30) as r:
                blob = r.read()
            f.write_bytes(blob)
            return blob
        except Exception as e:
            if getattr(e, "code", None) == 404:
                f.write_bytes(b"")
                return b""
            time.sleep(min(30, 3 * 2 ** attempt))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="F:/MTS/data/nq_raw")
    ap.add_argument("--start", default="2025-09-15")
    ap.add_argument("--end", default="2025-12-19")
    a = ap.parse_args()
    raw = Path(a.raw)
    raw.mkdir(parents=True, exist_ok=True)
    d0, d1 = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    days = [d0 + dt.timedelta(n) for n in range((d1 - d0).days + 1)]
    days = [d for d in days if d.weekday() < 5]
    first = dt.date(2025, 10, 15)
    days.sort(key=lambda d: (d != first, d))
    rows, nofile, fail = [], 0, 0
    for d in days:
        blob = fetch_day(d, raw)
        if blob is None:
            fail += 1
            continue
        bars = parse_bi5(blob, d)
        if not bars:
            nofile += 1
            continue
        s, ms, e = best_match(bars)
        rows.append((s, d, ms, e, len(bars)))
        if d == first:
            print("spoken day", d, "score", round(s, 3), "entry", dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc) if ms else None, "price", e, "n", len(bars), flush=True)
    rows.sort(key=lambda r: -r[0])
    print("days tried", len(days), "with bars", len(rows), "empty", nofile, "fetch fail", fail)
    for r in rows[:8]:
        print(r[0], r[1], dt.datetime.fromtimestamp(r[2] / 1000, dt.timezone.utc).strftime("%H:%M") if r[2] else "-", r[3], r[4])
    print("verdict", verdict([(r[0], r[1]) for r in rows]))


if __name__ == "__main__":
    main()
