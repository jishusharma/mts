"""Offline tests (fakes only): position_manager transient-error retry + rc 3, NETRETRY 2026-09-29."""
import sys
import unittest
import urllib.error
from unittest import mock

import deribit_orders as do
import position_manager as pm

STOP = {"order_id": "S1", "label": "stop", "amount": 10, "trigger": 84000.0, "side": "BUY"}


def transport(method="private/get_position"):
    return do.DeribitError(method, {"code": None, "message": "transport error: URLError('connection reset')"})


class ManagerRetryTest(unittest.TestCase):
    def setUp(self):
        self.sleeps, self.auth_calls, self.stop_placed = [], [], []
        patches = [
            mock.patch.object(pm.time, "sleep", lambda s: self.sleeps.append(s)),
            mock.patch.object(pm.journal, "reconstruct_belief", lambda pid: {"halted": False}),
            mock.patch.object(pm.journal, "append_event", lambda *a, **k: None),
            mock.patch.object(pm, "_plan_orders", lambda pid: (dict(STOP), {}, "SELL", 10)),
            mock.patch.object(pm, "_plan_max_hold_minutes", lambda pid: None),
            mock.patch.object(do, "authenticate", self.fake_auth),
            mock.patch.object(do, "get_order_state",
                              lambda tok, oid: {"order_state": "untriggered", "filled_amount": 0}),
            mock.patch.object(do, "stop_market", lambda *a, **k: self.stop_placed.append(a)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.get_position = lambda tok, ins: {"size": -10}

    def fake_auth(self):
        self.auth_calls.append(1)
        return f"tok{len(self.auth_calls)}"

    def run_once(self):
        with mock.patch.object(do, "get_position", lambda tok, ins: self.get_position(tok, ins)):
            return pm._manage_impl("P1", once=True)

    def test_transient_read_error_is_retried_reauthed_and_managed(self):
        seen = []

        def gp(tok, ins):
            seen.append(tok)
            if len(seen) <= 2:
                raise transport()
            return {"size": -10}
        self.get_position = gp
        res = self.run_once()
        self.assertEqual(res["status"], "managing")
        self.assertEqual(len(seen), 3)
        self.assertEqual(seen[0], "tok1")
        self.assertEqual(seen[-1], "tok3")          # re-authenticated after each failure
        self.assertEqual(len(self.sleeps), 2)
        self.assertEqual(self.stop_placed, [])       # an outage is not a "stop missing" state

    def test_raw_urlerror_http5xx_are_transient(self):
        errs = [urllib.error.URLError("connection reset"),
                do.DeribitError("m", {"code": None, "message": "transport error: RuntimeError('m: HTTP 503')"})]
        for e in errs:
            n = []

            def gp(tok, ins, e=e, n=n):
                n.append(1)
                if len(n) == 1:
                    raise e
                return {"size": -10}
            self.get_position = gp
            self.assertEqual(self.run_once()["status"], "managing", repr(e))

    def test_budget_exhausted_raises_contact_lost_without_flatten_or_replace(self):
        n = []

        def gp(tok, ins):
            n.append(1)
            raise transport()
        self.get_position = gp
        with self.assertRaises(pm.ContactLost):
            self.run_once()
        self.assertEqual(len(n), len(pm.READ_RETRY_DELAYS) + 1)
        self.assertEqual(self.sleeps, list(pm.READ_RETRY_DELAYS))
        self.assertGreaterEqual(sum(pm.READ_RETRY_DELAYS), 60)
        self.assertEqual(self.stop_placed, [])

    def test_auth_outage_beyond_budget_is_contact_lost(self):
        def bad_auth():
            raise transport("public/auth")
        with mock.patch.object(do, "authenticate", bad_auth):
            with self.assertRaises(pm.ContactLost):
                pm._manage_impl("P1", once=True)

    def test_definite_api_error_is_not_retried(self):
        n = []

        def gp(tok, ins):
            n.append(1)
            raise do.DeribitError("private/get_position", {"code": 10009, "message": "not_enough_funds"})
        self.get_position = gp
        with self.assertRaises(do.DeribitError):
            self.run_once()
        self.assertEqual(len(n), 1)
        self.assertEqual(self.sleeps, [])

    def test_main_returns_rc3_on_contact_lost(self):
        with mock.patch.object(sys, "argv", ["position_manager.py", "P1"]), \
                mock.patch.object(pm.journal, "append_event", lambda *a, **k: None), \
                mock.patch.object(pm, "manage", side_effect=pm.ContactLost("x")):
            self.assertEqual(pm.main(), 3)

    def test_main_halt_is_still_rc1(self):
        with mock.patch.object(sys, "argv", ["position_manager.py", "P1"]), \
                mock.patch.object(pm, "manage", side_effect=pm.ManagerHalted("x")):
            self.assertEqual(pm.main(), 1)


if __name__ == "__main__":
    unittest.main()
