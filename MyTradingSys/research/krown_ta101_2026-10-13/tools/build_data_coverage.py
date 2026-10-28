"""Build weekly bars (Monday 00:00 UTC) from the daily files and write DATA_COVERAGE.md (card krown-data-daily-majors).

Reads <data>/<SERIES>.csv written by fetch_daily_majors.py. Looks at timestamps and, for the weekly cross-check, OHLC equality
on bars dated before 2024-07-01 (DEV window only). No return or outcome is computed.
Run: python MyTradingSys/research/krown_ta101_2026-10-13/tools/build_data_coverage.py --data F:/MTS/data/krown_daily
"""
import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

DAY = 86400_000
DEV_END_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
FILES = [("Binance spot BTCUSDT", "BTCUSDT_1d.csv", DAY), ("Binance spot BTCUSDT (published 1w)", "BTCUSDT_1w.csv", 7 * DAY),
         ("Binance spot ETHUSDT", "ETHUSDT_1d.csv", DAY), ("Binance spot BNBUSDT", "BNBUSDT_1d.csv", DAY),
         ("Binance spot SOLUSDT", "SOLUSDT_1d.csv", DAY), ("Coinbase BTC-USD", "COINBASE_BTC-USD_1d.csv", DAY)]
WEEKLY_FROM = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        head = next(r)
        return head, [row for row in r]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def weekly(rows):
    """Full Monday-start weeks only (7 daily bars present). Day 0 (1970-01-01) is a Thursday."""
    weeks = {}
    for r in rows:
        d = int(r[0]) // DAY
        weeks.setdefault(((d + 3) // 7) * 7 - 3, []).append(r)
    out, partial = [], 0
    for wd in sorted(weeks):
        g = sorted(weeks[wd], key=lambda r: int(r[0]))
        if len(g) != 7 or int(g[0][0]) != wd * DAY:
            partial += 1
            continue
        out.append([wd * DAY, g[0][1], max(float(x[2]) for x in g), min(float(x[3]) for x in g), g[-1][4],
                    sum(float(x[5]) for x in g), int(g[-1][6])])
    return out, partial


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--doc-dir", default=str(Path(__file__).resolve().parents[1]))
    a = ap.parse_args()
    data = Path(a.data)
    md = ["# DATA_COVERAGE: Krown daily/weekly series (2026-10-16)\n",
          "Fetched by `tools/fetch_daily_majors.py`, summarised by `tools/build_data_coverage.py`. Files live in `F:/MTS/data/krown_daily/` (never in git);\n"
          "this table and `DATA_MANIFEST.csv` (every source file: URL, published SHA256, computed SHA256, status) are what is committed.\n"
          "Each Binance monthly zip was compared with its published `.CHECKSUM`: all matched (status OK in the manifest). Coverage reads timestamps only; the weekly\n"
          "aggregation touches OHLC mechanically (no return or outcome is computed) and its cross-check compares only bars before 2024-07-01. Bars from 2024-07-01 on are\n"
          "stored for the one-time VALIDATION and HOLDOUT reads and are not studied here.\n",
          "| series | first bar | last bar | bars | gaps | SHA256 of merged file |", "|---|---|---|---|---|---|"]
    gap_notes = []
    for label, fn, step in FILES:
        head, rows = read(data / fn)
        ts = [int(r[0]) for r in rows]
        gaps = [(ts[i - 1], ts[i]) for i in range(1, len(ts)) if ts[i] - ts[i - 1] != step]
        md.append(f"| {label} {fn.split('_')[-1][:2]} | {iso(ts[0])} | {iso(ts[-1])} | {len(ts)} | {len(gaps)} | `{sha(data / fn)}` |")
        if gaps:
            gap_notes.append(f"- {label} `{fn}`: missing bars between " + "; ".join(f"{iso(a_)} and {iso(b)}" for a_, b in gaps))
    md.append("")
    if gap_notes:
        md += ["## Gaps\n"] + gap_notes + [""]
    md += ["## Weekly bars built from the daily files (Monday 00:00 UTC start, full 7-day weeks only)\n",
           "Binance's published BTCUSDT 1w file has the gaps listed above (the monthly archive omits those weeks) and stops at the last full week "
           "of June 2026 (the 2026-07 to 2026-09 monthly 1w files are not published). The weekly series to use is the one built from the daily bars:\n",
           "| series | first week | last week | weeks | partial weeks dropped | SHA256 |", "|---|---|---|---|---|---|"]
    for sym in WEEKLY_FROM:
        _, rows = read(data / f"{sym}_1d.csv")
        wk, partial = weekly(rows)
        path = data / f"{sym}_1w_from_1d.csv"
        with open(path, "w", newline="\n", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["open_time_ms", "open", "high", "low", "close", "volume", "close_time_ms"])
            w.writerows(wk)
        md.append(f"| {sym} 1w_from_1d | {iso(wk[0][0])} | {iso(wk[-1][0])} | {len(wk)} | {partial} | `{sha(path)}` |")
        if sym == "BTCUSDT":
            _, pub = read(data / "BTCUSDT_1w.csv")
            pubmap = {int(r[0]): r for r in pub}
            n = eq = vol_bad = 0
            for r in wk:
                if r[0] >= DEV_END_MS or r[0] not in pubmap:
                    continue
                p = pubmap[r[0]]
                n += 1
                same = (float(p[1]) == float(r[1]) and float(p[2]) == r[2] and float(p[3]) == r[3] and float(p[4]) == float(r[4]))
                eq += same
                vol_bad += abs(float(p[5]) - r[5]) > 1e-6 * max(1.0, abs(r[5]))
            md_check = (f"\nCross-check, BTCUSDT weeks dated before 2024-07-01 present in both: {n}; open/high/low/close identical in {eq}; "
                        f"volume differs beyond 1e-6 relative in {vol_bad}.\n")
    md.append(md_check)
    md.append("Coinbase BTC-USD volume is in BTC on that venue only; Binance spot volume is in the base asset on Binance. The venue question (conflict C6) "
              "is answered by the study, not here.\n")
    (Path(a.doc_dir) / "DATA_COVERAGE.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print("DATA_COVERAGE.md written")


if __name__ == "__main__":
    main()
