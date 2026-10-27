"""exhaust-phase-tooling req 7: the boot ritual in CLAUDE.md runs exhaust.py plan after get_usage (no scheduler), so the
window opens the first time any session boots within 2 hours of the weekly reset."""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class BootExhaustTest(unittest.TestCase):
    def test_boot_runs_exhaust_plan(self):
        text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("scripts/dev/exhaust.py plan", text)
        self.assertIn("EXHAUST_PHASE.md", text)


if __name__ == "__main__":
    unittest.main()
