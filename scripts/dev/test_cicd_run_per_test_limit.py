"""cicd_run.py pytest calls carry the ship-gate per-test limit (cicd-run-per-test-limit-1111)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DEV = Path(__file__).resolve().parent
sys.path.insert(0, str(DEV))
import cicd_run


class CicdRunLimit(unittest.TestCase):
    def pytest_cmds(self):
        seen = []

        def fake(cmd, cwd=None, env=None):
            seen.append(list(cmd))
            return 0, "1 passed", 0.0
        ctx = cicd_run.Ctx(repo=DEV.parent.parent, run=fake, out_dir=tempfile.mkdtemp(), quick=True, profile="desktop")
        ctx.which = lambda n: None
        try:
            cicd_run.stage_build(ctx)
        except Exception:
            pass
        return [c for c in seen if "pytest" in c and "-m" in c]

    def test_all_four_pytest_invocations_carry_the_limit(self):
        cmds = self.pytest_cmds()
        self.assertGreaterEqual(len(cmds), 3, cmds)
        for c in cmds:
            self.assertIn("pytest_test_limit", c, c)

    def test_forbidden_phrases_call_carries_the_limit(self):
        src = (DEV / "cicd_run.py").read_text(encoding="utf-8")
        i = src.index("test_2_no_forbidden_refs")
        self.assertIn("TEST_LIMIT_ARGS", src[i - 300:i])

    def test_sleeping_test_fails_naming_the_test_through_default_run(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_sleepy.py").write_text("import time\n\ndef test_hangs_here():\n    time.sleep(60)\n", encoding="utf-8")
            old = os.environ.get("MTS_TEST_LIMIT_S"), os.environ.pop("GITHUB_ACTIONS", None)
            os.environ["MTS_TEST_LIMIT_S"] = "2"
            try:
                rc, out, _ = cicd_run.default_run([sys.executable, "-m", "pytest", "test_sleepy.py", "-q", "-p", "no:cacheprovider",
                                                   *cicd_run.TEST_LIMIT_ARGS], cwd=d)
            finally:
                if old[0] is None:
                    os.environ.pop("MTS_TEST_LIMIT_S", None)
                else:
                    os.environ["MTS_TEST_LIMIT_S"] = old[0]
                if old[1]:
                    os.environ["GITHUB_ACTIONS"] = old[1]
            self.assertNotEqual(rc, 0)
            self.assertIn("test_sleepy.py::test_hangs_here", out)
            self.assertIn("TEST TIMEOUT", out)

    def test_known_long_test_is_exempt_not_killed(self):
        import pytest_test_limit as p
        nid = "MyTradingSys/tests/test_aibridge_chain.py::T::test_long_unattended_chain_hidden_tab_with_failure_timeout_and_dropped_reply"
        self.assertGreaterEqual(p.limit_for(nid, {"MTS_TEST_LIMIT_S": "120"}), 432)


if __name__ == "__main__":
    unittest.main()
