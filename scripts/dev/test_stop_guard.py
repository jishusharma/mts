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

    def test_live_tree_and_off_switch_are_exempt(self):
        (self.a / "wip.py").write_text("x\n", newline="\n")
        os.environ["MTS_STOP_GUARD"] = "off"
        try:
            self.assertEqual(self.run_hook(), "")
        finally:
            os.environ.pop("MTS_STOP_GUARD", None)
        (self.a / ".mts_live").write_text("", newline="\n")
        self.assertEqual(self.run_hook(), "")

    def refs(self, bare):
        return subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/leftovers"], cwd=bare,
                              capture_output=True, text=True).stdout.split()

    def show(self, bare, spec):
        return subprocess.run(["git", "show", spec], cwd=bare, capture_output=True, text=True).stdout

    def test_stop_snapshots_the_dirty_tree_losslessly_to_the_backup_repo(self):
        backup = self.tmp / "backup.git"
        sh(self.tmp, "init", "-q", "--bare", str(backup))
        sh(self.a, "remote", "add", "backup", str(backup))
        (self.a / "wip.py").write_text("unsaved\n", newline="\n")
        out = json.loads(self.run_hook())
        self.assertEqual(out["decision"], "block")
        self.assertIn("refs/leftovers/a", out["reason"])
        self.assertEqual(self.refs(backup), ["refs/leftovers/a"])
        self.assertEqual(self.show(backup, "refs/leftovers/a:wip.py").strip(), "unsaved")
        st = subprocess.run(["git", "status", "--short"], cwd=self.a, capture_output=True, text=True).stdout
        self.assertEqual(st.strip(), "?? wip.py")                            # tree untouched: nothing staged or committed
        (self.a / "wip.py").write_text("newer\n", newline="\n")              # the second stop is allowed AND re-snapshots
        self.assertEqual(self.run_hook(stop_hook_active=True), "")
        self.assertEqual(self.show(backup, "refs/leftovers/a:wip.py").strip(), "newer")
        self.assertEqual(self.refs(self.tmp / "origin.git"), [])

    def test_missing_backup_remote_still_blocks_once_without_raising(self):
        (self.a / "wip.py").write_text("x\n", newline="\n")
        out = json.loads(self.run_hook())
        self.assertEqual(out["decision"], "block")

    def test_garbage_input_never_raises(self):
        self.assertEqual(stop_guard.hook("not json"), "")


if __name__ == "__main__":
    unittest.main()
