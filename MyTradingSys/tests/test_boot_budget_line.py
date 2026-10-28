"""tc3-budget-lines: the boot ritual in CLAUDE.md tells every session to send its BUDGET line (mts_signal.py budget),
the only source of traffic.py status per-login budgets."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class BootBudgetTest(unittest.TestCase):
    def test_boot_sends_budget(self):
        text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("mts_signal.py budget --login", text)
        self.assertIn("--five", text)


if __name__ == "__main__":
    unittest.main()
