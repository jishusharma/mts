"""Offline fail-closed tests for auto_trader.py: restart/reset recovery, exchange API errors, respawn/ledger failures,
plan/executor refusals. No exchange, no real subprocess. Each test is proven by mutation_check_auto_trader_failclosed.py
(it breaks one line of a temp copy of auto_trader.py and requires the named test to fail).
Run: python MyTradingSys/execution/test_auto_trader_failclosed.py"""
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402


class Proc:
    def __init__(self, rc=None):
        self.rc = rc
        self.pid = 4242

    def poll(self):
        return self.rc


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.saved = {k: getattr(at, k) for k in ("LOG_PATH", "OPERATOR_ALERTS", "spawn_manager", "exchange_flat",
                                                   "record_ledger", "run")}
        at.LOG_PATH = d / "log.jsonl"
        at.OPERATOR_ALERTS = d / "alerts.log"

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(at, k, v)
        self.tmp.cleanup()

    def events(self):
        if not at.LOG_PATH.exists():
            return []
        return [json.loads(x) for x in at.LOG_PATH.read_text(encoding="utf-8").splitlines()]

    def names(self):
        return [e["event"] for e in self.events()]

    def alerts(self):
        return at.OPERATOR_ALERTS.read_text(encoding="utf-8").splitlines() if at.OPERATOR_ALERTS.exists() else []


class ExchangeFlatTest(Base):
    def _do(self, auth=None, pos=None):
        m = types.ModuleType("deribit_orders")
        m.authenticate = auth or (lambda: "tok")
        m.get_position = pos or (lambda token, ins: {"size": 0})
        return mock.patch.dict(sys.modules, {"deribit_orders": m})

    def test_auth_error_is_unreadable_not_flat(self):
        def auth():
            raise OSError("timeout")
        with self._do(auth=auth):
            self.assertIsNone(at.exchange_flat("jishu_2"))

    def test_position_error_or_garbage_size_is_unreadable_not_flat(self):
        def boom(token, ins):
            raise ValueError("non-JSON")
        with self._do(pos=boom):
            self.assertIsNone(at.exchange_flat())
        with self._do(pos=lambda t, i: {"size": "abc"}):
            self.assertIsNone(at.exchange_flat())

    def test_size_decides_flat_and_short_position_is_open(self):
        with self._do(pos=lambda t, i: {"size": 0}):
            self.assertIs(at.exchange_flat(), True)
        with self._do(pos=lambda t, i: {"size": -3}):
            self.assertIs(at.exchange_flat(), False)
        with self._do(pos=lambda t, i: {}):
            self.assertIs(at.exchange_flat(), True)         # no size key = flat per get_position contract

    def test_account_env_restored_after_error_and_success(self):
        seen = []

        def auth():
            seen.append(os.environ.get("MTS_ACCOUNT"))
            raise OSError("down")
        with mock.patch.dict(os.environ, {"MTS_ACCOUNT": "keep_me"}), self._do(auth=auth):
            at.exchange_flat("jishu_2")
            self.assertEqual(os.environ["MTS_ACCOUNT"], "keep_me")
        self.assertEqual(seen, ["jishu_2"])
        env = {k: v for k, v in os.environ.items() if k != "MTS_ACCOUNT"}
        with mock.patch.dict(os.environ, env, clear=True), self._do():
            at.exchange_flat("jishu_2")
            self.assertNotIn("MTS_ACCOUNT", os.environ)     # was unset before: must be unset again


