"""tc5-lab-lane-dedupe: gemini_queue.run_job skips a card another lane already claimed (cards_worked_by_two_lanes)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import gemini_queue as gq  # noqa: E402


class ClaimSkipTest(unittest.TestCase):
    def test_holder(self):
        self.assertEqual(gq.claim_holder("tom-v2", [("tom-v2", {"host": "JIS-NB"})]), "JIS-NB")
        self.assertEqual(gq.claim_holder("tom-v2", [("other", {"host": "x"})]), "")

    def test_run_job_skips_claimed(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(gq, "ROOT", Path(t)), \
                mock.patch.object(gq, "git"), mock.patch("sync.open_claims", return_value=[("tom-v2", {"host": "JIS-NB"})]), \
                mock.patch.object(gq.subprocess, "run") as run:
            gq.run_job("tom-v2", "low")
            self.assertIn("SKIP", (Path(t) / "tom-v2.log").read_text(encoding="utf-8"))
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
