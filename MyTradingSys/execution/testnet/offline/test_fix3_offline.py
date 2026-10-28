"""
Offline tests for FIX3 (2026-09-28): one test (or more) per fixed finding of
review/ADVERSARIAL_REVIEW_FT2.md - C1 C2 C3 H1 H2 H3 H4 H5 H6 M1 M3 M5 M6 -
plus the 13 mutation survivors of review/MUTATION_REPORT_FT2.md (imported
from test_fix3_mutants_offline).
FIX4 (2026-09-28) supersedes part of M1: a well-formed PAST-dated
HALT_DAILY_LOSS used to be non-blocking (M1's own contract); FIX4 M2 makes
existence block regardless of date - see test_M2_valid_past_date_still_blocks
below (was test_M1_valid_past_date_does_not_block).

Runs against the STAGED code:
  python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_fix3_offline
No network, no secrets. Every HALT/state path is a temp file or the sandbox
copy next to the staged modules - never the repo's execution/ dir.
"""
import sys
sys.dont_write_bytecode = True

import io
import json
import os
import shutil
import socket
import tempfile
import types
import unittest
import urllib.error
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import deribit_orders as do
import journal
import executor
import position_manager as pm
import kill_switch
import daily_loss_monitor as dlm
from test_gh_executor_offline import FakeExchange, PATCHED_NAMES, _compiled
from test_fix3_mutants_offline import *  # noqa: F401,F403 - the 13 mutation-survivor tests

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


