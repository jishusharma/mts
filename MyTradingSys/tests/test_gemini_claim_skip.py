"""tc5-lab-lane-dedupe: gemini_queue.run_job skips a card another lane already claimed (cards_worked_by_two_lanes)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import gemini_queue as gq  # noqa: E402


class ClaimSkipTest(unittest.TestCase):
    def test_holder(self):
        self.assertEqual(gq.claim_holder("tom-v2", [("tom-v2", {"host": "JIS-NB"})]), "JIS-NB")
        self.assertEqual(gq.claim_holder("tom-v2", [("other", {"host": "x"})]), "")

    def test_run_job_skips_claimed(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)), \
                mock.patch.object(gq, "git"), mock.patch("sync.open_claims", return_value=[("tom-v2", {"host": "JIS-NB"})]), \
                mock.patch.object(gq.subprocess, "run") as run:
            gq.run_job("tom-v2", "low")
            self.assertIn("SKIP", (Path(t) / "tom-v2.log").read_text(encoding="utf-8"))
            run.assert_not_called()


class NoHangTest(unittest.TestCase):
    """gemini_queue must not hang on a credential prompt: every subprocess but agy has a timeout, all carry GCM_INTERACTIVE=never."""

    def _run(self, side_effect):
        import subprocess
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "c1").mkdir()
            with mock.patch.object(gq, "ROOT", Path(t)), mock.patch("sync.open_claims", return_value=[]),                     mock.patch.object(gq, "child_env", return_value={}),                     mock.patch.object(gq.subprocess, "run", side_effect=side_effect) as run:
                gq.run_job("c1", "low")
            return run, (Path(t) / "c1.log").read_text(encoding="utf-8")

    def test_every_call_has_timeout_and_no_prompt_env(self):
        import subprocess
        run, _ = self._run(lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "", ""))
        names = [str(c.args[0][1] if c.args[0][0] == gq.PY else c.args[0][0]) for c in run.call_args_list]
        self.assertTrue(any("sync.py" in n for n in names) and any(n == "git" for n in names), names)
        for c in run.call_args_list:
            self.assertEqual(c.kwargs["env"]["GCM_INTERACTIVE"], "never", c.args)
            if c.args[0][0] != str(gq.AGY):
                self.assertIn("timeout", c.kwargs, c.args)

    def test_claim_timeout_logs_and_skips_agy(self):
        import subprocess

        def fake(cmd, **kw):
            if "claim" in cmd:
                raise subprocess.TimeoutExpired(cmd, kw["timeout"])
            return subprocess.CompletedProcess(cmd, 0, "", "")
        run, log = self._run(fake)
        self.assertIn("CLAIM FAILED/TIMEOUT c1", log)
        self.assertFalse([c for c in run.call_args_list if c.args[0][0] == str(gq.AGY)])


if __name__ == "__main__":
    unittest.main()
