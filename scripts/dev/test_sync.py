"""sync.py: two clones of one origin ship to fast-track without losing each other's work."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
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
        # The template must be quiescent while copytree snapshots it. A pull/push
        # can otherwise leave background maintenance removing files during a copy.
        sh(origin, "config", "gc.auto", "0")
        sh(origin, "config", "maintenance.auto", "false")
        a, b = cls.tpl / "a", cls.tpl / "b"
        for c in (a, b):
            sh(cls.tpl, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
            sh(c, "config", "gc.auto", "0")
            sh(c, "config", "maintenance.auto", "false")
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

    def test_fixture_repositories_disable_background_git_maintenance(self):
        for repo in (self.tmp / "origin.git", self.a, self.b):
            with self.subTest(repo=repo.name):
                self.assertEqual(sh(repo, "config", "--local", "gc.auto").stdout.strip(), "0")
                self.assertEqual(sh(repo, "config", "--local", "maintenance.auto").stdout.strip(), "false")

    def test_gate_with_files_param_gets_the_changed_paths_and_docs_get_the_docs_gate(self):
        seen, docs = [], []
        commit(self.a, "NOTE.md", "n\n")
        sync.ship(self.a, gate=self.gate, docs_gate=lambda repo, files: docs.append(files))
        self.assertEqual(docs, [["NOTE.md"]])
        commit(self.a, "d.py", "d\n")
        sync.ship(self.a, gate=lambda repo, files: seen.append(files), docs_gate=lambda r, f: docs.append(f))
        self.assertEqual(seen, [["d.py"]])
        self.assertEqual(len(docs), 1)

    def test_ship_returns_the_pushed_sha_and_files_so_the_shell_can_wait_for_that_sha_s_ci(self):
        commit(self.a, "p.py", "p\n")
        pushed = sync.ship(self.a, gate=self.gate)
        sh(self.a, "fetch", "-q", "origin")
        self.assertEqual(pushed.sha, sh(self.a, "rev-parse", "origin/fast-track").stdout.strip())
        self.assertEqual(pushed.files, ["p.py"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(sync.ship(self.a, gate=self.gate))     # nothing left to ship: no sha, no wait

    def test_role_md_plus_card_json_is_a_docs_ship_not_a_code_ship(self):
        """5f12bc06c: a role .md plus card .json took the code path, which gate_select maps to zero steps, so the role byte budget never ran."""
        seen, docs = [], []
        for d in ("roles", "tasks"):
            (self.a / "MyTradingSys/system" / d).mkdir(parents=True)
        commit(self.a, "MyTradingSys/system/roles/x.md", "r" + chr(10))
        commit(self.a, "MyTradingSys/system/tasks/x.json", "{}" + chr(10))
        sync.ship(self.a, gate=lambda repo, files: seen.append(files), docs_gate=lambda r, f: docs.append(f))
        self.assertEqual(seen, [])
        self.assertEqual(len(docs), 1)
        self.assertEqual(sorted(docs[0]), ["MyTradingSys/system/roles/x.md", "MyTradingSys/system/tasks/x.json"])

    def test_wiring_registry_alone_still_runs_the_code_gate(self):
        seen, docs = [], []
        reg = "MyTradingSys/system/wiring_registry.json"
        (self.a / reg).parent.mkdir(parents=True, exist_ok=True)
        commit(self.a, reg, "{}" + chr(10))
        sync.ship(self.a, gate=lambda repo, files: seen.append(files), docs_gate=lambda r, f: docs.append(f))
        self.assertEqual(seen, [[reg]])
        self.assertEqual(docs, [])

    def test_a_docs_only_ship_over_a_doc_size_cap_is_refused(self):
        """2175ef80: a docs ship ran no gate and pushed CLAUDE.md over its cap; the default docs gate now checks the caps."""
        import preship   # the cap test plus the helpers beside it (42d8b197a: a new doc_drift.py import broke a one-file copy)
        preship.copy_cap_test(Path(__file__).resolve().parents[2], self.a)
        sh(self.a, "add", "-A")
        sh(self.a, "commit", "-q", "-m", "cap test")
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

    def test_ship_release_drops_the_gateway_hold_of_its_own_tree_only(self):
        # 2026-11-01 JIS-NB: 51 shipped trees kept 8.4 GB of C: for 12 h each because .gateway_owner outlived the task
        sh(self.a, "checkout", "-q", "-b", f"{sync.socket.gethostname()}/task-g-2")
        hold = self.a / sync.GATEWAY_MARKER
        hold.write_text("x", newline=chr(10))
        sync.claim(self.a, "Task other", area="scripts/dev", gate=self.gate)
        sync.release(self.a, "task-other", gate=self.gate)
        self.assertTrue(hold.exists())          # another slug's release: the tree is still this session's
        sync.claim(self.a, "Task g", area="scripts/dev", gate=self.gate)
        commit(self.a, "g.py", "g" + chr(10))
        sync.ship(self.a, gate=self.gate, release_slug="task-g")
        self.assertFalse(hold.exists())
        self.assertIn("g.py", self.head_files(self.a))

    def race_claim(self, task_b, area_a="-", area_b="-"):
        """coordination audit 2026-10-26 finding 1: clone b's claim lands between a's open-claims check and a's push. Returns
        (a's SyncError text or None, number of 'claimed' lines printed, final open claims {slug: account})."""
        real = sync.git
        fired = []

        def racing(repo, *args, **kw):
            if Path(repo) == self.a and args[:1] == ("push",) and args[-1].endswith(":refs/heads/claims") and not fired:
                fired.append(1)
                with mock.patch.dict(os.environ, {"MTS_ACCOUNT": "worker-b"}):
                    sync.claim(self.b, task_b, area=area_b, gate=self.gate, force=True)
            return real(repo, *args, **kw)
        out, err = io.StringIO(), None
        with contextlib.redirect_stdout(out), mock.patch.object(sync, "git", racing), \
                mock.patch.dict(os.environ, {"MTS_ACCOUNT": "worker-a"}):
            try:
                sync.claim(self.a, "Same task", area=area_a, gate=self.gate, force=True)
            except sync.SyncError as e:
                err = str(e)
        self.assertEqual(fired, [1])
        rows = {s: kv.get("account") for s, kv in sync.open_claims(self.a)}
        return err, out.getvalue().count("claimed "), rows

    def test_racing_claim_on_the_same_task_does_not_overwrite_the_winner(self):
        err, claimed, rows = self.race_claim("Same task")
        self.assertIsNotNone(err, "the loser must be refused, not told 'claimed'")
        self.assertIn("already claimed", err)
        self.assertEqual(claimed, 1)                       # only b's success line
        self.assertEqual(rows, {"same-task": "worker-b"})  # b keeps the lock it was told it holds

    def test_racing_claim_with_an_overlapping_area_is_refused(self):
        err, claimed, rows = self.race_claim("Other task", area_a="scripts/dev/x.py", area_b="scripts/dev")
        self.assertIsNotNone(err)
        self.assertIn("already claimed", err)
        self.assertEqual(rows, {"other-task": "worker-b"})

    def test_racing_claim_with_disjoint_areas_both_land(self):
        err, claimed, rows = self.race_claim("Same task", area_a="docs/a.md", area_b="scripts/dev")
        self.assertIsNone(err)
        self.assertEqual(claimed, 2)
        self.assertEqual(sorted(rows.values()), ["worker-a", "worker-b"])   # same name, disjoint areas: suffixed slug, no overwrite

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

    def test_second_ship_from_one_tree_within_ten_minutes_is_only_a_note(self):
        import contextlib, io
        os.environ.pop("SYNC_ALLOW_SECOND_SHIP", None)
        commit(self.a, "one.py", "1" + chr(10))
        sync.ship(self.a, gate=self.gate)
        commit(self.a, "two.py", "2" + chr(10))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.ship(self.a, gate=self.gate)                   # operator 2026-10-25: no refusal, one note line
        self.assertIn("two.py", self.head_files(self.a))
        self.assertIn("second ship from this tree", buf.getvalue())

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
            sync.claim(self.b, "Lab Run", gate=self.gate)   # free text that slugifies to the card: B2 still applies
            sync.claim(self.b, "Lab Md", gate=self.gate)
        self.assertIn("no claim needed", out.getvalue())
        self.assertEqual(self.claims_on_origin(), [])
        for name in ("code-task", "mixed", "live", "edits-existing", "no-such-card"):
            sync.claim(self.b, name, gate=self.gate)   # not provably new-files-only (or no card): claims as before
        self.assertEqual(sorted(self.claims_on_origin()), ["code-task", "edits-existing", "live", "mixed", "no-such-card"])

    def test_card_id_task_with_only_new_files_is_claimed_and_second_taker_refused(self):
        # claim-lease-expiry-and-b2-hole: B2 skipped the claim for new-file cards, so two workers could take one card
        self.card("lab-run", ["MyTradingSys/research/study_2026-10-17/", "read-only: scripts/dev/sync.py"])
        sh(self.a, "add", "-A")
        sh(self.a, "commit", "-q", "-m", "cards")
        sync.ship(self.a, gate=self.gate)
        sync.claim(self.b, "lab-run", gate=self.gate)
        self.assertEqual(self.claims_on_origin(), ["lab-run"])
        with self.assertRaises(sync.SyncError):
            sync.claim(self.a, "lab-run", gate=self.gate)

    def test_expired_lease_is_free_and_a_live_or_legacy_claim_still_blocks(self):
        real = time.time()
        with mock.patch.object(sync.time, "time", return_value=real - 4 * 3600):   # holder claims 4 h ago, then crashes
            sync.claim(self.a, "Crashed task", area="scripts/dev", gate=self.gate)
        self.assertEqual(self.claims_on_origin(), [])          # expired = not open
        sync.claim(self.b, "Crashed task", area="scripts/dev", gate=self.gate)   # second claimer wins, same slug
        self.assertEqual(self.claims_on_origin(), ["crashed-task"])
        with self.assertRaises(sync.SyncError):
            sync.claim(self.a, "Crashed task", area="scripts/dev", gate=self.gate)   # a live lease blocks
        self.assertFalse(sync.claim_expired({"task": "old claim without a lease", "epoch": "1"}, real))   # backward compatible
        self.assertFalse(sync.claim_expired({"expires_at": "garbage"}, real))   # fail closed: unreadable = held

    def test_heartbeat_refreshes_the_lease_and_refuses_a_missing_claim(self):
        real = time.time()
        with mock.patch.object(sync.time, "time", return_value=real - 4 * 3600):
            sync.claim(self.a, "Long job", gate=self.gate)
        sync.heartbeat(self.a, "long-job")
        kv = dict(sync.open_claims(self.a))["long-job"]
        self.assertGreater(int(kv["expires_at"]), real)
        with self.assertRaises(sync.SyncError):
            sync.heartbeat(self.a, "no-such-claim")

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

    def test_doctor_top_warnings_keeps_three_warn_rows_in_order(self):
        rows = [("A", "OK", "x"), ("B", "WARN", "b1"), ("C", "unavailable", "c"), ("D", "WARN", "d1"), ("E", "WARN", "e1"), ("F", "WARN", "f1")]
        out = sync.doctor_top_warnings(self.a, checklist=lambda: rows)
        self.assertEqual(len(out), 3)
        self.assertTrue(out[0].startswith("doctor WARN B:") and out[2].startswith("doctor WARN E:"))

    def test_doctor_top_warnings_fails_soft_when_the_doctor_errors(self):
        def boom():
            raise RuntimeError("doctor down")
        self.assertEqual(sync.doctor_top_warnings(self.a, checklist=boom), [])
        self.assertEqual(sync.doctor_top_warnings(self.a), [])  # throwaway repo has no doctor: nothing, no raise

    def test_start_prints_doctor_warnings_but_not_when_quiet(self):
        with mock.patch.object(sync, "doctor_top_warnings", return_value=["doctor WARN DISK: low"]):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sync.start(self.a, here=True)
            self.assertIn("doctor WARN DISK: low", buf.getvalue())
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sync.start(self.a, here=True, quiet=True)
            self.assertNotIn("doctor WARN", buf.getvalue())

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

    def test_start_worker_in_a_lane_tree_makes_a_worktree_and_leaves_the_lane(self):
        """B3: a worker Agent booted in the Supervisor's lane tree switched it and committed there. --worker always gets its own tree."""
        lane = self.make_lane()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            path = sync.start(lane, slug="cbp-query", worker=True)
        self.assertNotEqual(Path(path).resolve(), lane.resolve())
        self.assertIn("WORKTREE:", buf.getvalue())
        self.assertEqual(self.branch_of(lane), f"{sync.socket.gethostname()}/old-task")
        self.assertTrue(self.branch_of(Path(path)).endswith("/cbp-query"))

    def test_start_worker_inside_agent_isolation_worktree_makes_no_second_tree(self):
        """An Agent-tool isolation tree (.claude/worktrees/agent-*) is already private: --worker works there, no new worktree."""
        tree = self.make_tree(self.tmp.resolve() / ".claude" / "worktrees" / "agent-x1", "worktree-agent-x1")
        before = subprocess.run(["git", "-C", str(self.a), "worktree", "list"], capture_output=True, text=True).stdout
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            path = sync.start(tree, slug="cbp-query", worker=True)
        after = subprocess.run(["git", "-C", str(self.a), "worktree", "list"], capture_output=True, text=True).stdout
        self.assertEqual(Path(path).resolve(), tree.resolve())
        self.assertNotIn("WORKTREE:", buf.getvalue())
        self.assertEqual(before, after)

    def test_start_other_slug_in_another_sessions_tree_makes_a_worktree(self):
        """B3: `start <slug>` from a session tree made for another slug (the Supervisor's) never works in that tree."""
        host = sync.socket.gethostname()
        sup = self.make_tree(self.tmp.resolve() / f"mts-{host.lower()}-supervisor-b", f"{host}/supervisor-b")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            path = sync.start(sup, slug="cbp-query")
        self.assertNotEqual(Path(path).resolve(), sup.resolve())
        self.assertIn("WORKTREE:", buf.getvalue())
        self.assertEqual(self.branch_of(sup), f"{host}/supervisor-b")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(Path(sync.start(sup, slug="supervisor-b")).resolve(), sup.resolve())   # its own slug: stays

    def test_start_worker_flag_on_the_cli(self):
        lane = self.make_lane()
        buf = io.StringIO()
        with mock.patch.object(sync, "toplevel", lambda p: lane), contextlib.redirect_stdout(buf):
            self.assertEqual(sync.main(["start", "w2", "--worker", "-q"]), 0)
        self.assertIn("WORKTREE:", buf.getvalue())
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

    def test_tidy_skips_gateway_marked_worktree(self):
        with contextlib.redirect_stdout(io.StringIO()):
            marked = sync.new_worktree(self.a, "gw")
            plain = sync.new_worktree(self.a, "plain")
        (marked / sync.GATEWAY_MARKER).write_text('x', newline=chr(10))
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=later), [str(plain.resolve())])
            self.assertIsNone(sync.reuse_finished_tree(self.a, marked))
        self.assertTrue(marked.exists())
        self.assertFalse(plain.exists())

    def test_gateway_marker_alone_is_not_ignored_data(self):
        """2026-11-11 JIS-NB: tidy kept 19 released gateway trees as 'ignored data would be deleted (.gateway_owner)': the real repo
        gitignores the marker, so `status --ignored` listed it as data and no remover (tidy, start's retire, wt_maint) could go on."""
        with open(self.a / ".git" / "info" / "exclude", "a", encoding="utf-8") as f:
            f.write(chr(10) + sync.GATEWAY_MARKER + chr(10))
        with contextlib.redirect_stdout(io.StringIO()):
            rel = sync.new_worktree(self.a, "relx")
        (rel / sync.GATEWAY_MARKER).write_text("x", newline=chr(10))
        self.assertEqual(sync.ignored_data(rel), [])
        (rel / "Dumps").mkdir()
        (rel / "Dumps" / "keep.txt").write_text("x", newline=chr(10))
        with open(self.a / ".git" / "info" / "exclude", "a", encoding="utf-8") as f:
            f.write("Dumps/" + chr(10))
        self.assertEqual(sync.ignored_data(rel), ["Dumps/"])          # real data is still data
        later = time.time() + 48 * 3600
        (rel / "Dumps" / "keep.txt").unlink()
        with mock.patch.object(sync, "open_claims", return_value=[]), contextlib.redirect_stdout(io.StringIO()) as out:
            gone = sync.tidy(self.a, apply=True, now=later, fetch=False, gateway_only=True)
        self.assertEqual(gone, [str(rel.resolve())], out.getvalue())

    def test_start_retires_released_shipped_gateway_tree_despite_hold(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rel = sync.new_worktree(self.a, "rel")        # marked, clean, on trunk, no claim
            busy = sync.new_worktree(self.a, "busy")      # marked, clean, but an open claim
            own = sync.new_worktree(self.a, "own")        # marked, unshipped commit
        for t in (rel, busy, own):
            (t / sync.GATEWAY_MARKER).write_text("x", newline=chr(10))
        commit(own, "unshipped.py", "u" + chr(10))
        later = time.time() + 48 * 3600
        with mock.patch.object(sync, "open_claims", return_value=[("busy", {})]),                 contextlib.redirect_stdout(io.StringIO()) as out:
            gone = sync.tidy(self.a, apply=True, now=later, fetch=False, gateway_only=True)
        self.assertEqual(gone, [str(rel.resolve())], out.getvalue())
        self.assertFalse(rel.exists())
        self.assertTrue(busy.exists())
        self.assertTrue(own.exists())

    def test_start_calls_the_gateway_retire(self):
        with mock.patch.object(sync, "retire_released_gateway_trees") as m, contextlib.redirect_stdout(io.StringIO()):
            sync.start(self.a, slug="zzz", quiet=True)
        m.assert_called_once()

    def test_start_writes_gateway_marker_only_on_gateway_profile(self):
        with mock.patch.dict(os.environ, {"MTS_GATEWAY": "1"}):
            self.assertTrue(sync.mark_gateway(self.a))
        self.assertTrue((self.a / sync.GATEWAY_MARKER).exists())
        (self.a / sync.GATEWAY_MARKER).unlink()
        no_flag = str(self.a / "no_such_flag")
        with mock.patch.dict(os.environ, {"MTS_GATEWAY": "0", "MTS_GATEWAY_FLAG": no_flag}):
            self.assertFalse(sync.mark_gateway(self.a))
        flag = self.a / "flag_file"
        flag.write_text("on", encoding="utf-8")
        with mock.patch.dict(os.environ, {"MTS_GATEWAY": "0", "MTS_GATEWAY_FLAG": str(flag)}):
            self.assertTrue(sync.mark_gateway(self.a))
        (self.a / sync.GATEWAY_MARKER).unlink()

    def test_station_runs_where_all_then_tidy(self):
        with contextlib.redirect_stdout(io.StringIO()):
            done = sync.new_worktree(self.a, "done")
        later = time.time() + 48 * 3600
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = sync.station(self.a, now=later)
        self.assertIn("worktree(s) hold work", buf.getvalue())
        self.assertEqual(res, [str(done.resolve())])
        self.assertTrue(done.exists())  # dry run removes nothing

    def test_station_apply_removes_only_the_clean_shipped_idle_tree(self):
        with contextlib.redirect_stdout(io.StringIO()):
            done = sync.new_worktree(self.a, "done")
            ahead = sync.new_worktree(self.a, "ahead")
        commit(ahead, "unshipped.py", "u\n")
        later = time.time() + 48 * 3600
        with contextlib.redirect_stdout(io.StringIO()):
            res = sync.station(self.a, apply=True, now=later)
        self.assertEqual(res, [str(done.resolve())])
        self.assertFalse(done.exists())
        self.assertTrue(ahead.exists())
        self.assertTrue(self.a.exists())

    def test_tidy_dry_run_hint_is_a_command_that_runs_on_windows(self):
        # 2026-10-23: the hint printed `sync.py tidy --apply`, which Windows cannot run without `python scripts/dev/` in front
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.tidy(self.a)
        self.assertIn("`python scripts/dev/sync.py tidy --apply`", buf.getvalue())

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

    def test_tidy_retires_a_shipped_clean_tree_after_one_hour_not_24(self):
        with contextlib.redirect_stdout(io.StringIO()):
            done = sync.new_worktree(self.a, "shipped-hr")
            self.assertEqual(sync.tidy(self.a, now=time.time() + 0.5 * 3600), [])
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 2 * 3600), [str(done.resolve())])
        self.assertFalse(done.exists())

    def test_tidy_keeps_a_tree_with_an_open_claim(self):
        with contextlib.redirect_stdout(io.StringIO()):
            held = sync.new_worktree(self.a, "held-task")
            free = sync.new_worktree(self.a, "free-task")
            sync.claim(self.a, "held task", area="scripts/dev", gate=self.gate)
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 2 * 3600), [str(free.resolve())])
            self.assertTrue(held.exists())
            self.assertFalse(free.exists())
            # tidy_after_ship runs the same tidy: still kept
            later = lambda repo, **k: sync.tidy(repo, now=time.time() + 2 * 3600, **k)
            self.assertEqual(sync.tidy_after_ship(self.a, tidy_fn=later), [])
            self.assertTrue(held.exists())

    def test_tidy_two_hours_still_keeps_dirty_unshipped_live_and_stranger_trees(self):
        with contextlib.redirect_stdout(io.StringIO()):
            dirty = sync.new_worktree(self.a, "d2")
            ahead = sync.new_worktree(self.a, "a2")
            live = sync.new_worktree(self.a, "l2")
        (dirty / "scratch.txt").write_text("wip\n", newline="\n")
        commit(ahead, "unshipped.py", "u\n")
        (live / sync.LIVE_MARKER).write_text("", newline="\n")
        stranger = self.a.parent / "stranger-tree"
        sh(self.a, "worktree", "add", "-q", str(stranger), "-b", "stranger", "origin/fast-track")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 2 * 3600), [])
        for t in (dirty, ahead, live, stranger, self.a):
            self.assertTrue(t.exists(), t)

    def test_start_reuses_a_finished_same_slug_tree_instead_of_dash_2(self):
        with contextlib.redirect_stdout(io.StringIO()):
            first = sync.new_worktree(self.a, "again")
            real_idle = sync.idle_hours
            sync.idle_hours = lambda *a, **k: 5.0
            try:
                second = sync.new_worktree(self.a, "again")
            finally:
                sync.idle_hours = real_idle
        self.assertEqual(second.resolve(), first.resolve())
        self.assertFalse(second.with_name(second.name + "-2").exists())

    def test_start_twice_same_slug_reuses_unfinished_tree(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            first = sync.new_worktree(self.a, "unfinished")
            (first / "wip.txt").write_text("in-progress\n", newline="\n")
            second = sync.new_worktree(self.a, "unfinished")
        self.assertEqual(second.resolve(), first.resolve())
        self.assertFalse(first.with_name(first.name + "-2").exists())
        self.assertTrue((first / "wip.txt").exists())
        self.assertEqual((first / "wip.txt").read_text(encoding="utf-8"), "in-progress\n")
        self.assertIn(f"reusing existing tree {first} (1 uncommitted)", out.getvalue())

        # Unshipped commit also reuses same unfinished tree
        commit(first, "done.py", "d\n")
        with contextlib.redirect_stdout(io.StringIO()):
            third = sync.new_worktree(self.a, "unfinished")
        self.assertEqual(third.resolve(), first.resolve())

        # start(--worker) gets a fresh tree for a different slug
        with contextlib.redirect_stdout(io.StringIO()):
            worker_tree = sync.start(first, slug="diff-worker-slug", worker=True)
        self.assertNotEqual(worker_tree.resolve(), first.resolve())
        self.assertIn("diff-worker-slug", worker_tree.name)

    def test_start_makes_dash_2_when_the_same_slug_tree_is_live_or_gateway(self):
        with contextlib.redirect_stdout(io.StringIO()):
            live = sync.new_worktree(self.a, "live")
            gw = sync.new_worktree(self.a, "gw")
            (live / sync.LIVE_MARKER).write_text("", newline="\n")
            (gw / sync.GATEWAY_MARKER).write_text("", newline="\n")
            live2 = sync.new_worktree(self.a, "live")
            gw2 = sync.new_worktree(self.a, "gw")
        self.assertNotEqual(live2.resolve(), live.resolve())
        self.assertTrue(live2.name.endswith("-2"))
        self.assertNotEqual(gw2.resolve(), gw.resolve())
        self.assertTrue(gw2.name.endswith("-2"))

    def test_tidy_and_reuse_work_under_any_hostname(self):
        real = sync.socket.gethostname
        sync.socket.gethostname = lambda: "DESKTOP-F7IU69N"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                wt = sync.new_worktree(self.a, "lenovo-job")
                self.assertTrue(wt.name.startswith("mts-desktop-f7iu69n-"))
                self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 2 * 3600), [str(wt.resolve())])
        finally:
            sync.socket.gethostname = real

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

    def _push_ignore(self, text, *files):
        """Commit .gitignore (and `files`, name -> text) on the primary tree and push, so new trees carry them."""
        (self.a / ".gitignore").write_text(text, newline="\n")
        sh(self.a, "add", ".gitignore")
        for name, body in files:
            (self.a / name).parent.mkdir(parents=True, exist_ok=True)
            (self.a / name).write_text(body, newline="\n")
            sh(self.a, "add", name)
        sh(self.a, "commit", "-q", "-m", "fixture")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")

    def test_tidy_retires_a_tree_whose_only_change_is_the_regenerated_layers_md(self):
        rel = "MyTradingSys/system/LAYERS.md"
        self._push_ignore("", (rel, "# LAYERS\n"))
        with contextlib.redirect_stdout(io.StringIO()):
            gen = sync.new_worktree(self.a, "gen")
            mixed = sync.new_worktree(self.a, "mixed")
            gone = sync.new_worktree(self.a, "gone")
        (gen / rel).write_text("# LAYERS regenerated\n", newline="\n")
        (mixed / rel).write_text("# LAYERS regenerated\n", newline="\n")
        (mixed / "notes.txt").write_text("a person's file\n", newline="\n")
        (gone / rel).unlink()                                   # a deleted LAYERS.md is not a regeneration
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600), [str(gen.resolve())])
        self.assertTrue(mixed.exists() and gone.exists())
        # is_noise itself is unchanged: ship / start / stop_guard still see a modified LAYERS.md as work
        self.assertFalse(sync.is_noise(" M " + rel))

    def test_tidy_retires_a_tree_holding_rebuildable_ignored_outputs_but_keeps_sim_desk_answers(self):
        ign = ("MyTradingSys/research/sim_desk/cache/\nMyTradingSys/tools/live_aid/analyst_data.js\nMyTradingSys/runtime/BUILD_REPORT.md\n"
               "Dumps/*\nruntime_data/gate_fail_logs/\n")
        self._push_ignore(ign, ("MyTradingSys/keep.txt", "k\n"))
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "outputs")
            ans = sync.new_worktree(self.a, "answers")
        for t in (wt, ans):
            for rel in ("MyTradingSys/research/sim_desk/cache/bars/BTC.json", "MyTradingSys/tools/live_aid/analyst_data.js",
                        "MyTradingSys/runtime/BUILD_REPORT.md", "Dumps/SESSION_PASTE.txt", "runtime_data/gate_fail_logs/1_step-3.log"):
                (t / rel).parent.mkdir(parents=True, exist_ok=True)
                (t / rel).write_text("x\n", newline="\n")
        (ans / "MyTradingSys/research/sim_desk/cache/answers.jsonl").write_text("{}\n", newline="\n")
        self.assertEqual(sync.ignored_data(wt), [])
        self.assertTrue(sync.ignored_data(ans))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600), [str(wt.resolve())])
        self.assertTrue(ans.exists())

    def test_tidy_retires_gemini_job_and_dsa_trees_without_all(self):
        base = self.tmp.resolve()
        gq = self.make_tree(base / "gq" / "card-1", "gemini-q/card-1")
        dsa = self.make_tree(base / "mts-dsa-jis-nuc-1102-0608", "dsa/jis-nuc-1102-0608")
        lane = self.make_tree(base / "mts-gemini", "gemini/lane")                  # named lane stays
        elsewhere = self.make_tree(base / "other" / "card-2", "gemini-q/card-2")   # not under a gq folder
        real = sync.socket.gethostname
        sync.socket.gethostname = lambda: "JIS-NUC"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(sorted(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600)), sorted([str(gq), str(dsa)]))
        finally:
            sync.socket.gethostname = real
        self.assertTrue(lane.exists() and elsewhere.exists())
        branches = subprocess.run(["git", "-C", str(self.a), "branch", "--list", "gemini-q/*"], capture_output=True, text=True).stdout
        self.assertNotIn("card-1", branches)       # branch gone too, so the same card id can get a fresh tree

    def test_tidy_after_ship_retires_others_never_its_own_tree_and_never_raises(self):
        with contextlib.redirect_stdout(io.StringIO()):
            mine = sync.new_worktree(self.a, "mine")
            other = sync.new_worktree(self.a, "other")
            busy = sync.new_worktree(self.a, "busy")
        (busy / "wip.txt").write_text("wip\n", newline="\n")
        calls = []
        real_tidy = sync.tidy

        def spy(*a, **k):
            calls.append(k)
            return real_tidy(*a, now=time.time() + 48 * 3600, **k)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gone = sync.tidy_after_ship(mine, tidy_fn=spy)
        self.assertEqual(gone, [str(other.resolve())])
        self.assertTrue(mine.exists() and busy.exists() and not other.exists())
        self.assertTrue(calls[0]["apply"] and calls[0]["fetch"] is False and calls[0]["deadline"])
        self.assertIn("retired 1", buf.getvalue())

        def boom(*a, **k):
            raise RuntimeError("git exploded")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync.tidy_after_ship(mine, tidy_fn=boom), [])

    # 2026-11-13: 87 trees piled up (gateway marker kept them, the time-boxed scans were silent, stale index.lock files went unseen)
    def test_ship_release_removes_the_gateway_marked_own_tree_even_from_inside_it(self):
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "own-rel")
        (wt / sync.GATEWAY_MARKER).write_text("x", newline=chr(10))
        sync.claim(wt, "Own rel", area="scripts/dev", gate=self.gate)
        commit(wt, "own.py", "o" + chr(10))
        real_ship = sync.ship
        old_cwd = os.getcwd()
        os.chdir(wt)
        try:
            with mock.patch.object(sync, "ship", lambda repo, **kw: real_ship(repo, gate=self.gate, **kw)),                     mock.patch.object(sync, "check_route_tags"), mock.patch.object(sync, "stage_layers"),                     mock.patch.object(sync, "refuse_shared_main"), contextlib.redirect_stdout(io.StringIO()) as out:
                rc = sync.main(["ship", "--release", "own-rel"])
            self.assertEqual(rc, 0, out.getvalue())
        finally:
            os.chdir(old_cwd)
        self.assertFalse(wt.exists(), out.getvalue())
        self.assertIn("own.py", self.head_files(self.a))
        self.assertNotIn(wt.name, sh(self.a, "worktree", "list").stdout)

    def test_own_tree_with_uncommitted_files_or_unshipped_commits_is_never_removed(self):
        with contextlib.redirect_stdout(io.StringIO()):
            dirty = sync.new_worktree(self.a, "dirty-own")
            ahead = sync.new_worktree(self.a, "ahead-own")
        (dirty / "wip.txt").write_text("wip" + chr(10), newline=chr(10))
        (dirty / sync.GATEWAY_MARKER).write_text("x", newline=chr(10))
        commit(ahead, "u.py", "u" + chr(10))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(sync.retire_own_tree(dirty))
            self.assertFalse(sync.retire_own_tree(ahead))
            self.assertFalse(sync.retire_own_tree(self.a))          # primary
        self.assertTrue(dirty.exists() and ahead.exists() and self.a.exists())

    def test_failed_own_removal_is_queued_and_the_next_start_retries_it(self):
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "stuck")
            other = sync.new_worktree(self.a, "other-run")
        with mock.patch.object(sync, "remove_tree_now", return_value=False), contextlib.redirect_stdout(io.StringIO()):
            sync.retire_own_tree(wt)
        pending = self.a / ".git" / sync.TIDY_PENDING
        self.assertIn(wt.name, pending.read_text(encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()):
            sync.retry_pending_removals(other)        # runs from another tree
        self.assertFalse(wt.exists())
        self.assertFalse(pending.exists())

    def test_deadline_cut_scan_says_so_and_the_next_call_resumes_past_the_stop(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for i in range(4):
                sync.new_worktree(self.a, f"t{i}")
        later = time.time() + 48 * 3600
        checked = []
        real_git = sync.git

        def spy(repo, *a, **k):
            if a[:1] == ("status",) and Path(repo).resolve() != self.a.resolve():
                checked.append(Path(repo).name)
            return real_git(repo, *a, **k)

        def cut_after_two(deadline):
            return len(set(checked)) >= 2
        with mock.patch.object(sync, "git", spy), mock.patch.object(sync, "tidy_cutoff", cut_after_two),                 mock.patch.object(sync, "open_claims", return_value=[]), contextlib.redirect_stdout(io.StringIO()) as out:
            sync.tidy(self.a, now=later, fetch=False, deadline=1)
        self.assertRegex(out.getvalue(), r"tidy: stopped at budget, 2 tree\(s\) not checked")
        seen_first = set(checked)
        checked.clear()
        with mock.patch.object(sync, "git", spy), mock.patch.object(sync, "tidy_cutoff", cut_after_two),                 mock.patch.object(sync, "open_claims", return_value=[]), contextlib.redirect_stdout(io.StringIO()):
            sync.tidy(self.a, now=later, fetch=False, deadline=1)
        self.assertTrue(seen_first.isdisjoint(set(checked)), (seen_first, checked))

    def test_stale_index_lock_is_removed_fresh_or_git_alive_is_not(self):
        gd = Path(sh(self.a, "rev-parse", "--absolute-git-dir").stdout.strip())
        lock = gd / "index.lock"
        now = time.time()
        lock.write_text("", encoding="utf-8")
        os.utime(lock, (now - 3000, now - 3000))
        with contextlib.redirect_stdout(io.StringIO()):
            sync.stale_lock_state(self.a, now=now, running=lambda: True)
            self.assertTrue(lock.exists())           # git alive
            sync.stale_lock_state(self.a, now=now, running=lambda: None)
            self.assertTrue(lock.exists())           # cannot tell: fail closed
        with contextlib.redirect_stdout(io.StringIO()) as out:
            sync.stale_lock_state(self.a, now=now, running=lambda: False)
        self.assertFalse(lock.exists())
        self.assertIn("removed stale index.lock (age 50m)", out.getvalue())
        lock.write_text("", encoding="utf-8")
        os.utime(lock, (now - 60, now - 60))
        with contextlib.redirect_stdout(io.StringIO()):
            sync.stale_lock_state(self.a, now=now, running=lambda: False)
        self.assertTrue(lock.exists())               # fresh
        with self.assertRaisesRegex(sync.SyncError, r"index\.lock exists \(age 1m"):
            sync.lock_guard(self.a, fail=True, now=now, running=lambda: False)

    def test_pending_retry_removes_the_empty_folder_a_process_held_open(self):
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "held")
        sh(self.a, "worktree", "remove", "--force", str(wt))
        wt.mkdir()                                   # what Windows leaves when a shell sits inside the tree
        (self.a / ".git" / sync.TIDY_PENDING).write_text(str(wt) + chr(10), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            sync.retry_pending_removals(self.a)
        self.assertFalse(wt.exists())

    def test_where_prints_one_tree_count_line(self):
        with contextlib.redirect_stdout(io.StringIO()):
            sync.new_worktree(self.a, "cnt-done")
            dirty = sync.new_worktree(self.a, "cnt-dirty")
        (dirty / "wip.txt").write_text("wip" + chr(10), newline=chr(10))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            sync.where(self.a)
        self.assertIn("trees: total 3 / removable now 1 / uncommitted 1 / unshipped commits 0 / locked 0", out.getvalue())

    def test_tidy_deadline_stops_the_walk(self):
        with contextlib.redirect_stdout(io.StringIO()):
            wt = sync.new_worktree(self.a, "late")
            self.assertEqual(sync.tidy(self.a, apply=True, now=time.time() + 48 * 3600, fetch=False, deadline=time.time() - 1), [])
        self.assertTrue(wt.exists())

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



    # bg-process-audit 2026-10-28: network git calls have a deadline, and a push that failed for a non-race reason is not
    # retried (5 Gemini claims on 2026-10-28 retried 18 pushes each, all printed as 'someone shipped first').
    AUDIT_AUTH = "remote: Invalid username or token." + chr(10) + "fatal: Authentication failed for 'https://github.com/x/y.git/'"

    def failing_push(self, target):
        real = sync.git
        pushes = []

        def spy(repo, *args, **kw):
            if args[:1] == ("push",) and args[-1].endswith(target):
                pushes.append(args)
                return subprocess.CompletedProcess(args, 128, "", self.AUDIT_AUTH)
            return real(repo, *args, **kw)
        return spy, pushes

    def test_claim_push_auth_failure_fails_once_with_the_reason(self):
        spy, pushes = self.failing_push(":refs/heads/claims")
        with mock.patch.object(sync, "git", spy), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(sync.PushFailed) as e:
                sync.claim(self.a, "Task auth", gate=self.gate, force=True)
        self.assertEqual(len(pushes), 1)
        self.assertIn("Authentication failed", str(e.exception))
        self.assertIn("not a race", str(e.exception))

    def test_ship_push_auth_failure_is_not_regated(self):
        commit(self.a, "auth.py", "x" + chr(10))
        spy, pushes = self.failing_push("HEAD:refs/heads/fast-track")
        with mock.patch.object(sync, "git", spy), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(sync.PushFailed):
                sync.ship(self.a, gate=self.gate, sleep=lambda s: None)
        self.assertEqual(len(pushes), 1)
        self.assertEqual(len(self.gated), 1)

    def test_lost_race_message_still_retries(self):
        r = subprocess.CompletedProcess([], 1, "", " ! [rejected]        HEAD -> fast-track (fetch first)" + chr(10) + "error: failed to push some refs")
        self.assertTrue(sync.push_race_lost(r))
        self.assertFalse(sync.push_race_lost(subprocess.CompletedProcess([], 128, "", self.AUDIT_AUTH)))
        self.assertFalse(sync.push_race_lost(subprocess.CompletedProcess([], 124, "", "TIMEOUT git push after 180s")))

    def test_lost_claim_race_retries_after_a_jitter_not_in_lockstep(self):
        # 2026-10-28 NUC (gemini-lane-fix): two gemini claimers each lost 3 claim pushes back to back with ~0 s
        # between attempts (no backoff in the claims loop), so the second claimer re-fetched exactly when the
        # other's push landed: 6 'push rejected' lines, both claims 'still rejected after 3 tries'. The ship loop
        # already jitters 1-5 s between lost-race retries (GATE_SPEED D4); the claims loop now jitters 0.5-4 s too.
        rel = "MyTradingSys/system/claims/jitter.md"
        sync.push_claim_commit(self.a, rel, "host: a\n", "claim jitter")   # create origin/claims
        real = sync.git
        fired = []

        def spy(repo, *args, **kw):
            r = real(repo, *args, **kw)
            if r.returncode == 0 and args[:1] == ("push",) and args[-1].endswith(":refs/heads/claims") and not fired:
                fired.append(1)
                r.returncode, r.stderr = 1, " ! [rejected]  " + rel + " -> claims (fetch first)" + chr(10) + "error: failed to push some refs"
            return r
        sleeps = []
        with mock.patch.object(sync, "git", spy), contextlib.redirect_stdout(io.StringIO()):
            sync.push_claim_commit(self.a, rel, "host: a\n", "claim jitter", sleep=sleeps.append)
        self.assertEqual(fired, [1])        # first push lost the race; the jittered retry landed
        self.assertEqual(len(sleeps), 1)
        self.assertTrue(0.5 <= sleeps[0] <= 4.0, sleeps)

    def test_claim_and_release_take_a_sleep_arg(self):
        # the CLI claim/release paths thread the sleeper through, so a lost race there is jittered too
        sleeps = []
        spy = mock.Mock(wraps=sync.push_claim_commit)
        with mock.patch.object(sync, "push_claim_commit", spy):
            sync.claim(self.a, "Jitter claim", gate=self.gate, force=True, sleep=sleeps.append)
        self.assertTrue(any("sleep" in c.kwargs for c in spy.call_args_list), spy.call_args_list)
        spy.reset_mock()
        rel_slug = "jitter-claim"
        with mock.patch.object(sync, "push_claim_commit", spy):
            sync.release(self.a, rel_slug, sleep=sleeps.append)
        self.assertTrue(any("sleep" in c.kwargs for c in spy.call_args_list), spy.call_args_list)


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

    def _wait_log(self):
        p = self.slots_base / "wait.log"
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []

    def test_wait_is_logged(self):
        """ARCH_REVIEW row 3: the real slot wait lands in <slots base>/wait.log (temp dir, never the repo)."""
        a = sync.gate_slot(self.tmp, alive=lambda p: True).__enter__()
        b = sync.gate_slot(self.tmp, alive=lambda p: True).__enter__()
        threading.Timer(0.3, lambda: a.__exit__(None, None, None)).start()
        with contextlib.redirect_stdout(io.StringIO()):
            with sync.gate_slot(self.tmp, alive=lambda p: True, poll=0.05, mode="fast"):
                pass
        b.__exit__(None, None, None)
        rows = [r for r in self._wait_log() if r["mode"] == "fast"]
        self.assertEqual(len(rows), 1)
        self.assertGreaterEqual(rows[0]["wait_s"], 0.2)
        self.assertGreaterEqual(rows[0]["busy"], 1)
        self.assertEqual(rows[0]["pid"], os.getpid())

    def test_wait_log_is_rotated_and_a_log_failure_never_fails_the_gate(self):
        log = self.slots_base / "wait.log"
        log.write_text("".join(json.dumps({"i": i, "pad": "x" * 80}) + "\n" for i in range(300)), encoding="utf-8")
        with sync.gate_slot(self.tmp, alive=lambda p: True):
            pass
        lines = log.read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), sync.WAIT_LOG_KEEP + 1)
        self.assertEqual(json.loads(lines[-1])["mode"], "full")
        real_open = os.open

        def bad_open(path, flags, *a):
            if str(path).endswith("wait.log"):
                raise OSError("disk")
            return real_open(path, flags, *a)
        with mock.patch.object(sync.os, "open", side_effect=bad_open):
            with sync.gate_slot(self.tmp, alive=lambda p: True) as g:   # an unwritable log must not fail the gate
                self.assertTrue(g.path)

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

    def test_fix_ci_flag_keeps_the_fast_gate(self):
        with mock.patch.object(sync, "ship"), mock.patch.object(sync, "toplevel", return_value=Path(".")), mock.patch.object(sync, "stage_layers"), \
                mock.patch.object(sync, "run_host_health"), mock.patch.object(sync, "check_route_tags"), \
                mock.patch.dict(os.environ, {}, clear=False):   # the real host scan took 38-70 s here
            os.environ.pop("SYNC_FULL_GATE", None)
            os.environ.pop("SYNC_FIX_CI", None)
            self.assertEqual(sync.main(["ship", "--fix-ci"]), 0)
            self.assertEqual((os.environ.get("SYNC_FIX_CI"), os.environ.get("SYNC_FULL_GATE")), ("1", None))
            os.environ.pop("SYNC_FULL_GATE", None)
            os.environ.pop("SYNC_FIX_CI", None)

    def test_pure_revert_skips_the_local_gate_only_when_every_commit_is_a_revert(self):
        def fake(subjects):
            return mock.patch.object(sync, "git", return_value=mock.Mock(stdout=subjects))
        with fake('Revert "x"\nRevert "y"\n'):
            self.assertTrue(sync.pure_revert(Path(".")))
        with fake('Revert "x"\nfix: y\n'):
            self.assertFalse(sync.pure_revert(Path(".")))
        with fake(""):
            self.assertFalse(sync.pure_revert(Path(".")))

    def test_fast_and_full_gates_share_one_pool_and_an_empty_slot_file_is_busy(self):
        """ARCH_REVIEW row 3: one gate queue per machine. A fast gate takes a slot from the same pool as a full gate."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        sh(tmp, "init", "-q")
        slots_base = tmp / "slots_base"
        os.environ["MTS_GATE_SLOTS_DIR"] = str(slots_base)
        self.addCleanup(lambda: os.environ.pop("MTS_GATE_SLOTS_DIR", None))
        self.assertFalse(hasattr(sync, "GATE_PRECHECK_SLOTS"))
        import run_all_tests as rat
        self.assertFalse(hasattr(rat, "FAST_SLOTS"))
        main_d = sync.host_gate_slots_dir(sync.GATE_POOL)
        with sync.gate_slot(tmp, alive=lambda p: True), sync.gate_slot(tmp, alive=lambda p: True):
            fast = rat.gate_slot_factory("fast")()
            fast.timeout, fast.poll, fast.note_every = 0.2, 0.05, 99
            fast.alive = lambda p: True
            with self.assertRaises(sync.GateSlotTimeout):   # both slots busy: the fast gate queues behind them
                with fast:
                    pass
            self.assertEqual(fast.name, sync.GATE_POOL)
            self.assertEqual(rat.gate_slot_factory("full")().name, fast.name)
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


class OwnCiWaitTest(unittest.TestCase):
    """ship-waits-own-ci (CI red and flow review 2026-10-25, claim 1): after the push the ship shell waits for the CI run of ITS OWN sha and
    prints CI RED at once, so the author (the one person who knows what they just shipped) sees a red run in the same shell."""
    SHA = "deadbeef" + "0" * 32
    RED_RUN = {"id": 7, "status": "completed", "conclusion": "failure", "html_url": "https://github.com/o/r/actions/runs/7"}
    GREEN_RUN = {"id": 8, "status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/8"}

    def setUp(self):
        self.pushed = sync.Pushed(self.SHA, ["scripts/dev/example_tool.py"])
        self.t = 0.0
        self.slept = []
        self.asked = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s

    def run_wait(self, runs, pushed=None, **kw):
        """runs: one answer per poll (the last one repeats); an Exception instance is raised instead of returned."""
        seq = list(runs)

        def fetch(sha):
            self.asked.append(sha)
            a = seq.pop(0) if len(seq) > 1 else seq[0]
            if isinstance(a, Exception):
                raise a
            return a
        kw.setdefault("failed_jobs", lambda run_id: [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            state = sync.wait_own_ci(pushed or self.pushed, fetch=fetch, sleep=self.sleep, now_fn=self.now, poll=20, **kw)
        return state, out.getvalue()

    def test_a_red_run_of_the_shipped_sha_prints_CI_RED_at_once_with_the_failed_job(self):
        state, out = self.run_wait([[self.RED_RUN]], failed_jobs=lambda run_id: ["offline gate (windows-latest 4/12)"] if run_id == 7 else [])
        self.assertEqual(state, "red")
        self.assertIn("CI RED deadbeef", out)
        self.assertIn("offline gate (windows-latest 4/12)", out)
        self.assertIn(self.RED_RUN["html_url"], out)
        self.assertEqual(self.asked, [self.SHA])       # asked about its own sha, nobody else's
        self.assertEqual(self.slept, [])               # red is reported on the first poll that sees it, no extra wait

    def test_a_run_that_is_still_going_is_polled_until_it_goes_green(self):
        state, out = self.run_wait([[], [{"status": "queued"}], [{"status": "in_progress"}], [self.GREEN_RUN]])
        self.assertEqual(state, "green")
        self.assertIn("CI green deadbeef", out)
        self.assertNotIn("CI RED", out)
        self.assertEqual(self.slept, [20, 20, 20])

    def test_a_run_that_goes_red_after_polling_is_still_red(self):
        state, out = self.run_wait([[{"status": "in_progress"}], [self.RED_RUN]])
        self.assertEqual((state, self.slept), ("red", [20]))
        self.assertIn("CI RED deadbeef", out)

    def test_other_failure_kinds_are_red_and_cancelled_is_not_a_verdict(self):
        for c in ("timed_out", "startup_failure"):
            self.assertEqual(self.run_wait([[dict(self.RED_RUN, conclusion=c)]])[0], "red", c)
        state, out = self.run_wait([[dict(self.RED_RUN, conclusion="cancelled")]])
        self.assertEqual(state, "unknown")
        self.assertNotIn("CI RED", out)

    def test_no_run_ever_appearing_gives_up_after_the_start_window_and_says_so(self):
        state, out = self.run_wait([[]], start_s=90, wait_s=600)
        self.assertEqual(state, "none")
        self.assertIn("no CI run for deadbeef", out)
        self.assertTrue(90 <= self.t < 90 + 20 + 1, self.t)

    def test_a_run_that_never_finishes_stops_at_the_cap_and_is_not_called_red(self):
        state, out = self.run_wait([[{"status": "in_progress", "html_url": "https://x/9"}]], start_s=90, wait_s=100)
        self.assertEqual(state, "timeout")
        self.assertIn("deadbeef", out)
        self.assertNotIn("CI RED", out)
        self.assertTrue(100 <= self.t < 100 + 20 + 1, self.t)

    def test_offline_or_rate_limited_is_unknown_and_never_raises(self):
        state, out = self.run_wait([OSError("offline")])
        self.assertEqual(state, "unknown")
        self.assertNotIn("CI RED", out)
        self.assertEqual(len(self.asked), 3)           # three misses in a row, then stop; one blip does not
        state, out = self.run_wait([OSError("blip"), [self.GREEN_RUN]])
        self.assertEqual(state, "green")

    def test_a_failed_jobs_lookup_that_breaks_still_prints_red(self):
        def boom(run_id):
            raise OSError("jobs api down")
        state, out = self.run_wait([[self.RED_RUN]], failed_jobs=boom)
        self.assertEqual(state, "red")
        self.assertIn("CI RED deadbeef", out)

    def test_a_ship_the_ci_path_filter_skips_does_not_wait_or_ask(self):
        globs = ["scripts/**", "MyTradingSys/system/tasks/**"]
        docs = sync.Pushed(self.SHA, ["MyTradingSys/system/NEXT_SESSION.md"])
        state, out = self.run_wait([[]], pushed=docs, globs=globs)
        self.assertEqual((state, self.asked, self.slept), ("none", [self.SHA], []))
        self.assertIn("path filter", out)
        self.asked.clear()
        self.slept.clear()
        state, out = self.run_wait([[self.GREEN_RUN]], pushed=sync.Pushed(self.SHA, ["MyTradingSys/system/tasks/x.json"]), globs=globs)
        self.assertEqual(state, "green")

    def test_filter_skips_files_but_fetched_run_is_failure_reports_ci_red(self):
        globs = ["scripts/**", "MyTradingSys/system/tasks/**"]
        docs = sync.Pushed(self.SHA, ["MyTradingSys/system/NEXT_SESSION.md"])
        state, out = self.run_wait([[self.RED_RUN]], pushed=docs, globs=globs)
        self.assertEqual(state, "red")
        self.assertIn("CI RED deadbeef", out)

    def test_filter_skips_files_but_fetched_run_is_in_progress_reports_run_state(self):
        globs = ["scripts/**", "MyTradingSys/system/tasks/**"]
        docs = sync.Pushed(self.SHA, ["MyTradingSys/system/NEXT_SESSION.md"])
        in_prog = {"id": 9, "status": "in_progress", "html_url": "https://github.com/o/r/actions/runs/9"}
        state, out = self.run_wait([[in_prog], [self.GREEN_RUN]], pushed=docs, globs=globs)
        self.assertEqual(state, "green")
        self.assertIn("CI green deadbeef", out)
        self.assertNotIn("the ci.yml path filter skips these files", out)

    def test_ci_command_sha_reports_real_run_state_for_failed_and_in_progress(self):
        # 4d7c96522: failed run reports CI RED and exits CI_RED_EXIT
        with mock.patch.object(sync, "ci_runs_for", return_value=[self.RED_RUN]), \
                mock.patch.object(sync, "ci_failed_jobs", return_value=["offline gate"]), \
                mock.patch.object(sync, "ci_path_filter", return_value=["scripts/**"]):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = sync.ci_verb(Path("."), ["4d7c96522"])
            self.assertEqual(rc, sync.CI_RED_EXIT)
            self.assertIn("CI RED 4d7c9652", out.getvalue())
            self.assertNotIn("the ci.yml path filter skips these files", out.getvalue())

        # 14b12f2c: in progress run reports green upon completion and exits 0
        in_prog = {"id": 41675390817, "status": "in_progress", "html_url": "https://github.com/o/r/actions/runs/41675390817"}
        runs = [[in_prog], [self.GREEN_RUN]]
        def mock_runs(sha):
            return runs.pop(0) if len(runs) > 1 else runs[0]
        with mock.patch.object(sync, "ci_runs_for", side_effect=mock_runs), \
                mock.patch.object(sync, "ci_path_filter", return_value=["scripts/**"]):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = sync.wait_own_ci(sync.Pushed("14b12f2c", []), sleep=lambda s: None, globs=["scripts/**"])
            self.assertEqual(rc, "green")
            self.assertIn("CI green 14b12f2c", out.getvalue())
            self.assertNotIn("the ci.yml path filter skips these files", out.getvalue())

    def test_ci_path_filter_is_read_from_the_workflow_and_matches_like_github(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / ".github" / "workflows").mkdir(parents=True)
        (tmp / ".github" / "workflows" / "ci.yml").write_text(
            "name: CI\non:\n  push:\n    branches: [fast-track]\n    paths:\n      - 'src/**'\n      # a comment line\n"
            "      - 'MyTradingSys/research/**/*.py'   # trailing comment\n      - '.gitignore'\n      - scripts/*.sh\n"
            "  pull_request:\n    types: [opened]\njobs:\n  x:\n    runs-on: y\n", encoding="utf-8", newline="\n")
        globs = sync.ci_path_filter(tmp)
        self.assertEqual(globs, ["src/**", "MyTradingSys/research/**/*.py", ".gitignore", "scripts/*.sh"])
        yes = ["src/a/b.java", "MyTradingSys/research/x.py", "MyTradingSys/research/a/b/c.py", ".gitignore", "scripts/run.sh"]
        no = ["MyTradingSys/research/x/out.tsv", "MyTradingSys/system/NEXT_SESSION.md", "scripts/dev/run.sh", "docs/src/a.md", "xgitignore"]
        for f in yes:
            self.assertTrue(sync.ci_starts([f], globs), f)
        for f in no:
            self.assertFalse(sync.ci_starts([f], globs), f)
        self.assertTrue(sync.ci_starts(["src" + chr(92) + "a.java"], globs))   # Windows separators
        self.assertTrue(sync.ci_starts(["whatever.md"], None))                 # no filter known: assume a run starts (wait, then say none)
        self.assertIsNone(sync.ci_path_filter(tmp / "nowhere"))

    def test_the_real_ci_yml_filter_starts_a_run_for_code_and_cards_but_not_notes(self):
        globs = sync.ci_path_filter(Path(__file__).resolve().parents[2])
        self.assertTrue(globs, "ci.yml push paths not found")
        self.assertTrue(sync.ci_starts(["scripts/dev/sync.py", "MyTradingSys/system/NEXT_SESSION.md"], globs))
        self.assertTrue(sync.ci_starts(["MyTradingSys/system/tasks/some-card.json"], globs))
        self.assertFalse(sync.ci_starts(["MyTradingSys/system/NEXT_SESSION.md", "MyTradingSys/research/STATUS.md"], globs))

    def test_cli_ship_waits_for_its_own_sha_and_exits_3_on_red(self):
        for state, rc in (("red", sync.CI_RED_EXIT), ("green", 0), ("none", 0), ("unknown", 0), ("timeout", 0)):
            with mock.patch.object(sync, "toplevel", return_value=Path(".")), mock.patch.object(sync, "stage_layers"), mock.patch.object(sync, "run_host_health"), \
                    mock.patch.object(sync, "ship", return_value=self.pushed) as mock_ship, \
                    mock.patch.object(sync, "ci_path_filter", return_value=["scripts/**"]), \
                    mock.patch.object(sync, "wait_own_ci", return_value=state) as mock_wait:
                self.assertEqual(sync.main(["ship", "--wait-ci", "--release", "my-slug"]), rc, state)
                mock_ship.assert_called_once_with(Path("."), release_slug="my-slug", after_slug=None)
                self.assertEqual(mock_wait.call_args[0][0], self.pushed)
                self.assertEqual(mock_wait.call_args[1]["globs"], ["scripts/**"])
        self.assertEqual(sync.CI_RED_EXIT, 3)

    def test_ship_returns_without_the_ci_wait_by_default_and_ci_verb_waits_later(self):
        """B8 (2026-10-28): the 10-minute CI poll is opt-in on ship; `sync.py ci` does it for the last pushed sha."""
        with tempfile.TemporaryDirectory() as td, mock.patch.object(sync, "toplevel", return_value=Path(td)),                 mock.patch.object(sync, "run_host_health"), mock.patch.object(sync, "ship", return_value=self.pushed),                 mock.patch.object(sync, "check_route_tags"),                 mock.patch.object(sync, "write_last_pushed") as mock_save,                 mock.patch.object(sync, "ci_path_filter", return_value=None),                 mock.patch.object(sync, "wait_own_ci", return_value="red") as mock_wait:
            self.assertEqual(sync.main(["ship"]), 0)
            mock_wait.assert_not_called()
            mock_save.assert_called_once()
            with mock.patch.dict(os.environ, {"SYNC_WAIT_CI": "1"}):
                self.assertEqual(sync.main(["ship"]), sync.CI_RED_EXIT)
            self.assertEqual(mock_wait.call_count, 1)
            with mock.patch.object(sync, "read_last_pushed", return_value=self.pushed):
                self.assertEqual(sync.main(["ci"]), sync.CI_RED_EXIT)
            self.assertEqual(mock_wait.call_args[0][0], self.pushed)
            self.assertEqual(sync.main(["ci", "abcdef12"]), sync.CI_RED_EXIT)
            self.assertEqual(mock_wait.call_args[0][0].sha, "abcdef12")
            with mock.patch.object(sync, "read_last_pushed", return_value=None):
                self.assertEqual(sync.main(["ci"]), 1)    # nothing pushed from this tree and no sha given

    def test_last_pushed_sha_round_trips_through_the_git_dir(self):
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "init", "-q", td], check=True)
            self.assertIsNone(sync.read_last_pushed(td))
            sync.write_last_pushed(td, self.pushed)
            self.assertEqual(sync.read_last_pushed(td), self.pushed)

    def test_no_ci_wait_flag_env_and_a_ship_that_pushed_nothing_skip_the_wait(self):
        with mock.patch.object(sync, "toplevel", return_value=Path(".")), mock.patch.object(sync, "stage_layers"), mock.patch.object(sync, "run_host_health"), \
                mock.patch.object(sync, "ship", return_value=self.pushed) as mock_ship, \
                mock.patch.object(sync, "wait_own_ci", return_value="red") as mock_wait:
            self.assertEqual(sync.main(["ship", "--no-ci-wait"]), 0)
            mock_ship.assert_called_once_with(Path("."), release_slug=None, after_slug=None)   # the flag never reaches ship()
            with mock.patch.dict(os.environ, {"SYNC_NO_CI_WAIT": "1"}):
                self.assertEqual(sync.main(["ship"]), 0)
            mock_wait.assert_not_called()
        with mock.patch.object(sync, "toplevel", return_value=Path(".")), mock.patch.object(sync, "stage_layers"), mock.patch.object(sync, "run_host_health"), \
                mock.patch.object(sync, "ship", return_value=None), \
                mock.patch.object(sync, "wait_own_ci", return_value="red") as mock_wait:
            self.assertEqual(sync.main(["ship"]), 0)       # nothing shipped: nobody's sha to wait for
            mock_wait.assert_not_called()

    def test_fix_ci_docs_only_ship_dispatches_ci_once_and_other_ships_do_not(self):
        docs = sync.Pushed("abcdef1234", ["MyTradingSys/research/STATUS.md"])
        code = sync.Pushed("abcdef1234", ["scripts/dev/sync.py"])
        cases = ((docs, "--fix-ci", 1), (docs, None, 0), (code, "--fix-ci", 0))
        for pushed, flag, calls in cases:
            with mock.patch.dict(os.environ, {}, clear=False), mock.patch.object(sync, "toplevel", return_value=Path(".")), mock.patch.object(sync, "stage_layers"), \
                    mock.patch.object(sync, "run_host_health"), mock.patch.object(sync, "ship", return_value=pushed), \
                    mock.patch.object(sync, "write_last_pushed"), mock.patch.object(sync, "tidy_after_ship"), \
                    mock.patch.object(sync, "ci_path_filter", return_value=["scripts/**"]), \
                    mock.patch.object(sync, "dispatch_ci") as mock_dispatch:
                os.environ.pop("SYNC_FIX_CI", None)
                self.assertEqual(sync.main(["ship"] + ([flag] if flag else [])), 0)
                self.assertEqual(mock_dispatch.call_count, calls, (pushed.files, flag))

    def test_dispatch_ci_posts_ref_fast_track_or_prints_the_manual_command_and_never_raises(self):
        posted = []
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertTrue(sync.dispatch_ci(post=lambda u, b, t: posted.append((u, b, t)), token="tok"))
        self.assertEqual(len(posted), 1)
        self.assertTrue(posted[0][0].endswith("/workflows/ci.yml/dispatches"))
        self.assertEqual(posted[0][1], {"ref": "fast-track"})
        def boom(u, b, t):
            raise OSError("down")
        for kw in ({"post": boom, "token": "tok"}, {"token": "x", "post": None}):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                if kw["post"] is None:
                    with mock.patch.object(sync, "post_dispatch", side_effect=OSError("down")):
                        self.assertFalse(sync.dispatch_ci(**kw))
                else:
                    self.assertFalse(sync.dispatch_ci(**kw))
            self.assertIn("gh workflow run ci.yml --ref fast-track", buf.getvalue())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertFalse(sync.dispatch_ci(token=""))     # no login: manual command, no call
        self.assertIn("gh workflow run ci.yml --ref fast-track", buf.getvalue())

    def test_unattended_callers_of_ship_opt_out_of_the_wait(self):
        root = Path(__file__).resolve().parent
        for name in ("desk.py", "lane_health.py"):
            self.assertIn('"ship", "--no-ci-wait"', (root / name).read_text(encoding="utf-8"), name)
        import codex_run
        self.assertIn("--no-ci-wait", codex_run.SHIP_ARGS)


class ShipResultFlagTest(unittest.TestCase):
    """`ship --result` commits the tree's uncommitted files with a Result: body line (planner finding, 2026-10-28)."""

    def make_repo(self, td):
        g = lambda *a: subprocess.run(["git", "-C", td, *a], check=True, capture_output=True, text=True).stdout
        g("init", "-q")
        g("config", "user.email", "t@t")
        g("config", "user.name", "t")
        (Path(td) / "a.txt").write_text("one", encoding="utf-8")
        g("add", "-A")
        g("commit", "-q", "-m", "base")
        g("update-ref", f"refs/remotes/origin/{sync.TRUNK}", "HEAD")
        return g

    def test_commit_pending_writes_the_result_line_and_takes_new_and_changed_files(self):
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            (Path(td) / "a.txt").write_text("two", encoding="utf-8")
            (Path(td) / "b.txt").write_text("new", encoding="utf-8")
            self.assertEqual(sync.commit_pending(td, "ships in 40 s", "planner: card edits"), 2)
            msg = g("log", "-1", "--format=%B")
            self.assertTrue(msg.startswith("planner: card edits"))
            self.assertIn("Result: ships in 40 s", msg)
            self.assertEqual(g("status", "--short").strip(), "")
            self.assertEqual(sync.commit_pending(td, "x"), 0)       # clean tree: nothing to commit
            with self.assertRaises(sync.SyncError):
                sync.commit_pending(td, "  ")

    def test_commit_pending_never_stages_halt_or_runtime_data(self):
        """ship-refuse-main-checkout-sweep-1109: ebdf4dc6b swept another session's HALT, AUTO_PAUSE and runtime CSVs into a ship."""
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            rt = Path(td) / "MyTradingSys" / "runtime"
            rt.mkdir(parents=True)
            (rt / "fills.csv").write_text("x", encoding="utf-8")
            (rt / "NOTES.md").write_text("doc", encoding="utf-8")
            ex = Path(td) / "execution"
            ex.mkdir()
            (ex / "HALT").write_text("", encoding="utf-8")
            (ex / "AUTO_PAUSE").write_text("", encoding="utf-8")
            (Path(td) / "a.txt").write_text("two", encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(sync.commit_pending(td, "mine only"), 2)
            shipped = set(g("show", "--name-only", "--format=", "HEAD").split())
            self.assertEqual(shipped, {"a.txt", "MyTradingSys/runtime/NOTES.md"})
            self.assertIn("HALT", out.getvalue())

    def test_commit_pending_leaves_reverted_untracked_file_behind(self):
        """ship-result-sweeps-untracked-1109: 954009888 swept 2 files of a reverted census (deleted on trunk, back on disk) into a ship."""
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            (Path(td) / "a.txt").write_text("two", encoding="utf-8")          # tracked change at the root
            (Path(td) / "b.txt").write_text("new", encoding="utf-8")          # new file next to it: ships
            stray = Path(td) / "other" / "stray.py"
            stray.parent.mkdir()
            stray.write_text("x", encoding="utf-8")
            g("add", "other/stray.py"); g("commit", "-q", "-m", "land")
            g("rm", "-q", "other/stray.py"); g("commit", "-q", "-m", "revert")
            g("update-ref", f"refs/remotes/origin/{sync.TRUNK}", "HEAD")
            stray.parent.mkdir(exist_ok=True)
            stray.write_text("x", encoding="utf-8")                           # a reverted file reappears: left behind
            staged = Path(td) / "lab" / "keep.md"
            staged.parent.mkdir()
            staged.write_text("k", encoding="utf-8")
            g("add", "lab/keep.md")                                           # staged by hand: ships
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                sync.commit_pending(td, "mine only")
            shipped = set(g("show", "--name-only", "--format=", "HEAD").split())
            self.assertEqual(shipped, {"a.txt", "b.txt", "lab/keep.md"})
            self.assertIn("other/stray.py", out.getvalue())

    def test_refuse_shared_main_checkout(self):
        """A main checkout with other worktrees is a shared hub: ship refuses before any commit; a lone clone (cloud) ships."""
        with tempfile.TemporaryDirectory() as td:
            main = Path(td) / "main"
            main.mkdir()
            g = self.make_repo(str(main))
            sync.refuse_shared_main(main)          # lone clone: allowed
            g("worktree", "add", "-q", "--detach", str(Path(td) / "wt"))
            with self.assertRaises(sync.SyncError):
                sync.refuse_shared_main(main)
            sync.refuse_shared_main(Path(td) / "wt")   # a linked worktree is yours: allowed

    def test_stage_layers_commits_a_modified_layers_md_only(self):
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            f = Path(td) / sync.LAYERS_REL
            f.parent.mkdir(parents=True)
            f.write_text("a", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "layers")
            self.assertFalse(sync.stage_layers(td))      # unchanged: nothing
            f.write_text("b", encoding="utf-8")
            (Path(td) / "other.txt").write_text("x", encoding="utf-8")
            self.assertTrue(sync.stage_layers(td))
            self.assertIn("Result:", g("log", "-1", "--format=%B"))
            self.assertEqual(g("status", "--short", "--", sync.LAYERS_REL).strip(), "")
            self.assertIn("other.txt", g("status", "--short"))   # unrelated file untouched

    def _trunk_changes(self, td, extra=None):
        """Repo whose origin/fast-track is one commit ahead (LAYERS.md changed, plus a.txt when extra); HEAD stays behind."""
        g = self.make_repo(td)
        f = Path(td) / sync.LAYERS_REL
        f.parent.mkdir(parents=True)
        f.write_text("base\n", encoding="utf-8", newline="\n")
        g("add", "-A")
        g("commit", "-q", "-m", "layers")
        mine = g("rev-parse", "HEAD").strip()
        f.write_text("trunk\n", encoding="utf-8", newline="\n")
        if extra:
            (Path(td) / "a.txt").write_text("trunk a", encoding="utf-8")
        g("commit", "-aqm", "trunk change")
        g("update-ref", f"refs/remotes/origin/{sync.TRUNK}", "HEAD")
        g("reset", "-q", "--hard", mine)
        return g, f

    def test_merge_trunk_restores_dirty_layers_md(self):
        with tempfile.TemporaryDirectory() as td:
            g, f = self._trunk_changes(td)
            f.write_text("local crlf\r\n", encoding="utf-8", newline="")
            with mock.patch.object(sync, "fetch_trunk"):
                self.assertEqual(sync.merge_trunk(td), 1)
            self.assertEqual(f.read_text(encoding="utf-8"), "trunk\n")

    def test_merge_trunk_keeps_other_dirty_file_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            g, f = self._trunk_changes(td, extra=True)
            f.write_text("local\n", encoding="utf-8", newline="\n")
            (Path(td) / "a.txt").write_text("my work", encoding="utf-8")
            with mock.patch.object(sync, "fetch_trunk"):
                with self.assertRaises(sync.SyncError):
                    sync.merge_trunk(td)
            self.assertEqual((Path(td) / "a.txt").read_text(encoding="utf-8"), "my work")
            self.assertEqual(f.read_text(encoding="utf-8"), "local\n")

    def test_stage_layers_regenerates_stale_layers_md(self):
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            idx = Path(td) / "MyTradingSys" / "system" / "layer_index.json"
            idx.parent.mkdir(parents=True)
            idx.write_text("{}", encoding="utf-8")
            f = Path(td) / sync.LAYERS_REL
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("old content", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "init layers")

            fake = mock.Mock()
            fake.write = lambda r: f.write_text("regenerated content", encoding="utf-8")
            with mock.patch.dict(sys.modules, {"make_layers_md": fake}):
                self.assertTrue(sync.stage_layers(td))
                self.assertEqual(f.read_text(encoding="utf-8"), "regenerated content")
                self.assertIn("Result:", g("log", "-1", "--format=%B"))
                self.assertEqual(g("status", "--short").strip(), "")

    def test_ship_folds_layers_regen_into_own_commit(self):
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            f = Path(td) / sync.LAYERS_REL
            f.parent.mkdir(parents=True)
            f.write_text("a", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "layers")
            g("update-ref", f"refs/remotes/origin/{sync.TRUNK}", "HEAD")
            (Path(td) / "work.txt").write_text("w", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "own work" + chr(10) * 2 + "Result: w")       # the ship's own commit, not on origin yet
            own_parent = g("rev-parse", "HEAD~1").strip()
            f.write_text("regen", encoding="utf-8")
            self.assertTrue(sync.stage_layers(td, fold=True))
            self.assertEqual(g("rev-parse", "HEAD~1").strip(), own_parent)   # zero extra commits
            self.assertIn("own work", g("log", "-1", "--format=%B"))
            self.assertEqual(g("show", "HEAD:" + sync.LAYERS_REL), "regen")
            self.assertEqual(g("status", "--short").strip(), "")

    def test_stage_layers_fold_keeps_own_commit_when_head_is_on_origin(self):
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            f = Path(td) / sync.LAYERS_REL
            f.parent.mkdir(parents=True)
            f.write_text("a", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "layers")
            g("update-ref", f"refs/remotes/origin/{sync.TRUNK}", "HEAD")
            before = g("rev-parse", "HEAD").strip()
            f.write_text("regen", encoding="utf-8")
            self.assertTrue(sync.stage_layers(td, fold=True))
            self.assertEqual(g("rev-parse", "HEAD~1").strip(), before)       # pushed commit never rewritten

    def test_ship_refuses_staged_uncommitted_files(self):
        with tempfile.TemporaryDirectory() as td:
            g = self.make_repo(td)
            staged_file = Path(td) / "staged.txt"
            staged_file.write_text("staged content", encoding="utf-8")
            g("add", "staged.txt")
            with mock.patch.object(sync, "toplevel", return_value=Path(td)), \
                 mock.patch.object(sync, "run_host_health"), \
                 mock.patch.object(sync, "ship"), \
                 contextlib.redirect_stderr(io.StringIO()) as err:
                rc = sync.main(["ship"])
                self.assertEqual(rc, 1)
                self.assertIn("staged but not committed", err.getvalue())
                self.assertIn("staged.txt", err.getvalue())

    def test_cli_result_commits_before_ship_and_m_without_result_is_refused(self):
        with mock.patch.object(sync, "toplevel", return_value=Path(".")), mock.patch.object(sync, "stage_layers"), mock.patch.object(sync, "run_host_health"),                 mock.patch.object(sync, "ship", return_value=None) as mock_ship,                 mock.patch.object(sync, "commit_pending", return_value=1) as mock_commit:
            self.assertEqual(sync.main(["ship", "--result", "it works", "-m", "subj"]), 0)
            mock_commit.assert_called_once_with(Path("."), "it works", "subj")
            mock_ship.assert_called_once_with(Path("."), release_slug=None, after_slug=None)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(sync.main(["ship", "-m", "subj"]), 1)


class RealTreeGuardTest(unittest.TestCase):
    """CI run 41703965492 step 3k.4: a test ran sync.main(["ship"]) with toplevel mocked to Path(".") (the real checkout) and
    stage_layers unmocked; its `git update-index --refresh` / `git add LAYERS.md` took the real .git/index.lock while another
    shard's git held it ("index.lock: File exists"), so test_fix_ci_flag_keeps_the_fast_gate failed once. Every such test
    must also mock stage_layers, which writes (and can amend) the tree it is given."""
    def test_every_ship_cli_test_on_the_real_checkout_mocks_stage_layers(self):
        lines = Path(__file__).read_text(encoding="utf-8").splitlines()
        bad = [i + 1 for i, line in enumerate(lines)
               if 'toplevel", return_value=Path(".")' in line and '"stage_layers"' not in line and "lines[" not in line]
        self.assertEqual(bad, [], "mock sync.stage_layers next to toplevel=Path('.') on these lines")

    def test_stage_layers_touches_only_the_repo_it_is_given(self):
        seen = []
        with mock.patch.object(sync, "git", side_effect=lambda repo, *a, **k: seen.append(Path(repo)) or mock.Mock(returncode=1, stdout="")):
            sync.stage_layers(Path("some-temp-repo"))
        self.assertTrue(seen)
        self.assertEqual(set(seen), {Path("some-temp-repo")})


class PARALLEL_MainCheckoutRuleTest(unittest.TestCase):
    def test_rule_present(self):
        doc = Path(__file__).resolve().parents[2] / "MyTradingSys" / "system" / "PARALLEL.md"
        text = doc.read_text(encoding="utf-8")
        for needle in ("Main checkout rule", "never edit", "merge --ff-only origin/fast-track"):
            self.assertIn(needle, text)


class GitNetTimeoutTest(unittest.TestCase):
    def test_network_verb_gets_a_deadline_and_a_timeout_line(self):
        seen = {}

        def hang(cmd, **kw):
            seen.update(kw)
            raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
        with mock.patch.object(sync.subprocess, "run", hang), contextlib.redirect_stderr(io.StringIO()) as err:
            r = sync.git(".", "fetch", "--quiet", "origin", "fast-track", check=False)
        self.assertEqual(r.returncode, 124)
        self.assertEqual(seen.get("timeout"), sync.GIT_NET_TIMEOUT_S)
        self.assertEqual(seen["env"].get("GIT_TERMINAL_PROMPT"), "0")
        self.assertIn("TIMEOUT git fetch", err.getvalue())
        with mock.patch.object(sync.subprocess, "run", hang), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(sync.SyncError) as e:
                sync.git(".", "push", "origin", "x")
        self.assertIn("TIMEOUT git push", str(e.exception))


class GateReaderNonUtf8Test(unittest.TestCase):
    def test_gate_reader_survives_non_utf8_bytes(self):
        """subprocess output holding b'ok \x98 end' must not kill the reader thread (UnicodeDecodeError cp1251/utf-8)."""
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "init", "-q", td], check=True)
            sha = subprocess.run(["git", "-C", td, "hash-object", "-w", "--stdin"], input=b"ok \x98 end",
                                 capture_output=True, check=True).stdout.decode().strip()
            r = sync.git(td, "cat-file", "-p", sha)
            self.assertTrue(r.stdout.startswith("ok ") and r.stdout.endswith(" end"))


