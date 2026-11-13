"""gate-select-unknown-paths-1112: pages/scratch output are not a full gate, live path still is, ship rows carry gate_reason and the real slot wait."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_select as gs
import run_all_tests as rat
import sync

STEPS = [("3w", "x"), ("3x", "x"), ("3dl", "x"), ("3cm", "x"), ("4", "pytest MyTradingSys/tests/a")]


class PathClass(unittest.TestCase):
    def mode(self, f):
        return gs.explain([f], STEPS)[0]

    def test_pages_under_tools_are_smoke(self):
        for f in ("MyTradingSys/tools/live_aid/home.js", "MyTradingSys/tools/live_aid/live_aid.html", "MyTradingSys/tools/x/a.css"):
            self.assertEqual(self.mode(f), "smoke", f)

    def test_scratch_output_is_docs(self):
        for f in ("run.out", "gate.log", "scripts/dev/run.out", "notes.txt"):
            self.assertEqual(self.mode(f), "docs", f)

    def test_unknown_code_is_the_fast_gate(self):
        for f in ("tools/foo.py", "other/x.java", "foo.js"):
            self.assertEqual(self.mode(f), "smoke", f)   # change 1: an unknown path off the live list no longer fails closed to the full gate

    def test_live_path_file_is_live_mode(self):
        for f in ("MyTradingSys/execution/risk_guard.py", "src/main/java/A.java", "MyTradingSys/runtime/state.log", "MyTradingSys/runtime/x.out",
                  "MyTradingSys/execution/ui.js"):
            self.assertEqual(self.mode(f), "live", f)   # change 2: execution tests + static suite, full suite in CI


class PlanShape(unittest.TestCase):
    """changes 3 and 4 (SHIP_ARCH_REVIEW_2026-11-12): the card lint warns, the hand-kept test-list check is gone."""

    def test_card_lint_step_is_warn_only_and_3gd_is_gone(self):
        plan = {s.num: s for s in rat.build_plan(True)}
        self.assertIn("--warn", plan["3tl"].cmd)
        self.assertNotIn("3gd", plan)
        self.assertNotIn("3gd", gs.ALWAYS)
        self.assertNotIn("3gd", rat.CHEAP_STEPS)
        for keep in ("3pc", "3vd", "3la", "3x", "3w"):   # these stay blocking steps of the plan
            self.assertIn(keep, plan)

    def test_gate_slots_stay_two(self):
        self.assertEqual(sync.GATE_SLOTS, 2)


class CoordinatorTiming(unittest.TestCase):
    """change 8: one row per plan run, outside the repo; nothing is cut."""

    def test_plan_timing_row_is_written(self):
        import supervisor
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(supervisor.record_plan_timing("C", 3.456, n_lines=12, context_tokens=90000, running=2, home=d))
            row = json.loads((Path(d) / "C-plan-timing.jsonl").read_text().splitlines()[-1])
            self.assertEqual((row["login"], row["wall_s"], row["lines"], row["context_tokens"], row["running"]), ("C", 3.46, 12, 90000, 2))


class Staging(unittest.TestCase):
    def test_scratch_never_staged(self):
        self.assertTrue(sync.never_stage("run.out"))
        self.assertTrue(sync.never_stage("sub/gate.log"))
        self.assertFalse(sync.never_stage("scripts/dev/gate_select.py"))

    def test_root_junk_is_never_staged(self):
        # change 5 (SHIP_ARCH_REVIEW_2026-11-12): any *.log / *.out in the repo root, and ship*.log anywhere
        for f in ("build.log", "ship_out.out", "ship-20261112.log", "sub/ship.log", "nohup.out"):
            self.assertTrue(sync.never_stage(f), f)
        for f in ("notes.md", "scripts/dev/x.out.py", "docs/build.log.md"):
            self.assertFalse(sync.never_stage(f), f)


class Timing(unittest.TestCase):
    def test_slot_wait_and_reason_flow_into_ship_row(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.jsonl"
            rat.record_gate_row("gate_info", path=p, gate_reason="full: x is on the live path", mode="full")
            rat.record_gate_row("gate_slot", path=p, wait_s=12.5, mode="full")
            wait, reason = sync.gate_log_info(d, 0, path=p)
            self.assertEqual((wait, reason), (12.5, "full: x is on the live path"))
            sync.record_ship_timing(d, wait_s=wait, run_s=1, retry_s=0, path=p, sha="abc", gate_reason=reason)
            row = json.loads(p.read_text().splitlines()[-1])
            self.assertEqual((row["wait_s"], row["gate_reason"]), (12.5, "full: x is on the live path"))
            self.assertEqual(sync.failed_step_ids(d, 0, path=p), [])

    def test_gate_mode_and_phases_flow_into_ship_row(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.jsonl"
            rat.record_gate_row("gate_info", path=p, gate_reason="live: x", mode="live")
            self.assertEqual(sync.gate_log_mode(d, 0, path=p), "live")
            sync.record_ship_timing(d, wait_s=1, run_s=2, retry_s=0, path=p, sha="abc", gate_mode="live", phases={"merge_s": 1.234, "push_s": 0.5})
            row = json.loads(p.read_text().splitlines()[-1])
            self.assertEqual(row["gate_mode"], "live")
            self.assertEqual(row["phases"], {"merge_s": 1.23, "push_s": 0.5})

    def test_ship_row_also_lands_in_the_per_machine_home_log(self):
        # test_value_audit_1113: runtime_data/gate_timing.jsonl dies with its work tree; the home log survives it
        import os
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as home:
            tree, hp = Path(d), Path(home) / ".mts" / "gate_timing.jsonl"
            old = {k: os.environ.pop(k, None) for k in ("MTS_GATE_TIMING", "MTS_GATE_TIMING_HOME")}
            os.environ["MTS_GATE_TIMING_HOME"] = str(hp)
            try:
                sync.record_ship_timing(tree, wait_s=1, run_s=2, retry_s=0, sha="abc123", gate_mode="smoke")
            finally:
                os.environ.pop("MTS_GATE_TIMING_HOME", None)
                os.environ.update({k: v for k, v in old.items() if v is not None})
            local = json.loads((tree / "runtime_data" / "gate_timing.jsonl").read_text().splitlines()[-1])
            home_row = json.loads(hp.read_text().splitlines()[-1])
            self.assertEqual(home_row["sha"], local["sha"])
            self.assertEqual(home_row["tree"], str(tree))
            self.assertEqual(home_row["run_s"], 2)

    def test_an_explicit_path_does_not_touch_the_home_log(self):
        import os
        from unittest import mock
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as home:
            hp = Path(home) / "h.jsonl"
            old = {k: os.environ.pop(k, None) for k in ("MTS_GATE_TIMING", "MTS_GATE_TIMING_HOME")}
            try:
                with mock.patch.object(sync, "home_timing_path", return_value=hp):
                    sync.record_ship_timing(d, wait_s=1, run_s=2, retry_s=0, path=Path(d) / "t.jsonl", sha="abc")
            finally:
                os.environ.update({k: v for k, v in old.items() if v is not None})
            self.assertFalse(hp.exists())

    def test_slot_wrapper_records_wait(self):
        with tempfile.TemporaryDirectory() as d:
            import os
            os.environ["MTS_GATE_TIMING"] = str(Path(d) / "t.jsonl")
            try:
                inner = sync.gate_slot(Path(d), alive=lambda p: True)
                with rat._RecordedSlot(inner, "fast"):
                    pass
            finally:
                del os.environ["MTS_GATE_TIMING"]
            row = json.loads((Path(d) / "t.jsonl").read_text().splitlines()[0])
            self.assertEqual((row["step"], row["mode"]), ("gate_slot", "fast"))


if __name__ == "__main__":
    unittest.main()
