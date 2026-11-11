"""The gate's per-test limit names a hung test (ship-gate-per-test-timeout-1111)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DEV = Path(__file__).resolve().parent
sys.path.insert(0, str(DEV))


class PerTestLimit(unittest.TestCase):
    def run_pytest(self, extra_args, limit):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_sleepy.py").write_text("import time\n\ndef test_hangs_here():\n    time.sleep(60)\n", encoding="utf-8")
            env = dict(os.environ, MTS_TEST_LIMIT_S=str(limit), PYTHONPATH=str(DEV))
            return subprocess.run([sys.executable, "-m", "pytest", "test_sleepy.py", "-q", "-p", "no:cacheprovider", *extra_args],
                                  cwd=d, capture_output=True, text=True, env=env, timeout=50)

    def test_sleeping_test_is_named_within_the_limit(self):
        r = self.run_pytest(["-p", "pytest_test_limit"], 2)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("TEST TIMEOUT", r.stderr)
        self.assertIn("test_sleepy.py::test_hangs_here", r.stderr)

    def test_gate_pytest_cmd_loads_the_plugin(self):
        import run_all_tests as rat
        for cmd in (rat.pytest_cmd(["x"]),):
            self.assertIn("pytest_test_limit", cmd)

    def test_limit_for(self):
        import pytest_test_limit as p
        self.assertEqual(p.limit_for("a.py::t", {}), 120)
        self.assertEqual(p.limit_for("a.py::t", {"MTS_TEST_LIMIT_S": "0"}), 0)
        self.assertEqual(p.limit_for("x/test_aibridge_exploratory.py::t", {}), 400)


if __name__ == "__main__":
    unittest.main()
