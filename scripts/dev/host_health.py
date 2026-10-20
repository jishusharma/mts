"""Host-health preflight for `sync.py ship` and `sync.py health` (2026-10-20: ships stalled for hours because the 8-CPU box sat at 100%
with a processor queue of ~100: forgotten processes and desktop apps starved the BELOW_NORMAL gates; see
MyTradingSys/research/traffic/FLOW_2026-10-20.md "Ship root cause" and scripts/dev/proc_job.py, which stop false timeouts and orphan gates
of ships that DIE; this module cleans up what is already dead or forgotten and warns about the rest). No scheduler, no daemon: it runs
inside every ship and on demand.

  1. REAP what is provably dead: orphan gate trees (run_all_tests.py whose parent chain has no live claude.exe and no live ship/deploy
     process), ship-queue tickets and gate slots whose owner PID is dead or was reused by a younger process.
  2. STRAYS: a process outside the repo's known set with >= STRAY_CPU_S CPU seconds. Reported with PID, owner chain, CPU-s, age and the
     exact stop command (host file + one operator desk card per new stray); killed only when MyTradingSys/system/STRAY_REAP_POLICY.md
     allow-lists its command line.
  3. DISK: C: free space and its growth; below the threshold names the largest folders in the temp dir and the worktree dirs and deletes
     only this repo's own temp caches (OWN_TEMP_PREFIXES) older than a day.
  4. QUEUE: processor queue above 4 x CPUs: warn and name the top CPU consumers over a 10 s window.

Never kills: the live trading system (.mts_live, live_runner_cli, loop-supervisor, start-trading-day), this process and its ancestors,
another session's live ship (a gate with a live claude.exe / ship process above it). Fail closed: any error is logged to
<temp>/mts_host_health/health.log and never blocks a ship (run_safe never raises).

Usage: python scripts/dev/host_health.py [--no-reap] [--no-post]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

IS_WIN = os.name == "nt"
STRAY_CPU_S = 3600           # OURS (2026-10-20 incident: strays had 37000-60000 CPU-s; normal tools stay far below an hour)
STRAY_MIN_AGE_S = 2 * 3600   # OURS: a long CPU burn over hours, not a short build
QUEUE_FACTOR = 4             # OURS (spec): queue above 4 x CPUs = overloaded (healthy is ~1 x)
SAMPLE_S = 10
MIN_FREE_GB = float(os.environ.get("MTS_C_MIN_FREE_GB", "15"))   # same threshold as c_drive_guard.py
FALL_GB_PER_H = 2.0          # OURS: C: losing more than this per hour is warned about even above the threshold
OWN_TEMP_PREFIXES = ("mts_s4_", "mts_changed_")   # the only temp dirs this module deletes (this repo created them)
OWN_TEMP_AGE_H = 24
ORPHAN_MIN_AGE_S = 120       # a gate younger than this may still be attaching to its parent
PROTECTED = (".mts_live", "live_runner_cli", "loop-supervisor", "start-trading-day")
SHIP_CHAIN = ("sync.py", "auto_deploy", "wait_then_ship", "cicd_run")   # a live process of one of these above a gate = a live ship/deploy
SKIP_NAMES = {"system", "idle", "registry", "smss.exe", "csrss.exe", "wininit.exe", "services.exe", "lsass.exe", "svchost.exe",
              "dwm.exe", "winlogon.exe", "msmpeng.exe", "memory compression", "fontdrvhost.exe", "claude.exe", "chrome.exe",
              "msedge.exe", "searchindexer.exe", "system idle process", "wmiprvse.exe", "audiodg.exe", "sihost.exe"}
POLICY_REL = "MyTradingSys/system/STRAY_REAP_POLICY.md"
POLICY_TEXT = """# Stray-process reap policy

`sync.py ship` and `sync.py health` run `scripts/dev/host_health.py`. It REPORTS a stray CPU hog (a process outside the repo's known
set with 3600+ CPU-seconds) to the operator desk with the exact stop command. It stops one itself only when its command line matches a
line of the allow-list below. Never reaped whatever is listed: .mts_live, live_runner_cli, loop-supervisor, start-trading-day,
claude.exe, the ship/deploy processes.

