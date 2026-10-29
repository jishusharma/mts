#!/usr/bin/env python3
"""Session log: what each work session did, read from the trunk history (no model, no transcript).

A session opens with `sync.py claim <slug>` and closes with `sync.py ship --release <slug>` (or `release` when nothing shipped); the claim is a commit.
Everything shipped in between carries a `Result:` line. This module turns that history into
  units   - one row per claim..release pair: slug, host, opened, closed, minutes, empty (nothing shipped by anyone in the window)
  shipped - one row per work commit (bookkeeping removed): when, subject, result
  stats   - counts the operator can read: sessions, empty sessions, median minutes, bookkeeping share
The Control Room shows it (make_control_room.py). CLI: python scripts/dev/session_log.py [hours]
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

REPO = Path(__file__).resolve().parents[2]
TRUNK = "fast-track"
BOOK = re.compile(r"^(claim|release|desk: (taken|done|failed|reopen)|desk assign|Merge )\b")
HOST = re.compile(r"\bon (JIS-[A-Z0-9]+|DESKTOP-[A-Z0-9]+)\b")


def read(repo=REPO, hours=48):
    """[{h, epoch, subject, result}] newest first, from origin/<trunk> (what is shipped, not what is local)."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", f"origin/{TRUNK}", f"--since={hours} hours ago", "--no-merges",
                              "--format=%x1e%h|%ct|%s%n%b"], capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for rec in out.split("\x1e")[1:]:
        first, _, body = rec.partition("\n")
        parts = first.split("|", 2)
        if len(parts) != 3 or not parts[1].isdigit():
            continue
        result = next((l.strip()[7:].strip() for l in body.splitlines() if l.strip().lower().startswith("result:")), "")
        rows.append({"h": parts[0], "epoch": int(parts[1]), "subject": parts[2].strip(), "result": result})
    return rows


def group(rows, now_epoch):
    """Pure: rows (any order) -> {units, shipped, stats}. A unit is empty when no work commit at all landed in its window."""
    rows = sorted(rows, key=lambda r: r["epoch"])
    work = [r for r in rows if not BOOK.match(r["subject"])]
    opened, units = {}, []
    for r in rows:
        kind, _, slug = r["subject"].partition(" ")
        slug = slug.strip()
        if kind == "claim" and slug:
            m = HOST.search(r["result"])
            opened[slug] = {"slug": slug, "host": m.group(1) if m else "?", "opened": r["epoch"]}
        elif kind == "release" and slug:
            u = opened.pop(slug, None)
            if u is None:           # claim older than the window
                continue
            n = sum(1 for w in work if u["opened"] <= w["epoch"] <= r["epoch"])
            units.append({**u, "closed": r["epoch"], "minutes": round((r["epoch"] - u["opened"]) / 60), "empty": n == 0})
    for u in opened.values():       # still open
        units.append({**u, "closed": None, "minutes": round((now_epoch - u["opened"]) / 60), "empty": False})
    done = [u for u in units if u["closed"]]
    stats = {"sessions": len(units), "closed": len(done), "open": len(units) - len(done),
             "empty": sum(u["empty"] for u in done),
             "median_min": round(median(u["minutes"] for u in done)) if done else None,
             "commits": len(rows), "bookkeeping": len(rows) - len(work),
             "no_result": sum(1 for w in work if not w["result"])}
    units.sort(key=lambda u: u["opened"], reverse=True)
    return {"units": units, "shipped": work[::-1], "stats": stats}


def iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%m-%d %H:%MZ") if epoch else ""


def view(repo=REPO, hours=48, now=None, keep=40):
    """Page data: times as text, lists capped so the page stays small."""
    now = now or datetime.now(timezone.utc)
    g = group(read(repo, hours), int(now.timestamp()))
    return {"hours": hours, "stats": g["stats"],
            "units": [{"slug": u["slug"], "host": u["host"], "opened": iso(u["opened"]), "closed": iso(u["closed"]),
                       "minutes": u["minutes"], "empty": u["empty"]} for u in g["units"][:keep]],
            "shipped": [{"when": iso(w["epoch"]), "h": w["h"], "subject": w["subject"][:140], "result": w["result"][:260]}
                        for w in g["shipped"][:keep]]}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    hours = int(argv[0]) if argv else 48
    v = view(REPO, hours)
    s = v["stats"]
    print(f"last {hours} h: {s['sessions']} sessions ({s['open']} open, {s['empty']} closed with nothing shipped), "
          f"median {s['median_min']} min | {s['commits']} commits, {s['bookkeeping']} bookkeeping, {s['no_result']} work commits without a Result line")
    for u in v["units"]:
        print(f"  {u['opened']} {u['host']:8} {u['minutes']:>4} min {'EMPTY ' if u['empty'] else '      '}{u['slug']}{'' if u['closed'] else '  (open)'}")
    if "--json" in argv:
        print(json.dumps(v, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
