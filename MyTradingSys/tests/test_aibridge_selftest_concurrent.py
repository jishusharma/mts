import sys; sys.dont_write_bytecode = True
"""test_aibridge_selftest_concurrent.py - two AIBridge live selftests at once next to a squatter on port 7199.

Split out of test_aibridge_payload.py (2026-10-24): that file ran the full live selftest three times (81 s on a Windows CI shard,
the slowest file); in two files the shard balancer can put the single run and the concurrent pair on different shards.
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

from test_aibridge_payload import PAYLOAD, SELFTEST_TIMEOUT_S, _kill_tree


@pytest.mark.skipif(os.name != "nt" or shutil.which("powershell.exe") is None, reason="needs Windows PowerShell")
def test_agent_live_selftest_concurrent_and_port_clash():
    """Gate failure 2026-10-15: the selftest used fixed port 7199, so sessions shipping at the same time (or any
    listener on 7199) made it fail with ConnectionResetError. Two runs at once next to a squatter on 7199 must pass."""
    import socket
    squat = socket.socket()
    try:
        squat.bind(("127.0.0.1", 7199))
        squat.listen(5)
    except OSError:
        squat.close()
        squat = None   # someone else already holds 7199: the clash is already in place
    procs = []
    try:
        cmd = [sys.executable, "tests/agent_live_selftest.py"]
        procs = [subprocess.Popen(cmd, cwd=PAYLOAD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) for _ in range(2)]
        outs = [p.communicate(timeout=SELFTEST_TIMEOUT_S)[0] for p in procs]
    finally:
        if squat:
            squat.close()
        for p in procs:   # a timed-out run must not leave its python + PowerShell agent holding a port and CPU
            _kill_tree(p)
    for p, out in zip(procs, outs):
        fails = [ln for ln in out.splitlines() if ln.startswith("FAIL")]
        assert p.returncode == 0 and not fails, "\n".join(fails)[:3000] or out[-2000:]
        assert re.search(r"\d+ passed, 0 failed", out)
