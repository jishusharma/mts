"""Windowless hook launcher (operator 2026-11-11: consoles flash every time he types in the Claude app).

Claude runs every hook as a new process. A console python.exe started that way opens a visible console window, once per hook,
on every prompt, tool call and stop. This file runs under pythonw.exe (no console, so no window) and starts the real hook
script with python.exe and CREATE_NO_WINDOW, relaying stdin, stdout, stderr and the exit code (a hook exits 2 to block).
Use it through `sh scripts/dev/hook.sh <script.py> [args]`; hook.sh falls back to plain python where pythonw does not exist.
pythonw has no sys.stdin or sys.stdout: bytes go through file descriptors 0, 1 and 2.
"""
import os
import subprocess
import sys

TIMEOUT_S = 110


def read_stdin():
    chunks = []
    while True:
        try:
            b = os.read(0, 65536)
        except OSError:
            break
        if not b:
            break
        chunks.append(b)
    return b"".join(chunks)


def python_exe():
    exe = sys.executable or "python"
    if os.path.basename(exe).lower() == "pythonw.exe":
        sibling = os.path.join(os.path.dirname(exe), "python.exe")
        if os.path.isfile(sibling):
            return sibling
    return exe


def emit(fd, data):
    if not data:
        return
    try:
        os.write(fd, data)
    except OSError:
        pass


def main(argv):
    if not argv:
        return 2
    data = read_stdin()
    try:
        r = subprocess.run([python_exe(), *argv], input=data, capture_output=True, timeout=TIMEOUT_S,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except subprocess.TimeoutExpired:
        emit(2, b"nowin_hook: hook timed out after %d s: %s\n" % (TIMEOUT_S, " ".join(argv).encode("utf-8", "replace")))
        return 1
    emit(1, r.stdout)
    emit(2, r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
