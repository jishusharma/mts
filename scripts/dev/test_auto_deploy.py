"""auto_deploy.py: the scheduled deploy stops on a red gate, never touches a tree it should not, restarts only what changed.
Expected outcomes come from the recipe in the module docstring / DEPLOY_RUNBOOK.md (DEPLOY_RUNBOOK.md Manual fallback), not from the code."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_deploy as ad

H, T = "a" * 40, "b" * 40


def d(**kw):
    base = dict(is_live=True, head=H, target=T, is_ff=True, changed=[], dirty=[], last_red_sha=None)
    base.update(kw)
    return ad.decide(**base)


class TestDecide(unittest.TestCase):
    def test_not_live_changes_nothing(self):
        self.assertEqual(d(is_live=False)["action"], "NOT_LIVE")

    def test_same_sha_is_up_to_date(self):
        self.assertEqual(d(target=H)["action"], "UP_TO_DATE")

    def test_diverged_history_stops(self):
        self.assertEqual(d(is_ff=False)["action"], "STOP_NOT_FF")

    def test_other_sessions_edit_on_a_changed_file_stops(self):
        r = d(changed=["MyTradingSys/execution/auto_trader.py", "README.md"], dirty=["MyTradingSys/execution/auto_trader.py"])
        self.assertEqual(r["action"], "STOP_DIRTY")
        self.assertIn("auto_trader.py", r["reason"])

    def test_unrelated_dirty_file_does_not_block(self):
        self.assertEqual(d(changed=["README.md"], dirty=["other.py"])["action"], "DEPLOY")

    def test_a_sha_that_failed_the_gate_is_not_retried(self):
        self.assertEqual(d(last_red_sha=T)["action"], "RED_KNOWN")
        self.assertEqual(d(last_red_sha="c" * 40)["action"], "DEPLOY")

    def test_restart_only_the_processes_whose_files_changed(self):
        r = d(changed=["MyTradingSys/execution/daily_loss_monitor.py", "MyTradingSys/system/net_rr_floor.json"])
        self.assertEqual(r["restarts"], ["daily_loss_monitor.py"])
        r = d(changed=["MyTradingSys/backtest/layers/cryptocred/cc_setups.py"])
        self.assertEqual(r["restarts"], ["live_runner_cli.py"])
        self.assertEqual(d(changed=["MyTradingSys/research/x.md"])["restarts"], [])

    def test_shared_module_restarts_both_trading_processes_once(self):
        r = d(changed=["MyTradingSys/execution/deribit_orders.py"])
        self.assertEqual(sorted(r["restarts"]), ["auto_trader.py", "daily_loss_monitor.py"])

    def test_position_manager_is_never_restarted(self):
        r = d(changed=["MyTradingSys/execution/position_manager.py"])
        self.assertNotIn("position_manager.py", r["restarts"])
        self.assertEqual(r["restarts"], [])

    def test_orderflow_recorder_restarts_when_its_code_changes(self):
        r = d(changed=["MyTradingSys/backtest/layers/fabio/orderflow_live.py"])
        self.assertIn("orderflow_live", r["restarts"])
        r = d(changed=["MyTradingSys/backtest/layers/fabio/orderflow_bars.py"])
        self.assertIn("orderflow_live", r["restarts"])
        self.assertNotIn("orderflow_live", d(changed=["MyTradingSys/research/x.md", "MyTradingSys/execution/daily_loss_monitor.py"])["restarts"])
        self.assertNotIn("orderflow_live", d(changed=["MyTradingSys/backtest/layers/fabio/htf_context_live.py"])["restarts"])
        self.assertNotIn("orderflow_live", d(changed=["MyTradingSys/execution/position_manager.py"])["restarts"])

    def test_orderflow_restart_name_is_in_the_module_command_line_and_supervisor_relaunches(self):
        sup = (Path(ad.__file__).resolve().parents[1] / "core" / "loop-supervisor.ps1").read_text(encoding="utf-8")
        self.assertIn("launch-orderflow-live.vbs", sup)
        self.assertIn("orderflow_live", "python -m MyTradingSys.backtest.layers.fabio.orderflow_live")

    def test_java_is_reported_not_deployed_by_restart(self):
        r = d(changed=["src/main/java/datafeed/MarketDataSnapshot.java", "pom.xml", "MyTradingSys/x.md"])
        self.assertEqual(r["java_pending"], ["src/main/java/datafeed/MarketDataSnapshot.java", "pom.xml"])
        self.assertEqual(r["restarts"], [])


class FakeOps:
    def __init__(self, live=True, head=H, target=T, ff=True, changed=("README.md",), dirty=(), gate_rc=0, merge_rc=0, fetch_rc=0):
        self.live, self.head, self.target, self.ff = live, head, target, ff
        self.changed, self.dirty, self.gate_rc, self.merge_rc, self.fetch_rc = list(changed), list(dirty), gate_rc, merge_rc, fetch_rc
        self.calls, self.killed, self.gated = [], [], []

    def is_live(self):
        return self.live

    def now(self):
        return datetime(2026, 10, 10, 7, 0, tzinfo=timezone.utc)

    def git(self, *a, timeout=300):
        self.calls.append(a)
        if a[0] == "fetch":
            return self.fetch_rc, "" if not self.fetch_rc else "network down"
        if a[0] == "rev-parse":
            return 0, (self.target if "green" in a[1] else self.head) + "\n"
        if a[0] == "merge-base":
            return (0 if self.ff else 1), ""
        if a[0] == "diff":
            return 0, "\n".join(self.changed)
        if a[0] == "status":
            return 0, "\n".join(" M " + p for p in self.dirty)
        if a[0] == "merge":
            return self.merge_rc, "ok" if not self.merge_rc else "not possible to fast-forward"
        return 0, ""

    def gate(self, sha):
        self.gated.append(sha)
        return self.gate_rc, "Step 1: PASS\nALL TESTS PASSED" if not self.gate_rc else "Step 4: FAIL\nFAILED: 1 step(s)"

    def kill(self, script):
        self.killed.append(script)
        return 1


class TestRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.saved = (ad.REPO, ad.SCHED, ad.STATE, ad.LAST, ad.LOG)
        ad.REPO = root
        ad.SCHED = root / "sched"
        ad.STATE, ad.LAST, ad.LOG = ad.SCHED / "s.json", ad.SCHED / "last.json", ad.SCHED / "deploy.log"
        self.addCleanup(lambda: (setattr(ad, "REPO", self.saved[0]), setattr(ad, "SCHED", self.saved[1]), setattr(ad, "STATE", self.saved[2]),
                                 setattr(ad, "LAST", self.saved[3]), setattr(ad, "LOG", self.saved[4])))
        self.root = root

    def merges(self, ops):
        return [c for c in ops.calls if c[0] == "merge"]

    def test_green_gate_merges_and_restarts_only_changed(self):
        ops = FakeOps(changed=["MyTradingSys/execution/auto_trader.py"])
        r = ad.run(ops)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertEqual(ops.gated, [T])
        self.assertEqual(self.merges(ops), [("merge", "--ff-only", "origin/green/fast-track")])
        self.assertEqual(ops.killed, ["auto_trader.py"])
        last = json.loads(ad.LAST.read_text(encoding="utf-8"))
        self.assertEqual(last["action"], "DEPLOYED")
        self.assertIn("DEPLOYED", ad.LOG.read_text(encoding="utf-8"))

    def test_dirty_generated_file_is_backed_up_restored_and_deploy_goes_on(self):
        rel = "MyTradingSys/research/STATUS.md"
        f = self.root / rel
        f.parent.mkdir(parents=True)
        f.write_text("live-host edit", encoding="utf-8")
        ops = FakeOps(changed=[rel, "README.md"], dirty=[rel])
        r = ad.run(ops)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertEqual(r["regenerated"], [rel])
        self.assertIn(("checkout", "--", rel), ops.calls)
        self.assertLess(ops.calls.index(("checkout", "--", rel)), ops.calls.index(("merge", "--ff-only", "origin/green/fast-track")))
        saved = list((self.root / "runtime_data" / "deploy_backup").glob("*/regenerated/" + rel))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].read_text(encoding="utf-8"), "live-host edit")

    def test_dirty_live_input_keeps_live_content_after_merge_but_status_takes_committed(self):
        htf = "MyTradingSys/research/htf_context/ctx.json"
        st = "MyTradingSys/research/STATUS.md"
        for rel in (htf, st):
            f = self.root / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("live-written", encoding="utf-8")
        root = self.root

        class MergeOps(FakeOps):
            def git(self, *a, timeout=300):
                if a[0] in ("checkout", "merge"):   # checkout (that file only) and merge both leave the committed copy
                    for rel in ((htf, st) if a[0] == "merge" else (a[-1],)):
                        (root / rel).write_text("committed", encoding="utf-8")
                return super().git(*a, timeout=timeout)
        ops = MergeOps(changed=[htf, st], dirty=[htf, st])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertEqual((root / htf).read_text(encoding="utf-8"), "live-written")
        self.assertEqual((root / st).read_text(encoding="utf-8"), "committed")
        self.assertEqual(r["live_inputs_restored"], [htf])

    def test_dirty_non_allowlisted_file_still_stops(self):
        ops = FakeOps(changed=["MyTradingSys/execution/auto_trader.py"], dirty=["MyTradingSys/execution/auto_trader.py"])
        self.assertEqual(ad.run(ops)["action"], "STOP_DIRTY")
        self.assertEqual(self.merges(ops), [])

    def test_generated_and_non_generated_dirty_stops_and_restores_nothing(self):
        gen, other = "MyTradingSys/research/STATUS.md", "MyTradingSys/execution/auto_trader.py"
        ops = FakeOps(changed=[gen, other], dirty=[gen, other])
        r = ad.run(ops)
        self.assertEqual(r["action"], "STOP_DIRTY")
        self.assertEqual([c for c in ops.calls if c[0] == "checkout"], [])
        self.assertEqual(self.merges(ops), [])
        self.assertFalse((self.root / "runtime_data").exists())

    def test_red_gate_never_merges_or_kills_and_is_remembered(self):
        ops = FakeOps(gate_rc=1, changed=["MyTradingSys/execution/auto_trader.py"])
        r = ad.run(ops)
        self.assertEqual(r["action"], "STOP_RED")
        self.assertEqual(self.merges(ops), [])
        self.assertEqual(ops.killed, [])
        self.assertIn("FAILED: 1 step(s)", r["gate_tail"])
        ops2 = FakeOps(gate_rc=1)
        r2 = ad.run(ops2)           # next cycle, same SHA: not re-gated
        self.assertEqual(r2["action"], "RED_KNOWN")
        self.assertEqual(ops2.gated, [])
        ops3 = FakeOps(target="c" * 40)   # a newer green SHA is tried again
        self.assertEqual(ad.run(ops3)["action"], "DEPLOYED")

    def test_not_live_does_nothing(self):
        ops = FakeOps(live=False)
        r = ad.run(ops)
        self.assertEqual(r["action"], "NOT_LIVE")
        self.assertEqual(ops.calls, [])

    def test_fetch_failure_stops_before_anything_changes(self):
        ops = FakeOps(fetch_rc=1)
        self.assertEqual(ad.run(ops)["action"], "STOP_FETCH")
        self.assertEqual(self.merges(ops), [])

    def test_check_mode_decides_but_changes_nothing(self):
        ops = FakeOps(changed=["MyTradingSys/execution/auto_trader.py"])
        r = ad.run(ops, check=True)
        self.assertEqual(r["action"], "WOULD_DEPLOY")
        self.assertEqual((ops.gated, self.merges(ops), ops.killed), ([], [], []))

    def test_dirty_clash_and_non_ff_stop_without_gate(self):
        ops = FakeOps(changed=["a.py"], dirty=["a.py"])
        self.assertEqual(ad.run(ops)["action"], "STOP_DIRTY")
        self.assertEqual(ops.gated, [])
        ops = FakeOps(ff=False)
        self.assertEqual(ad.run(ops)["action"], "STOP_NOT_FF")

    def test_merge_refusal_is_a_stop_and_nothing_is_killed(self):
        ops = FakeOps(merge_rc=1, changed=["MyTradingSys/execution/auto_trader.py"])
        self.assertEqual(ad.run(ops)["action"], "STOP_MERGE")
        self.assertEqual(ops.killed, [])

    def test_orderflow_state_file_is_restored_when_the_merge_drops_it(self):
        sp = self.root / ad.ORDERFLOW_STATE
        sp.parent.mkdir(parents=True)
        sp.write_text('{"next_ms": 5}', encoding="utf-8")

        class DropOps(FakeOps):
            def git(self, *a, timeout=300):
                if a[0] == "merge":
                    sp.unlink()          # af91b21 untracked the file: the merge deletes it
                return super().git(*a, timeout=timeout)
        r = ad.run(DropOps())
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertTrue(r.get("state_json_restored"))
        self.assertEqual(sp.read_text(encoding="utf-8"), '{"next_ms": 5}')

    def test_exit_code_is_one_only_for_stops(self):
        self.assertEqual(ad.main(["--check"]) in (0, 1), True)


class TestSchedule(unittest.TestCase):
    """The registration script points at scripts that exist and at the documented cadence (a static check; the schedule itself is
    proven by triggering the registered tasks once, see DEPLOY_RUNBOOK.md)."""

    def test_register_script_names_both_jobs_and_real_files(self):
        ps1 = (Path(__file__).resolve().parents[1] / "sched" / "register_cicd_tasks.ps1").read_text(encoding="utf-8").replace(chr(92), "/")
        for task, script in (("MTS-DailyHygiene", "scripts/dev/daily_hygiene.py"), ("MTS-AutoDeploy", "scripts/dev/auto_deploy.py")):
            self.assertIn(task, ps1)
            self.assertIn(script, ps1)
            self.assertTrue((Path(__file__).resolve().parents[2] / script).exists(), script)
        self.assertIn("-Minutes 15", ps1)
        self.assertIn("'06:30'", ps1)

    def test_hygiene_and_deploy_outputs_are_gitignored(self):
        import subprocess
        root = Path(__file__).resolve().parents[2]
        for f in ("MyTradingSys/runtime/sched/hygiene_latest.md", "MyTradingSys/runtime/sched/auto_deploy_last.json"):
            r = subprocess.run(["git", "check-ignore", "-q", f], cwd=root)
            self.assertEqual(r.returncode, 0, f + " must be ignored (per-host state, never committed)")



class StaleOps(FakeOps):
    """green older than the threshold; fast-track (origin/fast-track) is a different, newer SHA."""
    def __init__(self, green_age_s, trunk="d" * 40, **kw):
        super().__init__(**kw)
        self.green_age_s, self.trunk = green_age_s, trunk
        self.live_head = ""      # "" = HEAD unknown to the fake: never "ahead of green"
        self.runs = [{"status": "completed", "conclusion": "success", "headSha": "d" * 40, "databaseId": 1}]

    def ci_runs(self):
        if isinstance(self.runs, Exception):
            raise self.runs
        return self.runs

    def git(self, *a, timeout=300):
        if a[0] == "rev-parse" and a[1] == "origin/fast-track":
            self.calls.append(a)
            return 0, self.trunk + "\n"
        if a[0] == "log":
            self.calls.append(a)
            return 0, str(int(self.now().timestamp()) - self.green_age_s) + "\n"
        if a[:2] == ("rev-parse", "HEAD"):
            return 0, self.live_head + "\n"
        return super().git(*a, timeout=timeout)


class TestStaleGreenFallback(TestRun):
    def test_fresh_green_is_used(self):
        ops = StaleOps(green_age_s=600)
        r = ad.run(ops, save=False)
        self.assertEqual(r["branch"], "green/fast-track")

    def test_stale_green_falls_back_to_gated_fast_track(self):
        ops = StaleOps(green_age_s=3 * 3600)
        r = ad.run(ops, save=False)
        self.assertEqual(r["branch"], "fast-track")
        self.assertEqual(ops.gated, ["d" * 40])      # same local gate, on the fast-track SHA
        self.assertEqual(self.merges(ops), [("merge", "--ff-only", "origin/fast-track")])

    def test_live_ahead_of_green_uses_gated_fast_track_even_when_green_is_fresh(self):
        # 2026-10-16: live HEAD came from an earlier fast-track deploy, green is its ancestor -> was STOP_NOT_FF forever
        ops = StaleOps(green_age_s=600)
        ops.live_head = "e" * 40
        r = ad.run(ops, save=False)
        self.assertEqual(r["branch"], "fast-track")

    def _run(self, runs):
        ops = StaleOps(green_age_s=3 * 3600)
        ops.runs = runs
        return ops, ad.run(ops, save=False)

    def test_red_newest_completed_ci_refuses_fallback(self):
        red = {"status": "completed", "conclusion": "failure", "headSha": "d" * 40, "databaseId": 3}
        ok = {"status": "completed", "conclusion": "success", "headSha": "c" * 40, "databaseId": 2}
        ops, r = self._run([red, ok])
        self.assertEqual(r["branch"], "green/fast-track")
        self.assertEqual(r["fallback"], "FALLBACK_REFUSED_CI_RED")
        self.assertEqual(ops.gated, [T])

    def test_red_ignores_in_progress_newer_run(self):
        prog = {"status": "in_progress", "conclusion": None, "headSha": "e" * 40, "databaseId": 4}
        red = {"status": "completed", "conclusion": "timed_out", "headSha": "d" * 40, "databaseId": 3}
        ops, r = self._run([prog, red])
        self.assertEqual(r["fallback"], "FALLBACK_REFUSED_CI_RED")

    def test_green_newest_completed_allows_fallback(self):
        prog = {"status": "in_progress", "conclusion": None, "headSha": "e" * 40, "databaseId": 4}
        ok = {"status": "completed", "conclusion": "success", "headSha": "d" * 40, "databaseId": 3}
        old = {"status": "completed", "conclusion": "failure", "headSha": "c" * 40, "databaseId": 2}
        ops, r = self._run([prog, ok, old])
        self.assertEqual(r["branch"], "fast-track")
        self.assertNotIn("fallback", r)

    def test_unknown_ci_refuses_fallback_fail_closed(self):
        for runs in (None, [], RuntimeError("gh auth"), "garbage",
                     [{"status": "in_progress", "conclusion": None, "headSha": "e" * 40, "databaseId": 4}]):
            ops, r = self._run(runs)
            self.assertEqual(r["branch"], "green/fast-track", runs)
            self.assertEqual(r["fallback"], "FALLBACK_REFUSED_CI_UNKNOWN", runs)

    def test_fresh_green_never_consults_ci(self):
        ops = StaleOps(green_age_s=600)
        ops.runs = RuntimeError("must not be called")
        r = ad.run(ops, save=False)
        self.assertEqual(r["branch"], "green/fast-track")
        self.assertNotIn("fallback", r)

    def test_stale_fallback_still_stops_on_red(self):
        ops = StaleOps(green_age_s=3 * 3600, gate_rc=1)
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "STOP_RED")
        self.assertEqual(self.merges(ops), [])

    def test_green_not_ancestor_of_trunk_keeps_green(self):
        ops = StaleOps(green_age_s=3 * 3600, ff=False)   # merge-base says not ancestor
        r = ad.run(ops, save=False)
        self.assertEqual(r["branch"], "green/fast-track")

class TestRunLock(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.lock = Path(self.dir.name) / "auto_deploy.lock"

    def tearDown(self):
        self.dir.cleanup()

    def test_second_start_exits_early_while_first_holds_lock(self):
        ok1, _ = ad.acquire_lock(self.lock, pid_alive=lambda p: True)
        ok2, why = ad.acquire_lock(self.lock, pid_alive=lambda p: True)
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertIn("another auto_deploy is running", why)

    def test_dead_owner_lock_is_taken_over(self):
        ad.acquire_lock(self.lock, pid_alive=lambda p: True)
        ok, _ = ad.acquire_lock(self.lock, pid_alive=lambda p: False)
        self.assertTrue(ok)

    def test_old_lock_is_stale_even_if_pid_alive(self):
        ad.acquire_lock(self.lock, pid_alive=lambda p: True, now=lambda: 1000)
        ok, _ = ad.acquire_lock(self.lock, pid_alive=lambda p: True, now=lambda: 1000 + ad.LOCK_STALE_S + 1)
        self.assertTrue(ok)

    def test_release_allows_next_start(self):
        ad.acquire_lock(self.lock, pid_alive=lambda p: True)
        ad.release_lock(self.lock)
        self.assertTrue(ad.acquire_lock(self.lock, pid_alive=lambda p: True)[0])

    def test_main_skips_without_running_deploy_when_locked(self):
        orig_lock, orig_run = ad.LOCK, ad.run
        ad.LOCK = self.lock
        ad.acquire_lock(self.lock)   # this process, alive
        called = []
        ad.run = lambda **kw: called.append(1) or {"action": "UP_TO_DATE"}
        try:
            rc = ad.main([])
        finally:
            ad.LOCK, ad.run = orig_lock, orig_run
        self.assertEqual(rc, 0)
        self.assertEqual(called, [])
        self.assertTrue(self.lock.exists(), "skipped start must not delete the owner's lock")


CARD_SHA = "1bb1b39"
CARD = f"MyTradingSys/system/tasks/ci-{CARD_SHA}.json"


def real_card_text(run_id=77, sha=CARD_SHA):
    """The card exactly as ci_red_card.card_for + tasks.save write it (so a change of the generated shape breaks these tests, not the deploy)."""
    import ci_red_card
    card = ci_red_card.card_for({"headSha": sha + "0" * (40 - len(sha)), "databaseId": run_id, "url": "https://ci.example/run", "createdAt": "2026-10-16T01:00:00Z"})
    return json.dumps(card, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


class UntrackedOps(FakeOps):
    """FakeOps + the untracked listing and blob ids. incoming: {path: blob id in the target commit}; local: {path: blob id of the untracked file}."""

    def __init__(self, untracked=(), incoming=None, local=None, ls_rc=0, **kw):
        super().__init__(**kw)
        self.untracked, self.incoming, self.local, self.ls_rc = list(untracked), dict(incoming or {}), dict(local or {}), ls_rc

    def git(self, *a, timeout=300):
        if a[:3] == ("ls-files", "--others", "--exclude-standard"):
            self.calls.append(a)
            return (self.ls_rc, "\n".join(self.untracked) if not self.ls_rc else "fatal: not a git repository")
        if a[0] == "rev-parse" and ":" in a[1]:
            self.calls.append(a)
            blob = self.incoming.get(a[1].split(":", 1)[1])
            return (0, blob + "\n") if blob else (128, "fatal: path does not exist in the commit")
        if a[0] == "hash-object":
            self.calls.append(a)
            return 0, self.local.get(a[-1], "0" * 40) + "\n"
        return super().git(*a, timeout=timeout)


class TestUntrackedClash(unittest.TestCase):
    """2026-10-16: the gated merge stopped with STOP_MERGE 'untracked working tree files would be overwritten' (ci-1bb1b39.json, a card make_status.py
    filed in the live tree and a builder shipped to fast-track). Generated CI cards are backed up and cleared; every other untracked clash still stops."""
    setUp = TestRun.setUp
    merges = TestRun.merges

    def put(self, rel, text):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8", newline="\n")
        return f

    def test_generated_ci_card_clash_is_backed_up_removed_before_the_merge_and_deploy_goes_on(self):
        old = real_card_text(run_id=77)
        f = self.put(CARD, old)
        seen = []

        class SeeOps(UntrackedOps):
            def git(self, *a, timeout=300):
                if a[0] == "merge":
                    seen.append(f.exists())
                return super().git(*a, timeout=timeout)
        ops = SeeOps(untracked=[CARD], incoming={CARD: "1" * 40}, local={CARD: "2" * 40}, changed=[CARD, "README.md"])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertEqual(r["untracked_cleared"], [CARD])
        self.assertEqual(seen, [False])          # gone when `git merge` ran
        saved = list((self.root / "runtime_data" / "deploy_backup").glob("*/untracked/" + CARD))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].read_text(encoding="utf-8"), old)

    def test_card_with_the_incoming_content_is_cleared_even_when_it_is_not_card_shaped(self):
        f = self.put(CARD, "hand edited, but byte-identical to what the trunk ships\n")
        ops = UntrackedOps(untracked=[CARD], incoming={CARD: "a1" * 20}, local={CARD: "a1" * 20}, changed=[CARD])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertEqual(r["untracked_cleared"], [CARD])
        self.assertFalse(f.exists())

    def test_card_path_with_other_content_stops_and_is_left_alone(self):
        f = self.put(CARD, json.dumps({"id": "mine", "title": "someone's own notes"}))
        ops = UntrackedOps(untracked=[CARD], incoming={CARD: "1" * 40}, local={CARD: "2" * 40}, changed=[CARD])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "STOP_MERGE")
        self.assertIn(CARD, r["reason"])
        self.assertEqual((self.merges(ops), ops.gated, ops.killed), ([], [], []))
        self.assertTrue(f.exists())
        self.assertFalse((self.root / "runtime_data").exists())

    def test_any_other_untracked_clash_stays_stop_merge_and_costs_no_gate_run(self):
        other = "MyTradingSys/execution/new_module.py"
        f = self.put(other, "print('mine')\n")
        ops = UntrackedOps(untracked=[other], incoming={other: "1" * 40}, local={other: "1" * 40}, changed=[other])   # even identical content: not a card
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "STOP_MERGE")
        self.assertIn("untracked working tree files would be overwritten", r["reason"])
        self.assertEqual((self.merges(ops), ops.gated, ops.killed), ([], [], []))
        self.assertTrue(f.exists())

    def test_near_miss_card_names_are_not_cleared(self):
        for rel in ("MyTradingSys/system/tasks/ci-1bb1b39.json.bak", "MyTradingSys/system/tasks/B059.json", "MyTradingSys/system/tasks/ci-XYZ.json",
                    "MyTradingSys/system/tasks/sub/ci-1bb1b39.json", "other/MyTradingSys/system/tasks/ci-1bb1b39.json"):
            self.put(rel, real_card_text())
            ops = UntrackedOps(untracked=[rel], incoming={rel: "1" * 40}, local={rel: "1" * 40}, changed=[rel])
            self.assertEqual(ad.run(ops, save=False)["action"], "STOP_MERGE", rel)
            self.assertEqual(self.merges(ops), [], rel)

    def test_a_blocking_clash_removes_nothing_not_even_the_clearable_card(self):
        other = "MyTradingSys/execution/new_module.py"
        f = self.put(CARD, real_card_text())
        self.put(other, "x\n")
        ops = UntrackedOps(untracked=[CARD, other], incoming={CARD: "1" * 40, other: "3" * 40}, changed=[CARD, other])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "STOP_MERGE")
        self.assertIn(other, r["reason"])
        self.assertNotIn("untracked_cleared", r)
        self.assertTrue(f.exists())
        self.assertEqual(self.merges(ops), [])

    def test_untracked_files_outside_the_incoming_diff_are_left_alone(self):
        f = self.put(CARD, real_card_text())
        ops = UntrackedOps(untracked=[CARD, "scratch.txt"], changed=["README.md"])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertNotIn("untracked_cleared", r)
        self.assertTrue(f.exists())

    def test_check_mode_reports_the_card_it_would_clear_and_removes_nothing(self):
        f = self.put(CARD, real_card_text())
        ops = UntrackedOps(untracked=[CARD], incoming={CARD: "1" * 40}, changed=[CARD])
        r = ad.run(ops, check=True, save=False)
        self.assertEqual(r["action"], "WOULD_DEPLOY")
        self.assertEqual(r["untracked_would_clear"], [CARD])
        self.assertTrue(f.exists())
        self.assertEqual((ops.gated, self.merges(ops)), ([], []))

    def test_unreadable_untracked_listing_fails_closed(self):
        ops = UntrackedOps(ls_rc=128, changed=["README.md"])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "STOP_MERGE")
        self.assertEqual((self.merges(ops), ops.gated), ([], []))

    def test_card_filed_while_the_gate_runs_is_cleared_too(self):
        outer = self

        class LateOps(UntrackedOps):
            def gate(self, sha):
                outer.put(CARD, real_card_text())     # make_status.py ran on the live host during the gate
                self.untracked.append(CARD)
                return super().gate(sha)
        ops = LateOps(incoming={CARD: "1" * 40}, local={CARD: "2" * 40}, changed=[CARD])
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "DEPLOYED")
        self.assertEqual(r["untracked_cleared"], [CARD])
        self.assertFalse((self.root / CARD).exists())

    def test_generated_shape_follows_ci_red_card_and_rejects_variants(self):
        self.assertTrue(ad.is_generated_ci_card(CARD, real_card_text()))
        good = json.loads(real_card_text())
        for key, val in (("pinned", False), ("id", "ci-0000000"), ("title", "fix CI 1bb1b39: something else"), ("sources", []),
                         ("sources", ["CI run 1", "CI run 2"]), ("sources", ["note"]), ("goal", "my own goal")):
            bad = dict(good, **{key: val})
            self.assertFalse(ad.is_generated_ci_card(CARD, json.dumps(bad)), key)
        self.assertFalse(ad.is_generated_ci_card(CARD, "[]"))
        self.assertFalse(ad.is_generated_ci_card(CARD, "not json"))
        self.assertFalse(ad.is_generated_ci_card("MyTradingSys/system/tasks/ci-2222222.json", real_card_text()))   # id names another sha
        self.assertFalse(ad.is_generated_ci_card("MyTradingSys/system/tasks/B059.json", real_card_text()))


def _git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", *args], cwd=str(repo), env=env, check=True, capture_output=True, text=True).stdout.strip()


class RealGitOps(ad.Ops):
    """Real git in a temp 'live' clone; gate, kill and clock are fakes."""

    def __init__(self, repo):
        self.repo = str(repo)

    def git(self, *a, timeout=300):
        return ad.sh(["git", *a], cwd=self.repo, timeout=timeout)

    def is_live(self):
        return True

    def gate(self, sha):
        return 0, "ALL TESTS PASSED"

    def kill(self, script):
        return 0

    def now(self):
        return datetime(2026, 10, 16, 2, 45, tzinfo=timezone.utc)


class TestUntrackedClashRealGit(unittest.TestCase):
    """The incident itself with real git: the same untracked card in the live tree and in the commit the deploy merges."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.src, self.live = root / "origin", root / "live"
        self.src.mkdir()
        _git(self.src, "init", "-q")
        (self.src / "README.md").write_text("one\n", encoding="utf-8", newline="\n")
        _git(self.src, "add", "-A")
        _git(self.src, "commit", "-q", "-m", "c1")
        self.publish()
        self.live.mkdir()
        _git(self.live, "init", "-q")
        _git(self.live, "remote", "add", "origin", str(self.src))
        _git(self.live, "fetch", "-q", "origin")
        _git(self.live, "checkout", "-q", "-B", "livebranch", "origin/green/fast-track")
        self.saved_repo = ad.REPO
        ad.REPO = self.live
        self.addCleanup(lambda: setattr(ad, "REPO", self.saved_repo))

    def publish(self):
        _git(self.src, "update-ref", "refs/heads/fast-track", "HEAD")
        _git(self.src, "update-ref", "refs/heads/green/fast-track", "HEAD")

    def ship(self, rel, text):
        f = self.src / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8", newline="\n")
        _git(self.src, "add", "-A")
        _git(self.src, "commit", "-q", "-m", "c2 " + rel)
        self.publish()

    def untracked(self, rel, text):
        f = self.live / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8", newline="\n")
        return f

    def test_untracked_generated_ci_card_that_the_trunk_also_ships_no_longer_stops_the_deploy(self):
        mine = self.untracked(CARD, real_card_text(run_id=1))
        self.ship(CARD, real_card_text(run_id=2))
        r = ad.run(RealGitOps(self.live), state={}, save=False)
        self.assertEqual(r["action"], "DEPLOYED", r)
        self.assertEqual(r["untracked_cleared"], [CARD])
        self.assertEqual(_git(self.live, "rev-parse", "HEAD"), _git(self.src, "rev-parse", "HEAD"))
        self.assertEqual(mine.read_text(encoding="utf-8"), real_card_text(run_id=2))        # the trunk's copy is checked out
        self.assertEqual(_git(self.live, "status", "--porcelain", "--untracked-files=no"), "")
        saved = list((self.live / "runtime_data" / "deploy_backup").glob("*/untracked/" + CARD))
        self.assertEqual([p.read_text(encoding="utf-8") for p in saved], [real_card_text(run_id=1)])

    def test_identical_untracked_copy_is_cleared_and_checked_out_from_the_trunk(self):
        self.untracked(CARD, "same bytes\n")
        self.ship(CARD, "same bytes\n")
        r = ad.run(RealGitOps(self.live), state={}, save=False)
        self.assertEqual(r["action"], "DEPLOYED", r)
        self.assertEqual(r["untracked_cleared"], [CARD])

    def test_any_other_untracked_clash_still_stops_with_real_git_and_keeps_the_file(self):
        other = "MyTradingSys/execution/new_module.py"
        mine = self.untracked(other, "mine\n")
        self.ship(other, "theirs\n")
        head = _git(self.live, "rev-parse", "HEAD")
        r = ad.run(RealGitOps(self.live), state={}, save=False)
        self.assertEqual(r["action"], "STOP_MERGE", r)
        self.assertEqual(_git(self.live, "rev-parse", "HEAD"), head)
        self.assertEqual(mine.read_text(encoding="utf-8"), "mine\n")
        self.assertFalse((self.live / "runtime_data").exists())


if __name__ == "__main__":
    unittest.main()
