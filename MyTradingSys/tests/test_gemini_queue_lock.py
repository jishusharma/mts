"""gemini-queue-parallel-runs-fail-concurre: parallel gemini_queue jobs must not die on a git .git/config lock."""
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import gemini_queue as gq  # noqa: E402

LOCKERR = "error: could not lock config file .git/config: File exists"


def _cp(rc, err=""):
    return subprocess.CompletedProcess([], rc, "", err)


class LockTest(unittest.TestCase):
    def test_retry_on_lock_error(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)):
            calls = []

            def fake(*a, **k):
                if a[0] == "worktree":
                    calls.append(a)
                    return _cp(255, LOCKERR) if len(calls) <= 2 else _cp(0)
                return _cp(0)
            with mock.patch.object(gq, "git", side_effect=fake):
                r = gq.add_worktree("c1", Path(t) / "c1", sleep=lambda s: None)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(len(calls), 3)

    def test_non_lock_error_not_retried(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)):
            n = []
            def fake(*a, **k):
                if a[0] == "worktree":
                    n.append(1)
                    return _cp(128, "fatal: invalid reference")
                return _cp(0)
            with mock.patch.object(gq, "git", side_effect=fake):
                r = gq.add_worktree("c1", Path(t) / "c1", sleep=lambda s: None)
            self.assertEqual((r.returncode, len(n)), (128, 1))

    def test_two_concurrent_setups_serialise(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)):
            active, peak, out = [0], [0], []
            guard = threading.Lock()

            def fake(*a, **k):
                if a[0] != "worktree":
                    return _cp(0)
                with guard:
                    active[0] += 1
                    peak[0] = max(peak[0], active[0])
                time.sleep(0.15)
                with guard:
                    active[0] -= 1
                return _cp(0)

            def job(c):
                out.append(gq.add_worktree(c, Path(t) / c, sleep=time.sleep).returncode)
            with mock.patch.object(gq, "git", side_effect=fake):
                ts = [threading.Thread(target=job, args=(c,)) for c in ("a", "b")]
                [x.start() for x in ts]
                [x.join() for x in ts]
            self.assertEqual(out, [0, 0])
            self.assertEqual(peak[0], 1)

    def test_lock_released_on_exception(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)):
            with mock.patch.object(gq, "git", side_effect=RuntimeError("boom")):
                with self.assertRaises(RuntimeError):
                    gq.add_worktree("c1", Path(t) / "c1", sleep=lambda s: None)
            self.assertFalse((Path(t) / ".git-setup.lock").exists())

    def test_stale_lock_broken_and_busy_times_out(self):
        import os
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)):
            lk = Path(t) / ".git-setup.lock"
            lk.write_text("x")
            old = time.time() - 500
            os.utime(lk, (old, old))
            with gq.setup_lock(sleep=lambda s: None):
                pass
            lk.write_text("x")
            with self.assertRaises(TimeoutError):
                with gq.setup_lock(timeout=0.3, sleep=lambda s: time.sleep(0.1)):
                    pass


if __name__ == "__main__":
    unittest.main()
