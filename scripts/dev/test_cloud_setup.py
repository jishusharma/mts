"""cloud_setup.py: silent no-op off cloud (Windows hosts run this hook too); exit 0 even when git is unusable.

Run: python scripts/dev/test_cloud_setup.py
"""
import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cloud_setup as cs

REPO = Path(__file__).resolve().parents[2]


class CloudSetup(unittest.TestCase):
    def test_is_cloud_only_on_remote_flag(self):
        self.assertTrue(cs.is_cloud({"CLAUDE_CODE_REMOTE": "true"}))
        self.assertFalse(cs.is_cloud({}))
        self.assertFalse(cs.is_cloud({"CLAUDE_CODE_REMOTE": ""}))

    def test_off_cloud_prints_nothing_and_runs_nothing(self):
        buf = io.StringIO()
        with mock.patch.object(cs.subprocess, "run") as run, contextlib.redirect_stdout(buf):
            self.assertEqual(cs.main({}), 0)
        run.assert_not_called()
        self.assertEqual(buf.getvalue(), "")

    def test_on_cloud_git_failure_still_exits_zero(self):
        fail = mock.Mock(returncode=1, stdout="", stderr="no git")
        buf = io.StringIO()
        with mock.patch.object(cs.subprocess, "run", return_value=fail), contextlib.redirect_stdout(buf):
            self.assertEqual(cs.main({"CLAUDE_CODE_REMOTE": "true"}), 0)
        self.assertIn("[CLOUD SETUP]", buf.getvalue())

    def test_gate_deps_match_ci(self):
        ci = (REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("pip install " + " ".join(cs.GATE_DEPS), ci)


if __name__ == "__main__":
    unittest.main()