class _ExchangeCase(unittest.TestCase):
    """Patches deribit_orders with a FakeExchange that records every call in
    order; HALT goes to the sandbox copy and is cleared around each test."""

    def setUp(self):
        self.fake = FakeExchange()
        self.calls = []
        self.inject = {}  # name -> exception (or callable(*a) returning one / None) raised instead of the call
        self._orig = {n: getattr(do, n) for n in PATCHED_NAMES}
        for n in PATCHED_NAMES:
            setattr(do, n, self._wrap(n, getattr(self.fake, n)))
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        for p in (executor.HALT_PATH, pm.HALT_PATH):
            p.unlink(missing_ok=True)

    def tearDown(self):
        for n, fn in self._orig.items():
            setattr(do, n, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        for p in (executor.HALT_PATH, pm.HALT_PATH):
            p.unlink(missing_ok=True)

    def _wrap(self, name, fn):
        def w(*a, **k):
            self.calls.append((name, a[1:] if a else a))
            f = self.inject.get(name)
            if f is not None:
                ex = f(*a) if callable(f) and not isinstance(f, BaseException) else f
                if ex is not None:
                    raise ex
            return fn(*a, **k)
        return w

    def names(self):
        return [c[0] for c in self.calls]

    def live_stops(self):
        return [o for o in self.fake.orders.values()
                if o["order_type"] == "stop_market" and o["order_state"] == "untriggered"]


# ---------------------------------------------------------------- C1 / R-DO
class C1TransportErrors(unittest.TestCase):
    def setUp(self):
        self._post, self._sleep = do._post, do.time.sleep
        do.time.sleep = lambda s: None
        self.n = 0

    def tearDown(self):
        do._post, do.time.sleep = self._post, self._sleep

    def _raise(self, ex):
        def post(method, params, token=None):
            self.n += 1
            raise ex
        do._post = post

    def test_C1_timeout_on_buy_is_order_state_unknown_no_retry(self):
        for ex in (socket.timeout("timed out"), ConnectionResetError("reset"),
                   urllib.error.URLError("dns"), RuntimeError("private/buy: HTTP 502"), ValueError("bad json")):
            self.n = 0
            self._raise(ex)
            with self.assertRaises(do.OrderStateUnknown, msg=repr(ex)):
                do._call("private/buy", {}, "tok", creates_order=True, params_label="p:entry_1")
            self.assertEqual(self.n, 1, f"order-creating call must never be resent after {ex!r}")

    def test_C1_timeout_on_read_retries_then_deribit_error(self):
        self._raise(socket.timeout("timed out"))
        with self.assertRaises(do.DeribitError) as ctx:
            do._call("private/get_position", {}, "tok")
        self.assertNotIsInstance(ctx.exception, do.OrderStateUnknown)
        self.assertEqual(self.n, do.MAX_RETRIES + 1)

    def test_C1_reauth_failure_is_deribit_error(self):
        do._post = lambda m, p, token=None: {"error": {"code": 13009}}
        with mock.patch.object(do, "authenticate", side_effect=RuntimeError("MISSING secret")):
            with self.assertRaises(do.DeribitError):
                do._call("private/get_position", {}, "tok")


# ---------------------------------------------------------------- C2
class C2PollReadFailure(_ExchangeCase):
    def test_C2_poll_read_failure_after_fill_flattens(self):
        self.inject["get_order_state"] = do.DeribitError("private/get_order_state", {"code": 10028})
        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(_compiled("fx_c2"))
        self.assertIn("flattened + halted", str(ctx.exception))
        self.assertEqual(self.fake.pos, 0)
        self.assertIn("close_position", self.names())

    def test_C2_raw_timeout_after_fill_flattens(self):
        # a non-DeribitError from a fake/transport layer is caught too
        self.inject["get_order_state"] = TimeoutError("timed out")
        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(_compiled("fx_c2b"))
        self.assertEqual(self.fake.pos, 0)

    def test_C1_R1_raw_timeout_on_entry_create_that_filled(self):
        def filled_then_timeout(*a):
            self.fake.pos += 100
            return TimeoutError("response lost")
        self.inject["buy"] = filled_then_timeout
        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(_compiled("fx_r1"))
        self.assertEqual(self.fake.pos, 0, "position must be flattened")


# ---------------------------------------------------------------- C3 / H1 / M5 (executor)
class C3ExecutorFlattenOrder(_ExchangeCase):
    def _run_to_fail_closed(self, pid):
        # fill + stop, then the verify step sees a mismatched position -> fail_closed
        real_gp = self.fake.get_position
        n = {"i": 0}

        def gp(token, instrument="BTC-PERPETUAL"):
            n["i"] += 1
            r = real_gp(token, instrument)
            return {"size": 999} if n["i"] == 2 else r  # 1 = R8 preflight, 2 = verify
        setattr(do, "get_position", self._wrap("get_position", gp))
        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(_compiled(pid))
        return str(ctx.exception)

    def test_C3_stop_cancelled_only_after_close(self):
        msg = self._run_to_fail_closed("fx_c3")
        self.assertIn("flattened + halted", msg)
        names = self.names()
        i_close = names.index("close_position")
        stop_cancels = [i for i, (n, a) in enumerate(self.calls)
                        if (n == "cancel_by_label" and a and str(a[0]).endswith(":stop_order"))
                        or (n == "cancel" and a and self.fake.orders.get(a[0], {}).get("order_type") == "stop_market")]
        self.assertTrue(stop_cancels, "stop must be cancelled once flat")
        self.assertTrue(all(i > i_close for i in stop_cancels), f"stop cancelled before close: {self.calls}")

    def test_C3_close_fails_stop_kept(self):
        self.inject["close_position"] = do.OrderStateUnknown("private/close_position", "x", 10050)
        msg = self._run_to_fail_closed("fx_c3b")
        self.assertIn("FAIL-CLOSED ITSELF FAILED", msg)
        self.assertEqual(self.fake.pos, 100)
        self.assertEqual(len(self.live_stops()), 1, "the protective stop must survive a failed close")
        self.assertEqual(self.live_stops()[0]["amount"], 100)

    def test_H1_reset_in_cancel_sweep_does_not_skip_flatten(self):
        self.inject["cancel_by_label"] = ConnectionResetError("reset")
        self.inject["cancel"] = ConnectionResetError("reset")
        msg = self._run_to_fail_closed("fx_h1")
        self.assertIn("flattened + halted", msg)
        self.assertIn("close_position", self.names())
        self.assertEqual(self.fake.pos, 0)

    def test_M5_fail_closed_writes_manual_halt(self):
        self._run_to_fail_closed("fx_m5")
        self.assertTrue(executor.HALT_PATH.exists(), "fail_closed must leave execution/HALT")
        self.assertIn("fx_m5", executor.HALT_PATH.read_text(encoding="utf-8"))
        # and the next plan is refused by preflight
        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(_compiled("fx_m5_next"))
        self.assertIn("HALT", str(ctx.exception))

    def test_M5_halt_written_even_if_flatten_fails(self):
        self.inject["close_position"] = TimeoutError("t")
        self._run_to_fail_closed("fx_m5b")
        self.assertTrue(executor.HALT_PATH.exists())


# ---------------------------------------------------------------- C3 / H1 / H5 / M5 (position_manager)
class _Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def time(self):
        return self.t

    def sleep(self, s):
        self.t += s

    def monotonic(self):
        return self.t


class PositionManagerFixes(_ExchangeCase):
    def setUp(self):
        super().setUp()
        executor.execute_plan(_compiled("fx_pm"))          # fill 100 + stop 100, journaled
        self.stop_id = self.live_stops()[0]["order_id"]
        self.calls.clear()
        self.clock = _Clock()
        self._p = mock.patch.object(pm, "time", self.clock)
        self._p.start()

    def tearDown(self):
        self._p.stop()
        super().tearDown()

    def _stop_read_fails(self):
        real = self.fake.get_order_state

        def gos(token, oid):
            if oid == self.stop_id:
                raise do.DeribitError("private/get_order_state", {"code": 10028})
            return real(token, oid)
        setattr(do, "get_order_state", self._wrap("get_order_state", gos))

    def test_H5_read_failure_never_replaces_stop(self):
        self._stop_read_fails()
        r = pm.manage("fx_pm", once=True, token="tok")
        self.assertEqual(r["status"], "managing")
        self.assertNotIn("stop_market", self.names())
        self.assertEqual(len(self.live_stops()), 1)

    def test_H5_consecutive_read_failures_flatten_after_bound_keeping_stop_until_flat(self):
        self._stop_read_fails()
        with self.assertRaises(pm.ManagerHalted) as ctx:
            pm.manage("fx_pm", max_seconds=60, token="tok")
        self.assertIn("unreadable", str(ctx.exception))
        self.assertNotIn("stop_market", self.names(), "never re-place on a read failure")
        self.assertEqual(self.fake.pos, 0)
        names = self.names()
        self.assertLess(names.index("close_position"),
                        max(i for i, n in enumerate(names) if n in ("cancel", "cancel_by_label")))

    def test_H5_short_read_blip_no_halt(self):
        real = self.fake.get_order_state
        n = {"i": 0}

        def gos(token, oid):
            if oid == self.stop_id:
                n["i"] += 1
                if n["i"] == 1:
                    raise do.DeribitError("private/get_order_state", {"code": 10028})
            return real(token, oid)
        setattr(do, "get_order_state", self._wrap("get_order_state", gos))
        r = pm.manage("fx_pm", max_seconds=20, token="tok")
        self.assertEqual(r["status"], "managing")
        self.assertNotIn("close_position", self.names())

    def _force_flatten(self):
        # a sign flip forces flatten_halt deterministically
        self.fake.pos = -100
        with self.assertRaises(pm.ManagerHalted) as ctx:
            pm.manage("fx_pm", once=True, token="tok")
        return str(ctx.exception)

    def test_C3_pm_close_fails_stop_kept(self):
        self.inject["close_position"] = TimeoutError("t")
        msg = self._force_flatten()
        self.assertIn("FLATTEN ITSELF FAILED", msg)
        self.assertEqual(len(self.live_stops()), 1, "stop must survive a failed flatten")

    def test_C3_pm_stop_cancelled_after_close(self):
        msg = self._force_flatten()
        self.assertIn("flattened + halted", msg)
        self.assertEqual(self.fake.pos, 0)
        i_close = self.names().index("close_position")
        stop_ops = [i for i, (n, a) in enumerate(self.calls)
                    if (n == "cancel" and a and a[0] == self.stop_id)
                    or (n == "cancel_by_label" and a and str(a[0]).endswith(":stop_order"))]
        self.assertTrue(stop_ops and all(i > i_close for i in stop_ops), self.calls)

    def test_H1_pm_reset_in_cancel_does_not_skip_flatten(self):
        self.inject["cancel_by_label"] = ConnectionResetError("reset")
        self.inject["cancel"] = ConnectionResetError("reset")
        msg = self._force_flatten()
        self.assertIn("flattened + halted", msg)
        self.assertEqual(self.fake.pos, 0)

    def test_M5_pm_flatten_writes_manual_halt(self):
        self._force_flatten()
        self.assertTrue(pm.HALT_PATH.exists())


# ---------------------------------------------------------------- H2 (kill_switch)
class _KillClient:
    def __init__(self, fail_positions=False):
        self.fail_positions = fail_positions
        self.orders = {"BTC-PERPETUAL": [{"order_id": "A"}]}
        self.cancelled, self.closed = [], []

    def get_positions(self, token, currency="BTC", kind="future"):
        if self.fail_positions:
            raise TimeoutError("timed out")
        return []

    def get_open_orders(self, token, instrument_name, type_="all"):
        return list(self.orders.get(instrument_name, []))

    def cancel(self, token, oid):
        self.cancelled.append(oid)

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.closed.append(instrument_name)


class H2KillSwitch(unittest.TestCase):
    def test_H2_get_positions_failure_still_cancels_btc_perp(self):
        c = _KillClient(fail_positions=True)
        r = kill_switch.kill_all(c, "tok")
        self.assertEqual(c.cancelled, ["A"])
        self.assertFalse(r["ok"])

    def test_H2_cli_writes_halt_even_if_authenticate_fails(self):
        tmp = Path(tempfile.mkdtemp())
        halt = tmp / "HALT"
        fake_do = types.SimpleNamespace(authenticate=mock.Mock(side_effect=RuntimeError("auth down")))
        try:
            with mock.patch.dict(sys.modules, {"deribit_orders": fake_do}), redirect_stdout(io.StringIO()):
                rc = kill_switch.main(["--confirm", "KILL"], halt_path=halt)
            self.assertEqual(rc, 1)
            self.assertTrue(halt.exists(), "HALT must be written before anything that can fail")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- H3 / H4 (daily_loss_monitor)
class _DLClient:
    def __init__(self, equity, mark=80000.0):
        self.equity, self.mark = equity, mark

    def get_account_summary(self, token, currency="BTC"):
        return {"equity": self.equity}

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": self.mark}


class H3H4DailyLossMonitor(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.state = self.tmp / "state.json"
        self.halt = self.tmp / "HALT_DAILY_LOSS"
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

    def test_H3_kill_all_failure_still_writes_halt(self):
        dlm.save_state({"date": TODAY, "day_start_equity": 1.0, "breached_today": False}, self.state)
        with mock.patch.object(dlm.kill_switch, "kill_all", side_effect=TimeoutError("down")):
            r = dlm.run_once(_DLClient(0.99), "tok", cap_usd=-100, state_path=self.state, halt_path=self.halt)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual(json.loads(self.halt.read_text(encoding="utf-8"))["date"], TODAY)
        self.assertTrue(json.loads(self.state.read_text(encoding="utf-8"))["breached_today"])

    def test_H3_halt_written_before_kill_all(self):
        dlm.save_state({"date": TODAY, "day_start_equity": 1.0, "breached_today": False}, self.state)
        seen = {}

        def ka(*a, **k):
            seen["halt_exists"] = self.halt.exists()
            return {"cancelled_orders": [], "closed_positions": [], "errors": [], "ok": True}
        with mock.patch.object(dlm.kill_switch, "kill_all", side_effect=ka):
            dlm.run_once(_DLClient(0.99), "tok", cap_usd=-100, state_path=self.state, halt_path=self.halt)
        self.assertTrue(seen["halt_exists"])

    def test_H4_torn_state_fails_closed_no_rebaseline(self):
        for torn in ('{"date": "' + TODAY + '", "day_start_eq', b"\xff\xfe\x00garbage", "[1, 2]"):
            self.halt.unlink(missing_ok=True)
            if isinstance(torn, bytes):
                self.state.write_bytes(torn)
            else:
                self.state.write_text(torn, encoding="utf-8")
            before = self.state.read_bytes()
            with mock.patch.object(dlm.kill_switch, "kill_all") as ka:
                r = dlm.run_once(_DLClient(0.99), "tok", cap_usd=-100, state_path=self.state,
                                 halt_path=self.halt)
            self.assertFalse(r["ok"], torn)
            self.assertTrue(self.halt.exists(), torn)
            self.assertEqual(self.state.read_bytes(), before, "unreadable state must be left for the operator")
            ka.assert_not_called()

    def test_H4_missing_state_still_baselines(self):
        r = dlm.run_once(_DLClient(1.0), "tok", cap_usd=-100, state_path=self.state, halt_path=self.halt)
        self.assertTrue(r["ok"])
        self.assertEqual(r["state"]["day_start_equity"], 1.0)

    def test_H4_save_state_is_atomic(self):
        with mock.patch.object(dlm.os, "replace", wraps=os.replace) as rep:
            dlm.save_state({"date": TODAY}, self.state)
        rep.assert_called_once()
        self.assertEqual(json.loads(self.state.read_text(encoding="utf-8")), {"date": TODAY})
        self.assertEqual([p.name for p in self.tmp.iterdir()], ["state.json"], "no temp file left behind")


# ---------------------------------------------------------------- H6 (static, testnet suites)
_REPO = os.environ.get("MTS_REPO_ROOT")


@unittest.skipUnless(_REPO, "set MTS_REPO_ROOT to check the testnet suite sources (not in the staged sandbox)")
class H6SuitesUseTempPaths(unittest.TestCase):
    def _src(self, rel):
        p = Path(_REPO) / "MyTradingSys/execution/testnet" / rel
        new = p.with_name(p.name + ".new")
        return (new if new.exists() else p).read_text(encoding="utf-8")

    def test_H6_ft2_suite_never_unlinks_real_halt_or_state(self):
        s = self._src("run_testnet_suite_ft2.py")
        self.assertNotIn("dlm.HALT_PATH", s)
        self.assertNotIn("dlm.STATE_PATH", s)
        self.assertIn("state_path=state_path", s)

    def test_H6_base_helpers_redirect_halt_and_refuse_if_present(self):
        s = self._src("run_testnet_suite.py")
        self.assertIn("SUITE_TMP", s)
        self.assertIn("REFUSED", s)
        self.assertLess(s.index("ex.HALT_PATH = "), s.index("\nfor n, f in [("))


# ---------------------------------------------------------------- M1 / M3 (HALT_DAILY_LOSS parsing)
class M1M3HaltDailyLossParsing(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.halt = self.tmp / "HALT"
        self.hdl = self.tmp / "HALT_DAILY_LOSS"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _reasons(self):
        with redirect_stdout(io.StringIO()):
            return executor._check_halt_files(self.halt, self.hdl)

    def test_M1_garbage_dates_block(self):
        for d in (20260928, "2026/09/28", "", "2026-09-28 ", None, "9999-12-31", [TODAY]):
            self.hdl.write_text(json.dumps({"date": d, "reason": "x"}), encoding="utf-8")
            self.assertTrue(self._reasons(), f"date {d!r} must block")

    def test_M1_non_object_json_blocks(self):
        for body in ("[]", "1", '"x"', "null"):
            self.hdl.write_text(body, encoding="utf-8")
            self.assertTrue(self._reasons(), body)

    def test_M2_valid_past_date_still_blocks(self):
        # FIX4 M2 supersedes the FIX3 M1 contract: existence blocks, whatever
        # the date - only an operator deleting the file resumes trading.
        # (was test_M1_valid_past_date_does_not_block, which asserted the
        # opposite - a well-formed past date used to be non-blocking.)
        y = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        self.hdl.write_text(json.dumps({"date": y, "reason": "x"}), encoding="utf-8")
        reasons = self._reasons()
        self.assertTrue(any(f"HALT_DAILY_LOSS from {y} still present" in r for r in reasons), reasons)

    def test_M3_utf16_and_bom_are_read_as_active_halt(self):
        body = json.dumps({"date": TODAY, "reason": "cap breached"})
        for enc in ("utf-16", "utf-16-le", "utf-8-sig"):
            self.hdl.write_bytes(body.encode(enc))
            r = self._reasons()
            self.assertTrue(any("daily loss halt active" in x and "cap breached" in x for x in r), (enc, r))

    def test_M3_undecodable_blocks_cleanly(self):
        self.hdl.write_bytes(b"\x80\x81\xfe")
        r = self._reasons()
        self.assertTrue(any("unreadable/malformed" in x for x in r), r)


# ---------------------------------------------------------------- M6 (plan_id)
class M6PlanId(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _refused(self, pid):
        r = executor.preflight(_compiled(pid), halt_path=self.tmp / "H", halt_daily_loss_path=self.tmp / "D")
        return any(x.startswith("M6") for x in r)

    def test_M6_bad_plan_ids_refused(self):
        for pid in ("p" * 25, "a:b", "a b", "", "é", None, 12, "x/y"):
            self.assertTrue(self._refused(pid), repr(pid))

    def test_M6_good_plan_ids_accepted(self):
        for pid in ("p" * 24, "c1_mkt_long_abc123", "A-z_0"):
            self.assertFalse(self._refused(pid), pid)

    def test_M6_xlabel_never_truncates(self):
        with self.assertRaises(executor.ExecutionHalted):
            executor._xlabel("p" * 60, "entry_rung_10")
        self.assertEqual(executor._xlabel("p" * 24, "entry_rung_10"), "p" * 24 + ":entry_rung_10")


if __name__ == "__main__":
    unittest.main()