How the operator pre-approves a pattern: add one line `- allow: <text>` under "Allow-list" (case-insensitive; the text must appear in
the process command line, e.g. `- allow: python vp.py`). Remove the line to withdraw it. Commit it through `sync.py ship`.

## Allow-list
"""


def state_dir():
    d = Path(os.environ.get("MTS_HOST_HEALTH_DIR") or Path(tempfile.gettempdir()) / "mts_host_health")
    d.mkdir(parents=True, exist_ok=True)
    return d


def log(msg):
    try:
        with open(state_dir() / "health.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}\n")
    except OSError:
        pass


def _ps(script, timeout=90):
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True,
                       timeout=timeout)
    if r.returncode:
        raise OSError(f"powershell failed: {r.stderr.strip()[:200]}")
    return r.stdout


_SNAP_PS = ("Get-CimInstance Win32_Process | ForEach-Object { [pscustomobject]@{pid=[int]$_.ProcessId; ppid=[int]$_.ParentProcessId; "
            "name=$_.Name; cmd=$_.CommandLine; created=$(if($_.CreationDate){([DateTimeOffset]$_.CreationDate).ToUnixTimeSeconds()}else{0}); "
            "cpu=([double]$_.KernelModeTime+[double]$_.UserModeTime)/1e7} } | ConvertTo-Json -Compress")


def snapshot():
    """[{pid, ppid, name, cmd, created (epoch s), cpu (CPU seconds)}] of every process; [] off Windows."""
    if not IS_WIN:
        return []
    rows = json.loads(_ps(_SNAP_PS) or "[]")
    rows = [rows] if isinstance(rows, dict) else rows
    return [{"pid": r["pid"], "ppid": r["ppid"], "name": r.get("name") or "", "cmd": r.get("cmd") or "",
             "created": r.get("created") or 0, "cpu": r.get("cpu") or 0.0} for r in rows]


def queue_length():
    if not IS_WIN:
        return 0
    return int(float(_ps("(Get-CimInstance Win32_PerfFormattedData_PerfOS_System).ProcessorQueueLength").strip() or 0))


def kill_tree(pid):
    r = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True)
    return r.returncode == 0


def alive_pid(pid):
    try:
        from sync import pid_alive
        return pid_alive(pid)
    except Exception:
        return False


# ---- process-tree helpers (pure, tested with synthetic snapshots) ----

def index(procs):
    return {p["pid"]: p for p in procs}


def chain(procs_by_pid, pid):
    """Process rows from pid's parent up to the root. Stops at a missing parent or a PID that was reused (parent younger than child)."""
    out, seen, cur = [], {pid}, procs_by_pid.get(pid)
    while cur:
        par = procs_by_pid.get(cur["ppid"])
        if not par or par["pid"] in seen or (par["created"] and cur["created"] and par["created"] > cur["created"]):
            break
        out.append(par)
        seen.add(par["pid"])
        cur = par
    return out


def own_pids(procs_by_pid, me=None):
    me = me or os.getpid()
    return {me} | {p["pid"] for p in chain(procs_by_pid, me)}


def is_protected(row, ancestors=()):
    text = " ".join([row["cmd"]] + [a["cmd"] for a in ancestors]).lower()
    return any(m in text for m in PROTECTED)


def find_orphan_gates(procs, now=None, me=None):
    """run_all_tests.py processes with no live claude.exe and no live ship/deploy process above them. Returns top-most such pids only."""
    now = now or time.time()
    by = index(procs)
    keep = own_pids(by, me)
    orphans = []
    for p in procs:
        if "run_all_tests.py" not in p["cmd"] or p["pid"] in keep:
            continue
        if p["created"] and now - p["created"] < ORPHAN_MIN_AGE_S:
            continue
        up = chain(by, p["pid"])
        if is_protected(p, up) or any(a["name"].lower() == "claude.exe" for a in up):
            continue
        if any(m in a["cmd"] for a in up for m in SHIP_CHAIN):
            continue
        orphans.append(p)
    ids = {p["pid"] for p in orphans}
    # a gate whose own parent is also a reaped gate is covered by the parent's tree kill
    return [p for p in orphans if p["ppid"] not in ids]


