"""Tier 0 clock (SCHEDULER_PLAN s2/s5): run every detector in order, debounce by state hash, write a tick report.

No Claude calls here. Exit code = worst exit of the checks run (0 OK, 1 WARN, 2 RED).
Debounce state: MyTradingSys/runtime/sched/tick_state.json
  event_seen    {hash: last_fired_utc}   event check fires only if hash unseen within 24 h
  digest_included [hash]                 hashes in the last completed digest (run_worker digest mode sets it);
                                         a digest item is new if its hash is not in that list
Output: MyTradingSys/research/sched_reports/tick_<utc>.md (ends with a "## Pick" section from pick_task.py) ; also prints a one-line summary.
Usage (repo root): python scripts/sched/tick.py [--now ISO] [--only name,name]
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO, state_hash

PY = sys.executable
SCHED_DIR = REPO / "MyTradingSys" / "runtime" / "sched"
STATE = SCHED_DIR / "tick_state.json"
REPORT_DIR = REPO / "MyTradingSys" / "research" / "sched_reports"
DEBOUNCE = timedelta(hours=24)
TS_FMT = "%Y%m%dT%H%M%SZ"

# (name, argv, kind). kind "event": non-OK on a RED fires Haiku event; "digest": any non-OK goes to the digest.
# canary: RED = event, WARN = digest (SCHEDULER_PLAN s5 #3). Build-Check and run_all_tests --quick are not wired
# (plan s9: verify their runtime and exit-code mapping before putting them on a 15-minute clock).
CHECKS = [
    ("snapshot_age", [PY, "scripts/sched/check_snapshot_age.py"], "event"),
    ("live_health", [PY, "scripts/sched/check_live_health.py"], "event"),  # stale recorder file / dropped process
    ("canary", [PY, "scripts/dev/testnet_canary.py"], "event"),
    ("autogo", [PY, "scripts/sched/autogo.py", "--tick"], "event"),
    ("sessions", [PY, "scripts/sched/check_sessions.py"], "digest"),
    ("bug_age", [PY, "scripts/sched/check_bug_age.py"], "digest"),
    ("paste_size", [PY, "scripts/sched/check_paste_size.py"], "digest"),
    ("new_aging", [PY, "scripts/sched/check_new_aging.py"], "digest"),
]
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?")


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"event_seen": {}, "digest_included": []}


def save_state(state):
    SCHED_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(STATE)


def run_check(name, argv):
    try:
        p = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return 2, f"{name} RED timeout 120s", state_hash(name, ["timeout"])
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    first = lines[0] if lines else f"{name} RED no output (stderr: {p.stderr.strip()[:120]})"
    hash_line = next((l.split(None, 1)[1].strip() for l in lines if l.startswith("HASH ")), None)
    if hash_line is None:  # non-sched detector (canary): hash name + status + reasons, clock stripped
        hash_line = state_hash(name, [ISO_RE.sub("", first)])
    code = p.returncode if p.returncode in (0, 1, 2) else 2
    return code, first, hash_line


def run_pick():
    try:
        p = subprocess.run([PY, "scripts/sched/pick_task.py"], cwd=REPO, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "ERROR: pick_task timeout 60s"
    except OSError as e:
        return f"ERROR: {e}"
    if p.returncode:
        return f"ERROR: exit {p.returncode}: {(p.stderr.strip() or p.stdout.strip())[:200]}"
    return (p.stdout.strip().splitlines() or ["ERROR: no output"])[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now")
    ap.add_argument("--only")
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else datetime.now(timezone.utc)
    only = set(args.only.split(",")) if args.only else None

    state = load_state()
    state["event_seen"] = {h: t for h, t in state["event_seen"].items()
                           if now - datetime.fromisoformat(t) < DEBOUNCE}
    rows, fires, digest, worst = [], [], [], 0
    for name, argv, kind in CHECKS:
        if only and name not in only:
            continue
        code, first, h = run_check(name, argv)
        worst = max(worst, code)
        action = "none"
        if code:
            if kind == "event" and code == 2:
                if h in state["event_seen"]:
                    action = "debounced(24h)"
                else:
                    action = "FIRE haiku event"
                    state["event_seen"][h] = now.isoformat()
                    fires.append({"check": name, "exit": code, "hash": h, "line": first})
            else:  # digest check, or event check at WARN
                if h in state["digest_included"]:
                    action = "digest(already included)"
                else:
                    action = "digest(new)"
                    digest.append({"check": name, "exit": code, "hash": h, "line": first})
        rows.append((name, kind, code, action, h, first))

    save_state(state)
    (SCHED_DIR / "digest_pending.json").write_text(json.dumps(digest, indent=1) + "\n", encoding="utf-8", newline="\n")
    (SCHED_DIR / "events_fired.json").write_text(json.dumps(fires, indent=1) + "\n", encoding="utf-8", newline="\n")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"tick_{now.strftime(TS_FMT)}.md"
    md = [f"# TICK {now.strftime('%Y-%m-%dT%H:%M:%SZ')}", "", f"worst exit: {worst}", "",
          "| check | kind | exit | action | hash12 |", "|---|---|---|---|---|"]
    md += [f"| {n} | {k} | {c} | {a} | {h[:12]} |" for n, k, c, a, h, _ in rows]
    md += ["", "## Lines", ""] + [f"- {first}" for *_, first in rows]
    out.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    with open(out, "a", encoding="utf-8", newline="\n") as f:  # Pick section; a failure here never stops the tick
        f.write("\n## Pick\n\n" + run_pick() + "\n")
    print(f"TICK worst={worst} fires={len(fires)} digest_new={len(digest)} report={out.name}")
    return worst


if __name__ == "__main__":
    sys.exit(main())
