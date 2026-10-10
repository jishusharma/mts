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

    def test_same_id_double_fire_blocked(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RELAY GO depth=0", r.stdout)
        self.assertIn("task=mts-relay-a", r.stdout)
        r2 = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", now="2026-10-10T10:05:00Z")
        self.assertEqual(r2.returncode, 1)
        self.assertIn("already launched", r2.stdout)

    def test_new_id_within_minutes_is_allowed(self):
        # 2026-10-10 06:42 chain death: a short session handed over a NEW id 15 min after the previous launch and the
        # old 20-minute clock lock stopped the chain. The lock is keyed by handoff id now.
        run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertEqual(run(self.home, "gate", "--file", str(self.f), "--started-id", "none").returncode, 0)
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", now="2026-10-10T10:15:00Z")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("depth=1", r.stdout)
        self.assertIn("task=mts-relay-b", r.stdout)

    def kick(self, now="2026-10-10T10:00:00Z"):
        return run(self.home, "kick", "--file", str(self.f), now=now)

    def test_kick_starts_a_go_handoff_and_records_chain_base(self):
        for _ in range(3):
            run(self.home, "handoff", "--file", str(self.f), "--go")  # depth 2
        r = self.kick()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("KICK depth=2", r.stdout)
        self.assertIn("task=mts-relay-a", r.stdout)
        # depth cap now counts from the kick: depth 2 with cap 2 would have stopped before, base 2 lets it through
        run(self.home, "handoff", "--file", str(self.f), "--go")
        g = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", extra={"MTS_RELAY_MAX_DEPTH": "2"})
        self.assertEqual(g.returncode, 0, g.stdout)

    def test_kick_idles_when_chain_moving_or_session_on_it(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertEqual(self.kick().returncode, 0)
        moving = self.kick(now="2026-10-10T10:20:00Z")
        self.assertEqual(moving.returncode, 1)
        self.assertIn("chain is moving", moving.stdout)
        working = self.kick(now="2026-10-10T10:50:00Z")
        self.assertEqual(working.returncode, 1)
        self.assertIn("session still on it", working.stdout)
        self.assertIn("lock=2026-10-10T10:00:00Z task=mts-relay-", working.stdout)
        retry = self.kick(now="2026-10-10T11:10:00Z")  # same id, 70 min: never started or died, retry (was 3 h)
        self.assertEqual(retry.returncode, 0, retry.stdout)

    def test_kick_idles_on_stop_header_no_header_and_stop_flag(self):
        self.assertEqual(self.kick().returncode, 1)
        run(self.home, "handoff", "--file", str(self.f), "--stop", "queue empty")
        r = self.kick()
        self.assertEqual(r.returncode, 1)
        self.assertIn("queue empty", r.stdout)
        run(self.home, "handoff", "--file", str(self.f), "--go")
        run(self.home, "stop", "weekly budget")
        self.assertIn("stop flag", self.kick().stdout)

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
