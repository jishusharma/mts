"""Scheduled Claude worker wrapper (SCHEDULER_PLAN s2/s3/s6/s7). Spawns one `claude -p` run, bounded and accounted.

  python scripts/sched/run_worker.py --mode event --check canary --exit 2 [--evidence PATH] [--tier haiku]
  python scripts/sched/run_worker.py --mode digest
  python scripts/sched/run_worker.py --print-prefix-hash [--prefix-file F]   (cache-discipline probe; exit 3 if unstable)
  add --dry-run to print the command, prefix hash and cap decision without locking, spawning or touching the ledger.

Guards: per-job atomic lock dir (os.mkdir) with owner.json {pid, ctime, start, ttl}; stale = dead PID / ctime mismatch /
TTL expired. Child runs in a Windows Job Object (kill-on-close) with a wall-clock TTL. Ledger
MyTradingSys/runtime/sched/ledger.jsonl: reserve row before, actual row after. Caps by monthly spend:
>= $10 no sonnet/opus, >= $15 haiku digest only, >= $18 nothing. Prompt = worker_prefix.md bytes + variable tail.
Worker tools are read-only (Read, Grep, Glob); this wrapper writes the report itself under sched_reports/.
Exit: 0 ran or skipped (SKIPPED_LOCKED / SKIPPED_CAP), 1 worker error, 3 bad prefix.
"""
import argparse
import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime, timezone

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO

SCHED = REPO / "MyTradingSys" / "runtime" / "sched"
LOCKS = SCHED / "locks"
LEDGER = SCHED / "ledger.jsonl"
REPORTS = REPO / "MyTradingSys" / "research" / "sched_reports"
PREFIX_FILE = REPO / "MyTradingSys" / "system" / "sched" / "worker_prefix.md"
CLAUDE_FALLBACK = r"C:\Users\E-ngineers\.local\bin\claude.exe"

# tier -> (max_turns, max_budget_usd, ttl_seconds)  [SCHEDULER_PLAN s2, s6]
TIERS = {"haiku": (8, 0.10, 600), "sonnet": (25, 0.60, 1200), "opus": (15, 1.00, 900)}
CAP_NO_BIG, CAP_DIGEST_ONLY, CAP_STOP = 10.0, 15.0, 18.0
VOLATILE = re.compile(rb"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|\d{8}T\d{6}Z")
ALLOWED_TOOLS = "Read Grep Glob"

# ---------------------------------------------------------------- prefix
def prefix_problems(data):
    probs = []
    if b"\r" in data:
        probs.append("CRLF")
    if VOLATILE.search(data):
        probs.append("timestamp/date in prefix")
    if any(l != l.rstrip() for l in data.decode("utf-8", "replace").split("\n")):
        probs.append("trailing whitespace")
    if not data.endswith(b"=== RUN ===\n"):
        probs.append("missing RUN terminator")
    return probs


def load_prefix(path=PREFIX_FILE):
    return pathlib_read(path)


def pathlib_read(path):
    with open(path, "rb") as f:
        return f.read()


# ---------------------------------------------------------------- windows process helpers
# Windows only. Off Windows (CI ubuntu, cloud) _k32 is None so --print-prefix-hash and --dry-run still work;
# anything that needs a PID check or a Job Object raises instead of running unbounded (fail closed).
if os.name == "nt":
    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.OpenProcess.restype = wintypes.HANDLE
    _k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]
    _k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    _k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    _k32.CreateJobObjectW.restype = wintypes.HANDLE
    _k32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    _k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    _k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
else:
    _k32 = None


def _need_k32():
    if _k32 is None:
        raise OSError("run_worker: Windows process helpers (kernel32) unavailable on this OS")
    return _k32


def pid_ctime(pid):
    """Creation time (epoch seconds) of a running PID, or None if it is not running."""
    h = _need_k32().OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return None
    try:
        code = wintypes.DWORD()
        if not _k32.GetExitCodeProcess(h, ctypes.byref(code)) or code.value != 259:  # STILL_ACTIVE
            return None
        c, e, k, u = (wintypes.FILETIME() for _ in range(4))
        if not _k32.GetProcessTimes(h, *(ctypes.byref(x) for x in (c, e, k, u))):
            return None
        ticks = (c.dwHighDateTime << 32) | c.dwLowDateTime
        return ticks / 1e7 - 11644473600
    finally:
        _k32.CloseHandle(h)


class _BasicLimit(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]


class _IoCounters(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint64) for n in ("r_ops", "w_ops", "o_ops", "r_bytes", "w_bytes", "o_bytes")]


