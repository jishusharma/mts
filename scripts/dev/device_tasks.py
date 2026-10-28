"""One registry of tasks every device must do: MyTradingSys/system/DEVICE_TASKS.json (rules: DEVICE_TASKS.md).

  python scripts/dev/device_tasks.py check [--send]     this host: run each applicable task's verify; table DONE/MISSING/UNKNOWN;
                                                         exit 1 if any MISSING. --send also posts the result as one mts_signal line
  python scripts/dev/device_tasks.py matrix              task x device from the latest reports (UNKNOWN = no report yet)
  python scripts/dev/device_tasks.py add --id X --what "..." --run "..." --verify "..." --applies all|JIS-NUC,... [--hook H] [--no-send]
                                                         appends the task and broadcasts it (HIGH, with the run command) to every host
  python scripts/dev/device_tasks.py add-device NAME     a new device; tasks with applies_to "all" cover it at once
  python scripts/dev/device_tasks.py probe <kind> [arg]  verify helpers: free-gb N | behind N | env NAME | git-min X.Y | no-mts-tasks

No scheduler (SCHEDULING_POLICY.md): the daily c_drive_guard SessionStart run calls `check --send`. DECISION (OURS): the report
is an `ack` record id "device-tasks" (acks are not shown as prompt news), one per host and day, holding {task: status}.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hosts  # noqa: E402

ROOT = HERE.parents[1]
REG = Path(os.environ.get("MTS_DEVICE_TASKS") or ROOT / "MyTradingSys" / "system" / "DEVICE_TASKS.json")
REPORT_ID = "device-tasks"
VERIFY_TIMEOUT = 90
ALLOWED_TASKS = ("MTS-WorktreeMaint-", "MTS-CBP-Ingestion", "MTS-SuccWake-")


def load_reg(path=None):
    return json.loads(Path(path or REG).read_text(encoding="utf-8"))


def save_reg(reg, path=None):
    Path(path or REG).write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def applies(task, device, devices=()):
    """True when `task` is for `device` (any of its names). "all" = every device in the registry's devices list."""
    a = task.get("applies_to")
    if a == "all":
        return hosts.key(device) in {hosts.key(d) for d in devices}
    return hosts.key(device) in {hosts.key(d) for d in (a or [])}


def default_runner(cmd):
    """Exit code of a verify command; None when it cannot run (timeout, no shell)."""
    try:
        return subprocess.run(cmd, shell=True, cwd=str(ROOT), capture_output=True, timeout=VERIFY_TIMEOUT,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).returncode
    except (subprocess.TimeoutExpired, OSError):
        return None


def check(reg, device, runner=default_runner):
    """[(task id, DONE|MISSING|UNKNOWN)] for the tasks that apply to `device`. UNKNOWN: no verify command, or it could not run."""
    out = []
    for t in reg["tasks"]:
        if not applies(t, device, reg.get("devices", [])):
            continue
        v = (t.get("verify") or "").strip()
        rc = runner(v) if v and v != "manual" else None
        out.append((t["id"], "UNKNOWN" if rc is None else "DONE" if rc == 0 else "MISSING"))
    return out


def latest_reports(rows):
    """{device key: {task id: status}} from the newest device-tasks report of each host."""
    best = {}
    for r in sorted(rows, key=lambda r: r.get("t", "")):
        if r.get("kind") == "ack" and r.get("id") == REPORT_ID and isinstance(r.get("dt"), dict):
            best[hosts.key(r.get("host", ""))] = r["dt"]
    return best


def matrix(reg, rows):
    """Header + rows: task x device. '-' = does not apply; UNKNOWN = applies, no report from that device."""
    devs = reg.get("devices", [])
    rep = latest_reports(rows)
    table = [["task"] + devs]
    for t in reg["tasks"]:
        line = [t["id"]]
        for d in devs:
            line.append(rep.get(hosts.key(d), {}).get(t["id"], "UNKNOWN") if applies(t, d, devs) else "-")
        table.append(line)
    return table


def fmt(table):
    w = [max(len(r[i]) for r in table) for i in range(len(table[0]))]
    return "\n".join("  ".join(c.ljust(w[i]) for i, c in enumerate(r)).rstrip() for r in table)


def broadcast_line(task):
    q = lambda s: '"' + s.replace('"', "'") + '"'
    who = "all devices" if task["applies_to"] == "all" else ",".join(task["applies_to"])
    return "python scripts/dev/mts_signal.py broadcast %s --prio high --cmd %s" % (
        q("DEVICE TASK %s (%s): %s Check: python scripts/dev/device_tasks.py check" % (task["id"], who, task["what"])),
        q(task["run"][:300]))


