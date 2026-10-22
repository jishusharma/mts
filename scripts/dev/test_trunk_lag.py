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
        sh(base, "init", "-q", str(self.origin))          # no `init -b`: JIS-NUC runs git 2.24 (the option came in 2.28)
        sh(self.origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
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

    def test_session_start_fast_forwards_a_clean_trunk_checkout_only(self):
        # 2026-10-22: NB and the laptop started Supervisors on main checkouts nobody had pulled (old hooks, old guards)
        commit(self.origin, "b", 1_000_100)
        (self.origin / ".claude").mkdir()
        (self.origin / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
        sh(self.origin, "add", ".claude")
        commit(self.origin, "c", 1_000_200)
        sh(self.tree, "config", "user.email", "t@t")
        sh(self.tree, "config", "user.name", "t")
        (self.tree / "a").write_text("edited", encoding="utf-8")
        self.assertEqual(T.catch_up(self.tree), "", "tracked edits: left alone")
        sh(self.tree, "checkout", "-q", "--", "a")
        sh(self.tree, "checkout", "-q", "-b", "jis-nb/work")
        commit(self.tree, "own", 1_000_150)
        self.assertEqual(T.catch_up(self.tree), "", "a branch with its own commits: left alone")
        sh(self.tree, "checkout", "-q", "fast-track")
        (self.tree / "untracked.txt").write_text("x", encoding="utf-8")
        note = T.catch_up(self.tree)
        self.assertIn("fast-forwarded 2 commit(s)", note)
        self.assertIn("settings.json changed", note)
        self.assertEqual(T.lag(self.tree, fetch=False), (0, 0))
        self.assertEqual(T.catch_up(self.tree), "", "already current")
        (self.tree / ".mts_live").write_text("", encoding="utf-8")
        commit(self.origin, "d", 1_000_300)
        self.assertEqual(T.catch_up(self.tree), "", "the live tree changes only by a deploy")

    def test_app_worktree_and_main_checkout_catch_up(self):
        # 2026-10-22: Supervisors started in App worktrees (.claude/worktrees/<name>, own branch) cut from a stale main checkout
        wt = Path(self.d.name) / "tree" / ".claude" / "worktrees" / "zen"
        sh(self.tree, "worktree", "add", "-q", "-b", "claude/zen", str(wt))
        commit(self.origin, "b", 1_000_100)
        note = T.catch_up(wt)
        self.assertIn("this checkout fast-forwarded 1 commit(s)", note)
        self.assertIn("Main checkout", note)
        self.assertEqual(T.lag(wt, fetch=False), (0, 0))
        self.assertEqual(T.lag(self.tree, fetch=False), (0, 0))
        sh(self.tree, "checkout", "-q", "-b", "jis-nb/work")
        commit(self.origin, "c", 1_000_200)
        self.assertNotIn("Main checkout", T.catch_up(wt), "a main checkout off fast-track is not moved")
        sh(self.tree, "checkout", "-q", "fast-track")
        (self.tree / "a").write_text("edited", encoding="utf-8")
        self.assertIn("left alone (local edits)", T.catch_up(wt), "a stale main checkout is named, never silent")

    def test_registered_first_at_session_start(self):
        root = Path(__file__).resolve().parents[2]
        ss = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]["SessionStart"]
        self.assertIn("trunk_lag.py\" session-start", ss[0]["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
