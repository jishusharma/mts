"""Super-session watchdog (relay.py watchdog / heartbeat): synthetic HOME only, never the real ~/.claude."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("MTS_TEST_RELAY") or REPO / "scripts" / "sched" / "relay.py")   # override: run against the pre-change copy
NOW = "2026-10-16T03:00:00Z"


def run(home, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
    env.update({"MTS_RELAY_HOME": str(home), "MTS_RELAY_NOW": NOW})
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


class WatchdogTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp()) / "home"
        self.home.mkdir()
        self.flag = self.home / "mts-relay-stop"
        self.hb = self.home / "mts-super-heartbeat.json"

    def beat(self, utc):
        self.hb.write_text(json.dumps({"coordinator": "local_x", "host": "H", "utc": utc, "note": "n"}), encoding="utf-8")

    def log(self):
        p = self.home / "mts-relay-log.jsonl"
        return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []

    def check_resumed(self, age):
        r = run(self.home, "watchdog")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("RESUMED", r.stdout)
        self.assertFalse(self.flag.exists())
        rows = [x for x in self.log() if x["event"] == "watchdog_resume"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["heartbeat_age"], age)
        return rows[0]

    def test_fresh_heartbeat_stays_stopped(self):
        self.flag.write_text("super-session local_x", encoding="utf-8")
        self.beat("2026-10-16T02:30:00Z")
        r = run(self.home, "watchdog")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("fresh", r.stdout)
        self.assertTrue(self.flag.exists())
        self.assertEqual(self.log(), [])

    def test_stale_resumes_and_logs(self):
        self.flag.write_text("super-session local_x", encoding="utf-8")
        self.beat("2026-10-16T01:30:00Z")
        self.assertEqual(self.check_resumed("90min")["who"], "local_x")

    def test_missing_resumes(self):
        self.flag.write_text("super-session local_x", encoding="utf-8")
        self.check_resumed("unreadable")

    def test_malformed_resumes(self):
        for bad in ("{not json", "[]", json.dumps({"coordinator": "c", "utc": "yesterday"})):
            self.flag.write_text("super-session local_x", encoding="utf-8")
            self.hb.write_text(bad, encoding="utf-8")
            self.assertIn("RESUMED", run(self.home, "watchdog").stdout, bad)
            self.assertFalse(self.flag.exists())

    def test_operator_stop_never_resumed(self):
        self.flag.write_text("operator: deploy freeze", encoding="utf-8")
        self.beat("2026-10-10T00:00:00Z")
        self.assertIn("operator stop", run(self.home, "watchdog").stdout)
        self.hb.unlink()
        self.assertIn("operator stop", run(self.home, "watchdog").stdout)
        self.assertTrue(self.flag.exists())
        self.assertEqual(self.log(), [])

    def test_not_stopped_is_noop(self):
        self.assertIn("not stopped", run(self.home, "watchdog").stdout)
        self.assertEqual(self.log(), [])

    def test_heartbeat_writer_roundtrip(self):
        self.flag.write_text("super-session local_x", encoding="utf-8")
        r = run(self.home, "heartbeat", "local_x", "--note", "wake")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = json.loads(self.hb.read_text(encoding="utf-8"))
        self.assertEqual((row["coordinator"], row["utc"], row["note"]), ("local_x", NOW, "wake"))
        self.assertIn("fresh", run(self.home, "watchdog").stdout)
        self.assertTrue(self.flag.exists())


if __name__ == "__main__":
    unittest.main()
