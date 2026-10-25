"""Ship-time guard (operator 2026-10-25: "can we ship in 2 minutes" kept drifting): the cap constants stay put,
every subprocess runner in the gate is a known one, and sync.ship records its own wall time."""
import ast
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_select
import run_all_tests as rat
import sync


class GateCap(unittest.TestCase):
    # Every function in run_all_tests.py that starts a process. exec_step honours STEP_TIMEOUT_S/GATE_DEADLINE (the 90 s cap); the
    # others are listed on purpose: adding a new runner fails here until its author checks it sits under the cap and adds its name.
    KNOWN_RUNNERS = {"_short_sha", "exec_step", "exec_layer_chunks", "exec_unittest_shards", "run_mvn", "_git_out"}

    def test_time_cap_constants_stay_inside_the_two_minute_ship(self):
        self.assertLessEqual(rat.GATE_HARD_STEP_S, 90)
        self.assertLessEqual(gate_select.GATE_BUDGET_S, 40)
        self.assertLess(rat.GATE_HARD_STEP_S + 25, sync.SHIP_SLOW_S)

    def test_a_new_gate_step_runner_must_be_acknowledged(self):
        tree = ast.parse((Path(rat.__file__)).read_text(encoding="utf-8"))
        found = set()
        for fn in ast.walk(tree):
            if isinstance(fn, ast.FunctionDef):
                for n in ast.walk(fn):
                    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                            and n.func.value.id == "subprocess"):
                        found.add(fn.name)
        self.assertEqual(found - self.KNOWN_RUNNERS, set(), "new process runner in run_all_tests.py: route it through exec_step "
                         "(90 s cap) or prove it is under the cap, then add it to KNOWN_RUNNERS")
        self.assertIn("GATE_DEADLINE", Path(rat.__file__).read_text(encoding="utf-8").split("def exec_step")[1].split("def ")[0])


class ShipWall(unittest.TestCase):
    def test_ship_wall_row_and_slow_line(self):
        import io
        import contextlib
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "t.jsonl"
            log.write_text(json.dumps({"step": "3k", "name": "old step", "secs": 999}) + "\n", encoding="utf-8")
            off = log.stat().st_size
            with log.open("a", encoding="utf-8") as fh:
                for n, s in (("a", 30), ("b", 70), ("c", 20), ("d", 50)):
                    fh.write(json.dumps({"step": n, "name": n, "secs": s}) + "\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sync.record_ship_wall(d, 150, offset=off, path=log)
            out = buf.getvalue().strip()
            self.assertEqual(out, "SHIP SLOW 150s: top 3 steps b 70s, d 50s, a 30s")
            last = json.loads(log.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual((last["step"], last["secs"]), ("ship_wall", 150.0))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sync.record_ship_wall(d, 60, offset=off, path=log)
            self.assertEqual(buf.getvalue(), "")                      # fast ship: a row, no line
            self.assertEqual(json.loads(log.read_text(encoding="utf-8").splitlines()[-1])["secs"], 60.0)

    def test_ship_calls_record_ship_wall(self):
        src = Path(sync.__file__).read_text(encoding="utf-8").split("def ship(repo")[1].split("\ndef ")[0]
        self.assertIn("record_ship_wall(", src)

    def test_record_ship_wall_never_raises(self):
        sync.record_ship_wall("/nonexistent/\0bad", 500, path="/nonexistent/\0bad/x.jsonl")


if __name__ == "__main__":
    unittest.main()
