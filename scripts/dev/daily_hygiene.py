#!/usr/bin/env python
"""daily_hygiene.py - the scheduled daily hygiene run (Step 4, 2026-10-10). No Claude, no operator, no network beyond git.

Runs, in order: the offline gate (run_all_tests.py --quick), `sync.py tidy --apply` (repairs case-broken worktree HEADs,
retires finished clean worktrees), `sync.py where` (worktrees holding work not on origin/fast-track),
declutter_backups.py in dry-run mode (never --apply), `desk.py assign` (the scheduled assigner: posts each ready DSA-lane
task card to the desk board once, B180), and make_status.py. Writes one file a session reads at boot:
  MyTradingSys/runtime/sched/hygiene_latest.md   (gitignored; STATUS.md embeds its first lines via make_status.py)
  MyTradingSys/runtime/sched/hygiene_latest.json
Exit 0 when every step passed, 1 when any failed (the gate being red is the case that matters).
Schedule: scripts/sched/register_cicd_tasks.ps1 (Windows Task Scheduler, 06:30 local). Run by hand: python scripts/dev/daily_hygiene.py
"""
import nowin  # B173: no console flash from git/python children under pythonw
nowin.install()
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "MyTradingSys" / "runtime" / "sched"
PY = sys.executable
STEPS = [
    ("gate", [PY, "scripts/dev/run_all_tests.py", "--quick"], 1500, True),
    ("tidy", [PY, "scripts/dev/sync.py", "tidy", "--apply"], 900, False),
    ("where", [PY, "scripts/dev/sync.py", "where"], 120, False),
    ("health", [PY, "scripts/dev/sync.py", "health"], 120, False),
    ("declutter_dry_run", [PY, "scripts/dev/declutter_backups.py"], 300, False),
    ("desk_assign", [PY, "scripts/dev/desk.py", "assign"], 1800, False),
    ("status", [PY, "scripts/dev/make_status.py"], 300, False),
]
TAIL = 8


def subprocess_runner(argv, timeout):
    """-> (returncode, combined output). A timeout is rc 124, never an exception."""
    try:
        p = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    except OSError as e:
        return 127, f"could not start: {e}"


def _tail(text, n=TAIL):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return lines[-n:]


def run(runner=subprocess_runner, now=None, out_dir=OUT_DIR):
    now = now or datetime.now(timezone.utc)
    results = []
    for name, argv, timeout, _ in STEPS:
        t0 = time.time()
        rc, out = runner(argv, timeout)
        results.append({"step": name, "rc": rc, "seconds": round(time.time() - t0, 1), "tail": _tail(out)})
    gate = next(r for r in results if r["step"] == "gate")
    failed = [r["step"] for r in results if r["rc"] != 0]
    status = "GREEN" if not failed else "RED"
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    where = next(r for r in results if r["step"] == "where")
    unshipped = [ln for ln in where["tail"] if ln.startswith("UNSHIPPED")]
    md = [f"# Daily hygiene {stamp} on {platform.node()}", "", f"STATUS: {status}"
          + (f" (failed: {', '.join(failed)})" if failed else ""),
          f"GATE: {'PASS' if gate['rc'] == 0 else 'FAIL'} ({gate['seconds']} s)", ""]
    if unshipped:
        md += ["Unshipped work (commit + `sync.py ship` it):"] + [f"- {u}" for u in unshipped] + [""]
    health = next((r for r in results if r["step"] == "health"), None)
    problems = [ln for ln in (health["tail"] if health else [])
                if ln.split(" ", 1)[0] in ("STALE-CLAIM", "OVERLAP", "ORPHAN", "SHARED", "NEVER-SHIPPED")]
    if problems:
        md += ["Parallel-work collisions (`sync.py health`):"] + [f"- {u}" for u in problems] + [""]
    for r in results:
        md += [f"## {r['step']}: rc {r['rc']} ({r['seconds']} s)", "```"] + r["tail"] + ["```", ""]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "hygiene_latest.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    (out_dir / "hygiene_latest.json").write_text(
        json.dumps({"utc": stamp, "host": platform.node(), "status": status, "failed": failed, "steps": results},
                   indent=1) + "\n", encoding="utf-8", newline="\n")
    return status, results


def main():
    status, results = run()
    for r in results:
        print(f"{r['step']:18} rc {r['rc']}  {r['seconds']} s")
    print(f"hygiene: {status} -> {OUT_DIR / 'hygiene_latest.md'}")
    return 0 if status == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
