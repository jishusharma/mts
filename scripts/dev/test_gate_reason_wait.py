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

STEPS = [("3w", "x"), ("3x", "x"), ("3gd", "x"), ("3dl", "x"), ("3cm", "x"), ("4", "pytest MyTradingSys/tests/a")]


class PathClass(unittest.TestCase):
    def mode(self, f):
        return gs.explain([f], STEPS)[0]

    def test_pages_under_tools_are_smoke(self):
        for f in ("MyTradingSys/tools/live_aid/home.js", "MyTradingSys/tools/live_aid/live_aid.html", "MyTradingSys/tools/x/a.css"):
            self.assertEqual(self.mode(f), "smoke", f)

    def test_scratch_output_is_docs(self):
        for f in ("run.out", "gate.log", "scripts/dev/run.out", "notes.txt"):
            self.assertEqual(self.mode(f), "docs", f)

    def test_unknown_code_still_fails_closed(self):
        for f in ("tools/foo.py", "other/x.java", "foo.js"):
            self.assertEqual(self.mode(f), "full", f)

    def test_live_path_file_still_full(self):
        for f in ("MyTradingSys/execution/risk_guard.py", "src/main/java/A.java", "MyTradingSys/runtime/state.log", "MyTradingSys/runtime/x.out",
                  "MyTradingSys/execution/ui.js"):
            self.assertEqual(self.mode(f), "full", f)


class Staging(unittest.TestCase):
    def test_scratch_never_staged(self):
        self.assertTrue(sync.never_stage("run.out"))
        self.assertTrue(sync.never_stage("sub/gate.log"))
        self.assertFalse(sync.never_stage("scripts/dev/gate_select.py"))


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
