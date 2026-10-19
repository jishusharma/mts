"""make_status.py: recent reports are dated by git commit, not mtime; CI line flags a stuck green ref; gate board.

Run: python scripts/dev/test_make_status.py
"""
import json
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
        t = commit_file(self.repo, "scripts/b.py", self.now - 5 * 60)
        self.refs(g, t)
        line = ms.get_ci_line(cwd=self.repo)
        self.assertIn("1 commit(s) behind", line)
        self.assertIn("CI running", line)
        self.assertNotIn("RED", line)

    def test_old_ungreen_commit_is_red(self):
        g = commit_file(self.repo, "a.txt", self.now - 2 * DAY)
        commit_file(self.repo, "scripts/b.py", self.now - 3 * 3600)
        t = commit_file(self.repo, "scripts/c.py", self.now - 60)
        self.refs(g, t)
        line = ms.get_ci_line(cwd=self.repo)
        self.assertIn("2 commit(s) behind", line)
        self.assertIn("RED", line)

    def test_docs_only_commits_ahead_are_ok_not_red(self):
        g = commit_file(self.repo, "a.txt", self.now - 2 * DAY)
        t = commit_file(self.repo, "MyTradingSys/research/NOTE.md", self.now - 3 * 3600)
        self.refs(g, t)
        line = ms.get_ci_line(cwd=self.repo)
        self.assertTrue(line.endswith("OK"), line)
        self.assertNotIn("RED", line)

    def test_missing_green_ref_says_so(self):
        commit_file(self.repo, "a.txt", self.now)
        self.assertIn("no origin/green/fast-track ref", ms.get_ci_line(cwd=self.repo))

    def test_behind_line_reports_landings_and_plain_commits_and_green_age(self):
        # A merge lands many commits as one first-parent step: the line must show both numbers, plus how old green is.
        g = commit_file(self.repo, "a.txt", self.now - 5 * 3600)
        git(self.repo, "checkout", "-q", "-b", "side")
        commit_file(self.repo, "scripts/s1.py", self.now - 4 * 3600)
        commit_file(self.repo, "scripts/s2.py", self.now - 3 * 3600)
        git(self.repo, "checkout", "-q", "-")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge side", "side", when=self.now - 60)
        t = git(self.repo, "rev-parse", "HEAD")
        self.refs(g, t)
        line = ms.get_ci_line(cwd=self.repo, now=datetime.fromtimestamp(self.now))
        self.assertTrue(line.startswith("CI green: "), line)       # dsa.py and cloud_setup.py read this prefix
        self.assertIn("1 trunk landing(s) / 3 commit(s) behind", line)
        self.assertIn("5.0 h old", line)


