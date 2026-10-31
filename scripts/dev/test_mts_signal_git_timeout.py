import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mts_signal


class TestGitTimeout(unittest.TestCase):
    def test_timeout_gives_clear_error(self):
        exc = subprocess.TimeoutExpired(["git"], 7)
        with mock.patch.object(mts_signal.subprocess, "run", side_effect=exc):
            with self.assertRaises(RuntimeError) as cm:
                mts_signal.git(".", "fetch", "origin", timeout=7)
        msg = str(cm.exception)
        self.assertIn("git fetch origin", msg)
        self.assertIn("7", msg)
        self.assertIn("timed out", msg)

    def test_timeout_still_raises_when_check_is_false(self):
        # fail closed: a hung git is never read as a clean result
        with mock.patch.object(mts_signal.subprocess, "run", side_effect=subprocess.TimeoutExpired(["git"], 3)):
            with self.assertRaises(RuntimeError):
                mts_signal.git(".", "status", check=False, timeout=3)


if __name__ == "__main__":
    unittest.main()
