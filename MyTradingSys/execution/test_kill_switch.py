"""
Unit tests for kill_switch module.
"""

import sys
import tempfile
import types
import unittest
from pathlib import Path
from typing import List, Dict, Any
import kill_switch
from kill_switch import kill_all, format_kill_report


class FakeClient:
    """Minimal in-memory stand-in for testing."""
    
    def __init__(self, data: Dict[str, Dict[str, Any]]):
        """
        Args:
            data: dict mapping instrument_name to {
                "size": int,
                "orders": [order_id, ...]
            }
        """
        self._data = data
        self.order_queries = []
        self._cancelled = set()
    
    def get_positions(self, token, currency="BTC", kind="future"):
        result = []
        for instrument, info in self._data.items():
            result.append({
                "instrument_name": instrument,
                "size": info["size"]
            })
        return result
    
    def get_open_orders(self, token, instrument_name, type_="all"):
        self.order_queries.append(instrument_name)
        if instrument_name not in self._data:
            return []
        return [{"order_id": oid} for oid in self._data[instrument_name]["orders"]]
    
    def cancel(self, token, order_id):
        if order_id in self._cancelled:
            raise KeyError(f"Order {order_id} already cancelled")
        self._cancelled.add(order_id)
        # Find which instrument this order belongs to
        for instrument, info in self._data.items():
            if order_id in info["orders"]:
                info["orders"].remove(order_id)
                return {}
        raise KeyError(f"Order {order_id} not found")
    
    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        if instrument_name not in self._data:
            raise ValueError(f"Instrument {instrument_name} not found")
        size = self._data[instrument_name]["size"]
        self._data[instrument_name]["size"] = 0
        return {"order": {"order_id": f"flat-{instrument_name}", "filled_amount": abs(size)}}


