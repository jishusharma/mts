"""Headless launcher (B094): start the next queued slot without the operator typing `mts go`.

Operator rule (2026-10-03): "enable it when operator askes and remember to disable ot whenit makes no sense to run it".
Enable is operator-only: runtime/sched/autogo_enabled must exist; `--enable --words "<operator words>"` creates it and
logs the words. Disable is automatic: any sense condition below removes the flag and logs the reason.
Sense conditions (each derived from disk): brake file (HALT, HALT_DAILY_LOSS, AUTO_PAUSE in execution/, existence only);
canary RED; no pickable slot; every slot older than STALE_H hours and never launched (the 2026-10-03 TF1 case).
Skips (flag stays, nothing launched this tick): running inside Claude Code (B086), a launched run still alive, a slot
launched within the last STALE_H hours.
One launch per tick, via go.py --id <rid> --headless (go.py carries the per-run --max-budget-usd cap).
Log: runtime/sched/autogo_log.jsonl. Stdout: `autogo <OK|WARN|RED> <reason>` + HASH (detector contract).
Test hooks: MTS_PICK_ROOT repo root, MTS_AUTOGO_CANARY canary command (default scripts/dev/testnet_canary.py), MTS_AUTOGO_NOW ISO.
Usage (repo root): python scripts/sched/autogo.py --tick | --enable --words "<text>" | --disable | --status
"""
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("MTS_PICK_ROOT") or HERE.parents[1])
SCHED = ROOT / "MyTradingSys" / "runtime" / "sched"
SLOTS = ROOT / "MyTradingSys" / "runtime" / "queue" / "slots"
EXEC = ROOT / "MyTradingSys" / "execution"
FLAG = SCHED / "autogo_enabled"
LOG = SCHED / "autogo_log.jsonl"
STATE = SCHED / "autogo_state.json"
BRAKES = ("HALT", "HALT_DAILY_LOSS", "AUTO_PAUSE")
STALE_H = 24
TS = "%Y-%m-%dT%H:%M:%SZ"


def now_utc():
    v = os.environ.get("MTS_AUTOGO_NOW")
    return datetime.fromisoformat(v.replace("Z", "+00:00")) if v else datetime.now(timezone.utc)


def log(event, now, **kw):
    SCHED.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"utc": now.strftime(TS), "event": event, **kw}, sort_keys=True) + "\n")


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"launched": {}, "pid": None}


def save_state(st):
    SCHED.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def pid_alive(pid):
    if not pid:
        return False
    if os.name == "nt":  # os.kill(pid, 0) would terminate on Windows
        out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out.split()
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:  # an exited child nobody reaped (orphan under a non-reaping PID 1, e.g. a container) is a zombie, not alive
        return Path("/proc/%d/stat" % pid).read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return True


def slots():
    rows = []
    for j in sorted(SLOTS.glob("*.json")):
        txt = j.with_suffix(".txt")
        try:
            meta = json.loads(j.read_text(encoding="utf-8"))
            body = txt.read_text(encoding="utf-8").strip()
        except (OSError, ValueError):
            continue
        if body and not body.startswith("IDLE"):
            rows.append(meta)
    return rows


def canary_red():
    cmd = os.environ.get("MTS_AUTOGO_CANARY")
    argv = shlex.split(cmd) if cmd else [sys.executable, str(HERE.parent / "dev" / "testnet_canary.py")]
    try:
        p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=100)
    except (OSError, subprocess.TimeoutExpired):
        return True  # fail closed
    return p.returncode not in (0, 1)


def disable_reason(rows, st, now):
    present = [b for b in BRAKES if (EXEC / b).exists()]
    if present:
        return "brake file present: " + ",".join(present)
    if canary_red():
        return "canary RED"
    if not rows:
        return "no pickable slot"
    cutoff = now - timedelta(hours=STALE_H)
    fresh = []
    for r in rows:
        try:
            t = datetime.strptime(r.get("composed_utc", ""), TS).replace(tzinfo=timezone.utc)
        except ValueError:
            t = now
        if r["id"] in st["launched"] or t > cutoff:
            fresh.append(r)
    if not fresh:
        return "every slot held over %dh with no launch" % STALE_H
    return None


def tick():
    now = now_utc()
    if not FLAG.exists():
        return emit("autogo", "OK", "disabled (no flag file)", ["disabled"])
    st = load_state()
    rows = slots()
    why = disable_reason(rows, st, now)
    if why:
        FLAG.unlink()
        log("auto_disable", now, reason=why)
        return emit("autogo", "WARN", "auto-disabled: " + why, ["disable", why])
    if os.environ.get("CLAUDECODE"):
        return emit("autogo", "OK", "skip: inside Claude Code (one writer per tree)", ["skip-cc"])
    if pid_alive(st.get("pid")):
        return emit("autogo", "OK", "skip: launched run pid %s still alive" % st["pid"], ["skip-alive"])
    recent = {k: v for k, v in st["launched"].items()
              if now - datetime.strptime(v, TS).replace(tzinfo=timezone.utc) < timedelta(hours=STALE_H)}
    st["launched"] = recent
    todo = [r for r in rows if r["id"] not in recent]
    if not todo:
        save_state(st)
        return emit("autogo", "OK", "skip: every slot already launched in the last %dh" % STALE_H, ["skip-done"])
    rid = todo[0]["id"]
    try:
        child = subprocess.Popen([sys.executable, str(HERE / "go.py"), "--id", rid, "--headless"], cwd=ROOT)
    except OSError as e:
        log("launch_error", now, id=rid, error=str(e))
        return emit("autogo", "RED", "cannot start go.py for %s: %s" % (rid, e), ["launch-error", rid])
    st["launched"][rid] = now.strftime(TS)
    st["pid"] = child.pid
    save_state(st)
    log("launch", now, id=rid, pid=child.pid)
    return emit("autogo", "OK", "launched %s (pid %d)" % (rid, child.pid), ["launch", rid])


def main(argv):
    now = now_utc()
    if "--enable" in argv:
        words = argv[argv.index("--words") + 1] if "--words" in argv and argv.index("--words") + 1 < len(argv) else ""
        if not words.strip():
            print("autogo: --enable needs --words \"<operator words that authorize it>\"", file=sys.stderr)
            return 2
        SCHED.mkdir(parents=True, exist_ok=True)
        FLAG.write_text(words.strip() + "\n", encoding="utf-8", newline="\n")
        log("enable", now, words=words.strip())
        print("autogo enabled")
        return 0
    if "--disable" in argv:
        if FLAG.exists():
            FLAG.unlink()
        log("disable", now, reason="operator")
        print("autogo disabled")
        return 0
    if "--status" in argv:
        print("autogo %s" % ("ENABLED" if FLAG.exists() else "disabled"))
        return 0
    if "--tick" in argv:
        return tick()
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
