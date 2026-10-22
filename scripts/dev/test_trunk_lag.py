"""trunk_lag.py: a running session is told when its tree has fallen behind trunk (operator 2026-10-22)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trunk_lag as T


def sh(cwd, *args, env=None):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, env=env)


def commit(repo, name, when):
    env = dict(os.environ, GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    (Path(repo) / name).write_text(name, encoding="utf-8")
    sh(repo, "add", name, env=env)
    sh(repo, "commit", "-q", "-m", name, env=env)


class TrunkLagTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        base = Path(self.d.name)
        self.origin, self.tree = base / "origin", base / "tree"
        sh(base, "init", "-q", "-b", "fast-track", str(self.origin))
        commit(self.origin, "a", 1_000_000)
        sh(base, "clone", "-q", "-b", "fast-track", str(self.origin), str(self.tree))

    def tearDown(self):
        self.d.cleanup()

    def test_message_thresholds(self):
        self.assertEqual(T.message(0, 0), "")
        self.assertEqual(T.message(3, 600), "")
        self.assertIn("TRUNK LAG: this tree is 3 commit(s)", T.message(3, 2 * 3600))
        self.assertIn("2.0 h", T.message(3, 2 * 3600))
        self.assertIn("40 commit(s)", T.message(40, 300))

    def test_tree_behind_trunk_is_reported(self):
        commit(self.origin, "b", 1_000_100)
        commit(self.origin, "c", 1_000_200)
        behind, age = T.lag(self.tree, now=1_000_100 + 7200)
        self.assertEqual((behind, age), (2, 7200))
        sh(self.tree, "merge", "-q", "--ff-only", "origin/fast-track")
        self.assertEqual(T.lag(self.tree, now=1_000_100 + 7200, fetch=False), (0, 0))

    def test_fetch_is_throttled(self):
        T.lag(self.tree, now=1_000_000 + 10)
        commit(self.origin, "b", 1_000_050)
        self.assertEqual(T.lag(self.tree, now=1_000_000 + 20)[0], 0)
        self.assertEqual(T.lag(self.tree, now=1_000_000 + 20 + T.FETCH_EVERY_S)[0], 1)

    def test_registered_as_prompt_hook(self):
        root = Path(__file__).resolve().parents[2]
        ups = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]["UserPromptSubmit"]
        cmds = [h["command"] for e in ups for h in e["hooks"]]
        self.assertTrue(any("trunk_lag.py" in c for c in cmds), cmds)


if __name__ == "__main__":
    unittest.main()
