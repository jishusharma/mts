"""nowin - no console flashes from child processes of windowless (pythonw) scheduled jobs.

Under pythonw there is no console, so every console child (git.exe, python.exe, mvn) that subprocess starts makes
Windows open a new console window: it flashes and steals focus (B173, operator 2026-10-16: git windows flashing on both
machines). `install()` makes subprocess.Popen add CREATE_NO_WINDOW when the caller set no creationflags. Active only
on Windows under pythonw.exe (or MTS_NOWIN=1), so interactive runs and tests are untouched. Idempotent.
"""
import os
import subprocess
import sys


def wanted():
    if sys.platform != "win32":
        return False
    return os.path.basename(sys.executable or "").lower() == "pythonw.exe" or os.environ.get("MTS_NOWIN") == "1"


def install(force=False):
    if not (force or wanted()) or getattr(subprocess.Popen, "_mts_nowin", False):
        return False
    flag = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    orig = subprocess.Popen.__init__

    def init(self, *a, **kw):
        if not kw.get("creationflags") and len(a) < 14:     # creationflags is the 14th positional of Popen
            kw["creationflags"] = flag
        orig(self, *a, **kw)

    subprocess.Popen.__init__ = init
    subprocess.Popen._mts_nowin = True
    return True
