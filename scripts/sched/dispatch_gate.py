"""Model-free dispatcher gate (operator 2026-10-15): run `relay.py tick` from Task Scheduler, start Claude only on `TICK KICK`.

Before, every 10-minute tick was a full Haiku session whose only job was to run this one script and print `TICK NOOP`.
Now the gate runs the same call in plain python: NOOP costs nothing; KICK launches ONE headless relay session with the tick
output (NEXT / UNLOCK commands and relay_session.md) as its prompt. The hourly refine and housekeep items need App-only tools, so
the gate runs the refiner status itself (tick --gate, own clock) and launches a session only for REFINE_NEEDED. Housekeep needs App-only tools, so the `mts-dispatcher` App routine runs once a day (cron `7 3 * * *`).

  python scripts/sched/dispatch_gate.py [--root <live tree>] [--peer-quiet-min 90] [--launcher "<argv>"] [--dry-run]

Log: ~/.claude/mts-dispatch-gate.log (one line per run). Exit 0; 1 = unparsable tick; 2 = no launcher binary (claude missing: the gate does nothing, so it never strands the lock).
Test hooks: MTS_GATE_RELAY (path of the relay.py to run), MTS_GATE_LAUNCHER (launcher argv, prompt on stdin), MTS_RELAY_HOME.
"""
import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_FALLBACK = r"C:\Users\E-ngineers\.local\bin\claude.exe"
HOURLY_MIN = "60"   # minutes: the gate runs the refiner status itself (model-free); the App routine only does the daily housekeep
REFINE_PREAMBLE = (
    "MTS refiner run (started headless by dispatch_gate.py, unattended, never ask). The hourly tick found cards to refine. Do "
    "MyTradingSys/system/TASK_REFINEMENT.md 'Refiner run' step 3 inside ../mts-refiner (beside the live tree), nothing else, and keep output "
    "short. Do NOT run `relay.py tick` or `kick`. CLAUDE.md hard rules apply.\n\n"
)
PREAMBLE = (
    "MTS dispatcher KICK (started headless by dispatch_gate.py, unattended, never ask). You are the relay session. The tick already ran "
    "and took the launch lock: do NOT run `relay.py tick` or `kick` again. Follow the text below exactly, run the UNLOCK command last "
    "unless it says --stop, and keep output short. CLAUDE.md hard rules apply.\n\n"
)


def home():
    return Path(os.environ.get("MTS_RELAY_HOME") or Path.home() / ".claude")


def log(msg):
    try:
        home().mkdir(parents=True, exist_ok=True)
        with open(home() / "mts-dispatch-gate.log", "a", encoding="utf-8", newline="\n") as f:
            f.write("%s %s\n" % (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), msg[:300]))
    except OSError:
        pass


def fetch_scripts(root):
    """Copy relay.py + handoff_lint.py from origin/fast-track (the live tree lags), like the App prompt did. Returns relay.py path."""
    override = os.environ.get("MTS_GATE_RELAY")
    if override:
        return Path(override)
    d = Path(tempfile.gettempdir()) / "mts_relay"
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(root), "fetch", "-q", "origin", "fast-track"], capture_output=True, timeout=120)
    for name in ("relay", "handoff_lint"):
        r = subprocess.run(["git", "-C", str(root), "show", "origin/fast-track:scripts/sched/%s.py" % name],
                           capture_output=True, timeout=60)
        if r.returncode == 0 and r.stdout:
            (d / (name + ".py")).write_bytes(r.stdout)
    return d / "relay.py"


def launcher_argv(arg):
    spec = arg or os.environ.get("MTS_GATE_LAUNCHER")
    if spec:
        return [t.strip('"') for t in shlex.split(spec, posix=False)]   # posix=False keeps Windows backslashes, and the quotes
    claude = shutil.which("claude") or CLAUDE_FALLBACK
    return [claude, "-p", "--model", "haiku", "--permission-mode", "bypassPermissions", "--max-budget-usd", "2.00"]


def decide(out):
    """('NOOP'|'KICK'|'ERROR', first TICK line) from the tick output."""
    first = next((ln for ln in out.splitlines() if ln.startswith("TICK ")), "")
    if first.startswith("TICK KICK"):
        return "KICK", first
    if first.startswith("TICK NOOP"):
        return "NOOP", first
    return "ERROR", first or "no TICK line"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--peer-quiet-min", default="90")
    ap.add_argument("--launcher", help="argv of the session launcher, prompt on stdin (default: claude -p, Haiku)")
    ap.add_argument("--dry-run", action="store_true", help="decide and print, never launch")
    a = ap.parse_args(argv)
    argv0 = launcher_argv(a.launcher)[0]
    if not (shutil.which(argv0) or Path(argv0).is_file()):   # tick would take the launch lock and strand it: leave the App routine in charge
        log("NO_LAUNCHER %s: gate idle, the App routine keeps ticking" % argv0)
        print("GATE NO_LAUNCHER", argv0)
        return 2
    relay = fetch_scripts(a.root)
    w = subprocess.run([sys.executable, str(relay), "watchdog"], capture_output=True, text=True, encoding="utf-8", timeout=60)
    if "RESUMED" in w.stdout:   # a dead super-session coordinator left the relay stopped; relay.py logged who/why/age
        log(w.stdout.strip())
    r = subprocess.run([sys.executable, str(relay), "tick", "--root", a.root, "--peer-quiet-min", a.peer_quiet_min,
                        "--hourly-min", HOURLY_MIN, "--gate"], capture_output=True, text=True, encoding="utf-8", timeout=300)
    verdict, line = decide(r.stdout)
    if verdict == "ERROR":
        log("ERROR tick: %s | rc=%s %s" % (line, r.returncode, (r.stderr.strip().splitlines() or [""])[-1]))
        print("GATE ERROR", line)
        return 1
    if verdict == "NOOP":
        log(line)
        hourly = next((ln for ln in r.stdout.splitlines() if ln.startswith("HOURLY ")), "")
        if "refine=REFINE_NEEDED" in hourly and not a.dry_run:   # the only hourly item that needs a model; an idle hour launches nothing
            try:
                p = subprocess.run(launcher_argv(a.launcher), input=REFINE_PREAMBLE + hourly, capture_output=True, text=True,
                                   encoding="utf-8", timeout=3600, cwd=a.root)
                log("REFINE launched rc=%s" % p.returncode)
            except (OSError, subprocess.SubprocessError) as e:
                log("REFINE launch FAILED (%s): %s" % (type(e).__name__, e))
        print("GATE NOOP", line)
        return 0
    if a.dry_run:
        log("DRY " + line)
        print("GATE KICK (dry-run)", line)
        return 0
    try:
        p = subprocess.run(launcher_argv(a.launcher), input=PREAMBLE + r.stdout, capture_output=True, text=True,
                           encoding="utf-8", timeout=3600, cwd=a.root)
        log("KICK launched rc=%s | %s" % (p.returncode, line))
        if p.returncode:   # the launch never ran the relay: free the lock so the next tick retries instead of waiting it out
            subprocess.run([sys.executable, str(relay), "unlock"], capture_output=True, text=True)
        print("GATE KICK rc=%s" % p.returncode, line)
    except (OSError, subprocess.SubprocessError) as e:
        subprocess.run([sys.executable, str(relay), "unlock"], capture_output=True, text=True)
        log("KICK launch FAILED (%s): %s" % (type(e).__name__, e))
        print("GATE KICK launch failed", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
