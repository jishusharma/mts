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
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def commit(repo, name, text):
    (repo / name).write_text(text, newline="\n")
    sh(repo, "add", name)
    sh(repo, "commit", "-q", "-m", name)


class SyncTest(unittest.TestCase):
    # The origin + two clones are built ONCE per run and copied per test: ~25 git calls per test became 2 (the step took 852 s on a
    # loaded machine, mostly fixture time). Each copy gets its own origin url; tests still mutate only their copy.
    @classmethod
    def setUpClass(cls):
        cls.tpl = Path(tempfile.mkdtemp())
        origin = cls.tpl / "origin.git"
        sh(cls.tpl, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git < 2.28 has no init -b
        a, b = cls.tpl / "a", cls.tpl / "b"
        for c in (a, b):
            sh(cls.tpl, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
        commit(a, "README.md", "x\n")
        sh(a, "push", "-q", "origin", "HEAD:fast-track")
        sh(b, "pull", "-q", "origin", "fast-track")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tpl, ignore_errors=True)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(self.tpl, self.tmp, dirs_exist_ok=True)
        origin = self.tmp / "origin.git"
        self.a, self.b = self.tmp / "a", self.tmp / "b"
        for c in (self.a, self.b):
            sh(c, "remote", "set-url", "origin", str(origin))
        self.slots_base = self.tmp / "slots_env"
        self.slots_base.mkdir(parents=True, exist_ok=True)
        os.environ["MTS_GATE_SLOTS_DIR"] = str(self.slots_base)
        os.environ["SYNC_ALLOW_SECOND_SHIP"] = "1"   # tests ship repeatedly; TierTest turns the 10-minute rule on
        self.gated = []

    def tearDown(self):
        os.environ.pop("MTS_GATE_SLOTS_DIR", None)
        os.environ.pop("SYNC_ALLOW_SECOND_SHIP", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gate(self, repo):
        self.gated.append(repo)

    def head_files(self, repo):
        sh(repo, "fetch", "-q", "origin")
        r = subprocess.run(["git", "ls-tree", "--name-only", "origin/fast-track"], cwd=repo,
                           capture_output=True, text=True)
        return set(r.stdout.split())

    def test_gate_with_files_param_gets_the_changed_paths_and_docs_get_the_docs_gate(self):
        seen, docs = [], []
        commit(self.a, "NOTE.md", "n\n")
        sync.ship(self.a, gate=self.gate, docs_gate=lambda repo, files: docs.append(files))
        self.assertEqual(docs, [["NOTE.md"]])
        commit(self.a, "d.py", "d\n")
        sync.ship(self.a, gate=lambda repo, files: seen.append(files), docs_gate=lambda r, f: docs.append(f))
        self.assertEqual(seen, [["d.py"]])
        self.assertEqual(len(docs), 1)

    def test_a_docs_only_ship_over_a_doc_size_cap_is_refused(self):
        """2175ef80: a docs ship ran no gate and pushed CLAUDE.md over its cap; the default docs gate now checks the caps."""
        cap = "MyTradingSys/tests/docs/test_integrity.py"
        (self.a / cap).parent.mkdir(parents=True)
        commit(self.a, cap, (Path(__file__).resolve().parents[2] / cap).read_text(encoding="utf-8"))
        sync.ship(self.a, gate=lambda repo, files: None)
        commit(self.a, "CLAUDE.md", "x" * 100_000)
        with self.assertRaisesRegex(sync.SyncError, "doc size cap.*100000 <= "):
            sync.ship(self.a, gate=self.gate)
        self.assertNotIn("CLAUDE.md", self.head_files(self.a))

    def test_run_gate_picks_smoke_and_full_flag_forces_everything(self):
        calls = []
        real = sync.subprocess.run
        def fake(cmd, **k):
            if any(str(c).endswith("run_all_tests.py") for c in cmd):   # only the gate; git calls stay real
                calls.append(cmd)
                return type("R", (), {"returncode": 0})()
            return real(cmd, **k)
        sync.subprocess.run = fake
        old_full = os.environ.pop("SYNC_FULL_GATE", None)
        try:
            sync.run_gate(self.a, ["MyTradingSys/system/X.md"])
            self.assertIn("--smoke", calls[-1])
            os.environ["SYNC_FULL_GATE"] = "1"
            sync.run_gate(self.a, ["MyTradingSys/system/X.md"])
            self.assertNotIn("--smoke", calls[-1])
        finally:
            sync.subprocess.run = real
            if old_full is not None:
                os.environ["SYNC_FULL_GATE"] = old_full
            else:
                os.environ.pop("SYNC_FULL_GATE", None)

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
        rows = sync.open_claims(self.b)
        self.assertEqual([r[0] for r in rows], ["build-thing-one"])
        with self.assertRaises(sync.SyncError):
            sync.claim(self.b, "Build thing one", gate=self.gate)
        sync.release(self.b, "build-thing-one", gate=self.gate)
        sh(self.a, "pull", "-q", "origin", "fast-track")
        self.assertEqual(sync.open_claims(self.a), [])

    def test_claim_and_release_make_no_merge_commit_and_ship_nothing_else(self):
        # Traffic buster 2026-10-16: 246 of 600 daily commits were claim/release, each with a merge commit.
        commit(self.b, "b.py", "b\n")
        sync.ship(self.b, gate=self.gate)       # a is now behind origin
        commit(self.a, "unshipped.py", "u\n")   # and holds work of its own: a claim must not ship it
        gated_before = len(self.gated)
        sync.claim(self.a, "Task x", area="scripts/dev", gate=self.gate)
        sync.release(self.a, "task-x", gate=self.gate)
        merges = subprocess.run(["git", "rev-list", "--merges", "origin/fast-track"], cwd=self.a,
                                capture_output=True, text=True).stdout.split()
        self.assertEqual(merges, [])
        self.assertNotIn("unshipped.py", self.head_files(self.a))
        self.assertEqual(len(self.gated), gated_before)

    def test_ship_release_drops_the_claim_in_the_same_push_as_the_work(self):
        # Traffic buster B4: release rides the last ship, one push less per task.
        sync.claim(self.a, "Task y", area="scripts/dev", gate=self.gate)
        commit(self.a, "y.py", "y"+chr(10))
        pushes = []
        real = sync.git
        def spy(repo, *args, **k):
            if args and args[0] == "push" and "HEAD:refs/heads/fast-track" in args:   # the release on the claims branch is not a trunk push
                pushes.append(args)
            return real(repo, *args, **k)
        sync.git = spy
        try:
            sync.ship(self.a, gate=self.gate, release_slug="task-y")
        finally:
            sync.git = real
        self.assertEqual(len(pushes), 1)
        self.assertIn("y.py", self.head_files(self.a))
        self.assertEqual(sync.open_claims(self.a), [])

    def test_ship_release_with_nothing_to_ship_still_releases(self):
        sync.claim(self.a, "Task z", area="scripts/dev", gate=self.gate)
        sync.ship(self.a, gate=self.gate, release_slug="task-z")
        sh(self.a, "fetch", "-q", "origin")
        self.assertEqual(sync.open_claims(self.a), [])

    def claim_files_on(self, ref):
        sh(self.a, "fetch", "-q", "origin")
        return [s for s, _ in sync.read_claims(self.a, ref)]

    def test_docs_ship_runs_no_gate_at_all(self):
        (self.a / "scripts" / "dev").mkdir(parents=True)
        commit(self.a, "scripts/dev/run_all_tests.py", "pass" + chr(10))     # a repo with a gate script: the old docs gate ran it
        sync.ship(self.a, gate=self.gate)
        commit(self.a, "NOTE.md", "n" + chr(10))
        with mock.patch.object(sync, "run_gate", side_effect=AssertionError("docs ship ran the gate")):
            sync.ship(self.a, gate=self.gate)
        self.assertIn("NOTE.md", self.head_files(self.a))

    def test_claim_and_release_land_on_the_side_branch_not_on_trunk(self):
        sh(self.a, "fetch", "-q", "origin")
        before = sh(self.a, "rev-parse", "origin/fast-track").stdout.strip()
        sync.claim(self.a, "Side one", area="scripts/dev", gate=self.gate)
        sh(self.a, "fetch", "-q", "origin")
        self.assertEqual(sh(self.a, "rev-parse", "origin/fast-track").stdout.strip(), before)   # no claim commit on trunk
        self.assertEqual(self.claim_files_on("origin/claims"), ["side-one"])
        self.assertEqual(self.claim_files_on("origin/fast-track"), [])
        with self.assertRaises(sync.SyncError):                  # the side branch is what a collision check reads
            sync.claim(self.b, "Side one", gate=self.gate)
        sync.release(self.a, "side-one", gate=self.gate)
        self.assertEqual(self.claim_files_on("origin/claims"), [])
        self.assertEqual(sh(self.a, "rev-parse", "origin/fast-track").stdout.strip(), before)

    def test_ship_release_closes_the_side_branch_claim_without_a_trunk_commit(self):
        sync.claim(self.a, "Side two", area="scripts/dev", gate=self.gate)
        commit(self.a, "two.py", "2" + chr(10))
        sync.ship(self.a, gate=self.gate, release_slug="side-two")
        self.assertEqual(self.claim_files_on("origin/claims"), [])
        subjects = sh(self.a, "log", "--format=%s", "origin/fast-track").stdout.split(chr(10))
        self.assertFalse([x for x in subjects if x.startswith(("claim ", "release "))])

    def test_second_ship_from_one_tree_within_ten_minutes_is_refused(self):
        os.environ.pop("SYNC_ALLOW_SECOND_SHIP", None)
        commit(self.a, "one.py", "1" + chr(10))
        sync.ship(self.a, gate=self.gate)
        commit(self.a, "two.py", "2" + chr(10))
        with self.assertRaises(sync.SyncError) as cm:
            sync.ship(self.a, gate=self.gate)
        self.assertIn("10 min", str(cm.exception))
        self.assertNotIn("two.py", self.head_files(self.a))
        with mock.patch.object(sync.time, "time", return_value=time.time() + 700):
            sync.ship(self.a, gate=self.gate)                   # ten minutes later it is allowed
        self.assertIn("two.py", self.head_files(self.a))

    def test_again_flag_and_other_trees_are_not_refused(self):
        os.environ.pop("SYNC_ALLOW_SECOND_SHIP", None)
        commit(self.a, "one.py", "1" + chr(10))
        sync.ship(self.a, gate=self.gate)
        commit(self.b, "b.py", "b" + chr(10))
        sync.ship(self.b, gate=self.gate)                       # another tree: its own clock
        commit(self.a, "three.py", "3" + chr(10))
        os.environ["SYNC_ALLOW_SECOND_SHIP"] = "1"
        sync.ship(self.a, gate=self.gate)
        self.assertIn("three.py", self.head_files(self.a))

    def card(self, cid, scope_in, **kw):
        import json
        d = self.a / sync.CARDS_DIR
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{cid}.json").write_text(json.dumps({"id": cid, "scope_in": scope_in, **kw}), newline="\n")

    def claims_on_origin(self):
        sh(self.a, "fetch", "-q", "origin")
        return [s for s, _ in sync.open_claims(self.a)]

    def test_claim_skips_itself_for_new_files_under_a_dated_folder(self):
        # B16 (B2 automatic): 51 claims + 56 standalone releases in 72 h, many for run-once report tasks.
        self.card("lab-run", ["MyTradingSys/research/study_2026-10-17/", "read-only: scripts/dev/sync.py"])
        self.card("lab-md", ["MyTradingSys/research/audit_2026-10-16/T01.md and MyTradingSys/research/audit_2026-10-16/scripts/T01/ (new files only)"])
        self.card("code-task", ["scripts/dev/sync.py"])
        self.card("mixed", ["MyTradingSys/research/study_2026-10-17/", "scripts/dev/sync.py"])
        self.card("live", ["MyTradingSys/research/study_2026-10-17/"], live_path=True)
        self.card("edits-existing", ["MyTradingSys/research/study_2026-10-17/README.md"])
        (self.a / "MyTradingSys/research/study_2026-10-17").mkdir(parents=True)
        (self.a / "MyTradingSys/research/study_2026-10-17/README.md").write_text("old" + chr(10), newline=chr(10))
        sh(self.a, "add", "-A")
        sh(self.a, "commit", "-q", "-m", "cards")
        sync.ship(self.a, gate=self.gate)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sync.claim(self.b, "lab-run", gate=self.gate)
            sync.claim(self.b, "lab-md", gate=self.gate)
        self.assertIn("no claim needed", out.getvalue())
        self.assertEqual(self.claims_on_origin(), [])
        for name in ("code-task", "mixed", "live", "edits-existing", "no-such-card"):
            sync.claim(self.b, name, gate=self.gate)   # not provably new-files-only (or no card): claims as before
        self.assertEqual(sorted(self.claims_on_origin()), ["code-task", "edits-existing", "live", "mixed", "no-such-card"])

    def test_claim_skip_by_area_and_force_override(self):
        sync.claim(self.b, "Dated report", area="MyTradingSys/research/x_2026-10-17/", gate=self.gate)
        self.assertEqual(self.claims_on_origin(), [])
        sync.claim(self.b, "Dated and code", area="MyTradingSys/research/x_2026-10-17/,scripts/dev", gate=self.gate)
        sync.claim(self.b, "Forced", area="MyTradingSys/research/y_2026-10-17/", gate=self.gate, force=True)
        self.assertEqual(sorted(self.claims_on_origin()), ["dated-and-code", "forced"])

    def test_release_hints_at_ship_release_when_the_tree_has_unshipped_commits(self):
        sync.claim(self.a, "Task h", area="scripts/dev", gate=self.gate)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sync.release(self.a, "task-h", gate=self.gate)
        self.assertNotIn("hint", out.getvalue())     # clean and level with trunk: nothing to say
        sync.claim(self.a, "Task i", area="scripts/dev", gate=self.gate)
        commit(self.a, "i.py", "i" + chr(10))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sync.release(self.a, "task-i", gate=self.gate)
        self.assertIn("ship --release task-i", out.getvalue())
        self.assertEqual(self.claims_on_origin(), [])   # and it still released

    def test_claim_blocks_only_on_overlapping_areas(self):
        sync.claim(self.a, "Task one", area="scripts/dev,MyTradingSys/backtest", gate=self.gate)
        sync.claim(self.a, "Task two", area="MyTradingSys/research", gate=self.gate)  # disjoint: allowed
        sync.claim(self.a, "No area given", gate=self.gate)  # nothing to compare: allowed
        with self.assertRaises(sync.SyncError) as cm:
            sync.claim(self.a, "Task three", area="scripts/dev/sync.py", gate=self.gate)  # nested in task one's area
        self.assertIn("scripts/dev", str(cm.exception))
        sync.claim(self.a, "Task one", area="docs", gate=self.gate)  # same name, disjoint area: both may work
        self.assertEqual(sorted(s for s, _ in sync.open_claims(self.a)),
                         ["no-area-given", "task-one", "task-one-2", "task-two"])
        with self.assertRaises(sync.SyncError):
            sync.claim(self.a, "No area given", gate=self.gate)  # same name, no areas: still the same task

    def make_lane(self, name="mts-app"):
        lane = self.make_tree(self.tmp.resolve() / name, f"{sync.socket.gethostname()}/old-task")
        sh(lane, "config", "user.email", "t@t")
        sh(lane, "config", "user.name", "t")
        return lane

    def branch_of(self, tree):
        return subprocess.run(["git", "-C", str(tree), "branch", "--show-current"], capture_output=True, text=True).stdout.strip()

    def test_start_slug_in_a_lane_tree_switches_branch_instead_of_making_a_worktree(self):
        lane = self.make_lane()
        commit(self.a, "later.txt", "l\n")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            path = sync.start(lane, slug="New Task")
        self.assertEqual(Path(path), lane)
        self.assertNotIn("WORKTREE:", buf.getvalue())
        self.assertEqual(self.branch_of(lane), f"{sync.socket.gethostname()}/new-task")
        self.assertTrue((lane / "later.txt").exists())  # off the fresh origin/fast-track
        branches = subprocess.run(["git", "-C", str(lane), "branch", "--list"], capture_output=True, text=True).stdout
        self.assertNotIn("old-task", branches)  # the finished task's branch is not left behind
        self.assertEqual(len(sync.worktrees(self.a)), 2)  # primary + the lane: no new tree

    def test_start_slug_in_a_lane_tree_refuses_dirty_or_ahead_and_changes_nothing(self):
        lane = self.make_lane()
        (lane / "README.md").write_text("half done\n", newline="\n")
        with self.assertRaises(sync.SyncError) as cm:
            sync.start(lane, slug="next")
        self.assertIn("sync.py where", str(cm.exception))
        self.assertEqual(self.branch_of(lane), f"{sync.socket.gethostname()}/old-task")
        sh(lane, "checkout", "-q", "--", "README.md")
        commit(lane, "unshipped.py", "u\n")
        with self.assertRaises(sync.SyncError):
            sync.start(lane, slug="next")
        self.assertEqual(self.branch_of(lane), f"{sync.socket.gethostname()}/old-task")
        self.assertTrue((lane / "unshipped.py").exists())

    def test_start_slug_in_a_lane_tree_never_in_the_live_tree(self):
        lane = self.make_lane()
        (lane / sync.LIVE_MARKER).write_text("", newline="\n")
        with self.assertRaises(sync.SyncError):
            sync.start(lane, slug="next")
        self.assertEqual(self.branch_of(lane), f"{sync.socket.gethostname()}/old-task")

    def test_start_slug_in_a_non_lane_clean_tree_still_stays_put(self):
        with contextlib.redirect_stdout(io.StringIO()):
            path = sync.start(self.a, slug="anything")
        self.assertEqual(Path(path), self.a)
        self.assertNotEqual(self.branch_of(self.a), f"{sync.socket.gethostname()}/anything")

    def test_tidy_all_keeps_every_named_lane_tree(self):
        lanes = [self.make_tree(self.tmp.resolve() / n, f"jisnb/{n}") for n in ("mts-app", "mts-relay", "mts-dsa")]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, include_named=True, now=time.time() + 48 * 3600), [])
        self.assertTrue(all(l.exists() for l in lanes))

    def test_claim_rejects_flag_like_name(self):
        with self.assertRaises(sync.SyncError):
            sync.claim(self.a, "--help", gate=self.gate)
        self.assertEqual(sync.open_claims(self.a), [])

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


    def test_start_names_prior_work_on_the_trunk_for_the_slug(self):
        # 2026-10-16: the same prompt ran twice; the second session saw the first one's folder only at ship time.
        d = self.a / "MyTradingSys" / "research" / "context_factors_2026-10-16"
        d.mkdir(parents=True)
        commit(self.a, "MyTradingSys/research/context_factors_2026-10-16/REPORT.md", "r\n")
        sync.ship(self.a, gate=self.gate)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.start(self.b, slug="context-factors", quiet=False)
        self.assertIn("prior work on fast-track matching 'context-factors'", buf.getvalue())
        self.assertIn("MyTradingSys/research/context_factors_2026-10-16", buf.getvalue())
        self.assertEqual(sync.prior_work(self.b, "context-null"), [])      # every slug word must match
        self.assertEqual(sync.prior_work(self.b, "factors"), ["MyTradingSys/research/context_factors_2026-10-16"])
        self.assertEqual(sync.prior_work(self.b, "fix"), [])               # stop words alone never match

    def test_start_quiet_suppresses_claims_table_and_mirror(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.start(self.b, quiet=True)
        out = buf.getvalue()
        self.assertNotIn("claims:", out)
        self.assertNotIn("live mirror:", out)
        self.assertIn("host=", out)
        self.assertLess(len(out.encode("utf-8")), 200)

    def test_start_quiet_cli_flag_is_accepted(self):
        cwd = os.getcwd()
        os.chdir(self.b)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = sync.main(["start", "--quiet"])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertNotIn("claims:", out)
            self.assertNotIn("live mirror:", out)
            self.assertLess(len(out.encode("utf-8")), 200)
        finally:
            os.chdir(cwd)


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

    def test_discard_saves_uncommitted_work_removes_tree_keeps_branch(self):
        # operator 2026-10-23: the App's discard action asked him 4-5 times; `sync.py discard` does it from Bash, no card
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "kept")
        br = subprocess.run(["git", "-C", str(wt), "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
        (wt / "README.md").write_text("edited\n", newline="\n")
        (wt / "new.txt").write_text("untracked\n", newline="\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(sync.discard(self.a, [wt.name, str(self.a), "nope"]),
                             [str(wt.resolve())])
        self.assertFalse(wt.exists())
        self.assertTrue(self.a.exists())                                  # the primary tree is never discarded
        self.assertIn("skip  nope", out.getvalue())
        rescue = self.a.resolve() / "Dumps" / "wt_rescue" / wt.name
        self.assertIn("+edited", (rescue / "changes.patch").read_text())
        self.assertEqual((rescue / "files" / "new.txt").read_text(), "untracked\n")
        self.assertEqual(subprocess.run(["git", "-C", str(self.a), "rev-parse", "--verify", "-q", br]).returncode, 0)  # branch kept

    def test_tidy_apply_repairs_a_case_broken_head(self):
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "casey")
        branch = subprocess.run(["git", "-C", str(wt), "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
        sh(self.a, "pack-refs", "--all")                           # packed refs are matched case-sensitively even on Windows
        wrong = branch.upper()
        sh(wt, "symbolic-ref", "HEAD", f"refs/heads/{wrong}")      # what a case-insensitive FS left behind
        broken = [t for t in sync.survey(self.a) if t["path"] == str(wt) or Path(t["path"]) == wt]
        if not broken or broken[0]["ahead"] is not None:
            self.skipTest("this filesystem still resolves the wrong-case ref")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.repair_heads(self.a, apply=False), [broken[0]["path"]])   # dry run moves nothing
            sync.tidy(self.a, apply=True)
        head = subprocess.run(["git", "-C", str(wt), "symbolic-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(head, f"refs/heads/{branch}")
        self.assertEqual(subprocess.run(["git", "-C", str(wt), "rev-parse", "--verify", "-q", "HEAD"]).returncode, 0)

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
        # claim() now refuses an overlapping area, so plant the colliding claim as a file (an old or racing one)
        two = self.a / sync.CLAIMS_DIR / "task-two.md"
        two.parent.mkdir(parents=True, exist_ok=True)   # a legacy claim still on the trunk is read beside the side branch
        two.write_text("task: Task two\nhost: h\naccount: t\narea: scripts/dev/sync.py\nepoch: %d\n" % time.time(), newline="\n")
        sh(self.a, "add", sync.CLAIMS_DIR)
        sh(self.a, "commit", "-q", "-m", "claim task-two")
        sync.ship(self.a, gate=self.gate)
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

    def test_new_worktree_branch_uses_the_exact_case_of_the_host_prefix(self):
        """On a case-insensitive FS `-b jis-nb/x` beside an existing JIS-NB/ ref dir left HEAD naming a ref that never resolved."""
        sh(self.a, "branch", "JIS-NB/old", "origin/fast-track")
        with mock.patch.object(sync.socket, "gethostname", return_value="jis-nb"):
            wt = sync.new_worktree(self.a, "casetest")
        head = subprocess.run(["git", "symbolic-ref", "HEAD"], cwd=wt, capture_output=True, text=True).stdout.strip()
        self.assertEqual(head, "refs/heads/JIS-NB/casetest")
        self.assertEqual(subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=wt, capture_output=True).returncode, 0)
        with mock.patch.object(sync.socket, "gethostname", return_value="Fresh-Host"):
            wt2 = sync.new_worktree(self.a, "other")
        self.assertEqual(subprocess.run(["git", "symbolic-ref", "HEAD"], cwd=wt2, capture_output=True, text=True).stdout.strip(),
                         "refs/heads/Fresh-Host/other")

    def test_gate_test_lists_are_one_entry_per_line(self):
        """Every new test appends to these lists; two entries on one line is a guaranteed merge conflict."""
        import re
        src = (Path(__file__).resolve().parent / "run_all_tests.py").read_text(encoding="utf-8")
        bad = [l.strip() for l in src.splitlines()
               if len(re.findall(r'"[\w/.-]+\.py"', l)) >= 2 and "sys.executable" not in l]
        self.assertEqual(bad, [])

    def test_ship_after_predecessor_shipped_proceeds(self):
        # When predecessor has shipped (claim removed or status done/released), wait_after returns 'shipped'
        (self.b / "MyTradingSys/system/claims").mkdir(parents=True, exist_ok=True)
        commit(self.b, f"MyTradingSys/system/claims/pred-task.md", "claimed\n")
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        now = [1000.0]
        # Simulate predecessor shipping
        commit(self.b, "pred-done.txt", "done\n")
        sh(self.b, "rm", "-q", "MyTradingSys/system/claims/pred-task.md")
        sh(self.b, "commit", "-q", "-m", "release pred-task")
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        res = sync.wait_after(self.a, "pred-task", timeout=3600, poll=1.0, sleep=lambda s: None, now_fn=lambda: now[0])
        self.assertEqual(res, "shipped")

    def test_ship_after_predecessor_failed_proceeds(self):
        # When predecessor card is marked failed, wait_after returns 'failed'
        import json
        card = {"id": "pred-fail", "status": "failed"}
        (self.b / "MyTradingSys/system/tasks").mkdir(parents=True, exist_ok=True)
        (self.b / "MyTradingSys/system/claims").mkdir(parents=True, exist_ok=True)
        commit(self.b, "MyTradingSys/system/claims/pred-fail.md", "claimed\n")
        commit(self.b, "MyTradingSys/system/tasks/pred-fail.json", json.dumps(card))
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        res = sync.wait_after(self.a, "pred-fail", timeout=3600, poll=1.0, sleep=lambda s: None, now_fn=lambda: 1000.0)
        self.assertEqual(res, "failed")

    def test_ship_after_timeout_lapses_proceeds(self):
        # When timeout (60 min default) is reached without signal, ticket lapses
        (self.b / "MyTradingSys/system/claims").mkdir(parents=True, exist_ok=True)
        commit(self.b, "MyTradingSys/system/claims/pred-slow.md", "claimed\n")
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        now = [1000.0]
        def advance_sleep(s):
            now[0] += 3601.0
        res = sync.wait_after(self.a, "pred-slow", timeout=3600, poll=1.0, sleep=advance_sleep, now_fn=lambda: now[0])
        self.assertEqual(res, "lapsed")

    def test_ship_after_waiting_holds_no_gate_slot(self):
        # While waiting for predecessor, no gate slot is acquired
        (self.b / "MyTradingSys/system/claims").mkdir(parents=True, exist_ok=True)
        commit(self.b, "MyTradingSys/system/claims/pred-hold.md", "claimed\n")
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        slot_dir = sync.gate_slot(self.a)._dir()
        now = [1000.0]
        def check_no_slot(s):
            self.assertFalse(slot_dir.exists() and any(slot_dir.iterdir()))
            now[0] += 3601.0
        sync.wait_after(self.a, "pred-hold", timeout=3600, poll=1.0, sleep=check_no_slot, now_fn=lambda: now[0])

    def test_ship_cli_after_flag_calls_ship(self):
        with mock.patch.object(sync, "toplevel", return_value=self.a), \
                mock.patch.object(sync, "ship") as mock_ship:
            self.assertEqual(sync.main(["ship", "--after", "pred-slug"]), 0)
            mock_ship.assert_called_once_with(self.a, release_slug=None, after_slug="pred-slug")

    def test_ship_cli_after_and_release_flags(self):
        with mock.patch.object(sync, "toplevel", return_value=self.a), \
                mock.patch.object(sync, "ship") as mock_ship:
            self.assertEqual(sync.main(["ship", "--release", "my-slug", "--after", "pred-slug"]), 0)
            mock_ship.assert_called_once_with(self.a, release_slug="my-slug", after_slug="pred-slug")



class GateSlotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        sh(self.tmp, "init", "-q")
        self.slots_base = self.tmp / "slots_env"
        self.slots_base.mkdir(parents=True, exist_ok=True)
        os.environ["MTS_GATE_SLOTS_DIR"] = str(self.slots_base)
        self.slots = self.slots_base / "gate-slots"

    def tearDown(self):
        os.environ.pop("MTS_GATE_SLOTS_DIR", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_third_acquirer_waits_while_two_slots_held(self):
        class Stop(Exception):
            pass

        def stop(_):
            raise Stop
        out = io.StringIO()
        with sync.gate_slot(self.tmp, alive=lambda p: True), sync.gate_slot(self.tmp, alive=lambda p: True):
            with contextlib.redirect_stdout(out), self.assertRaises(Stop):
                with sync.gate_slot(self.tmp, alive=lambda p: True, sleep=stop, note_every=0):
                    self.fail("third gate must not get a slot")
            self.assertIn("gate slot busy (2/2), waiting", out.getvalue())
            self.assertEqual(len(list(self.slots.iterdir())), 2)

    def test_stale_pid_slot_is_reclaimed(self):
        self.slots.mkdir()
        for i in (0, 1):
            (self.slots / f"slot-{i}").write_text("999999")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with sync.gate_slot(self.tmp, alive=lambda p: p != 999999) as g:
                self.assertEqual((self.slots / g.path.name).read_text(), str(os.getpid()))
        self.assertIn("999999 is dead", out.getvalue())

    def test_slot_released_after_gate_raises(self):
        real = subprocess.run

        def fake(cmd, *a, **k):
            if "run_all_tests.py" in " ".join(map(str, cmd)):
                raise RuntimeError("boom")
            return real(cmd, *a, **k)
        with mock.patch.object(sync.subprocess, "run", side_effect=fake):
            with self.assertRaises(RuntimeError):
                sync.run_gate(self.tmp)
        self.assertEqual(list(self.slots.iterdir()) if self.slots.exists() else [], [])

    def test_run_gate_leaves_the_slot_to_the_main_phase_of_run_all_tests(self):
        # GATE_SPEED D2: sync.py no longer holds a slot through the precheck; run_all_tests --slot takes it for the main phase
        seen = []
        real = subprocess.run

        def fake(cmd, *a, **k):
            if "run_all_tests.py" in " ".join(map(str, cmd)):
                seen.append((list(cmd), self.slots.exists() and list(self.slots.iterdir())))
                return type("R", (), {"returncode": 0})()
            return real(cmd, *a, **k)
        old_full = os.environ.pop("SYNC_FULL_GATE", None)
        try:
            with mock.patch.object(sync.subprocess, "run", side_effect=fake):
                sync.run_gate(self.tmp, ["scripts/dev/x.py"])
        finally:
            if old_full is not None:
                os.environ["SYNC_FULL_GATE"] = old_full
            else:
                os.environ.pop("SYNC_FULL_GATE", None)
        cmd, held = seen[0]
        self.assertFalse(held)
        for flag in ("--precheck", "--fail-fast", "--slot", "--record", "--smoke", "--changed-file"):
            self.assertIn(flag, cmd)


class ShipRaceTest(unittest.TestCase):
    """GATE_SPEED D4: fetch retries, jittered push retries, re-gate only when the incoming commits touch what we ship."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        self.a, self.b = self.tmp / "a", self.tmp / "b"
        for c in (self.a, self.b):
            sh(self.tmp, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
        commit(self.a, "README.md", "x\n")
        commit(self.a, "lib.py", "X = 1\n")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.b, "pull", "-q", "origin", "fast-track")
        self.sleeps = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def racing_gate(self, other_file, other_text):
        """A gate on `a` during which `b` ships first, once: a's first push is then rejected."""
        calls = []

        def gate(repo, files):
            calls.append(list(files))
            if len(calls) == 1:
                commit(self.b, other_file, other_text)
                sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        return gate, calls

    def test_lost_race_on_unrelated_files_pushes_again_without_a_regate(self):
        commit(self.a, "mine.py", "import lib\n")
        gate, calls = self.racing_gate("other.py", "y\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            sync.ship(self.a, gate=gate, sleep=self.sleeps.append)
        self.assertEqual(len(calls), 1)
        self.assertIn("retry 1/", out.getvalue())
        self.assertEqual(len(self.sleeps), 1)
        self.assertTrue(1.0 <= self.sleeps[0] <= 5.0)

    def test_lost_race_on_a_module_we_import_regates_once(self):
        commit(self.a, "mine.py", "import lib\n")
        gate, calls = self.racing_gate("lib.py", "X = 2\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            sync.ship(self.a, gate=gate, sleep=self.sleeps.append)
        self.assertEqual(len(calls), 2)
        self.assertIn("re-running the gate", out.getvalue())

    def test_race_overlap_same_path_reference_and_unrelated(self):
        commit(self.a, "mine.py", "import lib\n")
        self.assertEqual(sync.race_overlap(self.a, ["mine.py"], ["mine.py"]), ["mine.py"])
        self.assertEqual(sync.race_overlap(self.a, ["lib.py", "other.py", "NOTE.md"], ["mine.py"]), ["lib.py"])
        self.assertEqual(sync.race_overlap(self.a, ["other.py"], ["mine.py"]), [])

    def test_fetch_retries_then_raises(self):
        fails = []
        real = sync.git

        def flaky(repo, *args, check=True):
            if args[:1] == ("fetch",) and len(fails) < 2:
                fails.append(1)
                return type("R", (), {"returncode": 1, "stdout": "", "stderr": "cannot lock ref"})()
            return real(repo, *args, check=check)
        with mock.patch.object(sync, "git", side_effect=flaky):
            sync.fetch_trunk(self.a, sleep=self.sleeps.append)
        self.assertEqual((len(fails), len(self.sleeps)), (2, 2))
        with mock.patch.object(sync, "git", return_value=type("R", (), {"returncode": 1, "stdout": "", "stderr": "x"})()):
            with self.assertRaises(sync.SyncError):
                sync.fetch_trunk(self.a, sleep=lambda s: None)

    def test_changed_between_lists_both_sides_of_a_rename_and_spaced_paths(self):
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.a, capture_output=True, text=True).stdout.strip()
        sh(self.a, "mv", "lib.py", "new lib.py")
        sh(self.a, "commit", "-q", "-m", "mv")
        self.assertEqual(sorted(sync.changed_between(self.a, base, "HEAD")), ["lib.py", "new lib.py"])

    def test_pid_alive_self_and_dead(self):
        self.assertTrue(sync.pid_alive(os.getpid()))
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()
        self.assertFalse(sync.pid_alive(p.pid))


class FastShipTest(unittest.TestCase):
    """GATE_SPEED.md X3/X6: red-CI block, --fix-ci, the fast gate flag, slot pool names, the reverse race check."""
    RED = [{"conclusion": "failure", "head_sha": "a" * 40, "created_at": "2026-10-18T10:00:00Z"},
           {"conclusion": "failure", "head_sha": "b" * 40, "created_at": "2026-10-18T09:00:00Z"},
           {"conclusion": "success", "head_sha": "c" * 40, "created_at": "2026-10-18T08:00:00Z"}]
    GREEN = [{"conclusion": "success", "head_sha": "a" * 40, "created_at": "2026-10-18T10:00:00Z"}] + RED[1:]

    def test_two_failed_runs_in_a_row_are_red_and_one_is_not(self):
        self.assertEqual(sync.ci_state(lambda use_cache: self.RED)[0], "red")
        self.assertEqual(sync.ci_state(lambda use_cache: self.RED[1:])[0], "green")
        self.assertEqual(sync.ci_state(lambda use_cache: self.GREEN)[0], "green")

    def test_a_cached_red_is_refetched_and_the_fresh_answer_counts(self):
        calls = []

        def fetch(use_cache):
            calls.append(use_cache)
            return self.RED if use_cache else self.GREEN
        self.assertEqual(sync.ci_state(fetch)[0], "green")
        self.assertEqual(calls, [True, False])

    def test_offline_or_a_crash_is_unknown_never_red(self):
        self.assertEqual(sync.ci_state(lambda use_cache: None)[0], "unknown")

        def boom(use_cache):
            raise OSError("offline")
        self.assertEqual(sync.ci_state(boom)[0], "unknown")

    def test_red_blocks_a_code_ship_until_fix_ci(self):
        check = sync.CiCheck(lambda use_cache: self.RED)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SYNC_FIX_CI", None)
            with self.assertRaises(sync.SyncError) as cm:
                sync.enforce_ci(check)
            self.assertIn("--fix-ci", str(cm.exception))
            os.environ["SYNC_FIX_CI"] = "1"
            with contextlib.redirect_stdout(io.StringIO()) as out:
                sync.enforce_ci(check)
            self.assertIn("FULL gate", out.getvalue())

    def test_green_or_no_check_ships(self):
        with contextlib.redirect_stdout(io.StringIO()):
            sync.enforce_ci(sync.CiCheck(lambda use_cache: self.GREEN))
            sync.enforce_ci(None)

    def test_docs_only_ships_are_not_subject_to_the_block(self):
        self.assertFalse(sync.ci_applies(["MyTradingSys/system/GATE_SPEED.md", "MyTradingSys/research/x/out.tsv"]))
        self.assertTrue(sync.ci_applies(["scripts/dev/example_tool.py"]))
        self.assertTrue(sync.ci_applies(["MyTradingSys/runtime/run_list.txt"]))    # a live-path .txt is code to the gate

    def run_gate_cmd(self, files, env):
        seen = []
        with mock.patch.object(sync.subprocess, "run", side_effect=lambda cmd, **k: seen.append(cmd) or mock.Mock(returncode=0)), \
                mock.patch.dict(os.environ, env, clear=False):
            for k in ("SYNC_FULL_GATE", "SYNC_NO_FAST"):
                if k not in env:
                    os.environ.pop(k, None)
            sync.run_gate(Path("."), files)
        return seen[0]

    def test_run_gate_asks_for_the_fast_gate_unless_full_or_disabled(self):
        self.assertIn("--fast", self.run_gate_cmd(["scripts/dev/example_tool.py"], {}))
        self.assertNotIn("--fast", self.run_gate_cmd(["scripts/dev/example_tool.py"], {"SYNC_FULL_GATE": "1"}))
        self.assertNotIn("--fast", self.run_gate_cmd(["scripts/dev/example_tool.py"], {"SYNC_NO_FAST": "1"}))

    def test_fix_ci_flag_sets_the_full_gate(self):
        with mock.patch.object(sync, "ship"), mock.patch.object(sync, "toplevel", return_value=Path(".")), \
                mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SYNC_FULL_GATE", None)
            os.environ.pop("SYNC_FIX_CI", None)
            self.assertEqual(sync.main(["ship", "--fix-ci"]), 0)
            self.assertEqual((os.environ.get("SYNC_FIX_CI"), os.environ.get("SYNC_FULL_GATE")), ("1", "1"))
            os.environ.pop("SYNC_FULL_GATE", None)
            os.environ.pop("SYNC_FIX_CI", None)

    def test_fast_slots_use_their_own_folder_and_an_empty_slot_file_is_busy(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        sh(tmp, "init", "-q")
        slots_base = tmp / "slots_base"
        os.environ["MTS_GATE_SLOTS_DIR"] = str(slots_base)
        self.addCleanup(lambda: os.environ.pop("MTS_GATE_SLOTS_DIR", None))
        fast_d = sync.host_gate_slots_dir("gate-slots-fast")
        main_d = sync.host_gate_slots_dir("gate-slots")
        with sync.gate_slot(tmp, slots=1, name="gate-slots-fast", alive=lambda p: True):
            self.assertTrue((fast_d / "slot-0").is_file())
        main_d.mkdir(parents=True, exist_ok=True)
        (main_d / "slot-0").write_text("")           # creator is mid-write: another gate must not take it over
        (main_d / "slot-1").write_text("")
        with self.assertRaises(sync.GateSlotTimeout):
            with sync.gate_slot(tmp, alive=lambda p: False, timeout=0.2, poll=0.05, note_every=99):
                pass

    def test_race_overlap_also_catches_an_incoming_module_that_imports_ours(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        sh(tmp, "init", "-q")
        (tmp / "mine.py").write_text("X = 1\n")
        (tmp / "theirs.py").write_text("import mine\n")
        (tmp / "unrelated.py").write_text("Y = 1\n")
        self.assertEqual(sync.race_overlap(tmp, ["theirs.py", "unrelated.py"], ["mine.py"]), ["theirs.py"])

if __name__ == "__main__":
    unittest.main()

