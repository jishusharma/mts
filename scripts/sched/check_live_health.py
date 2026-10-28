"""Live health: a recorder/loop output file stopped growing, or a long-running live process dropped.

Read-only on the live system (never starts, stops or edits a process or a live file).
Detector contract (_common): line 1 `live_health <OK|WARN|RED> <reason>`, line 2 `HASH ...`, exit 0/1/2.

Stale files (newest matching file's mtime older than the limit -> RED):
  snapshots, state_code  300 s   loop-supervisor.ps1 $SnapshotStaleSec (same rule the supervisor restarts on)
  orderflow day csv      300 s   one row per closed UTC minute (orderflow_live.py docstring); 5 missed minutes
  oi_1m.csv              300 s   1-minute live OI rows (oi_recorder.py); 5 missed minutes
  htf_context jsonl    15000 s   one row 90 s after each 4H close (htf_context_live.py --loop) + 10 min slack
Processes (command-line regex; none alive -> RED, more than one top-level copy -> WARN):
  java statemachine loop, loop-supervisor.ps1, and the supervisor's $Aux list (auto_trader, live_runner_cli,
  orderflow_live, daily_loss_monitor), plus htf_context_live --loop.
runtime_data/loop_stop.flag present -> WARN "loop stopped by flag" (an intended stop is not an outage).

--alert: on RED, show the desktop popup (scripts/core/show-alert.ps1) when the failing set changed or 60 min
passed since the last popup for the same set. Debounce state: MyTradingSys/runtime/sched/live_health_state.json.
Usage: python scripts/sched/check_live_health.py [--root LIVE_TREE] [--alert] [--procs-json F] [--now EPOCH]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO, emit, run, state_hash

FILES = [  # (name, glob relative to root, stale seconds)
    ("snapshots", "runtime_data/snapshots/BTCUSDT_*.json", 300),
    ("state_code", "MyTradingSys/runtime/state_code.json", 300),
    ("orderflow", "MyTradingSys/runtime/orderflow_live/????-??-??.csv", 300),
    ("oi_1m", "MyTradingSys/runtime/oi_live/oi_1m.csv", 300),
    ("htf_context", "MyTradingSys/research/htf_context/????-??-??.jsonl", 15000),
]
PROCS = [  # (name, command-line regex)
    ("loop_java", r"statemachine"),
    ("loop_supervisor", r"loop-supervisor\.ps1"),
    ("auto_trader", r"MyTradingSys\.execution\.auto_trader"),
    ("live_runner_cli", r"MyTradingSys\.backtest\.layers\.alerts\.live_runner_cli"),
    ("orderflow_live", r"MyTradingSys\.backtest\.layers\.fabio\.orderflow_live"),
    ("daily_loss_monitor", r"daily_loss_monitor\.py"),
    ("htf_context_live", r"MyTradingSys\.backtest\.layers\.fabio\.htf_context_live"),
]
REPOPUP_SEC = 3600
PS_LIST = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine } | "
           "Select-Object @{n='pid';e={$_.ProcessId}},@{n='ppid';e={$_.ParentProcessId}},@{n='cmd';e={$_.CommandLine}} | "
           "ConvertTo-Json -Compress")


def list_procs(procs_json):
    if procs_json:
        return json.loads(Path(procs_json).read_text(encoding="utf-8"))
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST], capture_output=True, text=True,
                         timeout=60, check=True).stdout
    data = json.loads(out or "[]")
    return [data] if isinstance(data, dict) else data


def file_problems(root, now):
    bad = []
    for name, pattern, limit in FILES:
        found = list(root.glob(pattern))
        if not found:
            bad.append((name, f"{name}: no file {pattern}"))
            continue
        age = now - max(p.stat().st_mtime for p in found)
        if age > limit:
            bad.append((name, f"{name}: {int(age)}s since last write (> {limit}s)"))
    return bad


def proc_problems(procs):
    bad, warn = [], []
    for name, pat in PROCS:
        rx = re.compile(pat)
        hits = [p for p in procs if p.get("cmd") and rx.search(p["cmd"])]
        pids = {p["pid"] for p in hits}
        top = [p for p in hits if p.get("ppid") not in pids]  # launcher shim + child count once
        if not top:
            bad.append((name, f"{name}: process not running"))
        elif len(top) > 1:
            warn.append((name, f"{name}: {len(top)} copies running (pids {sorted(p['pid'] for p in top)})"))
    return bad, warn


def popup(root, state_path, h, reason, now):
    try:
        st = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st = {}
    if st.get("hash") == h and now - st.get("at", 0) < REPOPUP_SEC:
        return False
    alert = root / "runtime_data" / "live_health_alert.json"
    body = "MTS live health RED\n\n" + reason.replace("; ", "\n") + "\n\nChecked " + \
        time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(now))
    alert.write_text(json.dumps({"title": "MTS live health RED", "body": reason, "card_text": body,
                                 "repo": str(root)}, indent=1) + "\n", encoding="utf-8", newline="\n")
    subprocess.Popen(["wscript.exe", str(root / "scripts" / "core" / "launch-alert.vbs"),
                      str(root / "scripts" / "core" / "show-alert.ps1"), str(alert)])
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"hash": h, "at": now}) + "\n", encoding="utf-8", newline="\n")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("MTS_LIVE_ROOT", str(REPO)))
    ap.add_argument("--alert", action="store_true")
    ap.add_argument("--procs-json")
    ap.add_argument("--now", type=float)
    a = ap.parse_args(argv)
    root = Path(a.root)
    now = a.now if a.now is not None else time.time()
    if (root / "runtime_data" / "loop_stop.flag").exists():
        return emit("live_health", "WARN", "loop stopped by flag (runtime_data/loop_stop.flag)", ["stop_flag"])
    files = file_problems(root, now)
    procs_bad, procs_warn = proc_problems(list_procs(a.procs_json))
    bad = files + procs_bad
    if bad:
        reason = "; ".join(r for _, r in bad)
        evidence = [n for n, _ in bad]
        if a.alert:
            popup(root, root / "MyTradingSys" / "runtime" / "sched" / "live_health_state.json",
                  state_hash("live_health", evidence), reason, now)
        return emit("live_health", "RED", reason, evidence)
    if procs_warn:
        return emit("live_health", "WARN", "; ".join(r for _, r in procs_warn), [n for n, _ in procs_warn])
    return emit("live_health", "OK", f"{len(FILES)} files fresh, {len(PROCS)} processes up", ["ok"])


if __name__ == "__main__":
    run(main)
