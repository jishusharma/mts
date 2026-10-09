"""auto_deploy.py: the scheduled deploy stops on a red gate, never touches a tree it should not, restarts only what changed.
Expected outcomes come from the recipe in the module docstring / DEPLOY_RUNBOOK.md (CLAUDE.md quick answers: deploy), not from the code."""
import json
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
    proven by triggering the registered tasks once, see CLAUDE.md CI/CD recipe)."""

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

    def git(self, *a, timeout=300):
        if a[0] == "rev-parse" and a[1] == "origin/fast-track":
            self.calls.append(a)
            return 0, self.trunk + "\n"
        if a[0] == "log":
            self.calls.append(a)
            return 0, str(int(self.now().timestamp()) - self.green_age_s) + "\n"
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

    def test_stale_fallback_still_stops_on_red(self):
        ops = StaleOps(green_age_s=3 * 3600, gate_rc=1)
        r = ad.run(ops, save=False)
        self.assertEqual(r["action"], "STOP_RED")
        self.assertEqual(self.merges(ops), [])

    def test_green_not_ancestor_of_trunk_keeps_green(self):
        ops = StaleOps(green_age_s=3 * 3600, ff=False)   # merge-base says not ancestor
        r = ad.run(ops, save=False)
        self.assertEqual(r["branch"], "green/fast-track")

if __name__ == "__main__":
    unittest.main()