class CiCardLine(unittest.TestCase):
    """2026-10-16: make_status.py ran in the live tree while CI was red and filed an untracked ci-<sha>.json there; the same card shipped to
    fast-track then blocked the deploy merge. The live tree (marker FILE .mts_live) never files the card; builders' trees still do."""
    RED = "CI green: abc1234 (2026-10-15 20:00:00 +0000, 9.0 h old), 3 trunk landing(s) / 9 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 5.0 h old - CI is failing"

    def setUp(self):
        import ci_red_card
        self.calls = []
        self.orig = ci_red_card.run
        ci_red_card.run = lambda root, apply: (self.calls.append((root, apply)), ("FILED", "filed ci-abc1234"))[1]
        self.addCleanup(lambda: setattr(ci_red_card, "run", self.orig))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name

    def test_live_tree_does_not_file_the_card_and_says_so(self):
        (Path(self.root) / ".mts_live").write_text("", encoding="utf-8")
        self.assertEqual(ms.get_ci_card_line(self.RED, root=self.root, env={}), "CI card: not filed (live tree)")
        self.assertEqual(self.calls, [])
        self.assertEqual(list(Path(self.root).glob("MyTradingSys/**/*.json")), [])

    def test_builder_tree_still_files_the_card(self):
        line = ms.get_ci_card_line(self.RED, root=self.root, env={})
        self.assertEqual(line, "CI card: FILED; filed ci-abc1234")
        self.assertEqual(self.calls, [(str(Path(self.root).resolve()), True)])

    def test_nothing_to_say_when_ci_is_not_red_in_either_tree(self):
        ok = "CI green: abc1234 (2026-10-16 01:00:00 +0000) = origin/fast-track: OK"
        self.assertIsNone(ms.get_ci_card_line(ok, root=self.root, env={}))
        (Path(self.root) / ".mts_live").write_text("", encoding="utf-8")
        self.assertIsNone(ms.get_ci_card_line(ok, root=self.root, env={}))
        self.assertEqual(self.calls, [])

    def test_opt_out_env_keeps_the_line_out_entirely(self):
        self.assertIsNone(ms.get_ci_card_line(self.RED, root=self.root, env={"MTS_NO_CI_CARD": "1"}))
        self.assertEqual(self.calls, [])

    def test_a_filing_error_never_blocks_the_status_page(self):
        import ci_red_card

        def boom(root, apply):
            raise RuntimeError("gh")
        ci_red_card.run = boom
        self.assertIn("not filed (RuntimeError)", ms.get_ci_card_line(self.RED, root=self.root, env={}))

    def test_live_marker_is_a_file_at_the_root_not_a_nested_one(self):
        self.assertFalse(ms.is_live_tree(self.root))
        (Path(self.root) / "sub").mkdir()
        (Path(self.root) / "sub" / ".mts_live").write_text("", encoding="utf-8")
        self.assertFalse(ms.is_live_tree(self.root))
        (Path(self.root) / ".mts_live").write_text("", encoding="utf-8")
        self.assertTrue(ms.is_live_tree(self.root))

    def test_main_builds_its_card_line_through_get_ci_card_line(self):
        import inspect
        self.assertIn("get_ci_card_line(ci_line)", inspect.getsource(ms.main))


class TrunkLog(Base):
    def test_log_is_origin_fast_track_not_local_head(self):
        commit_file(self.repo, "a.txt", self.now - 3 * DAY)
        tip = commit_file(self.repo, "b.txt", self.now - 2 * DAY)
        git(self.repo, "update-ref", "refs/remotes/origin/fast-track", tip)
        commit_file(self.repo, "local_only.txt", self.now - DAY)       # this host's HEAD moved on; the trunk did not
        label, log = ms.get_trunk_log(2, cwd=self.repo)
        self.assertEqual(label, "origin/fast-track")
        self.assertEqual(len(log.splitlines()), 2)
        self.assertNotIn("local_only.txt", log)

    def test_without_the_trunk_ref_falls_back_to_head_and_says_so(self):
        commit_file(self.repo, "a.txt", self.now - DAY)
        label, log = ms.get_trunk_log(3, cwd=self.repo)
        self.assertIn("no origin/fast-track ref", label)
        self.assertEqual(len(log.splitlines()), 1)


class NewFiles(Base):
    def test_tracked_new_file_is_aged_by_its_commit_not_its_checkout_mtime(self):
        commit_file(self.repo, "MyTradingSys/x/staged.py.new", self.now - 3 * DAY)
        os.utime(Path(self.repo) / "MyTradingSys/x/staged.py.new", None)      # checkout stamps mtime = now
        (path, age), = ms.get_new_files(cwd=self.repo, now=datetime.fromtimestamp(self.now))
        self.assertEqual(path, "MyTradingSys/x/staged.py.new")
        self.assertAlmostEqual(age, 72.0, delta=0.1)

    def test_untracked_new_file_is_aged_by_mtime(self):
        commit_file(self.repo, "MyTradingSys/keep.txt", self.now - 30 * DAY)
        p = Path(self.repo) / "MyTradingSys/y/draft.py.new"
        p.parent.mkdir(parents=True)
        p.write_text("x\n", encoding="utf-8")
        os.utime(p, (self.now - 2 * 3600, self.now - 2 * 3600))
        (path, age), = ms.get_new_files(cwd=self.repo, now=datetime.fromtimestamp(self.now))
        self.assertAlmostEqual(age, 2.0, delta=0.1)


