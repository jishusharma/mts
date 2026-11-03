#!/usr/bin/env python3
"""Append one row to research/live_reads/divergence_events.csv (descriptive forward evidence only).

Refuses a duplicate utc and a row with an empty outcome column: a half-filled event is worse than none.
Usage: python divergence_event.py append --utc 2026-10-26T14:36:00Z --btc -0.10 --es 0.32 --nq 0.36 \
       --out30 "..." --out60 "..." --out120 "..."
"""
import argparse
import csv
import os
import sys

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "divergence_events.csv")
COLS = ["utc", "btc_since_open", "es_since_open", "nq_since_open", "vix", "r5m_1h_es", "r5m_1h_nq",
        "footprint_delta_note", "out_30m", "out_60m", "out_120m"]
REQUIRED = ("utc", "btc_since_open", "es_since_open", "nq_since_open", "out_30m", "out_60m", "out_120m")


def rows(path=CSV):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append(row, path=CSV):
    """Validate and append; returns the written dict. Raises ValueError on a bad row."""
    missing = [k for k in REQUIRED if not str(row.get(k, "")).strip()]
    if missing:
        raise ValueError("missing required column(s): %s" % ", ".join(missing))
    if any(r["utc"] == row["utc"] for r in rows(path)):
        raise ValueError("duplicate utc: %s" % row["utc"])
    full = {c: str(row.get(c, "") or "") for c in COLS}
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow(full)
    return full


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["append", "list"])
    ap.add_argument("--utc"); ap.add_argument("--btc"); ap.add_argument("--es"); ap.add_argument("--nq")
    ap.add_argument("--vix", default=""); ap.add_argument("--r1hes", default=""); ap.add_argument("--r1hnq", default="")
    ap.add_argument("--footprint", default="")
    ap.add_argument("--out30"); ap.add_argument("--out60"); ap.add_argument("--out120")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        for r in rows():
            print(r["utc"], r["out_30m"][:40], "|", r["out_120m"][:40])
        return 0
    try:
        r = append({"utc": a.utc, "btc_since_open": a.btc, "es_since_open": a.es, "nq_since_open": a.nq,
                    "vix": a.vix, "r5m_1h_es": a.r1hes, "r5m_1h_nq": a.r1hnq, "footprint_delta_note": a.footprint,
                    "out_30m": a.out30, "out_60m": a.out60, "out_120m": a.out120})
    except ValueError as e:
        print("refused: %s" % e)
        return 2
    print("appended", r["utc"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
