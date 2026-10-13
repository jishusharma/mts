"""Gate coverage: run_all_tests.py must run Fabio v3 + live-writer tests (TF1, review E7)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all_tests as rat


class GateCoverage(unittest.TestCase):
    def test_pytest_paths_cover_v3_and_live_writers(self):
        paths = getattr(rat, "PYTEST_LAYER_PATHS", [])
        for want in ("fabio/v3/tests", "test_orderflow_live.py", "test_of_backfill.py", "test_htf_context_live.py"):
            self.assertTrue(any(p.endswith(want) for p in paths), want)

    def test_every_gated_path_exists(self):
        for p in getattr(rat, "PYTEST_LAYER_PATHS", []):
            self.assertTrue((rat.REPO / p).exists(), p)



class TestPytestTmpIsolation(unittest.TestCase):
    def test_isolate_pytest_tmp_sets_fresh_root_for_children(self):
        import os
        old = os.environ.pop("PYTEST_DEBUG_TEMPROOT", None)
        try:
            root = rat.isolate_pytest_tmp()
            self.assertTrue(os.path.isdir(root))
            self.assertEqual(os.environ["PYTEST_DEBUG_TEMPROOT"], root)
        finally:
            os.environ.pop("PYTEST_DEBUG_TEMPROOT", None)
            if old is not None:
                os.environ["PYTEST_DEBUG_TEMPROOT"] = old


class TestParallelLayerGate(unittest.TestCase):
    def test_quick_gate_runs_every_layer_module(self):
        mods = rat.find_layer_modules()
        self.assertTrue(mods)
        for jobs in (1, 2, 4, 7, 10_000):
            chunks = rat.split_modules(mods, jobs)
            flat = [m for c in chunks for m in c]
            self.assertEqual(sorted(flat), sorted(mods), jobs)
            self.assertEqual(len(flat), len(set(flat)), jobs)
            self.assertTrue(all(chunks))

    def test_gate_jobs_env(self):
        import os
        old = os.environ.get("MTS_GATE_JOBS")
        try:
            os.environ["MTS_GATE_JOBS"] = "1"
            self.assertEqual(rat.gate_jobs(), 1)
            os.environ["MTS_GATE_JOBS"] = "0"
            self.assertEqual(rat.gate_jobs(), 1)
            os.environ.pop("MTS_GATE_JOBS")
            self.assertGreaterEqual(rat.gate_jobs(), 1)
        finally:
            os.environ.pop("MTS_GATE_JOBS", None)
            if old is not None:
                os.environ["MTS_GATE_JOBS"] = old

    def test_backup_trigger_minute_differs_from_deploy_slot(self):
        import re
        d = rat.REPO / "scripts"
        backup = (d / "dev" / "install_backup_task.ps1").read_text(encoding="utf-8")
        deploy = (d / "sched" / "register_cicd_tasks.ps1").read_text(encoding="utf-8")
        b = re.search(r"-At \(Get-Date\)\.Date(?:\.AddMinutes\((\d+)\))?\s+-RepetitionInterval", backup)
        self.assertIsNotNone(b, "backup trigger must anchor on today's midnight")
        d_ = re.search(r"-At \(Get-Date\)\.Date(?:\.AddMinutes\((\d+)\))?\s+-RepetitionInterval \(New-TimeSpan -Minutes 15\)", deploy)
        self.assertIsNotNone(d_)
        bo, do = int(b.group(1) or 0), int(d_.group(1) or 0)
        self.assertNotEqual(bo % 15, do % 15)


if __name__ == "__main__":
    unittest.main()