def dead_owner_files(d, now=None, alive=alive_pid, started=None):
    """Ship-queue tickets (*.json {pid, t}) and gate slots (slot-N holding a PID) in directory d whose owner is dead, or alive only as a
    younger process (PID reuse). started(pid) -> process creation epoch or None. Returns [(path, pid, why)]."""
    now = now or time.time()
    out = []
    for p in sorted(d.glob("*")):
        if p.suffix == ".tmp":
            continue
        try:
            raw = p.read_text(encoding="utf-8").strip()
            if p.suffix == ".json":
                info = json.loads(raw)
                pid, t = int(info["pid"]), float(info.get("t") or p.stat().st_mtime)
            else:
                pid, t = int(raw), p.stat().st_mtime
        except (OSError, ValueError, KeyError, TypeError):
            continue   # half-written or unknown: its creator may be mid-write; the queue code handles it
        if not alive(pid):
            out.append((p, pid, "owner dead"))
            continue
        st = started(pid) if started else None
        if st and st > t + 5:
            out.append((p, pid, "PID reused by a younger process"))
    return out


# ---- strays ----

def parse_policy(text):
    return [m.group(1).strip().lower() for m in re.finditer(r"^\s*-\s*allow:\s*(.+?)\s*$", text, re.M) if m.group(1).strip()]


def load_policy(repo):
    try:
        return parse_policy((Path(repo) / POLICY_REL).read_text(encoding="utf-8"))
    except OSError:
        return []


def find_strays(procs, now=None, me=None, cpu_s=STRAY_CPU_S, min_age=STRAY_MIN_AGE_S):
    now = now or time.time()
    by = index(procs)
    keep = own_pids(by, me)
    out = []
    for p in procs:
        if p["pid"] in keep or p["name"].lower() in SKIP_NAMES or p["cpu"] < cpu_s:
            continue
        age = now - p["created"] if p["created"] else 0
        if age < min_age:
            continue
        up = chain(by, p["pid"])
        if is_protected(p, up) or any(m in p["cmd"] for m in SHIP_CHAIN + ("run_all_tests.py",)):
            continue
        out.append({"pid": p["pid"], "name": p["name"], "cmd": p["cmd"], "cpu": p["cpu"], "age": age, "chain": describe_chain(by, p),
                    "stop": stop_command(by, p)})
    return sorted(out, key=lambda s: -s["cpu"])


def describe_chain(by, p):
    """'bash.exe[2] <- claude.exe[1]'; ends with '(parent gone)' when the top of the chain has exited."""
    ups = chain(by, p["pid"])
    top = ups[-1] if ups else p
    parts = [f"{a['name']}[{a['pid']}]" for a in ups]
    if top["ppid"] not in by:
        parts.append("(parent gone)")
    return " <- ".join(parts) if parts else "(none)"


def stop_command(by, p):
    """taskkill for the stray, plus a relauncher above it (wscript / .vbs) so it does not respawn."""
    pids = [p["pid"]]
    for a in chain(by, p["pid"]):
        if a["name"].lower() in ("wscript.exe", "cscript.exe") or ".vbs" in a["cmd"].lower():
            pids.append(a["pid"])
    return "taskkill " + " ".join(f"/PID {i}" for i in pids) + " /T /F"


def allowed(stray, allow):
    return any(a in stray["cmd"].lower() for a in allow)


def fmt_stray(s):
    return (f"STRAY PID {s['pid']} {s['name']} cpu={s['cpu']:.0f}s age={s['age'] / 3600:.1f}h chain: {s['chain']}\n"
            f"    cmd: {s['cmd'][:160]}\n    stop: {s['stop']}")


# ---- disk ----

def dir_size(path, budget_s=15):
    end, total = time.monotonic() + budget_s, 0
    for root, dirs, files in os.walk(path):
        for n in files:
            try:
                total += os.lstat(os.path.join(root, n)).st_size
            except OSError:
                pass
        if time.monotonic() > end:
            break
    return total


def disk_state(path):
    return state_dir() / path


def growth_gb_per_h(free_gb, now, history, min_gap_s=600):
    """GB/h that free space FELL since the oldest sample at least min_gap_s old within 24 h (positive = filling up); None w/o history."""
    old = [h for h in history if min_gap_s <= now - h[0] <= 86400]
    if not old:
        return None
    t0, f0 = min(old, key=lambda h: h[0])
    return (f0 - free_gb) / ((now - t0) / 3600)


