import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_status_parse as p

SAMPLE = """lab: 5 ready
Codex allowance (plus): 5-hour window 6% used (resets 10-19 08:32Z); week 27% used (resets 10-24 20:41Z)
NEEDS A LOOK: none
"""


class T(unittest.TestCase):
    def test_parse_sample(self):
        self.assertEqual(p.parse_status(SAMPLE), {"plan": "plus", "window_pct": 6.0, "window_resets": "10-19 08:32Z",
                                                  "week_pct": 27.0, "week_resets": "10-24 20:41Z"})

    def test_reset_passed_has_no_resets_part(self):
        r = p.parse_status("Codex allowance (plan ?): 5-hour window 0% used; week 0% used")
        self.assertEqual((r["window_pct"], r["week_pct"], r["window_resets"]), (0.0, 0.0, None))

    def test_no_reading(self):
        self.assertIsNone(p.parse_status("Codex allowance: no reading yet"))
        self.assertIsNone(p.parse_status(""))
        self.assertIsNone(p.parse_status(None))


if __name__ == "__main__":
    unittest.main()
