"""Habib plan scorer (card habib-plan-hit-rate-study). Execution excluded: no stop, no fees, no position; only "did price do what the plan said".

score_plan(): pure function over 1m candles. All thresholds OURS (fixed here before any scoring):
  fill window 24 h and open window 7 d after the post (RULES.md of qriptal_2026-10-10 uses the same two windows),
  full    = entry level touched inside the fill window AND the first target touched afterwards inside the open window,
  partial = entry touched, target not, but price travelled at least PARTIAL_FRAC (0.5) of the entry->target distance,
  miss    = entry not touched, or travelled less than PARTIAL_FRAC.
A plan with no candles in its window is NO_DATA (never a miss).
build_plan_ledger(): reads qriptal_2026-10-10/CALL_LEDGER.csv; PLAN rows with a priced entry AND a priced first target.
DEV/HOLDOUT split comes from that ledger; this module reads NO candles, so scoring a HOLDOUT plan is a decision for the caller (not allowed pre-reg).
Usage (repo root): python MyTradingSys/research/habib_plan_imbalance_2026-10-20/plan_score.py ledger
"""
import csv
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CALLS = HERE.parent / "qriptal_2026-10-10" / "CALL_LEDGER.csv"
OUT = HERE / "PLAN_LEDGER.csv"
FILL = timedelta(hours=24)
OPEN = timedelta(days=7)
PARTIAL_FRAC = 0.5
COLUMNS = ("call_id", "posted_utc", "split", "direction", "entry", "target1", "status")


class NoData(ValueError):
    pass


def first_price(text):
    """'65,600 (sweep...)' -> 65600.0; '' / 'NOT STATED...' -> None. Only a leading number counts (it must be spoken)."""
    m = re.match(r"\s*(\d{2,3}(?:,\d{3})+|\d{4,6})(?:\.\d+)?", text or "")
    return float(m.group(1).replace(",", "")) if m else None


def score_plan(candles, direction, entry, target, posted):
    """candles: [(open_time_utc datetime, high, low)] sorted. -> 'full' | 'partial' | 'miss'. Raises NoData on an empty window."""
    if direction not in ("long", "short"):
        raise ValueError(direction)
    win = [c for c in candles if posted <= c[0] < posted + OPEN]
    if not win:
        raise NoData("no candles in the plan window")
    sign = 1 if direction == "long" else -1  # long: entry below price, target above
    filled_at = None
    for t, hi, lo in win:
        if t >= posted + FILL:
            break
        if lo <= entry <= hi:
            filled_at = t
            break
    if filled_at is None:
        return "miss"
    best = 0.0
    for t, hi, lo in win:
        if t < filled_at:
            continue
        reach = hi if sign == 1 else lo
        if (reach - target) * sign >= 0:
            return "full"
        best = max(best, (reach - entry) * sign)
    return "partial" if best >= PARTIAL_FRAC * abs(target - entry) else "miss"


def build_plan_ledger(calls=None):
    out = []
    for r in csv.DictReader(open(calls or CALLS, encoding="utf-8", newline="")):
        e, t = first_price(r["entry"]), first_price(r["targets"])
        if r["kind"] == "PLAN" and r["asset"] == "BTC" and e and t and r["direction"] in ("long", "short"):
            status = "READY_DEV" if r["window_split"] == "DEV" else ("NO_TIME" if r["window_split"] == "NO_TIME"
                                                                     else "NOT_SCORED_HOLDOUT_WINDOW")
            out.append({"call_id": r["call_id"], "posted_utc": r["published_utc"], "split": r["window_split"],
                        "direction": r["direction"], "entry": int(e), "target1": int(t), "status": status})
    return out


def render(rows):
    lines = [",".join(COLUMNS)] + [",".join(str(r[c]) for c in COLUMNS) for r in rows]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    rows = build_plan_ledger()
    if len(sys.argv) > 1 and sys.argv[1] == "ledger":
        with open(OUT, "w", encoding="utf-8", newline="") as f:
            f.write(render(rows))
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(len(rows), "plans with a priced entry and target;", by)
