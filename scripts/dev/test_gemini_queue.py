"""gemini-queue-claim-race-fix: claim retries on a busy trunk, own claim = ok, other holder = skip, git identity set."""
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gemini_queue as gq  # noqa: E402

REJ = "push rejected (someone shipped first)"


def cp(rc, err=""):
    return subprocess.CompletedProcess([], rc, "", err)


class ClaimRetryTest(unittest.TestCase):
    def test_reject_3_times_then_accept(self):
        seq = [cp(1, REJ), cp(1, REJ), cp(1, REJ), cp(0)]
        sleeps = []
        with mock.patch.object(gq, "sh", side_effect=seq) as sh:
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=sleeps.append), ("ok", ""))
        self.assertEqual(sh.call_count, 4)
        self.assertEqual(len(sleeps), 3)
        self.assertTrue(all(2 <= s <= 10 for s in sleeps))

    def test_gives_up_after_6(self):
        with mock.patch.object(gq, "sh", return_value=cp(1, REJ)) as sh:
            st, why = gq.claim_with_retry("wt", "c1", sleep=lambda s: None)
        self.assertEqual((st, sh.call_count), ("fail", 6))
        self.assertIn("6 tries", why)

    def test_other_holder_skips_at_once(self):
        with mock.patch.object(gq, "sh", return_value=cp(1, "already claimed by OTHER-HOST / x: c1")) as sh:
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=lambda s: None)[0], "skip")
        self.assertEqual(sh.call_count, 1)

    def test_own_claim_is_success(self):
        err = f"already claimed by {socket.gethostname()} / me: c1"
        with mock.patch.object(gq, "sh", return_value=cp(1, err)):
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=lambda s: None)[0], "ok")

    def test_timeout_fails_without_retry(self):
        with mock.patch.object(gq, "sh", return_value=cp(124, "timeout after 120s")) as sh:
            self.assertEqual(gq.claim_with_retry("wt", "c1", sleep=lambda s: None)[0], "fail")
        self.assertEqual(sh.call_count, 1)


class RunJobTest(unittest.TestCase):
    def _run(self, claim_result):
        calls = []
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "c1").mkdir()

            def fake_git(*a, **kw):
                calls.append(a)
                return cp(0)
            with mock.patch.object(gq, "ROOT", Path(t)), mock.patch.object(gq, "git", side_effect=fake_git), \
                    mock.patch("sync.open_claims", return_value=[]), \
                    mock.patch.object(gq, "claim_with_retry", return_value=claim_result), \
                    mock.patch.object(gq.subprocess, "run") as run:
                gq.run_job("c1", "low")
            return calls, (Path(t) / "c1.log").read_text(encoding="utf-8"), run

    def test_identity_set_and_failure_logged(self):
        calls, log, run = self._run(("fail", "after 6 tries: rejected"))
        self.assertIn(("config", "user.name", "gemini-queue"), calls)
        self.assertIn(("config", "user.email", "gemini-queue@mts.local"), calls)
        self.assertTrue(log.startswith("CLAIM FAILED: c1: after 6 tries"), log)
        self.assertEqual(len(log.strip().splitlines()), 1)
        run.assert_not_called()

    def test_skip_logged(self):
        _, log, run = self._run(("skip", "already claimed by X"))
        self.assertTrue(log.startswith("SKIP c1"), log)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
