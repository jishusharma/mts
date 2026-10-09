"""B150: a new MyTradingSys/execution/test_*.py that is not wired into run_all_tests.py fails here."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {   # name -> reason it is deliberately not in the gate. Empty on purpose: add a reason, not a blind skip.
}


class GateDiscoveryTest(unittest.TestCase):
    def test_every_execution_test_is_gated_or_skipped_with_a_reason(self):
        gate = (ROOT / "scripts" / "dev" / "run_all_tests.py").read_text(encoding="utf-8")
        missing = sorted(p.stem for p in (ROOT / "MyTradingSys" / "execution").glob("test_*.py")
                         if f'"{p.stem}"' not in gate and p.stem not in SKIP)
        self.assertEqual(missing, [], "add to run_all_tests.py step 1 or to SKIP with a reason")
        self.assertTrue(all(isinstance(v, str) and v for v in SKIP.values()))


if __name__ == "__main__":
    unittest.main()
