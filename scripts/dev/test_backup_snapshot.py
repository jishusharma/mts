"""Tests for backup_snapshot.py: dirty + untracked work reaches the remote, the live tree is untouched,
and the public origin is never a target unless --allow-origin says so (the GitHub repo is public since 2026-10-11)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backup_snapshot as bs  # noqa: E402


def g(cwd, *args):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


class BackupSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        root = Path(self.td.name)
        self.remote = root / "remote.git"
        g(root, "init", "-q", "--bare", str(self.remote))
        self.repo = root / "repo"
        g(root, "init", "-q", str(self.repo))
        for k, v in (("user.name", "t"), ("user.email", "t@t"), ("commit.gpgsign", "false")):
            g(self.repo, "config", k, v)
        (self.repo / ".gitignore").write_text("ignored.txt\n", newline="\n")
        (self.repo / "a.txt").write_text("one\n", newline="\n")
        g(self.repo, "add", "-A")
        g(self.repo, "commit", "-q", "-m", "init")
        g(self.repo, "remote", "add", "backup", str(self.remote))            # the default target: the local bare repo
        self.public = root / "public.git"
        g(root, "init", "-q", "--bare", str(self.public))
        g(self.repo, "remote", "add", "origin", str(self.public))             # stands for the public GitHub repo
        self.wt = root / "wt"
        g(self.repo, "worktree", "add", "-q", "-b", "side", str(self.wt))

    def tearDown(self):
        self.td.cleanup()

    def remote_refs(self):
        return g(self.remote, "for-each-ref", "--format=%(refname)", "refs/heads/backup")

    def test_dirty_untracked_and_unpushed_work_is_backed_up_without_touching_trees(self):
        (self.repo / "a.txt").write_text("edited\n", newline="\n")           # modified tracked
        (self.repo / "new.txt").write_text("untracked\n", newline="\n")       # untracked
        (self.repo / "ignored.txt").write_text("skip\n", newline="\n")        # ignored
        (self.repo / ".env").write_text("KEY=1\n", newline="\n")              # secret-looking, not ignored here
        (self.wt / "b.txt").write_text("wt\n", newline="\n")
        g(self.wt, "add", "b.txt")
        g(self.wt, "commit", "-q", "-m", "unpushed")                          # commit only in the worktree
        status_before = g(self.repo, "status", "--porcelain")
        self.assertEqual(bs.main(["--repo", str(self.repo)]), 0)
        refs = self.remote_refs().splitlines()
        self.assertEqual(len(refs), 2, refs)
        main_ref = [r for r in refs if r.endswith("/repo")][0]
        files = g(self.remote, "ls-tree", "-r", "--name-only", main_ref).splitlines()
        self.assertIn("new.txt", files)
        self.assertNotIn("ignored.txt", files)
        self.assertNotIn(".env", files)
        self.assertEqual(g(self.remote, "show", "%s:a.txt" % main_ref), "edited")
        wt_ref = [r for r in refs if r.endswith("/wt")][0]
        self.assertIn("unpushed", g(self.remote, "log", "--format=%s", wt_ref))
        self.assertEqual(g(self.repo, "status", "--porcelain"), status_before)   # real index/files untouched
        self.assertEqual(g(self.repo, "stash", "list"), "")

    def test_second_run_is_noop_then_chains_fast_forward(self):
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        bs.main(["--repo", str(self.repo)])
        ref = [r for r in self.remote_refs().splitlines() if r.endswith("/repo")][0]
        first = g(self.remote, "rev-parse", ref)
        bs.main(["--repo", str(self.repo)])
        self.assertEqual(g(self.remote, "rev-parse", ref), first)                # unchanged -> no new commit
        (self.repo / "n.txt").write_text("2\n", newline="\n")
        self.assertEqual(bs.main(["--repo", str(self.repo)]), 0)
        second = g(self.remote, "rev-parse", ref)
        self.assertNotEqual(second, first)
        g(self.remote, "merge-base", "--is-ancestor", first, second)             # fast-forward, never forced

    def test_chains_onto_remote_tip_made_elsewhere(self):
        # another run/clone already pushed this worktree's ref: we must fast-forward it, not get rejected
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        bs.main(["--repo", str(self.repo)])
        ref = [r for r in self.remote_refs().splitlines() if r.endswith("/repo")][0]
        other = Path(self.td.name) / "other"
        g(self.td.name, "clone", "-q", str(self.remote), str(other))
        g(other, "config", "user.name", "o")
        g(other, "config", "user.email", "o@o")
        g(other, "checkout", "-q", "-B", "x", "origin/" + ref.replace("refs/heads/", ""))
        (other / "elsewhere.txt").write_text("e\n", newline="\n")
        g(other, "add", "-A")
        g(other, "commit", "-q", "-m", "elsewhere")
        g(other, "push", "-q", "origin", "x:" + ref)
        tip = g(self.remote, "rev-parse", ref)
        (self.repo / "n.txt").write_text("2\n", newline="\n")
        self.assertEqual(bs.main(["--repo", str(self.repo)]), 0)
        g(self.remote, "merge-base", "--is-ancestor", tip, ref)

    def public_refs(self):
        return g(self.public, "for-each-ref", "--format=%(refname)", "refs/heads/backup")

    def test_default_remote_is_backup_not_origin(self):
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        self.assertEqual(bs.main(["--repo", str(self.repo)]), 0)
        self.assertNotEqual(self.remote_refs(), "")
        self.assertEqual(self.public_refs(), "")

    def test_origin_is_refused_without_allow_origin(self):
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        self.assertEqual(bs.main(["--repo", str(self.repo), "--remote", "origin"]), 2)
        self.assertEqual(self.public_refs(), "")
        self.assertEqual(self.remote_refs(), "")

    def test_allow_origin_is_the_explicit_override(self):
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        self.assertEqual(bs.main(["--repo", str(self.repo), "--remote", "origin", "--allow-origin"]), 0)
        self.assertNotEqual(self.public_refs(), "")

    def test_a_second_name_or_the_bare_url_of_origin_is_refused_too(self):
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        g(self.repo, "remote", "add", "mirror", str(self.public))             # same URL as origin under another name
        self.assertEqual(bs.main(["--repo", str(self.repo), "--remote", "mirror"]), 2)
        self.assertEqual(bs.main(["--repo", str(self.repo), "--remote", str(self.public)]), 2)
        self.assertEqual(self.public_refs(), "")

    def test_dry_run_pushes_nothing(self):
        (self.repo / "n.txt").write_text("1\n", newline="\n")
        self.assertEqual(bs.main(["--repo", str(self.repo), "--dry-run"]), 0)
        self.assertEqual(self.remote_refs(), "")


if __name__ == "__main__":
    unittest.main()
