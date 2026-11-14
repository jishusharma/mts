"""Unit tests for scripts/dev/indicator_audit_compare.py.

Mutation failure verification (Step 3):
Mutated line 57 of scripts/dev/indicator_audit_compare.py:
  Original: tol, ok = TOL_ABS[key], abs(diff) <= TOL_ABS[key]
  Mutated:  tol, ok = TOL_ABS[key], abs(diff) > TOL_ABS[key]  # flipped <= to >
Failure observed when running pytest against the mutated module:
  FAILED scripts/dev/test_indicator_audit_compare.py::TestIndicatorAuditCompare::test_compare_value_absolute_tolerance
  AssertionError: False is not true : Expected ok=True for diff=0.01 within TOL_ABS=0.01
  at scripts/dev/test_indicator_audit_compare.py line 35
"""
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import indicator_audit_compare as iac  # noqa: E402


class TestIndicatorAuditCompare(unittest.TestCase):
    def test_compare_value_absolute_tolerance(self):
        """Absolute tolerance branch (TOL_ABS): diff <= 0.01 is ok, diff > 0.01 is not ok.
        Tolerance SOURCED: scripts/dev/indicator_audit_compare.py:23 (TOL_ABS['RSI'] = 0.01).
        Hand-calculated expected values:
          diff = 50.01 - 50.0 = 0.01 <= 0.01 -> ok: True
          diff = 50.02 - 50.0 = 0.02 > 0.01 -> ok: False
        """
        # Within absolute tolerance: diff = 50.01 - 50.0 = 0.01 <= 0.01
        rows_ok = iac.compare_value("RSI", {"RSI": 50.0}, {"RSI": 50.01})
        self.assertEqual(len(rows_ok), 1)
        self.assertEqual(rows_ok[0]["key"], "RSI")
        self.assertEqual(rows_ok[0]["tol"], 0.01)
        self.assertAlmostEqual(rows_ok[0]["diff"], 0.01, places=7)
        self.assertTrue(rows_ok[0]["ok"], "Expected ok=True for diff=0.01 within TOL_ABS=0.01")

        # Exceeding absolute tolerance: diff = 50.02 - 50.0 = 0.02 > 0.01
        rows_bad = iac.compare_value("RSI", {"RSI": 50.0}, {"RSI": 50.02})
        self.assertEqual(len(rows_bad), 1)
        self.assertFalse(rows_bad[0]["ok"], "Expected ok=False for diff=0.02 > TOL_ABS=0.01")

    def test_compare_value_relative_tolerance(self):
        """Relative tolerance branch (TOL_REL): diff <= 1e-6 * eng is ok, diff > 1e-6 * eng is not ok.
        Tolerance SOURCED: scripts/dev/indicator_audit_compare.py:24 (TOL_REL['BB_mid'] = 1e-6).
        Hand-calculated expected values:
          threshold = 1e-6 * 1000.0 = 0.001
          diff = 1000.001 - 1000.0 = 0.001 <= 0.001 -> ok: True
          diff = 1000.002 - 1000.0 = 0.002 > 0.001 -> ok: False
        """
        # Within relative tolerance: 1e-6 * 1000.0 = 0.001. Diff = 1000.001 - 1000.0 = 0.001
        rows_ok = iac.compare_value("BB", {"BB_mid": 1000.0}, {"BB_mid": 1000.001})
        self.assertEqual(len(rows_ok), 1)
        self.assertEqual(rows_ok[0]["tol"], 1e-6)
        self.assertTrue(rows_ok[0]["ok"], "Expected ok=True for diff=0.001 within TOL_REL 1e-6 * 1000.0")

        # Exceeding relative tolerance: diff = 1000.002 - 1000.0 = 0.002 > 0.001
        rows_bad = iac.compare_value("BB", {"BB_mid": 1000.0}, {"BB_mid": 1000.002})
        self.assertEqual(len(rows_bad), 1)
        self.assertFalse(rows_bad[0]["ok"], "Expected ok=False for diff=0.002 > TOL_REL 1e-6 * 1000.0")

    def test_compare_value_empty_and_malformed_inputs(self):
        """compare_value handles empty dict, None, non-numbers, bools, and non-finite floats."""
        # Empty dict reply
        res_empty = iac.compare_value("RSI", {"RSI": 50.0}, {})
        self.assertEqual(res_empty, [{"key": "RSI", "engine": 50.0, "reviewer": None, "diff": None, "tol": None, "ok": False}])

        # None reply
        res_none = iac.compare_value("RSI", {"RSI": 50.0}, None)
        self.assertEqual(res_none, [{"key": "RSI", "engine": 50.0, "reviewer": None, "diff": None, "tol": None, "ok": False}])

        # Malformed reply: string
        res_str = iac.compare_value("RSI", {"RSI": 50.0}, {"RSI": "bad"})
        self.assertEqual(res_str, [{"key": "RSI", "engine": 50.0, "reviewer": "bad", "diff": None, "tol": None, "ok": False}])

        # Malformed reply: boolean (bool is instance of int in Python, but excluded by _num)
        res_bool = iac.compare_value("RSI", {"RSI": 50.0}, {"RSI": True})
        self.assertEqual(res_bool, [{"key": "RSI", "engine": 50.0, "reviewer": True, "diff": None, "tol": None, "ok": False}])

        # Malformed reply: infinity
        res_inf = iac.compare_value("RSI", {"RSI": 50.0}, {"RSI": float("inf")})
        self.assertEqual(res_inf, [{"key": "RSI", "engine": 50.0, "reviewer": float("inf"), "diff": None, "tol": None, "ok": False}])

        # Malformed engine: nan
        res_nan = iac.compare_value("RSI", {"RSI": float("nan")}, {"RSI": 50.0})
        self.assertEqual(len(res_nan), 1)
        self.assertFalse(res_nan[0]["ok"])
        self.assertIsNone(res_nan[0]["diff"])

    def test_engine_values_indicators_and_unknown(self):
        """engine_values computes expected indicator values and raises ValueError on unknown.
        Population standard deviation formula SOURCED: FORMULAS.md s22, scripts/dev/chart_verify.py:43-50.
        Hand-calculated expected values for 20 closes of 100.0:
          mean = sum(closes) / 20 = 100.0
          sd = math.sqrt(sum((x - 100)^2) / 20) = 0.0
          up = 100.0 + 2.0 * 0.0 = 100.0
          mid = 100.0
          lo = 100.0 - 2.0 * 0.0 = 100.0
        """
        # Unknown indicator raises ValueError
        with self.assertRaises(ValueError):
            iac.engine_values("INVALID_IND", [100.0] * 20)

        # Constant 20-bar close series for BB: mean=100.0, sd=0.0 -> mid=100.0, up=100.0, low=100.0
        bb_vals = iac.engine_values("BB", [100.0] * 20)
        self.assertEqual(bb_vals, {"BB_mid": 100.0, "BB_up": 100.0, "BB_low": 100.0})

    def test_run_empty_and_missing_replies(self):
        """run handles empty packets list and packet with missing reply.
        Hand-calculated expected values (OURS):
          pkt-ok has 3 keys (BB_mid, BB_up, BB_low) -> 3 ok rows
          pkt-missing has 3 keys with empty reply -> 3 mismatch rows
          total values: 3 + 3 = 6
          total mismatches: 3
        """
        # Empty packets
        res_empty = iac.run([], {})
        self.assertEqual(res_empty, {"n_values": 0, "n_mismatch": 0, "rows": [], "mismatches": []})

        # Packet with matching reply vs packet with missing reply
        packets = [
            {"id": "pkt-ok", "indicator": "BB", "closes": [100.0] * 20},
            {"id": "pkt-missing", "indicator": "BB", "closes": [100.0] * 20},
        ]
        replies = {
            "pkt-ok": {"BB_mid": 100.0, "BB_up": 100.0, "BB_low": 100.0}
        }
        res = iac.run(packets, replies)
        self.assertEqual(res["n_values"], 6)      # 3 keys for pkt-ok + 3 keys for pkt-missing
        self.assertEqual(res["n_mismatch"], 3)    # 3 missing keys for pkt-missing
        self.assertEqual(len(res["mismatches"]), 3)
        self.assertTrue(all(m["packet"] == "pkt-missing" for m in res["mismatches"]))