def check_disk(repo, temp=None, drive=None, now=None, free=None, size=dir_size):
    """(lines, deleted_gb). Records a free-space sample; when low or falling fast names the largest folders and prunes own temp caches."""
    now = now or time.time()
    temp = Path(temp or tempfile.gettempdir())
    drive = drive or (os.path.splitdrive(str(temp))[0] + "\\" if IS_WIN else str(temp))
    lines = []
    free_gb = free if free is not None else shutil.disk_usage(drive).free / 1e9
    hist_f = disk_state("free_history.json")
    try:
        history = json.loads(hist_f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        history = []
    rate = growth_gb_per_h(free_gb, now, history)
    history = [h for h in history if now - h[0] < 86400] + [[now, free_gb]]
    try:
        hist_f.write_text(json.dumps(history[-300:]), encoding="utf-8")
    except OSError:
        pass
    low = free_gb < MIN_FREE_GB
    falling = rate is not None and rate > FALL_GB_PER_H
    if not (low or falling):
        return lines, 0.0
    why = []
    if low:
        why.append(f"{free_gb:.1f} GB free < {MIN_FREE_GB:g}")
    if falling:
        why.append(f"free space falling {rate:.1f} GB/h" + (f" (empty in {free_gb / rate:.0f} h)" if rate > 0 else ""))
    lines.append(f"DISK WARN {drive}: " + "; ".join(why))
    rows = []
    if temp.is_dir():
        for e in os.scandir(temp):
            if e.is_dir(follow_symlinks=False):
                rows.append((size(e.path, 5), e.path))
    rows.sort(reverse=True)
    if rows:
        lines.append("  largest in temp: " + "; ".join(f"{p} {b / 1e9:.2f} GB" for b, p in rows[:5]))
    wt = []
    for base in {Path(repo) / ".claude" / "worktrees", *[Path(repo).parent]}:
        if base.name == "worktrees" and base.is_dir():
            wt += [(size(e.path, 5), e.path) for e in os.scandir(base) if e.is_dir(follow_symlinks=False)]
    wt.sort(reverse=True)
    if wt:
        lines.append("  largest worktrees: " + "; ".join(f"{p} {b / 1e9:.2f} GB" for b, p in wt[:5])
                     + "  (remove idle ones with `sync.py tidy`)")
    freed = 0
    for b, p in rows:
        if not Path(p).name.startswith(OWN_TEMP_PREFIXES):
            continue
        try:
            if time.time() - Path(p).stat().st_mtime < OWN_TEMP_AGE_H * 3600:
                continue
        except OSError:
            continue
        shutil.rmtree(p, ignore_errors=True)
        if not os.path.exists(p):
            freed += b
    if freed:
        lines.append(f"  pruned own temp caches ({'/'.join(OWN_TEMP_PREFIXES)}*): {freed / 1e9:.2f} GB")
    return lines, freed / 1e9


# ---- queue ----

def top_consumers(a, b, dt, n=5):
    """[(cpu cores used, pid, name, cmd)] from two snapshots dt seconds apart."""
    base = {p["pid"]: p for p in a}
    rows = []
    for p in b:
        q = base.get(p["pid"])
        if q and q["created"] == p["created"] and dt > 0:
            rows.append(((p["cpu"] - q["cpu"]) / dt, p["pid"], p["name"], p["cmd"]))
    return sorted(rows, reverse=True)[:n]


def check_queue(ncpu=None, qlen=None, snap=snapshot, sleep=time.sleep, qfn=queue_length):
    ncpu = ncpu or os.cpu_count() or 1
    q = qlen if qlen is not None else qfn()
    if q <= QUEUE_FACTOR * ncpu:
        return []
    a = snap()
    t0 = time.monotonic()
    sleep(SAMPLE_S)
    b = snap()
    top = top_consumers(a, b, time.monotonic() - t0 if sleep is time.sleep else SAMPLE_S)
    return [f"QUEUE WARN: processor queue {q} > {QUEUE_FACTOR} x {ncpu} CPUs; top consumers over {SAMPLE_S} s: "
            + "; ".join(f"{name}[{pid}] {c:.2f} cores {cmd[:60]!r}" for c, pid, name, cmd in top)]


# ---- orchestration ----

def post_strays(repo, strays):
    """One desk card per stray PID not reported before (state file); never raises."""
    f = disk_state("reported_strays.json")
    try:
        seen = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        seen = {}
    new = [s for s in strays if f"{s['pid']}@{int(s['age'] // 3600)}" not in seen and str(s["pid"]) not in seen]
    if not new:
        return 0
    need = "\n".join(fmt_stray(s) for s in new)
    try:
        r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "desk.py"), "post",
                            "Stray CPU hog on " + os.environ.get("COMPUTERNAME", "host"), "--need", need,
                            "--done-when", "operator ran the stop command or allow-listed the pattern in " + POLICY_REL,
                            "--no-ship"], cwd=repo, capture_output=True, text=True, timeout=60)
        if r.returncode:
            log(f"desk post failed: {r.stderr.strip()[:300]}")
            return 0
    except Exception as e:
        log(f"desk post error: {e!r}")
        return 0
    for s in new:
        seen[str(s["pid"])] = time.time()
    try:
        f.write_text(json.dumps(seen), encoding="utf-8")
    except OSError:
        pass
    return len(new)


