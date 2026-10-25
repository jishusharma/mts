"""Exhaust phase (MyTradingSys/system/EXHAUST_PHASE.md): spend the paid quota in the last 2 hours before the weekly reset.

  python scripts/dev/exhaust.py plan --login C --week 99 --five 13 --reset 2026-10-23T09:00Z --read 2026-10-23T07:02Z [--model opus=10 ...]

Prints the phase (none | plan | exhaust | done), minutes to reset and the models to spend, most headroom first.
Reads numbers passed in (from get_usage); no scheduler, no network, changes nothing.
B199 (BUGS.md): a quota number names its source and read time. --read is the UTC time of the get_usage call; the JSON
echoes it as read_utc with source=get_usage. A reading older than READ_MAX_MIN, or from the future, exits 2 (no phase JSON);
without --read the JSON says read_utc=unstated, source=unstated.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

PLAN_MIN = 120     # OURS (operator 2026-10-23: "within 2 hours of the reset")
EXHAUST_MIN = 60   # OURS (operator 2026-10-23: "around 1 hour")
READ_MAX_MIN = 10  # OURS (B199: a quota reading older than this is re-read with get_usage, not trusted)
READ_SKEW_MIN = 2  # OURS (clock skew between the reader and this host that is still accepted)


def parse_utc(text: str) -> datetime:
    """UTC time from 2026-10-23T09:00Z style text; a time without a zone is taken as UTC."""
    t = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def fmt_utc(t: datetime) -> str:
    t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%MZ" if t.second == 0 else "%Y-%m-%dT%H:%M:%SZ")


def check_read(read: datetime, now: datetime) -> float:
    """Age of the quota reading in minutes (negative = read time is ahead of this clock)."""
    return (now - read).total_seconds() / 60


def plan(login: str, week: float, five: float, reset: datetime, models: dict, now: datetime | None = None,
         read_utc: str = "unstated", source: str = "unstated") -> dict:
    now = now or datetime.now(timezone.utc)
    minutes = int((reset - now).total_seconds() // 60)
    if minutes <= 0 or week >= 100:
        phase = "done"
    elif minutes <= EXHAUST_MIN:
        phase = "exhaust"
    elif minutes <= PLAN_MIN:
        phase = "plan"
    else:
        phase = "none"
    order = sorted((m for m, used in models.items() if used < 100), key=lambda m: models[m])
    return {"login": login, "phase": phase, "minutes_to_reset": minutes, "week": week, "five": five, "models": order,
            "read_utc": read_utc, "source": source}


def holder(login: str, claims) -> str:
    """Who holds the exhaust claim of `login` ('' = free): one actor per login, others carry on with their own task."""
    slug = f"exhaust-login-{login.lower()}"
    for s, kv in claims:
        if s == slug:
            return kv.get("host") or kv.get("who") or "unknown"
    return ""


def start(login: str) -> int:
    import sync
    repo = Path(__file__).resolve().parents[2]
    held = holder(login, sync.open_claims(repo))
    if held:
        print(f"HELD by {held}: do not act; ack told and carry on")
        return 3
    sync.claim(repo, f"exhaust-login-{login.lower()}")
    print(f"CLAIMED exhaust-login-{login.lower()}")
    return 0


def main(argv=None, now: datetime | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "start"])
    ap.add_argument("--login", required=True, choices=["A", "B", "C"])
    ap.add_argument("--week", type=float, default=0)
    ap.add_argument("--five", type=float, default=0)
    ap.add_argument("--reset", default="", help="UTC, e.g. 2026-10-23T09:00Z")
    ap.add_argument("--read", default="", help="UTC time of the get_usage call the numbers come from; older than %d min is refused" % READ_MAX_MIN)
    ap.add_argument("--model", action="append", default=[], help="name=percent used")
    a = ap.parse_args(argv)
    if a.cmd == "start":
        return start(a.login)
    now = now or datetime.now(timezone.utc)
    read_utc, source = "unstated", "unstated"
    if a.read:
        try:
            read = parse_utc(a.read)
        except ValueError:
            print(f"BAD --read {a.read!r}: want the UTC time of the get_usage call, e.g. 2026-10-23T07:02Z", file=sys.stderr)
            return 2
        read_utc, source = fmt_utc(read), "get_usage"
        age = check_read(read, now)
        if age > READ_MAX_MIN:
            print(f"STALE quota reading: read {read_utc}, {int(age)} min old, source {source}; re-run get_usage", file=sys.stderr)
            return 2
        if age < -READ_SKEW_MIN:
            print(f"quota reading is in the future: read {read_utc}, {int(-age)} min ahead of this clock, source {source}; re-run get_usage",
                  file=sys.stderr)
            return 2
    reset = datetime.fromisoformat(a.reset.replace("Z", "+00:00"))
    models = {k: float(v) for k, _, v in (s.partition("=") for s in a.model)}
    print(json.dumps(plan(a.login, a.week, a.five, reset, models, now, read_utc, source)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
