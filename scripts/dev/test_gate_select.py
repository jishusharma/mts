"""gate_select: path -> gate steps. Fail closed on live-path and unmapped code."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_select as gs

STEPS = [("1", "python scripts/dev/run_staged_tests.py MyTradingSys/execution -- test_risk_guard"), ("3k", "python scripts/dev/test_sync.py"),
         ("3ds", "python scripts/dev/test_dsa.py"), ("3tl", "python scripts/dev/tasks.py lint"), ("3q", "x"), ("3pc", "x"),
         ("3c", "x"), ("3w", "x"), ("3x", "x"), ("3xt", "x"), ("4", "pytest MyTradingSys/tests"), ("4b", "pytest other"),
         ("4d", "pytest MyTradingSys/tests/docs"), ("5b", "unittest"), ("5c", "pytest options")]


class Select(unittest.TestCase):
    def sel(self, *files):
        return gs.select(list(files), STEPS)

    def test_nothing(self):
        self.assertEqual(self.sel(), ("none", []))

    def test_docs_only_runs_doc_invariants_only(self):
        mode, steps = self.sel("MyTradingSys/system/RELAY.md", "MyTradingSys/system/tasks/x.json")
        self.assertEqual(mode, "docs")
        self.assertEqual(steps, ["3tl", "3q", "3pc", "3c", "4d"])

    def test_non_live_code_is_smoke_with_its_own_test(self):
        mode, steps = self.sel("scripts/dev/dsa.py")
        self.assertEqual(mode, "smoke")
        self.assertIn("3ds", steps)
        self.assertNotIn("3k", steps)
        self.assertTrue({"3w", "3x", "3tl", "4"} <= set(steps))

    def test_layer_code_runs_layer_tests(self):
        mode, steps = self.sel("MyTradingSys/backtest/layers/rsi/rsi.py")
        self.assertEqual(mode, "smoke")
        self.assertIn("5b", steps)

    def test_live_path_is_full(self):
        for f in ("MyTradingSys/execution/auto_trader.py", "scripts/dev/sync.py", "scripts/dev/run_all_tests.py",
                  "scripts/dev/auto_deploy.py", "scripts/sched/relay.py", "src/main/java/A.java", "pom.xml",
                  ".github/workflows/ci.yml", "MyTradingSys/runtime/x.py", "MyTradingSys/backtest/layers/fabio/orderflow_live.py"):
            mode, steps = self.sel(f)
            self.assertEqual(mode, "full", f)
            self.assertEqual(steps, [n for n, _ in STEPS])

    def test_unmapped_code_fails_closed(self):
        for f in ("weird/thing.py", "tools/run.ps1", "MyTradingSys/newarea/x.py", "scripts/dev/run.sh", "Makefile",
                  "MyTradingSys/backtest/data.bin"):
            self.assertEqual(self.sel(f)[0], "full", f)

    def test_one_live_file_among_docs_makes_it_full(self):
        self.assertEqual(self.sel("README.md", "MyTradingSys/execution/executor.py")[0], "full")

    def test_docs_ride_along_with_code(self):
        _, steps = self.sel("scripts/dev/dsa.py", "MyTradingSys/system/RELAY.md")
        self.assertIn("4d", steps)
        self.assertIn("3q", steps)

    def test_windows_separators(self):
        self.assertEqual(self.sel("MyTradingSys\execution\auto_trader.py")[0], "full")


if __name__ == "__main__":
    unittest.main()
