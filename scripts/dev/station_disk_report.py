"""One-line disk report for this machine (STATION_CLEANUP.md roll-call).

Prints free GB (C: and F: on Windows, / elsewhere), then the size in GB of the usual space eaters that exist here
(Claude VM bundles, Claude data, %TEMP%, worktrees beside the primary checkout, the live trees, Dumps), then the count of
java/python processes. `--send` posts it as `STATION <host> disk: ...`. Read-only: it never deletes anything.
"""
import argparse
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOME = Path.home()


def candidates():
    proj = HOME / "IdeaProjects"
    return {
        "vm_bundles": [Path("F:/ClaudeVM"), Path(os.environ.get("APPDATA", "")) / "Claude" / "vm_bundles"],
        "claude_data": [Path(os.environ.get("LOCALAPPDATA", "")) / "Claude-Data"],
        "temp": [Path(tempfile.gettempdir())],
        "worktrees": list(proj.glob("mts-*")) if proj.exists() else [],
        "mts_live": [Path("C:/MTS"), proj / "BinanceDataFeed" / ".mts_live"],
        "dumps": [Path("F:/Dumps"), Path("C:/Dumps"), HOME / "Dumps"],
    }


def drives(windows):
    return ("C:\\", "F:\\") if windows else ("/",)


def drive_label(path, windows):
    return path[0] if windows else "root"


def proc_command(windows):
    return ["tasklist", "/fo", "csv", "/nh"] if windows else ["ps", "-A", "-o", "comm="]


def count_procs(text):
    """java and python process counts from tasklist csv or `ps -o comm=` output."""
    names = [ln.split('","')[0].strip('"').strip().rsplit("/", 1)[-1].lower() for ln in text.splitlines() if ln.strip()]
    java = sum(n in ("java", "java.exe") for n in names)
    python = sum(n.startswith("python") for n in names)
    return "java=%d python=%d" % (java, python)


def tree_gb(path, budget_s=15):
    total = n = 0
    t0 = time.time()
    for root, _dirs, files in os.walk(path, onerror=lambda e: None):
        for f in files:
            try:
                total += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
            n += 1
            if n % 2000 == 0 and time.time() - t0 > budget_s:
                return total / 1e9, True
    return total / 1e9, False


def free_gb(drive):
    try:
        return shutil.disk_usage(drive).free / 1e9
    except OSError:
        return None


def procs(windows):
    try:
        out = subprocess.run(proc_command(windows), capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return "procs=n/a"
    return count_procs(out)


def report():
    windows = os.name == "nt"
    parts = []
    for d in drives(windows):
        g = free_gb(d)
        if g is not None:
            parts.append("%sfree=%.0fG" % (drive_label(d, windows), g))
    for label, paths in candidates().items():
        tot, cut = 0.0, False
        for p in paths:
            if p.exists():
                g, c = tree_gb(p)
                tot += g
                cut = cut or c
        if tot >= 0.1:
            parts.append("%s=%.1fG%s" % (label, tot, "+" if cut else ""))
    parts.append(procs(windows))
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true")
    a = ap.parse_args()
    line = report()
    print(line)
    if a.send:
        here = Path(__file__).resolve().parent
        msg = "STATION %s disk: %s" % (socket.gethostname(), line)
        subprocess.run([sys.executable, str(here / "mts_signal.py"), "send", msg[:200]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
