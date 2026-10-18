"""Block until a process exits, then print the Gemini queue status. Run it as a background shell so its exit wakes the coordinator
(operator 2026-10-18: a parked worker only moves when someone is woken to message it).  python scripts/dev/wait_pid.py <pid> [<pid> ...]"""
import subprocess
import sys
import time


def alive(pid):
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
    return str(pid) in out


pids = [int(a) for a in sys.argv[1:]]
while any(alive(p) for p in pids):
    time.sleep(30)
print(subprocess.run([sys.executable, "scripts/dev/gemini_queue.py", "status"], capture_output=True, text=True).stdout)
