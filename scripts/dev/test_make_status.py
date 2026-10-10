"""make_status.py: recent reports are dated by git commit, not mtime; CI line flags a stuck green ref.

Run: python scripts/dev/test_make_status.py
"""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_status as ms

DAY = 86400


def git(repo, *args, when=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    if when is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"@{int(when)} +0000"
    return subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True).stdout.strip()


def commit_file(repo, rel, when, text="# heading\n"):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", rel, when=when)
    return git(repo, "rev-parse", "HEAD")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-q")
        self.now = time.time()

    def tearDown(self):
        self.tmp.cleanup()


class RecentReports(Base):
    def test_old_commit_with_fresh_mtime_is_excluded(self):
        # A fresh clone stamps every file with checkout time; the old handoff must not show as recent.
        commit_file(self.repo, "MyTradingSys/research/OLD_HANDOFF.md", self.now - 30 * DAY)
        os.utime(Path(self.repo) / "MyTradingSys/research/OLD_HANDOFF.md", None)  # mtime = now
        names = [r[0] for r in ms.get_recent_reports(cwd=self.repo)]
        self.assertNotIn("MyTradingSys/research/OLD_HANDOFF.md", names)

    def test_recent_commit_is_listed_with_commit_time(self):
        when = self.now - 2 * DAY
        commit_file(self.repo, "MyTradingSys/research/x/NEW_REPORT.md", when, "# New report\n")
        reports = ms.get_recent_reports(cwd=self.repo)
        self.assertEqual([r[0] for r in reports], ["MyTradingSys/research/x/NEW_REPORT.md"])
        self.assertEqual(reports[0][1], datetime.fromtimestamp(int(when)).strftime("%Y-%m-%d %H:%M"))
        self.assertEqual(reports[0][2], "# New report")

    def test_old_file_touched_by_recent_commit_is_listed(self):
        commit_file(self.repo, "MyTradingSys/research/A_REPORT.md", self.now - 30 * DAY)
        commit_file(self.repo, "MyTradingSys/research/A_REPORT.md", self.now - 1 * DAY, "# edited\n")
        self.assertEqual([r[0] for r in ms.get_recent_reports(cwd=self.repo)], ["MyTradingSys/research/A_REPORT.md"])

    def test_untracked_report_uses_mtime(self):
        commit_file(self.repo, "MyTradingSys/research/keep.txt", self.now - 30 * DAY)
        p = Path(self.repo) / "MyTradingSys/research/DRAFT_SESSION.md"
        p.write_text("# draft\n", encoding="utf-8")
        self.assertIn("MyTradingSys/research/DRAFT_SESSION.md", [r[0] for r in ms.get_recent_reports(cwd=self.repo)])
        os.utime(p, (self.now - 9 * DAY, self.now - 9 * DAY))
        self.assertNotIn("MyTradingSys/research/DRAFT_SESSION.md", [r[0] for r in ms.get_recent_reports(cwd=self.repo)])

    def test_non_report_names_ignored(self):
        commit_file(self.repo, "MyTradingSys/research/notes.md", self.now - DAY)
        self.assertEqual(ms.get_recent_reports(cwd=self.repo), [])


class CiLine(Base):
    def refs(self, green, tip):
        git(self.repo, "update-ref", "refs/remotes/origin/green/fast-track", green)
        git(self.repo, "update-ref", "refs/remotes/origin/fast-track", tip)

    def test_green_equals_tip_ok(self):
        sha = commit_file(self.repo, "a.txt", self.now - DAY)
        self.refs(sha, sha)
        self.assertTrue(ms.get_ci_line(cwd=self.repo).endswith("OK"))

    def test_fresh_ungreen_commit_is_running_not_red(self):
        g = commit_file(self.repo, "a.txt", self.now - DAY)
        t = commit_file(self.repo, "b.txt", self.now - 5 * 60)
        self.refs(g, t)
        line = ms.get_ci_line(cwd=self.repo)
        self.assertIn("1 commit(s) behind", line)
        self.assertIn("CI running", line)
        self.assertNotIn("RED", line)

    def test_old_ungreen_commit_is_red(self):
        g = commit_file(self.repo, "a.txt", self.now - 2 * DAY)
        commit_file(self.repo, "b.txt", self.now - 3 * 3600)
        t = commit_file(self.repo, "c.txt", self.now - 60)
        self.refs(g, t)
        line = ms.get_ci_line(cwd=self.repo)
        self.assertIn("2 commit(s) behind", line)
        self.assertIn("RED", line)

    def test_missing_green_ref_says_so(self):
        commit_file(self.repo, "a.txt", self.now)
        self.assertIn("no origin/green/fast-track ref", ms.get_ci_line(cwd=self.repo))


class LessonsLine(Base):
    def write(self, rel, text):
        p = Path(self.repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def blob(self):
        return git(self.repo, "hash-object", ms.LESSONS)[:8]

    def test_in_sync(self):
        self.write(ms.LESSONS, "# L\n- one\n")
        self.write(ms.DIGEST, f"Synced at blob: {self.blob()} x\n")
        self.assertEqual(ms.get_lessons_line(cwd=self.repo), "LESSONS: digest in sync")

    def test_new_lesson_makes_digest_stale(self):
        self.write(ms.LESSONS, "# L\n- one\n")
        self.write(ms.DIGEST, f"Synced at blob: {self.blob()} x\n")
        self.write(ms.LESSONS, "# L\n- one\n- two\n")
        self.assertIn("STALE", ms.get_lessons_line(cwd=self.repo))

    def test_missing_digest_points_to_full_file(self):
        self.write(ms.LESSONS, "# L\n")
        self.assertIn("read MyTradingSys/system/LESSONS_LEARNED.md in full", ms.get_lessons_line(cwd=self.repo))


if __name__ == "__main__":
    unittest.main()
