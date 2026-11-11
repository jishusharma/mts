"""dsa_watch.py: zero-token DSA monitor for a supervisor loop (no LLM, no network).

  python scripts/dev/dsa_watch.py [--stale-hours 3] [--audit F:/AIBridge/src/audit.jsonl]

Prints one line per DSA target (DSA, DSA-NB, DSA-NUC): pending, taken, oldest-pending age, and a verdict.
Exit 0 = every bridge with work is moving, 1 = at least one STALLED line (verdicts: EMPTY, OK, STALLED). Run it from the stop-guard;
only a non-zero exit needs a Claude look. The audit file is read as its last line only, for the bridge_last_call age (no host filter).
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

QUEUE = "MyTradingSys/system/desk_queue"
TARGETS = ("DSA", "DSA-NB", "DSA-NUC")


def _ts(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def summarize(rows, now, stale_h):
    out = []
    for t in TARGETS:
        mine = [r for r in rows if r.get("target") == t]
        pend = [r for r in mine if r.get("status") == "pending"]
        taken = [r for r in mine if r.get("status") == "taken"]
        ages = [(now - d).total_seconds() / 3600 for d in (_ts(r.get("posted")) for r in pend) if d]
        oldest = max(ages) if ages else 0.0
        if not pend and not taken:
            verdict = "EMPTY"
        elif oldest > stale_h:
            verdict = "STALLED"
        else:
            verdict = "OK"
        out.append((t, len(pend), len(taken), oldest, verdict))
    return out


def audit_age(path, now):
    try:
        last = Path(path).read_text(encoding="utf-8", errors="replace").strip().splitlines()[-1]
        d = _ts(json.loads(last.split("\t", 1)[-1]).get("ts", "")[:26] + "+00:00")
        return (now - d).total_seconds() / 3600 if d else None
    except (OSError, IndexError, ValueError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-hours", type=float, default=3.0)
    ap.add_argument("--audit", default="F:/AIBridge/src/audit.jsonl")
    ap.add_argument("--queue", default=QUEUE)
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    rows = []
    for p in Path(a.queue).glob("*.json"):
        try:
            rows.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    bad = False
    for t, pend, taken, oldest, verdict in summarize(rows, now, a.stale_hours):
        print(f"{t}: pending={pend} taken={taken} oldest_pending={oldest:.1f}h {verdict}")
        bad = bad or verdict == "STALLED"
    age = audit_age(a.audit, now)
    print("bridge_last_call=" + ("unknown" if age is None else f"{age:.1f}h ago"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
