"""
Offline test: position_manager has no equity/margin reference (card
test-position-manager-margin-drain, Gemini execution plan rank 1). The manage
loop watches contract count and stop state only; daily_loss_monitor watches
total equity loss, but nothing watches LIQUIDATION DISTANCE while a position
is open.

DECISION (OURS): the test pins "manager flattens + halts when
available_funds / equity falls under maintenance margin with the stop still
live". The live-path owner may instead choose a documented hand-off to
daily_loss_monitor; then replace this test. Until the manager reacts, the test
is marked expectedFailure (this change is test-only, no live-path edit).

  python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_margin_drain_offline
No network, no secrets.
"""
import sys
sys.dont_write_bytecode = True

import unittest
from unittest import mock

import deribit_orders as do
import position_manager as pm
import test_fix3_offline as _t3


class MarginDrain(_t3.PositionManagerFixes):
    # inherit setUp/tearDown (filled 100 + live stop, fake clock); drop the
    # inherited tests so only the new one runs from this module
    for _n in [n for n in dir(_t3.PositionManagerFixes) if n.startswith("test_")]:
        locals()[_n] = None
    del _n

    def _drain(self):
        """Equity collapses below maintenance margin while the stop stays live."""
        poll = {"n": 0}

        def summary(token, currency="BTC"):
            poll["n"] += 1
            eq = max(0.0, 1.0 - 0.3 * poll["n"])
            return {"equity": eq, "available_funds": 0.0, "maintenance_margin": 0.5,
                    "initial_margin": 0.8, "margin_balance": eq}
        return mock.patch.object(do, "get_account_summary", summary, create=True)


    @unittest.expectedFailure  # BUG: position_manager never reads equity/margin -> keeps managing (gap confirmed)
    def test_manager_reacts_to_margin_drain(self):
        with self._drain():
            try:
                r = pm.manage("fx_pm", max_seconds=60, token="tok")
            except pm.ManagerHalted:
                r = None
        self.assertIsNone(r, "manager kept managing while equity < maintenance margin")
        self.assertEqual(self.fake.pos, 0, "position must be flattened")
        self.assertIn("close_position", self.names())


if __name__ == "__main__":
    unittest.main()
