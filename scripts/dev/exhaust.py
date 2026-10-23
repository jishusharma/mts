"""Exhaust phase (MyTradingSys/system/EXHAUST_PHASE.md): spend the paid quota in the last 2 hours before the weekly reset.

  python scripts/dev/exhaust.py plan --login C --week 99 --five 13 --reset 2026-10-23T09:00Z [--model opus=10 ...]

Prints the phase (none | plan | exhaust | done), minutes to reset and the models to spend, most headroom first.
Reads numbers passed in (from get_usage); no scheduler, no network, changes nothing.
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


def plan(login: str, week: float, five: float, reset: datetime, models: dict, now: datetime | None = None) -> dict:
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
    return {"login": login, "phase": phase, "minutes_to_reset": minutes, "week": week, "five": five, "models": order}


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "start"])
    ap.add_argument("--login", required=True, choices=["A", "B", "C"])
    ap.add_argument("--week", type=float, default=0)
    ap.add_argument("--five", type=float, default=0)
    ap.add_argument("--reset", default="", help="UTC, e.g. 2026-10-23T09:00Z")
    ap.add_argument("--model", action="append", default=[], help="name=percent used")
    a = ap.parse_args(argv)
    if a.cmd == "start":
        return start(a.login)
    reset = datetime.fromisoformat(a.reset.replace("Z", "+00:00"))
    models = {k: float(v) for k, _, v in (s.partition("=") for s in a.model)}
    print(json.dumps(plan(a.login, a.week, a.five, reset, models)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
