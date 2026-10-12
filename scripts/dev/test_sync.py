"""sync.py: two clones of one origin ship to fast-track without losing each other's work."""
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def commit(repo, name, text):
    (repo / name).write_text(text, newline="\n")
    sh(repo, "add", name)
    sh(repo, "commit", "-q", "-m", name)


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git < 2.28 has no init -b
        self.a, self.b = self.tmp / "a", self.tmp / "b"
        for c in (self.a, self.b):
            sh(self.tmp, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
        commit(self.a, "README.md", "x\n")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.b, "pull", "-q", "origin", "fast-track")
        self.gated = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gate(self, repo):
        self.gated.append(repo)

    def head_files(self, repo):
        sh(repo, "fetch", "-q", "origin")
        r = subprocess.run(["git", "ls-tree", "--name-only", "origin/fast-track"], cwd=repo,
                           capture_output=True, text=True)
        return set(r.stdout.split())

    def test_concurrent_ships_both_land(self):
        commit(self.a, "a.py", "a\n")
        commit(self.b, "b.py", "b\n")
        sync.ship(self.a, gate=self.gate)
        sync.ship(self.b, gate=self.gate)  # b is behind: must merge, not fail or overwrite
        self.assertEqual(self.head_files(self.a), {"README.md", "a.py", "b.py"})

    def test_docs_only_skips_gate_code_runs_it(self):
        commit(self.a, "NOTE.md", "n\n")
        sync.ship(self.a, gate=self.gate)
        self.assertEqual(self.gated, [])
        commit(self.a, "c.py", "c\n")
        sync.ship(self.a, gate=self.gate)
        self.assertEqual(self.gated, [self.a])

    def test_claim_visible_to_other_clone_and_collision_refused(self):
        sync.claim(self.a, "Build thing one", area="scripts/dev", gate=self.gate)
        self.assertEqual(self.gated, [])  # claim files are docs: no gate
        sh(self.b, "pull", "-q", "origin", "fast-track")
        rows = sync.read_claims(self.b, "HEAD")
        self.assertEqual([r[0] for r in rows], ["build-thing-one"])
        with self.assertRaises(sync.SyncError):
            sync.claim(self.b, "Build thing one", gate=self.gate)
        sync.release(self.b, "build-thing-one", gate=self.gate)
        sh(self.a, "pull", "-q", "origin", "fast-track")
        self.assertEqual(sync.read_claims(self.a, "HEAD"), [])

    def test_claim_rejects_flag_like_name(self):
        with self.assertRaises(sync.SyncError):
            sync.claim(self.a, "--help", gate=self.gate)
        self.assertEqual(sync.read_claims(self.a, "HEAD"), [])

    def test_live_tree_refused(self):
        (self.a / sync.LIVE_MARKER).write_text("", newline="\n")
        with self.assertRaises(sync.SyncError):
            sync.start(self.a)
        with self.assertRaises(sync.SyncError):
            sync.ship(self.a, gate=self.gate)

    def test_other_sessions_uncommitted_work_does_not_block(self):
        (self.a / "README.md").write_text("half-done by another session\n", newline="\n")
        commit(self.a, "mine.py", "m\n")
        commit(self.b, "theirs.py", "t\n")
        sync.ship(self.b, gate=self.gate)
        sync.ship(self.a, gate=self.gate)  # merges theirs.py, pushes mine.py, leaves README.md alone
        self.assertEqual(self.head_files(self.a), {"README.md", "mine.py", "theirs.py"})
        self.assertEqual((self.a / "README.md").read_text(), "half-done by another session\n")

    def test_news_shows_result_line_not_code(self):
        (self.a / "f.py").write_text("x\n", newline="\n")
        sh(self.a, "add", "f.py")
        sh(self.a, "commit", "-q", "-m", "Tom alerts fire on 3m", "-m", "Result: 4 alerts in 2h replay")
        sync.ship(self.a, gate=self.gate)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.news(self.b)
        self.assertIn("Tom alerts fire on 3m", buf.getvalue())
        self.assertIn("Result: 4 alerts in 2h replay", buf.getvalue())

    def test_where_flags_unshipped_commit_and_clears_after_ship(self):
        commit(self.a, "w.txt", "w" + chr(10))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.where(self.a)
        self.assertIn("UNSHIPPED", buf.getvalue())
        self.assertIn("unshipped-commits=1", buf.getvalue())
        sync.ship(self.a, gate=self.gate)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.where(self.a)
        self.assertNotIn("UNSHIPPED ", buf.getvalue())

    def test_failed_gate_pushes_nothing(self):
        commit(self.a, "bad.py", "x\n")

        def fail(repo):
            raise sync.SyncError("gate")
        with self.assertRaises(sync.SyncError):
            sync.ship(self.a, gate=fail)
        self.assertNotIn("bad.py", self.head_files(self.b))

    def test_start_pulls_others_work(self):
        commit(self.a, "a.py", "a\n")
        sync.ship(self.a, gate=self.gate)
        sync.start(self.b)
        self.assertTrue((self.b / "a.py").exists())


    # ---- per-session tree, hot files, health (parallel-health task) ----
    def test_start_in_dirty_shared_tree_makes_fresh_worktree(self):
        (self.a / "README.md").write_text("another session's half-done edit\n", newline="\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            path = sync.start(self.a, slug="mine")
        self.assertNotEqual(Path(path), self.a)
        self.assertIn("WORKTREE:", buf.getvalue())
        self.assertEqual((Path(path) / "README.md").read_text(), "x\n")  # clean copy of origin
        self.assertEqual((self.a / "README.md").read_text(), "another session's half-done edit\n")
        br = subprocess.run(["git", "-C", str(path), "branch", "--show-current"],
                            capture_output=True, text=True).stdout.strip()
        self.assertTrue(br.endswith("/mine"), br)

    def test_start_in_tree_ahead_of_trunk_makes_fresh_worktree(self):
        commit(self.a, "unshipped.py", "u\n")  # commits no session has shipped
        with contextlib.redirect_stdout(io.StringIO()):
            path = sync.start(self.a, slug="next")
        self.assertNotEqual(Path(path), self.a)
        self.assertFalse((Path(path) / "unshipped.py").exists())

    def test_tidy_removes_only_clean_shipped_session_worktrees(self):
        with contextlib.redirect_stdout(io.StringIO()):
            done = sync.new_worktree(self.a, "done")        # clean, nothing of its own
            dirty = sync.new_worktree(self.a, "dirty")      # uncommitted file
            ahead = sync.new_worktree(self.a, "ahead")      # unshipped commit
        (dirty / "scratch.txt").write_text("wip\n", newline="\n")
        commit(ahead, "unshipped.py", "u\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a), [str(done.resolve())])      # dry run lists, removes nothing
            self.assertTrue(done.exists())
            self.assertEqual(sync.tidy(self.a, apply=True), [str(done.resolve())])
        self.assertFalse(done.exists())
        self.assertTrue(dirty.exists())
        self.assertTrue(ahead.exists())
        self.assertTrue(self.a.exists())  # primary tree never touched

    def test_start_in_clean_tree_stays_put(self):
        with contextlib.redirect_stdout(io.StringIO()):
            path = sync.start(self.b)
        self.assertEqual(Path(path), self.b)

    def test_hot_file_conflict_resolved_to_origin_not_stalled(self):
        name = "MyTradingSys/system/NEXT_SESSION.md"
        (self.a / name).parent.mkdir(parents=True, exist_ok=True)
        commit(self.a, name, "base\n")
        sync.ship(self.a, gate=self.gate)
        sh(self.b, "pull", "-q", "origin", "fast-track")
        commit(self.a, name, "from a\n")
        commit(self.b, name, "from b\n")
        commit(self.b, "b.py", "b\n")
        sync.ship(self.a, gate=self.gate)
        with contextlib.redirect_stdout(io.StringIO()):
            sync.ship(self.b, gate=self.gate)  # NEXT_SESSION.md collides: origin's text wins, ship goes on
        sh(self.a, "fetch", "-q", "origin")
        shown = subprocess.run(["git", "-C", str(self.a), "show", f"origin/fast-track:{name}"],
                               capture_output=True, text=True).stdout
        self.assertEqual(shown, "from a\n")
        self.assertIn("b.py", self.head_files(self.a))

    def test_real_code_conflict_still_stops(self):
        commit(self.a, "x.py", "base\n")
        sync.ship(self.a, gate=self.gate)
        sh(self.b, "pull", "-q", "origin", "fast-track")
        commit(self.a, "x.py", "a\n")
        commit(self.b, "x.py", "b\n")
        sync.ship(self.a, gate=self.gate)
        with self.assertRaises(sync.SyncError):
            sync.ship(self.b, gate=self.gate)

    def test_health_flags_overlap_and_shared_tree(self):
        sync.claim(self.a, "Task one", area="scripts/dev,MyTradingSys/backtest", gate=self.gate)
        sync.claim(self.a, "Task two", area="scripts/dev/sync.py", gate=self.gate)
        (self.a / "README.md").write_text("dirty\n", newline="\n")  # trunk tree with an uncommitted file
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            n = sync.health(self.a)
        out = buf.getvalue()
        self.assertIn("OVERLAP", out)
        self.assertIn("SHARED", out)
        self.assertGreaterEqual(n, 2)
        self.assertIn("HEALTH:", out.strip().splitlines()[-1])

    def test_health_clean_reports_zero(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            n = sync.health(self.a)
        self.assertEqual(n, 0)
        self.assertIn("HEALTH: 0", buf.getvalue())

    def test_gate_test_lists_are_one_entry_per_line(self):
        """Every new test appends to these lists; two entries on one line is a guaranteed merge conflict."""
        import re
        src = (Path(__file__).resolve().parent / "run_all_tests.py").read_text(encoding="utf-8")
        bad = [l.strip() for l in src.splitlines()
               if len(re.findall(r'"[\w/.-]+\.py"', l)) >= 2 and "sys.executable" not in l]
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
