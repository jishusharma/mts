"""nowin - no console flashes from child processes of windowless (pythonw) scheduled jobs.

Under pythonw there is no console, so every console child (git.exe, python.exe, mvn) that subprocess starts makes
Windows open a new console window: it flashes and steals focus (B173, operator 2026-10-16: git windows flashing on both
machines). `install()` makes subprocess.Popen add CREATE_NO_WINDOW when the caller set no creationflags. Active only
on Windows under pythonw.exe (or MTS_NOWIN=1), so interactive runs and tests are untouched. Idempotent.
Gate note (GATE_SPEED.md): a change here is an ordinary smoke ship, so the fast gate runs only the tests the import graph reaches.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def wanted():
    if sys.platform != "win32":
        return False
    if os.path.basename(sys.executable or "").lower() == "pythonw.exe" or os.environ.get("MTS_NOWIN") == "1":
        return True
    return _console_hidden()


def _console_hidden():
    """No console (detached, or started by a GUI app such as Claude desktop) or a hidden one. B190: the wscript launchers start python.exe with a hidden console (style 0). Console children of such a process were
    still seen flashing on JIS-NB, so treat 'console window exists but is not visible' like pythonw. An interactive terminal
    (visible console) is untouched, so output of children that inherit the console still shows."""
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        return not hwnd or not ctypes.windll.user32.IsWindowVisible(hwnd)   # no console at all: every child opens one
    except Exception:
        return False


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
DEFAULT_SPAWN_LOG = Path.home() / ".claude" / "nowin_spawns.jsonl"


def log_path():
    return Path(os.environ.get("MTS_NOWIN_LOG") or DEFAULT_SPAWN_LOG)


def _log_spawn(parent_pid, child_pid, cmd, creationflags, elapsed_ms):
    log_file = log_path()
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        has_flag = bool(creationflags and (creationflags & CREATE_NO_WINDOW) == CREATE_NO_WINDOW)
        row = {
            "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "parent_pid": parent_pid,
            "child_pid": child_pid,
            "cmd": cmd if isinstance(cmd, (list, tuple, str)) else str(cmd),
            "creationflags": creationflags,
            "elapsed_ms": round(elapsed_ms, 2),
            "has_create_no_window": has_flag,
        }
        with log_file.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def audit_spawns(log_path=None):
    """List spawns executed without CREATE_NO_WINDOW (RU8)."""
    lp = Path(log_path) if log_path else globals()["log_path"]()
    if not lp.is_file():
        return []
    rows = []
    for line in lp.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                row = json.loads(line)
                cf = row.get("creationflags", 0) or 0
                has_flag = row.get("has_create_no_window")
                if has_flag is None:
                    has_flag = bool((cf & CREATE_NO_WINDOW) == CREATE_NO_WINDOW)
                if not has_flag:
                    rows.append(row)
            except Exception:
                pass
    return rows


def cmd_audit(args):
    spawns = audit_spawns()
    if getattr(args, "json", False):
        print(json.dumps(spawns, indent=2, ensure_ascii=False))
        return
    if not spawns:
        print("audit: no spawns without CREATE_NO_WINDOW found")
        return
    print(f"audit: {len(spawns)} spawn(s) executed without CREATE_NO_WINDOW:")
    for n, s in enumerate(spawns, 1):
        cmd = s.get("cmd")
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        print(f"{n}. child_pid={s.get('child_pid')} parent_pid={s.get('parent_pid')} flags={s.get('creationflags')} elapsed={s.get('elapsed_ms')}ms")
        print(f"   cmd: {cmd_str[:120]}")


def install(force=False):
    logging_enabled = bool(os.environ.get("MTS_NOWIN_LOG"))
    if not (force or wanted() or logging_enabled) or getattr(subprocess.Popen, "_mts_nowin", False):
        return False
    flag = CREATE_NO_WINDOW
    orig = subprocess.Popen.__init__

    def init(self, *a, **kw):
        # Apply CREATE_NO_WINDOW if eligible (when caller explicitly set no creationflags)
        if (force or wanted()) and kw.get("creationflags") is None and len(a) < 14:  # creationflags is the 14th positional of Popen
            kw["creationflags"] = flag

        t0 = time.monotonic()
        orig(self, *a, **kw)
        elapsed_ms = (time.monotonic() - t0) * 1000.0

        if os.environ.get("MTS_NOWIN_LOG"):
            # Extract cmd
            cmd = kw.get("args") if "args" in kw else (a[0] if a else "")
            cf = kw.get("creationflags") if "creationflags" in kw else (a[13] if len(a) >= 14 else 0)
            child_pid = getattr(self, "pid", None)
            _log_spawn(os.getpid(), child_pid, cmd, cf or 0, elapsed_ms)

    subprocess.Popen.__init__ = init
    subprocess.Popen._mts_nowin = True
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    aud = sub.add_parser("audit", help="list spawns executed without CREATE_NO_WINDOW")
    aud.add_argument("--json", action="store_true", help="output JSON array")
    aud.set_defaults(fn=cmd_audit)
    args = p.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

