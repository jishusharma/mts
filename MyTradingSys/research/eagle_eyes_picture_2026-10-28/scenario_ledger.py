"""Scenario ledger: every A/B map Eagle_Eyes gives the operator, scored by machine (operator 11-04: "how are we gonna track it?").

add     log a map the same turn it is given (likely side, up level, down level, window end)
score   after the window ends, read Binance spot BTCUSDT 1m bars (public data) and record which level was touched first
summary running hit count and what the count means for the pipeline

Levels, windows and the 'likely' side are OURS. Scoring is mechanical: no pixel reads, no hindsight edits.
Library use (daily_playbook.py, tools/live_aid): add_row, find_tag, score_rows work on a list of rows, so a caller can log
a whole day of maps with one load and one save.
"""
import argparse
import csv
import datetime as dt
import json
import math
import sys
import urllib.request
from pathlib import Path

LEDGER = Path(__file__).with_name("scenario_ledger.csv")
FIELDS = ["id", "given_utc", "end_utc", "likely", "up", "down", "text", "outcome", "touched_utc", "score", "rates"]
KLINES = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000"
PROMOTE_N = 20


def parse_utc(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def first_touch(bars, up, down):
    """bars: [(open_ms, high, low)] in time order. Returns (outcome, open_ms of the touching bar or None).
    outcome = UP, DOWN, BOTH (same bar, order unknown) or NEITHER."""
    for t, hi, lo in bars:
        u, d = hi >= up, lo <= down
        if u and d:
            return "BOTH", t
        if u:
            return "UP", t
        if d:
            return "DOWN", t
    return "NEITHER", None


def score_of(likely, outcome):
    if likely not in ("UP", "DOWN") or outcome in ("BOTH", "NEITHER"):
        return "NA"
    return "HIT" if likely == outcome else "MISS"


def fetch_bars(start, end):
    bars, t0, t1 = [], int(start.timestamp() * 1000), int(end.timestamp() * 1000)
    while t0 < t1:
        rows = json.load(urllib.request.urlopen(f"{KLINES}&startTime={t0}&endTime={t1}", timeout=30))
        if not rows:
            break
        bars += [(r[0], float(r[2]), float(r[3])) for r in rows if r[0] < t1]
        t0 = rows[-1][0] + 60_000
    return bars


def load(path=LEDGER):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows, path=LEDGER):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def add_row(rows, given, end, likely, up, down, text, rates=""):
    """Append one map to rows (datetimes in, ledger row out). Same rules as the add command: down < up and given < end."""
    if not down < up or not given < end:
        raise ValueError("need down < up and given < end")
    rows.append({"id": f"S{len(rows) + 1:03d}", "given_utc": given.strftime("%Y-%m-%dT%H:%MZ"),
                 "end_utc": end.strftime("%Y-%m-%dT%H:%MZ"), "likely": likely, "up": up,
                 "down": down, "text": text, "outcome": "", "touched_utc": "", "score": "",
                 "rates": ",".join(x.strip() for x in rates.split(",") if x.strip())})
    return rows[-1]


def find_tag(rows, tag):
    """The row whose text starts with tag (daily_playbook.py puts '[PB <day> <session> <n>]' first), or None."""
    return next((r for r in rows if r["text"].startswith(tag)), None)


def score_rows(rows, now, fetch=fetch_bars):
    """Score every unscored row whose window has ended (first touch of up/down on 1m bars). Returns the rows scored."""
    done = []
    for r in rows:
        if r["outcome"] or parse_utc(r["end_utc"]) > now:
            continue
        out, t = first_touch(fetch(parse_utc(r["given_utc"]), parse_utc(r["end_utc"])), float(r["up"]), float(r["down"]))
        r["outcome"], r["score"] = out, score_of(r["likely"], out)
        r["touched_utc"] = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ") if t else ""
        done.append(r)
    return done


def summary(rows):
    hits = sum(r["score"] == "HIT" for r in rows)
    miss = sum(r["score"] == "MISS" for r in rows)
    n = hits + miss
    open_ = sum(not r["outcome"] for r in rows)
    out = [f"maps {len(rows)} | open {open_} | scored with a side {n}: HIT {hits} MISS {miss}"]
    if n:
        p = hits / n
        lo = (p + 1.92 / n - 1.96 * math.sqrt(p * (1 - p) / n + 0.96 / n / n)) / (1 + 3.84 / n)  # Wilson 95% low
        out.append(f"hit rate {p:.0%}, 95% low {lo:.0%}")
        if n < PROMOTE_N:
            out.append(f"pipeline: keep logging ({n}/{PROMOTE_N} before any verdict)")
        elif lo > 0.5:
            out.append("pipeline: PROMOTE - file a BACKTEST_CANDIDATES row + PRE_REG for the map rules")
        else:
            out.append("pipeline: no edge in the maps yet - maps stay descriptive")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--given", required=True)
    a.add_argument("--end", required=True)
    a.add_argument("--likely", choices=["UP", "DOWN", "NONE"], required=True)
    a.add_argument("--up", type=float, required=True)
    a.add_argument("--down", type=float, required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--rates", default="", help="base-rate registry ids used (tools/live_aid/base_rates.js), comma separated")
    sub.add_parser("score")
    sub.add_parser("summary")
    args = ap.parse_args(argv)
    rows = load(LEDGER)
    if args.cmd == "add":
        try:
            add_row(rows, parse_utc(args.given), parse_utc(args.end), args.likely, args.up, args.down, args.text, args.rates)
        except ValueError as ex:
            sys.exit(str(ex))
        save(rows, LEDGER)
        print("added", rows[-1]["id"])
    elif args.cmd == "score":
        for r in score_rows(rows, dt.datetime.now(dt.timezone.utc)):
            print(r["id"], r["outcome"], r["score"])
        save(rows, LEDGER)
    print(summary(rows))


if __name__ == "__main__":
    main()
