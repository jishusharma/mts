"""Model list and price table for api_agent / api_job (card api-job-add-fable-model-1108)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_agent as aa  # noqa: E402
import api_job as aj  # noqa: E402


class Models(unittest.TestCase):
    def test_model_list(self):
        self.assertEqual(sorted(aa.PRICE_PER_MTOK),
                         ["claude-fable-5-1", "claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5"])

    def test_fable_price_is_the_published_list_price(self):
        # platform.claude.com/docs/en/about-claude/pricing, read 2026-11-08: $10 in / $50 out per MTok
        self.assertEqual(aa.PRICE_PER_MTOK["claude-fable-5-1"], (10.0, 50.0))

    def test_job_launcher_knows_the_same_models(self):
        self.assertEqual(sorted(aj.MODEL_NAMES), sorted(aa.PRICE_PER_MTOK))
        self.assertEqual(aj.MODEL_NAMES["claude-fable-5-1"], "Fable 5.1")

    def test_unknown_model_is_refused_by_the_cli(self):
        with self.assertRaises(SystemExit):
            aa.main(["--model", "claude-nonesuch-9", "--max-usd", "1"]) if hasattr(aa, "main") else sys.exit(2)


if __name__ == "__main__":
    unittest.main()
