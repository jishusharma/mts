"""budget.py (SUPER_SESSION.md Pacing): ~/.claude/mts-budget.json -> SPEND / NORMAL / THROTTLE, and the tick/gate wiring.

Expected states are computed by hand. Week ends 2026-10-20T00:00Z, so it started 2026-10-13T00:00Z.
now 10-15 12:00Z: 2.5 d elapsed, f = 2.5/7 = 0.35714 -> SPEND below U=25.714, THROTTLE above U=40.714.
now 10-19 12:00Z: 12 h to reset, f = 6.5/7 = 0.92857 -> last-day rule: SPEND while U < 85 (THROTTLE above 97.857)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "budget.py"
RESET = "2026-10-20T00:00:00Z"
MID = "2026-10-15T12:00:00Z"
LAST = "2026-10-19T12:00:00Z"
NL = chr(10)


def run(home, *args, now=MID):
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
    env.update({"MTS_RELAY_HOME": str(home), "MTS_RELAY_NOW": now})
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


class BudgetState(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def put(self, u, five=10, utc=MID, resets=RESET):
        (self.home / "mts-budget.json").write_text(json.dumps(
            {"utc": utc, "weekly_all_pct": u, "weekly_resets_at": resets, "five_hour_pct": five}), encoding="utf-8", newline=NL)

    def state(self, now=MID):
        r = run(self.home, "state", now=now)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout.split()[0]

    def test_spend_below_pace_minus_ten(self):
        self.put(25.0)
        self.assertEqual(self.state(), "SPEND")

    def test_pace_minus_ten_boundary_is_normal(self):
        self.put(25.8)
        self.assertEqual(self.state(), "NORMAL")

    def test_normal_band(self):
        self.put(30)
        self.assertEqual(self.state(), "NORMAL")

    def test_throttle_above_pace_plus_five(self):
        self.put(40.8)
        self.assertEqual(self.state(), "THROTTLE")
        self.put(40.6)
        self.assertEqual(self.state(), "NORMAL")

    def test_five_hour_window_over_80_throttles_even_when_week_is_low(self):
        self.put(10, five=81)
        self.assertEqual(self.state(), "THROTTLE")
        self.put(10, five=80)
        self.assertEqual(self.state(), "SPEND")

    def test_last_day_spend_until_85(self):
        now = LAST
        self.put(84.9, utc=now)
        self.assertEqual(self.state(now), "SPEND")
        self.put(85.0, utc=now)
        self.assertEqual(self.state(now), "NORMAL")

    def test_missing_corrupt_and_stale_reading_is_normal(self):
        self.assertEqual(self.state(), "NORMAL")   # missing
        (self.home / "mts-budget.json").write_text("{nope", encoding="utf-8")
        self.assertEqual(self.state(), "NORMAL")
        self.put(99, utc="2026-10-15T05:59:00Z")   # 6 h 01 min old, would be THROTTLE
        self.assertEqual(self.state(), "NORMAL")
        self.put(99, utc="2026-10-15T06:30:00Z")   # 5.5 h old: still counts
        self.assertEqual(self.state(), "THROTTLE")

    def test_write_then_read_roundtrip(self):
        r = run(self.home, "write", "--weekly-all-pct", "40.8", "--weekly-resets-at", RESET, "--five-hour-pct", "12")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        d = json.loads((self.home / "mts-budget.json").read_text(encoding="utf-8"))
        self.assertEqual(d, {"utc": MID, "weekly_all_pct": 40.8, "weekly_resets_at": RESET, "five_hour_pct": 12.0})
        self.assertEqual(self.state(), "THROTTLE")


class TickWiring(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(REPO / "MyTradingSys" / "tests"))
        import test_relay_tick as t
        self.t = t
        self.case = t.TickLineTest("test_idle_tick_is_one_noop_line")
        self.case.setUp()
        self.case.home.mkdir(exist_ok=True)
        (self.case.home / "mts-hourly.json").write_text(json.dumps({"last_utc": "2026-10-15T09:50:00Z", "last_housekeep_utc": "2026-10-15T09:50:00Z"}))

    def budget(self, u, five=10):
        (self.case.home / "mts-budget.json").write_text(json.dumps(
            {"utc": MID, "weekly_all_pct": u, "weekly_resets_at": RESET, "five_hour_pct": five}), encoding="utf-8")

    def tick(self):
        c = self.case
        c.write(self.t.GO + self.t.BLOCK)
        return c.lines(c.tick("--refiner-tree", str(c.tmp / "none"), now=MID))

    def test_throttle_does_not_kick(self):
        self.budget(60)
        out = self.tick()
        self.assertTrue(out[0].startswith("TICK NOOP | budget=THROTTLE"), out[0])
        self.assertFalse((self.case.home / "mts-relay-lock.json").exists())   # no launch recorded

    def test_normal_still_kicks_and_the_line_names_the_state(self):
        self.budget(30)
        out = self.tick()
        self.assertTrue(out[0].startswith("TICK KICK"), out[0])
        self.assertIn("budget=NORMAL", out[0])

    def test_no_file_is_normal(self):
        out = self.tick()
        self.assertIn("budget=NORMAL", out[0])


class PromptAndGate(unittest.TestCase):
    def test_kick_prompt_writes_the_budget_first(self):
        text = (REPO / "scripts" / "sched" / "relay_prompts" / "relay_session.md").read_text(encoding="utf-8")
        self.assertIn("get_usage", text)
        self.assertIn("budget.py write", text)


if __name__ == "__main__":
    unittest.main()
