"""Offline tests for orphan_watchdog (spec 122). Derived from the spec, not from the implementation."""
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import orphan_watchdog as ow

NOW = datetime(2026, 9, 29, 12, 0, 0, tzinfo=timezone.utc)
POS10 = [{"instrument_name": "BTC-PERPETUAL", "size": 10}]


class FakeReadClient:
    """Read-only fake: any attribute other than the two reads fails the test (the watchdog must never trade)."""

    def __init__(self, positions=None, orders=None, fail=False):
        self.positions = positions or []
        self.orders = orders or []
        self.fail = fail
        self.calls = []

    def get_positions(self, token, currency="BTC", kind="future"):
        self.calls.append("get_positions")
        if self.fail:
            raise RuntimeError("boom")
        return self.positions

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        self.calls.append("get_open_orders")
        if self.fail:
            raise RuntimeError("boom")
        return self.orders

    def __getattr__(self, name):
        raise AssertionError(f"watchdog touched forbidden client method {name}")


class TestAccountState(unittest.TestCase):
    def test_flat_and_no_orders(self):
        self.assertEqual(ow.account_state(FakeReadClient(), "tok"), {"position": 0, "open_orders": 0})

    def test_position_abs_and_only_btc_perp(self):
        c = FakeReadClient(positions=[{"instrument_name": "BTC-PERPETUAL", "size": -30},
                                      {"instrument_name": "ETH-PERPETUAL", "size": 99}],
                           orders=[{"order_id": "a"}, {"order_id": "b"}])
        self.assertEqual(ow.account_state(c, "tok"), {"position": 30, "open_orders": 2})

    def test_missing_size_treated_zero(self):
        c = FakeReadClient(positions=[{"instrument_name": "BTC-PERPETUAL"}])
        self.assertEqual(ow.account_state(c, "tok")["position"], 0)


class TestFindOrphans(unittest.TestCase):
    def test_flat_account_is_not_orphan(self):
        self.assertEqual(ow.find_orphans({"default": {"position": 0, "open_orders": 0}}, set()), [])

    def test_position_without_manager_is_orphan(self):
        got = ow.find_orphans({"fabio": {"position": 10, "open_orders": 0}}, set())
        self.assertEqual(got, [{"account": "fabio", "position": 10, "open_orders": 0}])

    def test_orders_only_without_manager_is_orphan(self):
        got = ow.find_orphans({"default": {"position": 0, "open_orders": 2}}, set())
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["account"], "default")

    def test_live_manager_protects_only_its_own_account(self):
        states = {"default": {"position": 10, "open_orders": 1}, "fabio": {"position": 10, "open_orders": 1}}
        got = ow.find_orphans(states, {"default"})
        self.assertEqual([g["account"] for g in got], ["fabio"])

    def test_error_state_is_not_an_orphan(self):
        self.assertEqual(ow.find_orphans({"fabio": {"error": "RuntimeError('x')"}}, set()), [])

    def test_sorted_by_account(self):
        states = {"zeta": {"position": 1, "open_orders": 0}, "alpha": {"position": 1, "open_orders": 0}}
        self.assertEqual([g["account"] for g in ow.find_orphans(states, set())], ["alpha", "zeta"])


class TestRunOnce(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="orphan_wd_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.halt = self.tmp / "HALT"
        self.log = self.tmp / "orphan_watchdog.jsonl"

    def _run(self, clients, live, accounts=("default", "fabio")):
        return ow.run_once(lambda label: (clients[label], "tok"), list(accounts), live,
                           self.halt, log_path=self.log, now=NOW)

    def test_orphan_writes_halt_with_reason_and_logs(self):
        clients = {"default": FakeReadClient(), "fabio": FakeReadClient(positions=POS10)}
        res = self._run(clients, set())
        self.assertTrue(res["halted"])
        self.assertEqual([o["account"] for o in res["orphans"]], ["fabio"])
        text = self.halt.read_text(encoding="utf-8")
        self.assertIn("orphan_watchdog", text)
        self.assertIn("fabio", text)
        self.assertIn("2026-09-29T12:00:00", text)
        rec = json.loads(self.log.read_text(encoding="utf-8").strip().splitlines()[-1])
        self.assertEqual(rec["event"], "orphan_halt")

    def test_clean_run_writes_no_halt_but_logs_ok(self):
        res = self._run({"default": FakeReadClient(), "fabio": FakeReadClient()}, set())
        self.assertFalse(res["halted"])
        self.assertEqual(res["orphans"], [])
        self.assertFalse(self.halt.exists())
        rec = json.loads(self.log.read_text(encoding="utf-8").strip().splitlines()[-1])
        self.assertEqual(rec["event"], "ok")

    def test_live_manager_prevents_halt(self):
        clients = {"default": FakeReadClient(positions=POS10), "fabio": FakeReadClient()}
        res = self._run(clients, {"default"})
        self.assertFalse(res["halted"])
        self.assertFalse(self.halt.exists())

    def test_read_error_recorded_no_halt_others_still_checked(self):
        clients = {"default": FakeReadClient(fail=True), "fabio": FakeReadClient(orders=[{"order_id": "x"}])}
        res = self._run(clients, set())
        self.assertIn("default", res["errors"])
        self.assertTrue(res["halted"])  # fabio still evaluated
        self.assertEqual([o["account"] for o in res["orphans"]], ["fabio"])

    def test_get_client_failure_is_an_error_not_a_crash(self):
        def gc(label):
            raise RuntimeError("no secret file")
        res = ow.run_once(gc, ["fabio"], set(), self.halt, log_path=self.log, now=NOW)
        self.assertIn("fabio", res["errors"])
        self.assertFalse(res["halted"])

    def test_existing_halt_content_is_preserved(self):
        self.halt.write_text("earlier reason\n", encoding="utf-8")
        self._run({"default": FakeReadClient(orders=[{"order_id": "x"}])}, set(), accounts=("default",))
        text = self.halt.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("earlier reason"))
        self.assertIn("orphan_watchdog", text)

    def test_never_calls_anything_but_reads(self):
        c = FakeReadClient(positions=POS10, orders=[{"order_id": "x"}])
        self._run({"default": c}, set(), accounts=("default",))
        self.assertTrue(set(c.calls) <= {"get_positions", "get_open_orders"})

    def test_no_log_path_ok(self):
        res = ow.run_once(lambda l: (FakeReadClient(), "tok"), ["default"], set(), self.halt, now=NOW)
        self.assertFalse(res["halted"])


if __name__ == "__main__":
    unittest.main()
