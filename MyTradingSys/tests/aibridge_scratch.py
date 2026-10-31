import sys; sys.dont_write_bytecode = True
"""aibridge_scratch.py - start a scratch AIBridge agent (payload copy, own port/token/policy) and drive it over HTTP.

Test helper for the exploratory regression tests (research/dsa_bridge_exploratory_2026-10-31). Windows PowerShell only.
Never touches F:/AIBridge or the live agent on 7181.
"""
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
PAYLOAD = ROOT / "scripts" / "aibridge"
ORIGIN = "chrome-extension://selftestselftestselftestselftest"


class Scratch:
    def __init__(self):
        self.work = tempfile.mkdtemp(prefix="aib_probe_")
        self.sdir = os.path.join(self.work, "src")
        os.makedirs(self.sdir)
        for f in ("agent.ps1", "checks.ps1", "concurrency.ps1", "audit.ps1"):
            shutil.copy(PAYLOAD / "src" / f, self.sdir)
        os.makedirs(os.path.join(self.work, "scripts"))
        os.makedirs(os.path.join(self.work, "tasks"))
        shutil.copy(PAYLOAD / "scripts" / "run-task.ps1", os.path.join(self.work, "scripts"))
        for f in (PAYLOAD / "tasks").glob("*.json"):
            shutil.copy(f, os.path.join(self.work, "tasks"))
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        self.token = "probe" + os.urandom(8).hex()
        json.dump({"token": self.token, "allowed_origins": [ORIGIN], "port": self.port, "bind": "127.0.0.1"},
                  open(os.path.join(self.sdir, "config.json"), "w"))
        pol = {"roots": [self.work], "deny_path_regex": [{"re": r"(^|[\/\s'\"=(,;@])\.secrets(?![A-Za-z0-9_])", "why": "secrets directory"}], "timeout_soft_s": 60, "timeout_hard_s": 300,
               "max_output_bytes": 262144, "mode": "open"}
        pol.update(json.load(open(PAYLOAD / "policy_patch.json", encoding="utf-8")))
        json.dump(pol, open(os.path.join(self.sdir, "policy.json"), "w"))
        self.proc = subprocess.Popen(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(self.sdir, "agent.ps1")],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000)
        for _ in range(80):
            time.sleep(0.5)
            try:
                if self.http("GET", "/ping", timeout=3)[1].get("ok"):
                    return
            except Exception:
                pass
        raise RuntimeError("scratch agent did not start")

    def http(self, method, path, body=None, timeout=180):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), data=data, method=method,
                                     headers={"Origin": ORIGIN, "Content-Type": "text/plain"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8") or "{}")

    def run(self, cmd, auto=True, timeout=180, **kw):
        b = {"cmd": cmd, "cwd": self.work, "token": self.token, "auto": auto}
        b.update(kw)
        return self.http("POST", "/run", b, timeout=timeout)

    def close(self):
        try:
            self.proc.kill()
            subprocess.call(["taskkill", "/T", "/F", "/PID", str(self.proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        shutil.rmtree(self.work, ignore_errors=True)