def add_task(reg, task):
    """Appends task (id unique, fields required); returns the broadcast line. Raises ValueError on a bad entry."""
    for k in ("id", "what", "run", "verify", "applies_to", "added", "by_hook"):
        if not task.get(k):
            raise ValueError("missing field " + k)
    if any(t["id"] == task["id"] for t in reg["tasks"]):
        raise ValueError("task id exists: " + task["id"])
    reg["tasks"].append(task)
    return broadcast_line(task)


def report_line(device, res):
    return "device-tasks %s: " % device + ", ".join("%s=%s" % r for r in res)


def send_report(device, res):
    import mts_signal as sig
    return sig.send(report_line(device, res), kind="ack", extra={"id": REPORT_ID, "host": sig.host(), "dt": dict(res)})


# ---- probes (exit 0 = done) ----
def primary():
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"], capture_output=True, text=True)
    p = Path(r.stdout.strip())
    return (p if p.is_absolute() else ROOT / p).resolve().parent


def probe(kind, arg=""):
    if kind == "free-gb":
        return 0 if shutil.disk_usage(Path(ROOT.anchor or "/")).free / 1e9 >= float(arg) else 1
    if kind == "behind":
        pr = str(primary())
        subprocess.run(["git", "-C", pr, "fetch", "-q", "origin", "fast-track"], capture_output=True, timeout=60)
        r = subprocess.run(["git", "-C", pr, "rev-list", "--count", "HEAD..origin/fast-track"], capture_output=True, text=True)
        n = int(r.stdout.strip() or 10 ** 9)
        print("primary checkout %s is %d behind" % (pr, n))
        return 0 if n <= int(arg) else 1
    if kind == "env":
        if os.environ.get(arg):
            return 0
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                return 0 if winreg.QueryValueEx(k, arg)[0] else 1
        except (ImportError, OSError):
            return 1
    if kind == "git-min":
        m = re.search(r"(\d+)\.(\d+)", subprocess.run(["git", "--version"], capture_output=True, text=True).stdout)
        return 0 if m and (int(m[1]), int(m[2])) >= tuple(int(x) for x in arg.split(".")[:2]) else 1
    if kind == "no-mts-tasks":
        if os.name != "nt":
            return 0
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-ScheduledTask | Where-Object { $_.TaskName -like 'MTS-*' }).TaskName"],
                           capture_output=True, text=True, timeout=60)
        bad = [n for n in r.stdout.split() if not n.startswith(ALLOWED_TASKS)]
        print("stray MTS tasks: " + (", ".join(bad) or "none"))
        return 1 if bad else 0
    print("unknown probe " + kind)
    return 2


def signal_rows():
    import mts_signal as sig
    h = sig.ensure()
    return sig.load(h) if h else []


def main(argv):
    import argparse
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "probe":
        return probe(rest[0], rest[1] if len(rest) > 1 else "")
    reg = load_reg()
    if cmd == "check":
        dev = hosts.this_host()
        res = check(reg, dev)
        print(fmt([["task", "status on " + dev]] + [list(r) for r in res]))
        if "--send" in rest:
            try:
                send_report(dev, res)
            except Exception as e:   # report-only: never fails the caller
                print("report not sent: %r" % (e,))
        return 1 if any(s == "MISSING" for _, s in res) else 0
    if cmd == "matrix":
        print(fmt(matrix(reg, signal_rows())))
        return 0
    if cmd == "add":
        ap = argparse.ArgumentParser(prog="device_tasks.py add")
        for k in ("id", "what", "run", "verify", "applies"):
            ap.add_argument("--" + k, required=True)
        ap.add_argument("--hook", default="manual")
        ap.add_argument("--no-send", action="store_true")
        a = ap.parse_args(rest)
        to = "all" if a.applies == "all" else [x.strip() for x in a.applies.split(",") if x.strip()]
        import datetime
        try:
            line = add_task(reg, {"id": a.id, "what": a.what, "run": a.run, "verify": a.verify, "applies_to": to,
                                  "added": datetime.date.today().isoformat(), "by_hook": a.hook})
        except ValueError as e:
            print("refused: %s" % e)
            return 2
        save_reg(reg)
        print("added %s; commit it with sync.py ship. Broadcast line:\n%s" % (a.id, line))
        if not a.no_send:
            t = reg["tasks"][-1]
            import mts_signal as sig
            sig.main(["broadcast", "DEVICE TASK %s: %s Check: python scripts/dev/device_tasks.py check" % (t["id"], t["what"]),
                      "--prio", "high", "--cmd", t["run"][:300]])
        return 0
    if cmd == "add-device":
        if any(hosts.same_host(d, rest[0]) for d in reg["devices"]):
            print("device exists")
            return 2
        reg["devices"].append(rest[0])
        save_reg(reg)
        print("added device %s; tasks with applies_to all now cover it" % rest[0])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
