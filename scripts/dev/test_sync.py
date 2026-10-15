"""sync.py: two clones of one origin ship to fast-track without losing each other's work."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

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

    def test_tidy_removes_only_clean_idle_shipped_session_worktrees(self):
        with contextlib.redirect_stdout(io.StringIO()):
            done = sync.new_worktree(self.a, "done")        # clean, nothing of its own, idle long enough
            dirty = sync.new_worktree(self.a, "dirty")      # uncommitted file
            ahead = sync.new_worktree(self.a, "ahead")      # unshipped commit
        (dirty / "scratch.txt").write_text("wip\n", newline="\n")
        commit(ahead, "unshipped.py", "u\n")
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, now=later), [str(done.resolve())])      # dry run lists, removes nothing
            self.assertTrue(done.exists())
            self.assertEqual(sync.tidy(self.a, apply=True, now=later), [str(done.resolve())])
        self.assertFalse(done.exists())
        self.assertTrue(dirty.exists())
        self.assertTrue(ahead.exists())
        self.assertTrue(self.a.exists())  # primary tree never touched

    def test_tidy_keeps_a_just_started_worktree(self):
        with contextlib.redirect_stdout(io.StringIO()):
            fresh = sync.new_worktree(self.a, "fresh")      # clean and on origin, but a session may be about to use it
            self.assertEqual(sync.tidy(self.a, apply=True), [])
        self.assertTrue(fresh.exists())

    def test_tidy_keeps_a_worktree_holding_ignored_data(self):
        (self.a / ".gitignore").write_text("Dumps/*\n", newline="\n")
        sh(self.a, "add", ".gitignore")
        sh(self.a, "commit", "-q", "-m", "ignore")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "data")
        (wt / "Dumps").mkdir()
        (wt / "Dumps" / "klines.csv").write_text("1,2,3\n", newline="\n")
        (wt / "__pycache__").mkdir()
        (wt / "__pycache__" / "x.pyc").write_bytes(b"0")
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=later), [])
        self.assertTrue((wt / "Dumps" / "klines.csv").exists())

    def test_tidy_ignores_only_regenerable_ignored_files(self):
        (self.a / ".gitignore").write_text("__pycache__/\ntarget/\n", newline="\n")
        sh(self.a, "add", ".gitignore")
        sh(self.a, "commit", "-q", "-m", "ignore")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "cache")
        (wt / "target").mkdir()
        (wt / "target" / "A.class").write_bytes(b"0")
        (wt / "__pycache__").mkdir()
        (wt / "__pycache__" / "x.pyc").write_bytes(b"0")
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=later), [str(wt.resolve())])

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

    # ---- repo hygiene across machines: the pulled mirror, App-named trees, a readable `where` ----
    def track_mirror(self):
        """Old base: runtime_data/_mirror was committed, so every `sync.py start` (pull) dirtied the tree."""
        (self.a / "runtime_data" / "_mirror").mkdir(parents=True)
        commit(self.a, "runtime_data/_mirror/m.txt", "m0\n")
        sync.ship(self.a, gate=self.gate)

    def noisy_tree(self, slug):
        """A clean tree on origin whose only changes are the pulled mirror and a stray AGENTS.md."""
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, slug)
        (wt / "runtime_data" / "_mirror" / "m.txt").write_text("m1\n", newline="\n")
        (wt / "AGENTS.md").write_text("stray\n", newline="\n")
        return wt

    def out_of(self, fn, *a, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fn(*a, **kw)
        return buf.getvalue()

    def test_where_default_lists_only_real_work_and_stays_short(self):
        self.track_mirror()
        with contextlib.redirect_stdout(io.StringIO()):
            sync.new_worktree(self.a, "clean1")
            real = sync.new_worktree(self.a, "real")
        self.noisy_tree("noisy")
        commit(real, "r.py", "r\n")
        out = self.out_of(sync.where, self.a)
        self.assertIn("unshipped-commits=1", out)
        self.assertNotIn("clean1", out)
        self.assertNotIn("noisy", out)
        self.assertIn("1 worktree(s) hold work that is not on origin/fast-track", out)
        self.assertIn("where --all", out)
        self.assertLess(len(out), 1500)

    def test_where_all_lists_every_tree_and_counts_noise_as_ok(self):
        self.track_mirror()
        with contextlib.redirect_stdout(io.StringIO()):
            sync.new_worktree(self.a, "clean1")
        self.noisy_tree("noisy")
        out = self.out_of(sync.where, self.a, True)
        rows = {l.split()[1]: l.split()[0] for l in out.splitlines() if l.split() and l.split()[0] in ("ok", "UNSHIPPED")}
        self.assertEqual(rows[next(n for n in rows if "clean1" in n)], "ok")
        self.assertEqual(rows[next(n for n in rows if "noisy" in n)], "ok")  # mirror edits and AGENTS.md are not work
        self.assertIn("0 worktree(s) hold work", out)

    def test_where_names_the_real_branch_of_a_case_mismatched_shell(self):
        sh(self.a, "branch", "Case/Real", "origin/fast-track")
        wt = self.tmp.resolve() / "casewt"
        sh(self.a, "worktree", "add", "-q", str(wt), "Case/Real")
        sh(self.a, "pack-refs", "--all")                       # packed refs are matched case-sensitively, loose files are not
        sh(wt, "symbolic-ref", "HEAD", "refs/heads/case/real")  # what the 7 JIS-NB shells look like
        if subprocess.run(["git", "-C", str(wt), "rev-parse", "--verify", "--quiet", "HEAD"], capture_output=True).returncode == 0:
            self.skipTest("this git resolves refs case-insensitively")
        full = self.out_of(sync.where, self.a, True)
        self.assertIn("BROKEN", full)
        self.assertIn("symbolic-ref HEAD refs/heads/Case/Real", full)
        short = self.out_of(sync.where, self.a)
        self.assertIn("BROKEN", short)
        self.assertIn("casewt", short)
        self.assertNotIn("symbolic-ref", short)  # one line for all shells; the fix per tree is in --all

    def test_where_all_flag_is_accepted_on_the_command_line(self):
        import os
        cwd = os.getcwd()
        os.chdir(self.a)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = sync.main(["where", "--all"])
        finally:
            os.chdir(cwd)
        self.assertEqual(rc, 0)
        self.assertIn("worktree(s) hold work", buf.getvalue())

    def test_health_ignores_mirror_and_agents_noise(self):
        self.track_mirror()
        self.noisy_tree("noisy")
        out = self.out_of(sync.health, self.a)
        self.assertNotIn("UNSHIPPED", out)
        self.assertIn("HEALTH: 0", out)

    def test_status_never_takes_the_index_lock_of_another_sessions_tree(self):
        seen = []
        real = subprocess.run

        def spy(argv, *a, **kw):
            seen.append(list(argv))
            return real(argv, *a, **kw)
        with mock.patch.object(sync.subprocess, "run", spy):
            sync.git(self.a, "status", "--short")
        self.assertIn("--no-optional-locks", seen[0])

    def test_merge_drops_an_edited_pulled_mirror_when_trunk_untracks_it(self):
        """The commit that untracks runtime_data/_mirror deletes files an old-base tree edited by pulling: that must not stall."""
        self.track_mirror()
        sh(self.b, "pull", "-q", "origin", "fast-track")
        (self.b / "runtime_data" / "_mirror" / "m.txt").write_text("pulled later\n", newline="\n")
        (self.b / "runtime_data" / "_mirror" / "new.txt").write_text("untracked pull result\n", newline="\n")
        sh(self.a, "rm", "-q", "--cached", "-r", "runtime_data/_mirror")
        (self.a / ".gitignore").write_text("runtime_data/_mirror/\n", newline="\n")
        sh(self.a, "add", ".gitignore")
        sh(self.a, "commit", "-q", "-m", "untrack the mirror")
        sync.ship(self.a, gate=self.gate)
        self.assertEqual(sync.merge_trunk(self.b), 1)
        tracked = subprocess.run(["git", "-C", str(self.b), "ls-files", "runtime_data/_mirror"], capture_output=True, text=True).stdout
        self.assertEqual(tracked.strip(), "")

    def test_start_keeps_a_tree_whose_only_dirt_is_the_pulled_mirror(self):
        self.track_mirror()
        sh(self.b, "pull", "-q", "origin", "fast-track")
        (self.b / "runtime_data" / "_mirror" / "m.txt").write_text("pulled later\n", newline="\n")
        with contextlib.redirect_stdout(io.StringIO()):
            path = sync.start(self.b)
        self.assertEqual(Path(path), self.b)  # no extra worktree for mirror churn

    def make_tree(self, path, branch):
        path.parent.mkdir(parents=True, exist_ok=True)
        sh(self.a, "worktree", "add", "-q", "-b", branch, str(path), "origin/fast-track")
        return path

    def test_tidy_retires_app_named_and_relay_trees_but_not_lanes_or_strangers(self):
        base = self.tmp.resolve()
        app = self.make_tree(base / ".claude" / "worktrees" / "brave-noether-416473", "claude/brave-noether-416473")
        relay = self.make_tree(base / "mts-relay-20261014T0517", "jisnb/relay-20261014T0517")
        lane = self.make_tree(base / "mts-relay", "jisnb/relay")
        other = self.make_tree(base / "scratch-thing", "x/scratch")
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sorted(sync.tidy(self.a, now=later)), sorted([str(app), str(relay)]))
            self.assertTrue(app.exists())  # dry run removes nothing
            sync.tidy(self.a, apply=True, now=later)
        self.assertFalse(app.exists())
        self.assertFalse(relay.exists())
        self.assertTrue(lane.exists())
        self.assertTrue(other.exists())
        branches = subprocess.run(["git", "-C", str(self.a), "branch", "--list", "claude/*", "jisnb/*"], capture_output=True, text=True).stdout
        self.assertNotIn("brave-noether", branches)
        self.assertIn("jisnb/relay\n", branches + "\n")

    def test_tidy_keeps_an_app_tree_with_commits_not_on_origin(self):
        base = self.tmp.resolve()
        app = self.make_tree(base / ".claude" / "worktrees" / "keen-ramanujan-0e0dbf", "claude/keen-ramanujan-0e0dbf")
        commit(app, "unshipped.py", "u\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600), [])
        self.assertTrue(app.exists())

    def test_idle_clock_reads_the_last_reflog_entry_not_the_reflog_file_mtime(self):
        # JIS-NB 2026-10-15: a `git gc` reflog expire rewrote logs/HEAD of 95 trees without adding entries, and tidy
        # called trees idle 32-140 h "active 5.3 h". The last entry inside logs/HEAD is the sign of life, not its mtime.
        base = self.tmp.resolve()
        app = self.make_tree(base / ".claude" / "worktrees" / "idle-gc-touched", "claude/idle-gc-touched")
        later = time.time() + 48 * 3600
        gd = Path(subprocess.run(["git", "-C", str(app), "rev-parse", "--absolute-git-dir"],
                                 capture_output=True, text=True).stdout.strip())
        self.assertTrue((gd / "logs" / "HEAD").read_text().strip())  # last entry stamped now, i.e. 48 h before `later`
        os.utime(gd / "logs" / "HEAD", (later, later))  # gc rewrote the file at `later`
        self.assertAlmostEqual(sync.idle_hours(app, "claude/idle-gc-touched", later), 48, delta=0.5)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, now=later), [str(app)])

    def test_tidy_all_keeps_the_mts_control_room_routine_folder(self):
        lane = self.make_tree(self.tmp.resolve() / "mts-control-room", "jisnb/control-room")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, include_named=True, now=time.time() + 48 * 3600), [])
        self.assertTrue(lane.exists())

    def test_tidy_does_not_count_noise_or_empty_ignored_dirs_as_work(self):
        (self.a / ".gitignore").write_text("Dumps/*\n.claude/settings.local.json\n", newline="\n")
        sh(self.a, "add", ".gitignore")
        sh(self.a, "commit", "-q", "-m", "ignore")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        self.track_mirror()
        wt = self.noisy_tree("quiet")
        (wt / "Dumps" / "workers").mkdir(parents=True)                       # empty ignored dir: the 33 trees tidy refused
        (wt / ".claude").mkdir()
        (wt / ".claude" / "settings.local.json").write_text("{}\n", newline="\n")  # identical copy in every tree
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=later), [str(wt.resolve())])
        self.assertFalse(wt.exists())

    def test_tidy_still_keeps_a_tree_with_a_real_uncommitted_file(self):
        self.track_mirror()
        wt = self.noisy_tree("realdirt")
        (wt / "notes.py").write_text("work\n", newline="\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600), [])
        self.assertTrue((wt / "notes.py").exists())

    def test_tidy_prints_counts_and_at_most_ten_keep_lines(self):
        for i in range(12):
            with contextlib.redirect_stdout(io.StringIO()):
                wt = sync.new_worktree(self.a, f"dirty{i}")
            (wt / "scratch.txt").write_text("wip\n", newline="\n")
        out = self.out_of(sync.tidy, self.a, now=time.time() + 48 * 3600)
        lines = out.splitlines()
        self.assertLessEqual(len([l for l in lines if l.startswith("keep")]), 10)
        self.assertIn("kept 12", lines[-1])
        self.assertIn("uncommitted 12", lines[-1])

    def test_tidy_retires_a_new_base_tree_holding_the_ignored_mirror_pytest_tmp_and_codex(self):
        """New base: the mirror is git-ignored, so `status --ignored` lists it and a pull fills it. It is regenerable, not data."""
        (self.a / ".gitignore").write_text("runtime_data/_mirror/\nruntime_data/_mirror.*\n.pytest_tmp/\n.codex/\n", newline="\n")
        sh(self.a, "add", ".gitignore")
        sh(self.a, "commit", "-q", "-m", "ignore the droppings")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "newbase")
        for rel in ("runtime_data/_mirror/live/state.json", "runtime_data/_mirror.lock/pid", ".pytest_tmp/run1/out.txt", ".codex/cache/c.bin"):
            f = wt / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x\n", newline="\n")
        self.assertEqual(sync.ignored_data(wt), [])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600), [str(wt.resolve())])
        self.assertFalse(wt.exists())

    def test_tidy_still_keeps_a_tree_with_other_ignored_data(self):
        (self.a / ".gitignore").write_text("runtime_data/_mirror/\nDumps/*\n", newline="\n")
        sh(self.a, "add", ".gitignore")
        sh(self.a, "commit", "-q", "-m", "ignore")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "hasdata")
        (wt / "runtime_data" / "_mirror").mkdir(parents=True)
        (wt / "runtime_data" / "_mirror" / "m.txt").write_text("m\n", newline="\n")
        (wt / "Dumps").mkdir()
        (wt / "Dumps" / "result.csv").write_text("1,2\n", newline="\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600), [])
        self.assertTrue((wt / "Dumps" / "result.csv").exists())

    def test_where_always_prints_the_row_of_the_tree_it_runs_in(self):
        """Own tree sorts last in `git worktree list` and holds real work: it is still printed, ahead of the cap."""
        with contextlib.redirect_stdout(io.StringIO()):
            others = [sync.new_worktree(self.a, f"other{i}") for i in range(5)]
            own = sync.new_worktree(self.a, "mine")
        for i, wt in enumerate(others):
            commit(wt, f"o{i}.py", "o\n")
        commit(own, "mine.py", "m\n")
        real = sync.worktrees

        def own_last(repo):
            rows = real(repo)
            return [r for r in rows if Path(r[0]).resolve() != own.resolve()] + [r for r in rows if Path(r[0]).resolve() == own.resolve()]
        with mock.patch.object(sync, "ROW_CAP", 3), mock.patch.object(sync, "worktrees", own_last):
            out = self.out_of(sync.where, own)
        rows = [l for l in out.splitlines() if l.startswith("UNSHIPPED")]
        self.assertIn(own.name, rows[0], out)  # this tree first, whatever the list order
        self.assertEqual(len(rows), 3)
        self.assertIn("3 more with unshipped work", out)  # 6 unshipped trees: 3 rows, the rest counted
        self.assertIn("6 worktree(s) hold work", out)

    def test_where_prints_the_own_tree_row_even_when_it_is_clean(self):
        with contextlib.redirect_stdout(io.StringIO()):
            own = sync.new_worktree(self.a, "cleanown")
        out = self.out_of(sync.where, own)
        self.assertTrue(any(l.startswith("ok") and own.name in l for l in out.splitlines()), out)
        self.assertIn("0 worktree(s) hold work", out)

    def test_health_keeps_the_collision_rows_in_the_last_eight_lines(self):
        """daily_hygiene reads only the tail of `sync.py health`: many UNSHIPPED trees must not push SHARED/NEVER-SHIPPED out of it."""
        import daily_hygiene
        fake = [dict(path=str(self.tmp), name=f"t{i}", branch=f"x/t{i}", ahead=1, work=[], noise=[], fix="") for i in range(sync.ROW_CAP + 5)]
        fake.append(dict(path=str(self.a), name="a", branch="fast-track", ahead=1, work=[], noise=[], fix=""))
        sh(self.b, "switch", "-q", "-c", "idea")
        commit(self.b, "idea.py", "i\n")
        sh(self.b, "push", "-q", "origin", "idea")
        sh(self.a, "fetch", "-q", "origin")
        with mock.patch.object(sync, "survey", return_value=fake), mock.patch.object(sync, "NOT_SHIPPED_HOURS", -1):
            out = self.out_of(sync.health, self.a)
        lines = out.splitlines()
        tail = daily_hygiene._tail(out)
        self.assertTrue(lines[-1].startswith("HEALTH:"))
        self.assertTrue(any(l.startswith("SHARED") for l in tail), tail)
        self.assertTrue(any(l.startswith("NEVER-SHIPPED") for l in tail), tail)
        self.assertEqual(len([l for l in lines if l.startswith("UNSHIPPED")]), sync.ROW_CAP)
        self.assertTrue(any("more UNSHIPPED" in l for l in lines))

    def test_gate_test_lists_are_one_entry_per_line(self):
        """Every new test appends to these lists; two entries on one line is a guaranteed merge conflict."""
        import re
        src = (Path(__file__).resolve().parent / "run_all_tests.py").read_text(encoding="utf-8")
        bad = [l.strip() for l in src.splitlines()
               if len(re.findall(r'"[\w/.-]+\.py"', l)) >= 2 and "sys.executable" not in l]
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
