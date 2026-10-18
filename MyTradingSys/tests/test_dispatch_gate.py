"""dispatch_gate.py (2026-10-15): the model-free dispatcher gate. NOOP launches nothing; KICK launches one session with the tick output."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE = REPO / "scripts" / "sched" / "dispatch_gate.py"
NL = chr(10)

# stub relay.py: `tick` prints $STUB_TICK, `unlock` records that it ran
RELAY_STUB = """import os, sys
from pathlib import Path
if sys.argv[1] == "tick":
    print(os.environ["STUB_TICK"])
    Path(os.environ["STUB_DIR"], "tick_args.txt").write_text(" ".join(sys.argv[2:]))
elif sys.argv[1] == "unlock":
    Path(os.environ["STUB_DIR"], "unlocked").write_text("1")
"""
# launcher stub: stores stdin, exits with $STUB_RC
LAUNCH_STUB = """import os, sys
from pathlib import Path
Path(os.environ["STUB_DIR"], "prompt.txt").write_text(sys.stdin.read())
sys.exit(int(os.environ.get("STUB_RC", "0")))
"""


class GateTest(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        (self.d / "relay.py").write_text(RELAY_STUB, encoding="utf-8", newline=NL)
        (self.d / "launch.py").write_text(LAUNCH_STUB, encoding="utf-8", newline=NL)

    def gate(self, tick, rc="0"):
        env = {**os.environ, "STUB_TICK": tick, "STUB_DIR": str(self.d), "STUB_RC": rc, "MTS_RELAY_HOME": str(self.d / "home"),
               "MTS_GATE_RELAY": str(self.d / "relay.py")}
        launcher = '"%s" "%s"' % (sys.executable, self.d / "launch.py")
        return subprocess.run([sys.executable, str(GATE), "--root", str(self.d), "--launcher", launcher],
                              capture_output=True, text=True, env=env)

    def test_noop_launches_nothing_and_passes_hourly_off(self):
        r = self.gate("TICK NOOP | handoff says stop: queue empty | route=nothing")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(r.stdout.startswith("GATE NOOP"), r.stdout)
        self.assertFalse((self.d / "prompt.txt").exists())   # no model session for an idle tick
        args = (self.d / "tick_args.txt").read_text()
        self.assertIn("--hourly-min 60", args)
        self.assertIn("--gate", args)

    def test_idle_hour_with_refine_ok_launches_nothing(self):
        r = self.gate("TICK NOOP | queue empty | route=nothing" + NL + "HOURLY housekeep=yes")
        self.assertTrue(r.stdout.startswith("GATE NOOP"), r.stdout)
        self.assertFalse((self.d / "prompt.txt").exists())

    def test_refine_needed_hour_launches_one_refiner_session(self):
        r = self.gate("TICK NOOP | queue empty | route=nothing" + NL + "HOURLY refine=REFINE_NEEDED")
        self.assertTrue(r.stdout.startswith("GATE NOOP"), r.stdout)
        prompt = (self.d / "prompt.txt").read_text()
        self.assertIn("Refiner run", prompt)
        self.assertIn("do NOT run `relay.py tick`".replace("do NOT", "Do NOT"), prompt)

    def test_kick_launches_one_session_with_the_tick_text(self):
        r = self.gate("TICK KICK depth=3 id=aaaa1111 | route=none" + NL + "NEXT: relay begin" + NL + "UNLOCK: relay unlock")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        prompt = (self.d / "prompt.txt").read_text()
        self.assertIn("NEXT: relay begin", prompt)
        self.assertIn("do NOT run `relay.py tick`", prompt)
        self.assertFalse((self.d / "unlocked").exists())   # a launch that ran keeps the lock; the session frees it

    def test_failed_launch_frees_the_lock(self):
        self.gate("TICK KICK depth=3 id=aaaa1111 | route=none", rc="3")
        self.assertTrue((self.d / "unlocked").exists())   # else the next ticks wait out the lock for a session that never ran

    def test_missing_launcher_does_not_tick(self):
        env = {**os.environ, "STUB_TICK": "TICK KICK x", "STUB_DIR": str(self.d), "MTS_RELAY_HOME": str(self.d / "home"),
               "MTS_GATE_RELAY": str(self.d / "relay.py")}
        r = subprocess.run([sys.executable, str(GATE), "--root", str(self.d), "--launcher", "no_such_claude_binary -p"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertFalse((self.d / "tick_args.txt").exists())   # tick never ran, so no lock was taken for a session that cannot start

    def test_unparsable_tick_never_launches(self):
        r = self.gate("Traceback: boom")
        self.assertEqual(r.returncode, 1)
        self.assertFalse((self.d / "prompt.txt").exists())


class RegisterScriptTest(unittest.TestCase):
    def test_hidden_window_and_no_switch_shadow(self):
        text = (REPO / "scripts" / "sched" / "register_dispatch_gate.ps1").read_text(encoding="utf-8")
        self.assertIn("conhost.exe", text)   # a bare pythonw flashes a console for every git child
        self.assertIn("--headless", text)
        self.assertNotRegex(text.lower(), r"(?m)^\$trigger\s*=")   # PowerShell is case-insensitive: it would shadow the -Trigger switch


if __name__ == "__main__":
    unittest.main()
