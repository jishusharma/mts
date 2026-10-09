"""Fixtures for scripts/sched/relay.py: header stamping, every gate STOP condition, GO writes the launch lock."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "relay.py"


def run(home, *args, now="2026-10-10T10:00:00Z", extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
    env.update(MTS_RELAY_HOME=str(home), MTS_RELAY_NOW=now, **(extra or {}))
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


class RelayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        self.f = self.tmp / "NEXT_SESSION.md"
        self.f.write_text("# NEXT SESSION\nbody\n", encoding="utf-8", newline="\n")

    def header_id(self):
        return self.f.read_text(encoding="utf-8").split("id=")[1].split(" ")[0]

    def test_no_header_stops(self):
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no relay header", r.stdout)

    def test_go_then_lock_blocks_second_launch(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RELAY GO depth=0", r.stdout)
        self.assertIn("task=mts-relay-a", r.stdout)
        r2 = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", now="2026-10-10T10:05:00Z")
        self.assertEqual(r2.returncode, 1)
        self.assertIn("launched", r2.stdout)
        r3 = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", now="2026-10-10T10:30:00Z")
        self.assertEqual(r3.returncode, 0)

    def test_stop_header_stops_with_reason(self):
        run(self.home, "handoff", "--file", str(self.f), "--stop", "queue empty")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 1)
        self.assertIn("queue empty", r.stdout)

    def test_unchanged_id_stops(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", self.header_id())
        self.assertEqual(r.returncode, 1)
        self.assertIn("unchanged", r.stdout)

    def test_depth_increments_and_caps(self):
        for _ in range(3):
            run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertIn("depth=2", self.f.read_text(encoding="utf-8"))
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", extra={"MTS_RELAY_MAX_DEPTH": "2"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("cap", r.stdout)
        run(self.home, "handoff", "--file", str(self.f), "--go", "--reset-depth")
        self.assertIn("depth=0", self.f.read_text(encoding="utf-8"))
        self.assertEqual(self.f.read_text(encoding="utf-8").count("relay:"), 1)

    def test_operator_stop_flag_and_resume(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        run(self.home, "stop", "weekly budget")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 1)
        self.assertIn("weekly budget", r.stdout)
        run(self.home, "resume")
        self.assertEqual(run(self.home, "gate", "--file", str(self.f), "--started-id", "none").returncode, 0)


if __name__ == "__main__":
    unittest.main()