def run(repo, reap=True, post=True, procs=None, kill=kill_tree, now=None):
    """All four checks. Returns report lines. Each part is isolated: an error in one is logged and the rest still run."""
    lines = []
    now = now or time.time()

    def part(name, fn):
        try:
            lines.extend(fn() or [])
        except Exception as e:   # fail closed: a health-check error never blocks a ship
            log(f"{name} error: {e!r}")

    if procs is None:
        try:
            procs = snapshot()
        except Exception as e:
            log(f"snapshot error: {e!r}")
            procs = []
    by = index(procs)

    def orphans():
        out = []
        for p in find_orphan_gates(procs, now):
            ok = kill(p["pid"]) if reap else False
            out.append(f"{'REAPED' if ok else 'ORPHAN'} gate tree PID {p['pid']} (no live claude.exe/ship above it)"
                       + ("" if ok or not reap else " - kill failed"))
        return out

    def files():
        out = []
        try:
            from sync import host_gate_slots_dir
        except Exception:
            return out
        for name in ("ship-queue", "gate-slots"):
            d = host_gate_slots_dir(name, repo)
            started = lambda pid: (by.get(pid) or {}).get("created")
            for path, pid, why in dead_owner_files(d, now, started=started):
                if reap:
                    try:
                        path.unlink()
                        out.append(f"REAPED {name}/{path.name}: PID {pid} {why}")
                        continue
                    except OSError:
                        pass
                out.append(f"STALE {name}/{path.name}: PID {pid} {why}")
        return out

    def strays():
        allow = load_policy(repo)
        found = find_strays(procs, now)
        out, report = [], []
        for s in found:
            if allow and allowed(s, allow):
                ok = kill(s["pid"]) if reap else False
                out.append(f"{'REAPED' if ok else 'ALLOWED-BUT-NOT-KILLED'} stray PID {s['pid']} {s['name']} (policy allow-list)")
            else:
                out.append(fmt_stray(s))
                report.append(s)
        if report and post:
            n = post_strays(repo, report)
            if n:
                out.append(f"  reported {n} stray(s) to the operator desk (desk.py post)")
        return out

    part("orphan gates", orphans)
    part("stale tickets", files)
    part("strays", strays)
    part("disk", lambda: check_disk(repo)[0])
    part("queue", check_queue)
    return lines


def run_safe(repo, **kw):
    """Never raises, never blocks: prints the report. SYNC_NO_HOST_HEALTH=1 skips it."""
    if os.environ.get("SYNC_NO_HOST_HEALTH"):
        return []
    try:
        lines = run(repo, **kw)
    except BaseException as e:   # includes KeyboardInterrupt? no: only real errors are swallowed below
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        log(f"run error: {e!r}")
        return []
    if lines:
        print("host health:")
        for ln in lines:
            print("  " + ln)
    else:
        print("host health: ok")
    return lines


def ensure_policy(repo):
    p = Path(repo) / POLICY_REL
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(POLICY_TEXT, encoding="utf-8", newline="\n")


def main(argv):
    repo = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
    run_safe(repo, reap="--no-reap" not in argv, post="--no-post" not in argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