class TestKillSwitch(unittest.TestCase):
    
    def test_kill_all_two_instruments(self):
        """Test kill_all with two instruments each having 2 open orders and a nonzero position."""
        client = FakeClient({
            "BTC-PERPETUAL": {"size": 10, "orders": ["order1", "order2"]},
            "ETH-PERPETUAL": {"size": 5, "orders": ["order3", "order4"]}
        })
        
        result = kill_all(client, "fake_token")
        
        self.assertEqual(len(result["cancelled_orders"]), 4)
        self.assertEqual(len(result["closed_positions"]), 2)
        self.assertEqual(len(result["errors"]), 0)
        self.assertTrue(result["ok"])
    
    def test_kill_all_with_duplicate_order_id(self):
        """Test kill_all when one cancel() call hits an id already removed."""
        client = FakeClient({
            "BTC-PERPETUAL": {"size": 10, "orders": ["order1", "order1"]}  # duplicate order ID
        })
        
        result = kill_all(client, "fake_token")
        
        # Should still cancel both orders (but one will fail)
        self.assertEqual(len(result["cancelled_orders"]), 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(len(result["closed_positions"]), 1)  # errors never stop phase 2  # One error from duplicate removal
        self.assertFalse(result["ok"])
    
    def test_kill_all_instruments_none_with_discovered_positions(self):
        """Test kill_all with instruments=None and discovered positions."""
        client = FakeClient({
            "ETH-PERPETUAL": {"size": 5, "orders": ["order1", "order2"]},
            "BTC-PERPETUAL": {"size": 0, "orders": []}  # This should not be processed
        })
        
        result = kill_all(client, "fake_token", instruments=None)
        
        # Should process ETH-PERPETUAL and BTC-PERPETUAL (always included)
        self.assertIn("BTC-PERPETUAL", client.order_queries)  # orders always checked on default instrument
        self.assertNotIn("BTC-PERPETUAL", [p["instrument_name"] for p in result["closed_positions"]])  # size 0: nothing to close
        self.assertIn("ETH-PERPETUAL", [p["instrument_name"] for p in result["closed_positions"]])
    
    def test_kill_all_instruments_none_no_positions(self):
        """Test kill_all with instruments=None and no nonzero positions."""
        client = FakeClient({
            "BTC-PERPETUAL": {"size": 0, "orders": []},
            "ETH-PERPETUAL": {"size": 0, "orders": []}
        })
        
        result = kill_all(client, "fake_token", instruments=None)
        
        # Should fall back to BTC-PERPETUAL
        self.assertEqual(len(result["cancelled_orders"]), 0)
        self.assertEqual(len(result["closed_positions"]), 0)
        self.assertEqual(len(result["errors"]), 0)
        self.assertTrue(result["ok"])
    
    def test_format_kill_report_clean(self):
        """Test format_kill_report on a clean result."""
        result = {
            "cancelled_orders": ["order1", "order2"],
            "closed_positions": [{"instrument_name": "BTC-PERPETUAL"}],
            "errors": [],
            "ok": True
        }
        
        report = format_kill_report(result)
        self.assertIn("KILL SWITCH", report)
        self.assertNotIn("ERRORS DURING KILL", report)
    
    def test_format_kill_report_with_errors(self):
        """Test format_kill_report on a result with errors."""
        result = {
            "cancelled_orders": ["order1"],
            "closed_positions": [],
            "errors": [{"error": "test error"}],
            "ok": False
        }
        
        report = format_kill_report(result)
        self.assertIn("KILL SWITCH", report)
        self.assertIn("ERRORS DURING KILL", report)


class FakeDeribitModule(types.ModuleType):
    """Stands in for the real `deribit_orders` module that kill_switch.main()
    imports at CLI runtime (see this module's docstring: not imported at
    import time, only inside main()). Exposes both authenticate() and the
    kill_all client surface (get_positions/get_open_orders/cancel/
    close_position), same fake data shape as TestKillSwitch.FakeClient
    above."""

    def __init__(self, data):
        super().__init__("deribit_orders")
        self._data = data
        self.auth_calls = 0

    def authenticate(self):
        self.auth_calls += 1
        return "fake_token"

    def get_positions(self, token, currency="BTC", kind="future"):
        return [{"instrument_name": i, "size": d["size"]} for i, d in self._data.items()]

    def get_open_orders(self, token, instrument_name, type_="all"):
        return [{"order_id": oid} for oid in self._data.get(instrument_name, {}).get("orders", [])]

    def cancel(self, token, order_id):
        for info in self._data.values():
            if order_id in info["orders"]:
                info["orders"].remove(order_id)
                return {}
        raise KeyError(order_id)

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self._data[instrument_name]["size"] = 0
        return {"order": {"order_id": f"flat-{instrument_name}", "filled_amount": 0}}


class TestKillSwitchCli(unittest.TestCase):
    """FT-2 (2026-09-28): the kill_switch.py CLI (main()) - arg refusal and
    the unconditional HALT-file write on a real confirm."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="kill_switch_cli_"))
        self.halt_path = self.tmp / "HALT"
        self._orig_module = sys.modules.get("deribit_orders")

    def tearDown(self):
        if self._orig_module is not None:
            sys.modules["deribit_orders"] = self._orig_module
        else:
            sys.modules.pop("deribit_orders", None)

    def _install_fake(self, data):
        fake = FakeDeribitModule(data)
        sys.modules["deribit_orders"] = fake
        return fake

    def test_no_confirm_refuses_without_touching_exchange(self):
        fake = self._install_fake({"BTC-PERPETUAL": {"size": 10, "orders": ["o1"]}})
        rc = kill_switch.main([], halt_path=self.halt_path)
        self.assertEqual(rc, 1)
        self.assertEqual(fake.auth_calls, 0, "no --confirm KILL must never authenticate")
        self.assertFalse(self.halt_path.exists(), "no --confirm KILL must never write HALT")

    def test_wrong_confirm_value_refuses(self):
        fake = self._install_fake({"BTC-PERPETUAL": {"size": 10, "orders": ["o1"]}})
        for bad in ("kill", "Kill", "KILL ", "yes"):
            rc = kill_switch.main(["--confirm", bad], halt_path=self.halt_path)
            self.assertEqual(rc, 1, bad)
        self.assertEqual(fake.auth_calls, 0)
        self.assertFalse(self.halt_path.exists())

    def test_confirm_kill_authenticates_kills_and_writes_halt(self):
        fake = self._install_fake({"BTC-PERPETUAL": {"size": 10, "orders": ["o1", "o2"]}})
        rc = kill_switch.main(["--confirm", "KILL"], halt_path=self.halt_path)
        self.assertEqual(rc, 0)
        self.assertEqual(fake.auth_calls, 1)
        self.assertEqual(fake._data["BTC-PERPETUAL"]["size"], 0)
        self.assertEqual(fake._data["BTC-PERPETUAL"]["orders"], [])
        self.assertTrue(self.halt_path.exists(), "a real --confirm KILL must always write HALT")

    def test_confirm_kill_writes_halt_even_when_kill_all_reports_errors(self):
        # cancel() raising for an unknown order id -> kill_all returns ok=False,
        # but HALT must still be written (the whole point of the CLI is that
        # nothing resumes trading until an operator reviews it, success or not).
        fake = self._install_fake({"BTC-PERPETUAL": {"size": 5, "orders": ["missing_order"]}})
        real_cancel = fake.cancel
        def boom(token, order_id):
            raise RuntimeError("simulated cancel failure")
        fake.cancel = boom
        rc = kill_switch.main(["--confirm", "KILL"], halt_path=self.halt_path)
        self.assertEqual(rc, 1)
        self.assertTrue(self.halt_path.exists(), "HALT must be written even when kill_all is not fully ok")


if __name__ == "__main__":
    unittest.main()
