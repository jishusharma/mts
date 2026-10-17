"""B150: a tracked test_*.py that no gate step runs fails here.

Covered when ANY of: the stem is named in run_all_tests.py; the file is in scripts/dev/run_extra_tests.py EXTRA; it sits under
a directory the gate collects wholesale (MyTradingSys/tests pytest step, MyTradingSys/backtest rglob steps, options tests step);
or it is in SKIP with a reason. Archives are ignored.
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import run_extra_tests  # noqa: E402

SKIP = {   # relative path -> reason it is deliberately not in the gate. Empty on purpose: add a reason, not a blind skip.
}
COLLECTED_DIRS = ("MyTradingSys/tests/", "MyTradingSys/backtest/", "MyTradingSys/options/tests/")


def tracked_tests():
    out = subprocess.check_output(["git", "ls-files", "*test_*.py"], cwd=ROOT, text=True).splitlines()
    return [p for p in out if Path(p).name.startswith("test_") and "archive" not in p.lower()
            and not p.startswith(("Dumps/", "_archive/"))]


class GateDiscoveryTest(unittest.TestCase):
    def test_every_tracked_test_file_is_gated_or_skipped_with_a_reason(self):
        gate = (ROOT / "scripts" / "dev" / "run_all_tests.py").read_text(encoding="utf-8")
        extra = set(run_extra_tests.all_tests())          # EXTRA plus every study-folder test (discovered, no entry to keep)
        missing = []
        for rel in tracked_tests():
            stem = Path(rel).stem
            if rel in SKIP or rel in extra or rel.startswith(COLLECTED_DIRS) or f'"{stem}"' in gate or f"{stem}.py" in gate:
                continue
            missing.append(rel)
        self.assertEqual(missing, [], "add to run_all_tests.py, to run_extra_tests.EXTRA, or to SKIP with a reason")
        self.assertTrue(all(isinstance(v, str) and v for v in SKIP.values()))

    def test_extra_list_has_no_dead_entries(self):
        self.assertEqual([p for p in run_extra_tests.EXTRA if not (ROOT / p).exists()], [])


if __name__ == "__main__":
    unittest.main()
