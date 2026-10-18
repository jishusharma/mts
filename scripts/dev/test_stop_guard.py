import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stop_guard


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class StopGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        self.a = self.tmp / "a"
        sh(self.tmp, "clone", "-q", str(origin), str(self.a))
        sh(self.a, "config", "user.email", "t@t")
        sh(self.a, "config", "user.name", "t")
        (self.a / "README.md").write_text("x\n", newline="\n")
        sh(self.a, "add", "README.md")
        sh(self.a, "commit", "-q", "-m", "init")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.a, "checkout", "-q", "-b", "claude/work")   # a session tree is never on the trunk branch
        os.environ.pop("MTS_STOP_GUARD", None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_hook(self, **extra):
        return stop_guard.hook(json.dumps({"cwd": str(self.a), **extra}))

    def test_clean_tree_may_stop(self):
        self.assertEqual(self.run_hook(), "")

    def test_uncommitted_file_blocks_once(self):
        (self.a / "wip.py").write_text("x\n", newline="\n")
        out = json.loads(self.run_hook())
        self.assertEqual(out["decision"], "block")
        self.assertIn("sync.py ship", out["reason"])
        self.assertEqual(self.run_hook(stop_hook_active=True), "")   # never a loop

    def test_unshipped_commit_blocks_until_shipped(self):
        (self.a / "w.py").write_text("w\n", newline="\n")
        sh(self.a, "add", "w.py")
        sh(self.a, "commit", "-q", "-m", "w")
        self.assertIn("not shipped", self.run_hook())
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.a, "fetch", "-q", "origin")
        self.assertEqual(self.run_hook(), "")

    def test_same_state_blocks_a_session_only_once(self):
        os.environ["MTS_STOP_GUARD_HOME"] = str(self.tmp)
        self.addCleanup(os.environ.pop, "MTS_STOP_GUARD_HOME", None)
        (self.a / "wip.py").write_text("x\n", newline="\n")
        self.assertIn("block", self.run_hook(session_id="s1"))
        self.assertEqual(self.run_hook(session_id="s1"), "")                  # unchanged state: no second ~150k-token turn
        (self.a / "more.py").write_text("y\n", newline="\n")
        self.assertIn("block", self.run_hook(session_id="s1"))                # new work: blocks again
        self.assertIn("block", self.run_hook(session_id="s2"))                # another session: blocks

    def test_live_tree_and_off_switch_are_exempt(self):
        (self.a / "wip.py").write_text("x\n", newline="\n")
        os.environ["MTS_STOP_GUARD"] = "off"
        try:
            self.assertEqual(self.run_hook(), "")
        finally:
            os.environ.pop("MTS_STOP_GUARD", None)
        (self.a / ".mts_live").write_text("", newline="\n")
        self.assertEqual(self.run_hook(), "")

    def test_garbage_input_never_raises(self):
        self.assertEqual(stop_guard.hook("not json"), "")

    def test_antigravity_stop_hook_and_gemini_q_exemption(self):
        os.environ["MTS_STOP_GUARD_HOME"] = str(self.tmp)
        self.addCleanup(os.environ.pop, "MTS_STOP_GUARD_HOME", None)
        (self.a / "wip.py").write_text("x\n", newline="\n")
        payload = json.dumps({
            "conversationId": "conv-123",
            "workspacePaths": [str(self.a)],
            "terminationReason": "NO_TOOL_CALL",
        })
        out = json.loads(stop_guard.hook(payload))
        self.assertEqual(out["decision"], "continue")
        self.assertIn("sync.py ship", out["reason"])
        # Non-NO_TOOL_CALL termination (e.g. USER_CANCELED) is allowed to stop
        canceled = json.dumps({
            "conversationId": "conv-456",
            "workspacePaths": [str(self.a)],
            "terminationReason": "USER_CANCELED",
        })
        self.assertEqual(stop_guard.hook(canceled), "")
        # gemini-q/* branches commit without shipping (reviewed by Claude)
        sh(self.a, "checkout", "-q", "-b", "gemini-q/test-card")
        self.assertEqual(stop_guard.hook(json.dumps({
            "conversationId": "conv-789",
            "workspacePaths": [str(self.a)],
            "terminationReason": "NO_TOOL_CALL",
        })), "")


if __name__ == "__main__":
    unittest.main()