class _ExtLimit(ctypes.Structure):
    _fields_ = [("Basic", _BasicLimit), ("Io", _IoCounters), ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


def make_kill_on_close_job():
    job = _need_k32().CreateJobObjectW(None, None)
    if not job:
        raise OSError(ctypes.get_last_error(), "CreateJobObject failed")
    info = _ExtLimit()
    info.Basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not _k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
        raise OSError(ctypes.get_last_error(), "SetInformationJobObject failed")
    return job


# ---------------------------------------------------------------- locks
def now_utc():
    return datetime.now(timezone.utc)


def acquire_lock(job, ttl_s, wait_s=0.0):
    """True if acquired. Stale lock (dead PID, ctime mismatch, TTL expired) is removed and re-acquired once."""
    LOCKS.mkdir(parents=True, exist_ok=True)
    d = LOCKS / f"{job}.lock"
    deadline = time.time() + wait_s
    while True:
        for attempt in (1, 2):
            try:
                os.mkdir(d)
            except FileExistsError:
                if attempt == 2 or not _lock_stale(d):
                    break
                shutil.rmtree(d, ignore_errors=True)
                continue
            owner = {"pid": os.getpid(), "ctime": pid_ctime(os.getpid()), "start_utc": now_utc().isoformat(),
                     "start_epoch": time.time(), "ttl_s": ttl_s, "job": job}
            (d / "owner.json").write_text(json.dumps(owner), encoding="utf-8", newline="\n")
            return True
        if time.time() >= deadline:
            return False
        time.sleep(0.2)


def _lock_stale(d):
    try:
        o = json.loads((d / "owner.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return time.time() - d.stat().st_mtime > 30  # owner.json never written: crashed between mkdir and write
    if time.time() - o["start_epoch"] > o["ttl_s"]:
        return True
    ct = pid_ctime(o["pid"])
    return ct is None or (o.get("ctime") is not None and abs(ct - o["ctime"]) > 2)


def release_lock(job):
    shutil.rmtree(LOCKS / f"{job}.lock", ignore_errors=True)


# ---------------------------------------------------------------- ledger / caps
def ledger_rows():
    try:
        return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    except OSError:
        return []


def ledger_append(row):
    SCHED.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def month_spend(rows, month):
    """Per run_id: actual if present else reserve (a run not confirmed ended still counts as reserved)."""
    best = {}
    for r in rows:
        if not r.get("ts", "").startswith(month):
            continue
        if r["phase"] == "actual" or r["run_id"] not in best:
            best[r["run_id"]] = r["usd"]
    return sum(best.values())


def cap_decision(spend, tier, mode):
    if spend >= CAP_STOP:
        return False, f"spend ${spend:.2f} >= ${CAP_STOP:.0f}: all Claude runs stopped"
    if spend >= CAP_DIGEST_ONLY and not (tier == "haiku" and mode == "digest"):
        return False, f"spend ${spend:.2f} >= ${CAP_DIGEST_ONLY:.0f}: haiku digest only"
    if spend >= CAP_NO_BIG and tier != "haiku":
        return False, f"spend ${spend:.2f} >= ${CAP_NO_BIG:.0f}: sonnet/opus disabled"
    return True, f"spend ${spend:.2f} ok"


# ---------------------------------------------------------------- run
def find_claude():
    return shutil.which("claude") or CLAUDE_FALLBACK


def supports_flag(claude, flag):
    try:
        p = subprocess.run([claude, "--help"], capture_output=True, text=True, timeout=60)
        return flag in p.stdout
    except (OSError, subprocess.TimeoutExpired):
        return False


def evidence_excerpt(path, limit=3000):
    if not path:
        return "(none)"
    p = REPO / path if not os.path.isabs(path) else __import__("pathlib").Path(path)
    try:
        return p.read_bytes()[:limit].decode("utf-8", "replace")
    except OSError as e:
        return f"(unreadable: {e})"


def build_prompt(prefix, mode, check, exit_code, evidence, utc):
    tail = (f"mode: {mode}\ncheck: {check}\nexit: {exit_code}\nevidence_path: {evidence or '(none)'}\n"
            f"evidence_excerpt:\n{evidence_excerpt(evidence)}\nutc: {utc}\n")
    return prefix + tail.encode("utf-8")


def spawn(cmd, prompt, ttl):
    """Run cmd in a kill-on-close Job Object; wall-clock TTL kills the whole tree. Returns (rc, out, err, pid, timed_out)."""
    job = make_kill_on_close_job()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=REPO)
    _k32.AssignProcessToJobObject(job, int(proc._handle))
    timed_out = False
    try:
        out, err = proc.communicate(prompt, timeout=ttl)
    except subprocess.TimeoutExpired:
        timed_out = True
        _k32.TerminateJobObject(job, 1)
        out, err = proc.communicate()
    finally:
        _k32.CloseHandle(job)  # kill-on-close reaps anything still alive
    return proc.returncode, out, err, proc.pid, timed_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("event", "digest"))
    ap.add_argument("--check", default="digest")
    ap.add_argument("--exit", type=int, default=0, dest="exit_code")
    ap.add_argument("--evidence")
    ap.add_argument("--tier", choices=tuple(TIERS), default="haiku")
    ap.add_argument("--prefix-file", default=str(PREFIX_FILE))
    ap.add_argument("--print-prefix-hash", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    prefix = load_prefix(a.prefix_file)
    phash = hashlib.sha256(prefix).hexdigest()
    probs = prefix_problems(prefix)
    if a.print_prefix_hash:
        print(phash)
        if probs:
            print("PREFIX PROBLEMS: " + "; ".join(probs), file=sys.stderr)
            return 3
        return 0
    if probs:
        print("PREFIX PROBLEMS: " + "; ".join(probs), file=sys.stderr)
        return 3
    if not a.mode:
        ap.error("--mode required")

    tier = a.tier
    max_turns, budget, ttl = TIERS[tier]
    month = now_utc().strftime("%Y-%m")
    ok, why = cap_decision(month_spend(ledger_rows(), month), tier, a.mode)
    utc = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    claude = find_claude()
    cmd = [claude, "-p", "--model", tier, "--output-format", "json", "--max-budget-usd", f"{budget:.2f}",
           "--allowedTools", ALLOWED_TOOLS, "--permission-mode", "default", "--no-session-persistence"]
    turns_flag = supports_flag(claude, "--max-turns")
    if turns_flag:
        cmd[2:2] = ["--max-turns", str(max_turns)]
    job = f"{tier}-{a.check}"

    if a.dry_run:
        print(json.dumps({"job": job, "cmd": cmd, "max_turns_flag_supported": turns_flag, "ttl_s": ttl,
                          "prefix_sha256": phash, "prefix_bytes": len(prefix), "cap_ok": ok, "cap_reason": why}, indent=1))
        return 0
    if not ok:
        print(f"SKIPPED_CAP {job}: {why}")
        return 0
    if not acquire_lock(job, ttl):
        print(f"SKIPPED_LOCKED {job}")
        return 0
    held = [job]
    try:
        if tier in ("sonnet", "opus"):
            if not acquire_lock("tree", ttl):
                print(f"SKIPPED_LOCKED tree ({job})")
                return 0
            held.append("tree")
        run_id = f"{utc}-{job}-{os.getpid()}"
        if acquire_lock("ledger", 30, wait_s=10):  # brief lock so cap-read + reserve is not racy
            try:
                ok, why = cap_decision(month_spend(ledger_rows(), month), tier, a.mode)
                if not ok:
                    print(f"SKIPPED_CAP {job}: {why}")
                    return 0
                ledger_append({"ts": utc, "run_id": run_id, "phase": "reserve", "job": job, "tier": tier,
                               "mode": a.mode, "usd": budget, "prefix_sha256": phash})
            finally:
                release_lock("ledger")
        else:
            print(f"SKIPPED_LOCKED ledger ({job})")
            return 0
        prompt = build_prompt(prefix, a.mode, a.check, a.exit_code, a.evidence, utc)
        t0 = time.time()
        rc, out, err, pid, timed_out = spawn(cmd, prompt, ttl)
        usd, result, turns, is_error = budget, "", None, True  # unknown cost => assume the full reserve
        try:
            j = json.loads(out.decode("utf-8", "replace"))
            usd = float(j.get("total_cost_usd", budget))
            result, turns, is_error = j.get("result", ""), j.get("num_turns"), bool(j.get("is_error"))
        except (ValueError, TypeError):
            result = out.decode("utf-8", "replace")[:2000] + "\n" + err.decode("utf-8", "replace")[:500]
        ledger_append({"ts": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), "run_id": run_id, "phase": "actual",
                       "job": job, "tier": tier, "mode": a.mode, "usd": usd, "rc": rc, "timed_out": timed_out,
                       "turns": turns, "is_error": is_error, "pid": pid, "pid_gone": pid_ctime(pid) is None,
                       "secs": round(time.time() - t0, 1), "max_turns_flag": turns_flag, "prefix_sha256": phash})
        REPORTS.mkdir(parents=True, exist_ok=True)
        rep = REPORTS / f"worker_{tier}_{a.mode}_{a.check}_{utc.replace(':', '').replace('-', '')}.md"
        rep.write_text(f"# WORKER {tier} {a.mode} {a.check} {utc}\n\nrc={rc} timed_out={timed_out} usd={usd} "
                       f"turns={turns}\n\n{result}\n", encoding="utf-8", newline="\n")
        if a.mode == "digest" and rc == 0 and not is_error:
            _mark_digest_included()
        print(f"WORKER {job} rc={rc} usd={usd:.4f} turns={turns} report={rep.name}")
        return 0 if rc == 0 and not is_error and not timed_out else 1
    finally:
        for j in reversed(held):
            release_lock(j)


def _mark_digest_included():
    try:
        pend = json.loads((SCHED / "digest_pending.json").read_text(encoding="utf-8"))
        st_path = SCHED / "tick_state.json"
        st = json.loads(st_path.read_text(encoding="utf-8")) if st_path.exists() else {"event_seen": {}}
        st["digest_included"] = sorted({p["hash"] for p in pend})
        st_path.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    except (OSError, ValueError, KeyError):
        pass


if __name__ == "__main__":
    sys.exit(main())
