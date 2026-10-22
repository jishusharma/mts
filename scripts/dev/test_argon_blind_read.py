"""Unit test for argon_blind_read prompt validation and comparison logic.

Gates:
- Each prompt must require nullable fields {position, entry, stop, target} with null option.
- No prompt may contain claim, reference, or truth values.
- Comparison logic must count numeric outputs for truth-null fields as INVENTED.
- Comparison logic must exclude '?' / unverified references from accuracy denominators.
- Reports must provide only descriptive 7-frame counts, never general catch-rate claims.
"""
import unittest
import sys
from pathlib import Path

# Add scripts/dev to path
sys.path.insert(0, str(Path(__file__).parent))

import argon_blind_read as abr


class TestArgonBlindRead(unittest.TestCase):
    def test_prompt_validation(self):
        """Prompt must include all nullable fields and no injected claims."""
        valid_prompt = abr.build_blind_prompt("frame_01.jpg")
        self.assertIn("position,entry,stop,target", valid_prompt)
        self.assertIn("null", valid_prompt)
        self.assertTrue(abr.validate_prompt(valid_prompt, "frame_01.jpg"))

        # Prompt with injected claim must fail validation
        bad_prompt = valid_prompt + " Claim: stop is 24690."
        self.assertFalse(abr.validate_prompt(bad_prompt, "frame_01.jpg"))

        # Prompt missing null option must fail validation
        bad_prompt2 = "Open image frame_01.jpg. Return {position,entry,stop,target} as numbers."
        self.assertFalse(abr.validate_prompt(bad_prompt2, "frame_01.jpg"))

    def test_comparison_invented_numbers(self):
        """A number for a field our audit marked null counts as INVENTED."""
        truth = {"pos": -1, "entry": 25344, "sl": None, "tp": None}
        # Model returns invented stop and target
        model_out = {"position": -1, "entry": 25344, "stop": 25400, "target": 25200}
        scored = abr.score_fields(model_out, truth)
        self.assertEqual(scored["position"], abr.MATCH)
        self.assertEqual(scored["entry"], abr.MATCH)
        self.assertEqual(scored["stop"], abr.INVENTED)
        self.assertEqual(scored["target"], abr.INVENTED)

    def test_comparison_unverified_exclusion(self):
        """Reference '?' / missing values are UNVERIFIED and excluded from accuracy denominators."""
        truth = {"pos": "?", "entry": 23887, "sl": 23857, "tp": 23962}
        model_out = {"position": 1, "entry": 23887, "stop": 23857, "target": 23962}
        scored = abr.score_fields(model_out, truth)
        self.assertEqual(scored["position"], abr.UNVERIFIED)
        self.assertEqual(scored["entry"], abr.MATCH)
        self.assertEqual(scored["stop"], abr.MATCH)
        self.assertEqual(scored["target"], abr.MATCH)

    def test_descriptive_counts_summary(self):
        """Aggregation must produce descriptive counts, not a general catch-rate."""
        items = [
            {
                "frame": "f1.jpg",
                "truth": {"pos": -3, "entry": 24690, "sl": None, "tp": 24184},
                "parsed": {"position": -3, "entry": 24690, "stop": None, "target": 24184},
            },
            {
                "frame": "f2.jpg",
                "truth": {"pos": -2, "entry": None, "sl": None, "tp": 24184},
                "parsed": {"position": -2, "entry": None, "stop": 24690, "target": 24184},
            },
        ]
        summary = abr.summarize_descriptive_counts(items)
        self.assertIn("matches", summary)
        self.assertIn("mismatches", summary)
        self.assertIn("correct_nulls", summary)
        self.assertIn("missed_nulls", summary)
        self.assertIn("invented_numbers", summary)
        self.assertIn("unverified", summary)
        # Verify invented count for f2 stop 24690 where truth is None
        self.assertEqual(summary["invented_numbers"], 1)
        self.assertEqual(summary["matches"], 5)  # f1 pos, entry, tp (3); f2 pos, tp (2)


if __name__ == "__main__":
    unittest.main()
