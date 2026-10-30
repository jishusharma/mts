"""One-line disk report for this machine (STATION_CLEANUP.md roll-call).

Prints free GB on C: and F:, then the size in GB of the usual space eaters that exist here
(Claude VM bundles, %TEMP%, worktrees beside the primary checkout, .mts_live trees, Dumps),
then the count of java/python processes. `--send` posts it as `STATION <host>/<login> disk: ...`.
Read-only: it never deletes anything.
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
CANDIDATES = {
    "vm_bundles": [Path("F:/ClaudeVM"), Path(os.environ.get("APPDATA", "")) / "Claude" / "vm_bundles"],
    "claude_data": [Path(os.environ.get("LOCALAPPDATA", "")) / "Claude-Data"],
    "temp": [Path(tempfile.gettempdir())],
    "worktrees": [p for p in (HOME / "IdeaProjects").glob("mts-*")] if (HOME / "IdeaProjects").exists() else [],
    "mts_live": [Path("C:/MTS"), HOME / "IdeaProjects" / "BinanceDataFeed" / ".mts_live"],
    "dumps": [Path("F:/Dumps"), Path("C:/Dumps"), HOME / "Dumps"],
}


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


def procs():
    try:
        out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return "n/a"
    names = [line.split('","')[0].strip('"').lower() for line in out.splitlines() if line]
    return "java=%d python=%d" % (sum(x == "java.exe" for x in names), sum(x.startswith("python") for x in names))


def report():
    parts = []
    for d in ("C:\\", "F:\\"):
        g = free_gb(d)
        if g is not None:
            parts.append("%sfree=%.0fG" % (d[0], g))
    for label, paths in CANDIDATES.items():
        tot = 0.0
        cut = False
        for p in paths:
            if p.exists():
                g, c = tree_gb(p)
                tot += g
                cut = cut or c
        if tot >= 0.1:
            parts.append("%s=%.1fG%s" % (label, tot, "+" if cut else ""))
    parts.append(procs())
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
