"""Measure bytes of every source loaded at a Supervisor session start. Run from repo root:
python MyTradingSys/research/context_loading_wiring_2026-10/measure.py
Hook outputs are measured by running each hook with a fake session id (side effects: only the hooks' own cache/state files)."""
import json, os, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
HOME = Path.home()
MEM = HOME / ".claude/projects/C--Users-E-ngineers-IdeaProjects-BinanceDataFeed/memory/MEMORY.md"
FILES = [
 ("CLAUDE.md (project instructions, auto-loaded)", REPO/"CLAUDE.md"),
 ("MEMORY.md (auto-memory index, auto-loaded)", MEM),
 ("roles/supervisor.md (role_loader injects)", REPO/"MyTradingSys/system/roles/supervisor.md"),
 ("handover/SUPERVISOR_A.md (login hand-over, injected)", REPO/"MyTradingSys/system/handover/SUPERVISOR_A.md"),
 ("handover/SUPERVISOR_B.md", REPO/"MyTradingSys/system/handover/SUPERVISOR_B.md"),
 ("research/STATUS.md (boot step 2, read by session)", REPO/"MyTradingSys/research/STATUS.md"),
 ("system/ANNOUNCEMENTS.md (boot step 2, whole file; ACTIVE part is read)", REPO/"MyTradingSys/system/ANNOUNCEMENTS.md"),
 ("system/SUPER_SESSION.md (Boot facts section is read)", REPO/"MyTradingSys/system/SUPER_SESSION.md"),
 ("system/NEXT_SESSION.md (history, read on task pick)", REPO/"MyTradingSys/system/NEXT_SESSION.md"),
 ("system/LESSONS_DIGEST.md (live-path/backtest only)", REPO/"MyTradingSys/system/LESSONS_DIGEST.md"),
 ("system/ROUTING.md (boot step 2 pointer)", REPO/"MyTradingSys/system/ROUTING.md"),
]
print("| Source | Bytes | ~tokens (B/4) |\n|---|---|---|")
tot = 0
for label, p in FILES:
    n = p.stat().st_size if p.exists() else None
    print(f"| {label} | {n if n is not None else 'MISSING'} | {n//4 if n else '-'} |")
HOOKS = [
 ("SessionStart", "trunk_lag.py", "session-start"), ("SessionStart", "shot.py", "hook"), ("SessionStart", "mts_signal.py", "hook"),
 ("SessionStart", "ci_watch.py", "hook"), ("SessionStart", "c_drive_guard.py", "hook"), ("SessionStart", "role_loader.py", "hook"),
 ("UserPromptSubmit", "shot.py", "hook"), ("UserPromptSubmit", "mts_signal.py", "hook"), ("UserPromptSubmit", "ci_watch.py", "hook"),
 ("UserPromptSubmit", "role_loader.py", "hook"), ("UserPromptSubmit", "trunk_lag.py", "hook"),
]
print("\n| Hook event | Script | stdout bytes (fake sid; first prompt `You are Supervisor. Login A.`) |\n|---|---|---|")
env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO))
for ev, s, arg in HOOKS:
    payload = {"hook_event_name": ev, "session_id": "ctxmeasure-"+ev, "prompt": "You are Supervisor. Login A. measure only", "cwd": str(REPO)}
    try:
        r = subprocess.run([sys.executable, str(REPO/"scripts/dev"/s), arg], input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=60, cwd=REPO)
        out = r.stdout
        extra = ""
        if s == "role_loader.py" and out:
            try: extra = f" (additionalContext {len(json.loads(out)['hookSpecificOutput']['additionalContext'].encode())} B)"
            except Exception: pass
        print(f"| {ev} | {s} {arg} | {len(out.encode())}{extra} |")
    except Exception as e:
        print(f"| {ev} | {s} | ERR {e} |")
