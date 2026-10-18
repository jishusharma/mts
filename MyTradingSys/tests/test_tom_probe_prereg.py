"""Test suite for PRE_REG_ARMS.md and tom-probe-runner task card."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
PRE_REG_ARMS = ROOT / "MyTradingSys" / "research" / "tom_transfer_2026-10-11" / "PRE_REG_ARMS.md"
RUNNER_CARD = ROOT / "MyTradingSys" / "system" / "tasks" / "tom-probe-runner.json"


class TestTomProbePrereg(unittest.TestCase):
    def test_pre_reg_arms_exists(self):
        self.assertTrue(PRE_REG_ARMS.is_file(), f"Missing file: {PRE_REG_ARMS}")

    def test_pre_reg_arms_content_and_rules(self):
        if not PRE_REG_ARMS.is_file():
            self.skipTest("PRE_REG_ARMS.md does not exist yet")
        content = PRE_REG_ARMS.read_text(encoding="utf-8")

        # Check survival statuses for axes
        self.assertIn("M (management): GO", content)
        self.assertIn("S (session): SKIP", content)
        self.assertIn("Q (selection): SKIP", content)

        # Check arms M0..M4 and M_all are declared
        for arm in ["M0", "M1", "M2", "M3", "M4", "M_all"]:
            self.assertIn(f"**{arm}**", content)

        # Check source labels
        self.assertIn("SOURCED", content)
        self.assertIn("OURS", content)
        self.assertIn("NO-SOURCE", content)

        # Check transfer rule and N5/N7/B154 requirements
        self.assertIn("0.40 %", content)
        self.assertIn("0.20 %", content)
        self.assertIn("W_min", content)
        self.assertIn("N5", content)
        self.assertIn("N7", content)
        self.assertIn("session-matched", content)
        self.assertIn("trade-through", content)
        self.assertIn("B154", content)
        self.assertIn("underpowered", content)

        # Check holdouts
        self.assertIn("2026-09-27", content)
        self.assertIn("2026-06-26", content)
        self.assertIn("burned", content.lower())
        self.assertIn("HOLDOUT_CLEAN.json", content)
        self.assertIn("2026-10-10", content)

        # Check trial counts and DSR
        self.assertIn("24", content)
        self.assertIn("121", content)
        self.assertIn("DSR", content)
        self.assertIn("PBO", content)

    def test_runner_card_exists_and_valid(self):
        self.assertTrue(RUNNER_CARD.is_file(), f"Missing card: {RUNNER_CARD}")
        if not RUNNER_CARD.is_file():
            return
        data = json.loads(RUNNER_CARD.read_text(encoding="utf-8"))
        self.assertEqual(data.get("id"), "tom-probe-runner")
        self.assertTrue(data.get("title"))
        self.assertTrue(data.get("goal"))
        self.assertTrue(data.get("done_when"))
        self.assertTrue(data.get("tests"))
        self.assertIn(data.get("size"), ("S", "M"))
        self.assertIn(data.get("worker"), ("agent", "session"))
        self.assertIsInstance(data.get("est_turns"), int)
        self.assertTrue(data.get("scope_in"))
        self.assertTrue(data.get("steps"))
        self.assertIn("PRE_REG_ARMS.md", str(data.get("scope_in")))


if __name__ == "__main__":
    unittest.main()