class ShipStagePrintTest(unittest.TestCase):
    """ship-prints-nothing-until-exit-1111: each stage prints a flushed start line before it runs and an end line with seconds."""

    class Pipe(io.StringIO):
        def __init__(self):
            super().__init__()
            self.flushed = ""

        def flush(self):
            self.flushed = self.getvalue()

    def test_stage_lines_appear_before_exit_and_are_flushed(self):
        ticks = iter([0.0, 12.5, 12.5, 40.0, 40.0, 41.0])
        clock = lambda: next(ticks)
        pipe = self.Pipe()
        seen_during = []
        with mock.patch.object(sys, "stdout", pipe):
            for name in ("merge", "gate", "push"):
                with sync.ship_stage(name, clock=clock):
                    seen_during.append(pipe.flushed)   # what a background shell could already read mid-stage
        self.assertIn("ship stage merge: start", seen_during[0])
        self.assertNotIn("ship stage merge: end", seen_during[0])
        self.assertIn("ship stage gate: start", seen_during[1])
        self.assertIn("ship stage merge: end 12.5s", seen_during[1])
        out = pipe.flushed
        self.assertIn("ship stage gate: end 27.5s", out)
        self.assertIn("ship stage push: end 1.0s", out)

    def test_end_line_printed_when_step_raises(self):
        pipe = self.Pipe()
        with mock.patch.object(sys, "stdout", pipe):
            with self.assertRaises(ValueError):
                with sync.ship_stage("gate"):
                    raise ValueError("red")
        self.assertIn("ship stage gate: end", pipe.flushed)


if __name__ == "__main__":
    unittest.main()

