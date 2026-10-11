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


if __name__ == "__main__":
    unittest.main()