class SettleSlotFailureTest(Base):
    def slot(self, **kw):
        return {"proc": Proc(rc=3), "plan_id": "px", "source": "s", **kw}

    def test_respawn_exception_keeps_dead_proc_and_retries_next_cycle(self):
        at.exchange_flat = lambda acct=None: False
        calls = []

        def spawn(pid, acct=None):
            calls.append(pid)
            raise OSError("process table full")
        at.spawn_manager = spawn
        s = self.slot()
        dead = s["proc"]
        self.assertFalse(at.settle_slot(s, "jishu_2"))      # no exception escapes, slot stays busy
        self.assertIs(s["proc"], dead)
        self.assertIn("respawn_error", self.names())
        self.assertFalse(at.settle_slot(s, "jishu_2"))
        self.assertEqual(calls, ["px", "px"])               # retried
        self.assertNotIn("trade_closed", self.names())

    def test_unreadable_position_counts_and_logs_throttled(self):
        at.exchange_flat = lambda acct=None: None
        s = self.slot()
        for _ in range(11):
            self.assertFalse(at.settle_slot(s))
        self.assertEqual(s["flat_check_fails"], 11)
        self.assertEqual(self.names().count("manager_exit_unverified"), 2)   # 1st and 11th only
        self.assertNotIn("trade_closed", self.names())

    def test_ledger_failure_does_not_stop_close(self):
        at.exchange_flat = lambda acct=None: True
        m = types.ModuleType("trade_ledger")

        def rec(*a):
            raise OSError("ledger unavailable")
        m.record_closed = rec
        with mock.patch.dict(sys.modules, {"trade_ledger": m}):
            self.assertTrue(at.settle_slot(self.slot(), "jishu_2"))
        names = self.names()
        self.assertIn("trade_closed", names)
        self.assertIn("ledger_error", names)

    def test_running_manager_keeps_slot_and_does_not_touch_exchange(self):
        at.exchange_flat = lambda acct=None: self.fail("exchange read while manager alive")
        self.assertFalse(at.settle_slot(self.slot(proc=Proc(rc=None))))
        self.assertEqual(self.names(), [])


class PlaceRefusalTest(Base):
    def fake_run(self, results):
        calls = []
        it = iter(results)

        def run(cmd, timeout=900, account=None):
            calls.append(cmd)
            return next(it)
        at.run = run
        return calls

    def spawn_forbidden(self):
        at.spawn_manager = lambda *a, **k: self.fail("manager spawned without a confirmed entry")

    SIG = {"plan_args": ["--side", "long"], "executor_args": []}

    def test_plan_refused_nonzero_or_no_saved_id_never_reaches_executor(self):
        self.spawn_forbidden()
        calls = self.fake_run([(1, "SAVED p1 but rc 1")])
        self.assertEqual(at.place(self.SIG, False)["outcome"], "plan_refused")
        self.assertEqual(len(calls), 1)
        calls = self.fake_run([(0, "no id here")])
        self.assertEqual(at.place(self.SIG, False)["outcome"], "plan_refused")
        self.assertEqual(len(calls), 1)

    def test_executor_api_error_is_entry_failed_and_no_manager(self):
        self.spawn_forbidden()
        self.fake_run([(0, "SAVED p1"), (2, "deribit 10009 not_enough_funds")])
        out = at.place(self.SIG, False)
        self.assertEqual(out["outcome"], "entry_failed")
        self.assertNotIn("proc", out)

    def test_no_fill_spawns_no_manager(self):
        self.spawn_forbidden()
        self.fake_run([(0, "SAVED p1"), (0, "limit no_fill after 60s")])
        self.assertEqual(at.place(self.SIG, False)["outcome"], "no_fill")

    def test_dry_run_never_sends_go(self):
        self.spawn_forbidden()
        calls = self.fake_run([(0, "SAVED p1"), (0, "dry")])
        self.assertEqual(at.place(self.SIG, True)["outcome"], "dry_run")
        self.assertNotIn("--go", calls[1])

    def test_confirmed_entry_spawns_manager_with_account(self):
        spawned = []
        at.spawn_manager = lambda pid, acct=None: (spawned.append((pid, acct)), Proc())[1]
        self.fake_run([(0, "SAVED p9"), (0, "filled")])
        out = at.place(self.SIG, False, "jishu_2")
        self.assertEqual(out["outcome"], "entered")
        self.assertEqual(spawned, [("p9", "jishu_2")])


def entered(pid, acct=None, src="s"):
    return {"event": "trade_attempt", "outcome": "entered", "plan_id": pid, "source": src,
            **({"account": acct} if acct else {})}


