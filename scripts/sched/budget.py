"""Weekly-budget pacing state (SUPER_SESSION.md, Pacing): SPEND / NORMAL / THROTTLE from ~/.claude/mts-budget.json.

get_usage is readable only inside App sessions, so a session records it here and the model-free gate reads the file.
  python scripts/sched/budget.py write --weekly-all-pct 32 --weekly-resets-at 2026-10-20T00:00:00Z --five-hour-pct 12
  python scripts/sched/budget.py state     prints `<STATE> <why>`
f = fraction of the 7-day week elapsed (week ends at weekly_resets_at), U = weekly all-models %.
THROTTLE: five_hour_pct > 80 or U > 100 f + 5.  SPEND: U < 100 f - 10, or under 24 h to the reset with U < 85.  Else NORMAL.
A missing, unreadable or older-than-6-h reading is NORMAL (never block work on a guess)."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TS = "%Y-%m-%dT%H:%M:%SZ"
MAX_AGE = timedelta(hours=6)
WEEK = timedelta(days=7)


def home():
    return Path(os.environ.get("MTS_RELAY_HOME") or Path.home() / ".claude")


def now():
    v = os.environ.get("MTS_RELAY_NOW")
    return datetime.fromisoformat(v.replace("Z", "+00:00")) if v else datetime.now(timezone.utc)


def parse(s):
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def compute(d, at):
    """(state, why) for a reading dict at time `at`."""
    try:
        u, five = float(d["weekly_all_pct"]), float(d["five_hour_pct"])
        resets, taken = parse(d["weekly_resets_at"]), parse(d["utc"])
    except (KeyError, TypeError, ValueError):
        return "NORMAL", "reading unreadable"
    if at - taken > MAX_AGE:
        return "NORMAL", "reading older than 6h"
    to_reset = resets - at
    if to_reset < timedelta(0) or to_reset > WEEK:
        return "NORMAL", "reset time outside the week"
    f = 1 - to_reset / WEEK
    pace = 100 * f
    if five > 80:
        return "THROTTLE", "5h window %.0f%% > 80" % five
    if u > pace + 5:
        return "THROTTLE", "U=%.1f > pace %.1f + 5" % (u, pace)
    if u < pace - 10 or (to_reset < timedelta(hours=24) and u < 85):
        return "SPEND", "U=%.1f, pace %.1f, %.1fh to reset" % (u, pace, to_reset.total_seconds() / 3600)
    return "NORMAL", "U=%.1f, pace %.1f" % (u, pace)


def state(at=None):
    try:
        d = json.loads((home() / "mts-budget.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "NORMAL", "no reading"
    return compute(d, at or now())


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--weekly-all-pct", type=float, required=True)
    w.add_argument("--weekly-resets-at", required=True)
    w.add_argument("--five-hour-pct", type=float, required=True)
    sub.add_parser("state")
    a = ap.parse_args(argv)
    if a.cmd == "write":
        parse(a.weekly_resets_at)   # reject garbage now, not at the next tick
        rec = {"utc": now().strftime(TS), "weekly_all_pct": a.weekly_all_pct, "weekly_resets_at": a.weekly_resets_at,
               "five_hour_pct": a.five_hour_pct}
        home().mkdir(parents=True, exist_ok=True)
        (home() / "mts-budget.json").write_text(json.dumps(rec, sort_keys=True), encoding="utf-8", newline="\n")
        print("BUDGET written", " ".join("%s=%s" % kv for kv in rec.items()))
    s, why = state()
    print(s, why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
