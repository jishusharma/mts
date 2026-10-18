import sys
sys.dont_write_bytecode = True
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE / "LEDGER_FEASIBILITY.md"

class TestLedgerFeasibility(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(DOC.exists(), "LEDGER_FEASIBILITY.md missing")

    def test_verdict_line_present(self):
        txt = DOC.read_text(encoding="utf-8")
        m = re.search(r"^Verdict:\s*(SCORABLE|HYPOTHESIS)", txt, re.MULTILINE | re.IGNORECASE)
        self.assertIsNotNone(m, "LEDGER_FEASIBILITY.md missing 'Verdict: SCORABLE' or 'Verdict: HYPOTHESIS'")

    def test_every_event_row_carries_file_line(self):
        txt = DOC.read_text(encoding="utf-8")
        # Check that events table/section exists and every event row has a file:line reference
        self.assertIn("## Listed events", txt)
        events_section = txt.split("## Listed events")[1].split("##")[0]
        # Look for table rows or bullet items describing events
        lines = [line.strip() for line in events_section.splitlines() if line.strip().startswith("|") or line.strip().startswith("-")]
        # Filter out table header or separator rows
        event_rows = [l for l in lines if not l.startswith("|-") and not "Video" in l and not "Extract" in l and not "Source" in l]
        self.assertGreater(len(event_rows), 0, "No event rows found in Listed events section")
        for row in event_rows:
            self.assertTrue(
                re.search(r"[\w/.-]+\.(?:md|txt):\d+", row),
                f"Event row missing file:line citation: {row}"
            )

if __name__ == "__main__":
    unittest.main()
