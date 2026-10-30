"""US open: which levels get reached in the first 2 h, and does a touch hold?  (BTCUSDT 1m, 2022-01..2026-09)

Ask (operator, 2026-10-30, voice): "anticipation = know in advance what happens if price goes up or down, e.g. the new
candle taking the prior 1-day, 2-day, 3-day or weekly high/low, then failing" and (same day) "anything for the dashboard
... so that I use it for live trading" before the US open.

Definitions, fixed before the first run (all OURS unless marked):
- Open = NYSE cash open, 09:30 America/New_York (SOURCED: exchange hours) on Mon-Fri. US holidays are not removed.
- Open price = open of the 1m bar at the open. Window = the 120 bars from the open.
- Levels known at the open: dayH/dayL = high/low of 00:00Z..open (the UTC day so far); pdh/pdl = prior complete UTC day;
  d3h/d3l = extreme of the prior 3 complete UTC days; d7h/d7l = prior 7 complete UTC days.
- A high-type level counts only when above the open price, a low-type level only when below (the rest is already behind price).
- Distance bucket = |level - open| / open: 0-0.25 %, 0.25-0.5 %, 0.5-1 %, 1-2 %, 2 %+.
- Reached = some bar in the window has high >= level (low <= level for lows). Touch bar = the first such bar.
- Held = the close 60 bars after the touch bar is still beyond the level (above a high, below a low); else failed back.
Descriptive base rates, no fees, no entries: context for the live aid, never a signal.
Hindsight by design (looks forward from the open to score the window); lookahead allowlist rows name this file.
"""
import glob
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

SRC = "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv"
OUT = Path(__file__).resolve().parent
JS_OUT = OUT.parents[1] / "tools" / "live_aid" / "us_open_rates.js"
NY = ZoneInfo("America/New_York")
WINDOW, HOLD = 120, 60
BUCKETS = [("0-0.25", 0, 0.0025), ("0.25-0.5", 0.0025, 0.005), ("0.5-1", 0.005, 0.01), ("1-2", 0.01, 0.02), ("2+", 0.02, 9)]
KINDS = ["dayH", "dayL", "pdh", "pdl", "d3h", "d3l", "d7h", "d7l"]


def load():
    frames = []
    for f in sorted(glob.glob(SRC)):
        d = pd.read_csv(f, usecols=["open_time", "open", "high", "low", "close"])
        frames.append(d)
    df = pd.concat(frames).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    return df


def bucket(x):
    for name, lo, hi in BUCKETS:
        if lo <= x < hi:
            return name
    return None


def main():
    df = load()
    t = df["open_time"].values.astype(np.int64)
    o, h, l, c = (df[k].values.astype(float) for k in ("open", "high", "low", "close"))
    day = (t // 86_400_000) * 86_400_000
    days = pd.DataFrame({"day": day, "h": h, "l": l}).groupby("day").agg(h=("h", "max"), l=("l", "min"))
    day_list = days.index.values
    pos = {int(ts): i for i, ts in enumerate(t)}  # ms -> row
    first = datetime.fromtimestamp(int(t[0]) / 1000, timezone.utc).date()
    last = datetime.fromtimestamp(int(t[-1]) / 1000, timezone.utc).date()
    tally = {k: {b[0]: {"n": 0, "touch": 0, "held": 0} for b in BUCKETS} for k in KINDS}
    n_days = 0
    d = first + timedelta(days=8)
    while d <= last:
        if d.weekday() < 5:
            open_ms = int(datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).timestamp() * 1000)
            i = pos.get(open_ms)
            if i is not None and i + WINDOW + HOLD < len(t):
                d0 = (open_ms // 86_400_000) * 86_400_000
                j0 = pos.get(d0)
                k = np.searchsorted(day_list, d0)  # index of today in the day table
                if j0 is not None and k >= 7 and j0 < i:
                    n_days += 1
                    op = o[i]
                    lv = {"dayH": h[j0:i].max(), "dayL": l[j0:i].min(),
                          "pdh": days["h"].values[k - 1], "pdl": days["l"].values[k - 1],
                          "d3h": days["h"].values[k - 3:k].max(), "d3l": days["l"].values[k - 3:k].min(),
                          "d7h": days["h"].values[k - 7:k].max(), "d7l": days["l"].values[k - 7:k].min()}
                    wh, wl = h[i:i + WINDOW], l[i:i + WINDOW]
                    for kind, level in lv.items():
                        up = kind.endswith("H") or kind.endswith("h")
                        if (up and level <= op) or (not up and level >= op):
                            continue
                        b = bucket(abs(level - op) / op)
                        if b is None:
                            continue
                        cell = tally[kind][b]
                        cell["n"] += 1
                        hits = np.nonzero(wh >= level)[0] if up else np.nonzero(wl <= level)[0]
                        if len(hits):
                            cell["touch"] += 1
                            tb = i + int(hits[0])
                            cc = c[tb + HOLD]
                            if (up and cc > level) or (not up and cc < level):
                                cell["held"] += 1
        d += timedelta(days=1)
    rates = {}
    for kind in KINDS:
        rates[kind] = {}
        for b, _, _ in BUCKETS:
            cell = tally[kind][b]
            rates[kind][b] = {"n": cell["n"], "touch": round(100 * cell["touch"] / cell["n"]) if cell["n"] else None,
                              "nt": cell["touch"], "held": round(100 * cell["held"] / cell["touch"]) if cell["touch"] else None}
    meta = {"source": "Binance USD-M BTCUSDT 1m", "range": [str(first), str(last)], "days": n_days, "window_min": WINDOW,
            "hold_min": HOLD, "buckets": [b[0] for b in BUCKETS], "note": "weekdays, US holidays not removed; OURS definitions in study.py"}
    res = {"meta": meta, "rates": rates}
    (OUT / "results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    JS_OUT.write_text("// built by research/us_open_levels_2026-10-30/study.py; do not edit\nvar US_OPEN_RATES = "
                      + json.dumps(res, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    lines = ["# US open: levels reached in the first 2 h, and whether a touch holds 60 min later", "",
             f"BTCUSDT 1m {first}..{last}, {n_days} weekdays. Window = 120 min from the 09:30 New York open; held = close 60 min after the "
             "first touch is still beyond the level. Definitions in `study.py` (OURS), fixed before the run. Descriptive, no fees, no signal.", "",
             "| level | distance at open | days | reached in 2 h | held 60 min after touch |", "|---|---|---|---|---|"]
    for kind in KINDS:
        for b, _, _ in BUCKETS:
            r = rates[kind][b]
            if r["n"]:
                lines.append(f"| {kind} | {b} % | {r['n']} | {r['touch']} % | {r['held']} % (n={r['nt']}) |")
    (OUT / "RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(meta))
    for kind in KINDS:
        print(kind, {b: (r["n"], r["touch"], r["held"]) for b, r in rates[kind].items()})


if __name__ == "__main__":
    sys.exit(main())
