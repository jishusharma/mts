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
        self.assertEqual(p.limit_for("a.py::t", {}), 300)
        self.assertEqual(p.limit_for("a.py::t", {"MTS_TEST_LIMIT_S": "0"}), 0)
        self.assertEqual(p.limit_for("x/test_aibridge_exploratory.py::t", {}), 400)
        self.assertEqual(p.limit_for("MyTradingSys/tests/test_aibridge_selftest_concurrent.py::t::test_agent_live_selftest_concurrent_and_port_clash", {}), 450)

    def test_ci_has_the_300s_limit_unless_env_set(self):
        import pytest_test_limit as p
        self.assertEqual(p.limit_for("a.py::t", {"GITHUB_ACTIONS": "true"}), 300)
        self.assertEqual(p.limit_for("a.py::t", {"GITHUB_ACTIONS": "true", "MTS_TEST_LIMIT_S": "90"}), 90)

    def test_aibridge_chain_allowance_covers_ci_time(self):
        import pytest_test_limit as p
        nid = "MyTradingSys/tests/test_aibridge_chain.py::T::test_long_unattended_chain_hidden_tab_with_failure_timeout_and_dropped_reply"
        self.assertGreaterEqual(p.limit_for(nid, {}), 3 * 144)   # CI file total 144 s (run 43075303873) is the bound for one test
        self.assertEqual(p.limit_for(nid, {"MTS_TEST_LIMIT_S": "5"}), 450)   # the allowance wins over a short base, like any listed test

    def test_recorded_slot_forwards_settings_to_the_real_slot(self):
        """ci-hang-fix-1113: timeout/poll set on the gate_slot_factory wrapper were dropped, so test_sync's gate-slot test waited forever."""
        import run_all_tests as rat
        slot = rat.gate_slot_factory("fast")()
        slot.timeout, slot.poll = 0.2, 0.05
        self.assertEqual((slot.inner.timeout, slot.inner.poll), (0.2, 0.05))

    def test_hung_unittest_shard_is_killed_with_a_hung_line(self):
        import run_all_tests as rat
        p = subprocess.Popen([sys.executable, "-c", "import time;print('test_x (m.T.test_x) ...', flush=True);time.sleep(60)"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out = rat.communicate_or_kill(p, timeout=2)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("HUNG", out)
        self.assertIn("test_x", out)

    def test_gate_notice_lists_per_test_seconds(self):
        import run_all_tests as rat
        rat.TEST_SECONDS.clear(); rat.FILE_SECONDS.clear()
        rat.note_file_seconds("\n".join(["12.40s call     MyTradingSys/tests/test_a.py::T::slow",
                                         "0.70s call     MyTradingSys/tests/test_a.py::T::fast"]))
        self.assertIn("Gate test times::MyTradingSys/tests/test_a.py::T::slow=12s", rat.times_notice())
        rat.TEST_SECONDS.clear(); rat.FILE_SECONDS.clear()


if __name__ == "__main__":
    unittest.main()