class HygieneSection(unittest.TestCase):
    def test_host_without_a_hygiene_report_gets_no_section_text(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ms.get_hygiene_status(Path(d)), "")


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


class GateBoard(Base):
    """Expected values by hand: proof committed 30 h / 2 h before now; commit mix 2 research, 1 claim, 1 other of 4 in 24 h."""
    def board(self, layers, when):
        commit_file(self.repo, ms.GATE_BOARD, when, json.dumps({"layers": layers}))

    def test_stale_proof_age_and_no_move_flag(self):
        self.board([{"layer": "tom", "gate": "G2", "proof": ["MyTradingSys/research/a/CAT.md"], "next": "G3"}], self.now - 50 * 3600)
        commit_file(self.repo, "MyTradingSys/research/a/CAT.md", self.now - 30 * 3600)
        lines = ms.get_gate_board(cwd=self.repo, now=self.now)
        self.assertTrue(lines[0].startswith("tom     G2  proof changed 30h ago | next: G3"), lines[0])
        self.assertIn("NO GATE MOVED IN 24h", lines[1])

    def test_recent_proof_clears_flag_and_missing_proof_says_so(self):
        self.board([{"layer": "tom", "gate": "G2", "proof": ["MyTradingSys/research/a/CAT.md"], "next": "G3"},
                    {"layer": "krown", "gate": "G1", "proof": ["MyTradingSys/research/k/NONE.md"], "next": "G2"}], self.now - 50 * 3600)
        commit_file(self.repo, "MyTradingSys/research/a/CAT.md", self.now - 2 * 3600)
        lines = ms.get_gate_board(cwd=self.repo, now=self.now)
        self.assertIn("proof changed 2h ago", lines[0])
        self.assertIn("proof not on trunk", lines[1])
        self.assertFalse(any("NO GATE MOVED" in ln for ln in lines))

    def test_commit_mix_counts_only_the_last_24h(self):
        commit_file(self.repo, "scripts/dev/old.py", self.now - 48 * 3600)
        commit_file(self.repo, "MyTradingSys/research/a/X.md", self.now - 3600)
        commit_file(self.repo, "MyTradingSys/methodology/W.md", self.now - 3500)
        commit_file(self.repo, "scripts/dev/y.py", self.now - 3400)
        git(self.repo, "commit", "--allow-empty", "-q", "-m", "claim some-task", when=self.now - 3300)
        self.assertEqual(ms.get_commit_mix("HEAD", cwd=self.repo, now=self.now),
                         "commits 24h: 4 = research 50% | claim/release 25% | other 25%")

    def test_status_md_alone_is_not_research_and_cap_flag_shows(self):
        commit_file(self.repo, "MyTradingSys/research/STATUS.md", self.now - 3600)
        commit_file(self.repo, "MyTradingSys/research/a/X.md", self.now - 3500)
        self.assertEqual(ms.get_commit_mix("HEAD", cwd=self.repo, now=self.now),
                         "commits 24h: 2 = research 50% | claim/release 0% | other 50%  OVER 30% CAP")


class TestStatusPath(unittest.TestCase):
    """Card move-live-host-generated-files: the live tree never rewrites the tracked STATUS.md (it blocked hand deploys)."""

    def test_live_tree_writes_the_ignored_copy(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ms.get_status_path(d), "MyTradingSys/research/STATUS.md")
            Path(d, ".mts_live").write_text("x")
            self.assertEqual(ms.get_status_path(d), "runtime_data/STATUS_live.md")


if __name__ == "__main__":
    unittest.main()