class RecoveryTest(Base):
    def write(self, *rows, raw=()):
        lines = [json.dumps(r) for r in rows] + list(raw)
        at.LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def procs(*pids_plans):
        return [(pid, f'"C:\\Python\\python.exe" "C:\\x\\position_manager.py" {plan}') for pid, plan in pids_plans]

    def test_reentered_plan_after_close_is_open_again_and_garbage_lines_skipped(self):
        self.write(entered("a"), {"event": "trade_closed", "plan_id": "a"}, entered("a"), entered("b"),
                   {"event": "trade_closed", "plan_id": "b"}, raw=["{not json", ""])
        self.assertEqual([e["plan_id"] for e in at.open_plans_from_log()], ["a"])

    def test_two_live_managers_one_account_adopts_newest_only_and_alerts(self):
        self.write(entered("old", "jishu_2"), entered("new", "jishu_2"))
        active, extra = at.recover_slots(procs=self.procs((11, "old"), (22, "new")), alive_fn=lambda p: True)
        self.assertEqual(active, {})
        self.assertEqual(list(extra), ["jishu_2"])
        self.assertEqual(extra["jishu_2"]["plan_id"], "new")
        self.assertIn("adopt_skipped", self.names())
        self.assertEqual(len(self.alerts()), 1)
        self.assertIn("two live managers", self.alerts()[0])

    def test_older_dead_plan_same_account_is_superseded_with_ledger_row(self):
        ledger = []
        at.record_ledger = lambda *a: ledger.append(a)
        self.write(entered("old", "jishu_2"), entered("new", "jishu_2"))
        _, extra = at.recover_slots(procs=self.procs((22, "new")), alive_fn=lambda p: True)
        self.assertEqual(extra["jishu_2"]["plan_id"], "new")
        closed = [e for e in self.events() if e["event"] == "trade_closed"]
        self.assertEqual([(e["plan_id"], e["note"]) for e in closed], [("old", "superseded_at_restart")])
        self.assertEqual(ledger, [("old", "s", "jishu_2", at.ADOPTED_RC)])
        self.assertEqual(self.alerts(), [])

    def test_dead_manager_slot_with_open_position_is_respawned_not_freed(self):
        self.write(entered("p1"))
        active, _ = at.recover_slots(procs=[], alive_fn=lambda p: False)
        self.assertEqual(active["plan_id"], "p1")
        at.exchange_flat = lambda acct=None: False
        spawned = []
        at.spawn_manager = lambda pid, acct=None: (spawned.append(pid), Proc())[1]
        self.assertFalse(at.settle_slot(active))
        self.assertEqual(spawned, ["p1"])
        self.assertNotIn("trade_closed", self.names())

    def test_dead_manager_slot_with_unreadable_exchange_stays_busy(self):
        self.write(entered("p1"))
        active, _ = at.recover_slots(procs=[], alive_fn=lambda p: False)
        at.exchange_flat = lambda acct=None: None
        at.spawn_manager = lambda *a, **k: self.fail("respawn on unreadable exchange")
        self.assertFalse(at.settle_slot(active))
        self.assertNotIn("trade_closed", self.names())

    def test_manager_pids_exact_plan_token_and_python_only(self):
        procs = self.procs((1, "plan_1"), (2, "plan_10")) + [(3, "notepad position_manager.py plan_1")]
        self.assertEqual(at.manager_pids("plan_1", procs), [1])
        self.assertEqual(at.manager_pids("plan_10", procs), [2])

    def test_process_enumeration_failure_returns_empty_list(self):
        with mock.patch.object(at.subprocess, "run", side_effect=OSError("powershell unavailable")):
            self.assertEqual(at.list_process_cmdlines(), [])
        bad = types.SimpleNamespace(stdout="not json", returncode=0)
        with mock.patch.object(at.subprocess, "run", return_value=bad):
            self.assertEqual(at.list_process_cmdlines(), [])
        one = types.SimpleNamespace(stdout=json.dumps({"ProcessId": 7, "CommandLine": None}), returncode=0)
        with mock.patch.object(at.subprocess, "run", return_value=one):
            self.assertEqual(at.list_process_cmdlines(), [(7, "")])


if __name__ == "__main__":
    unittest.main()
