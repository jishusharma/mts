"""Test for gemini-blind-read-tom-fabio-setup-review-1031 audit card output.
Verifies that:
1. Output file MyTradingSys/research/gemini_audits_2026-10-31/setup_review_blind_read.md exists.
2. The audit table has rows for cited items.
3. Every row has a cited file:line or command.
4. Every row has a verdict of FOUND, DIFF, or NOT_IN_DATA.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT_FILE = REPO / "MyTradingSys" / "research" / "gemini_audits_2026-10-31" / "setup_review_blind_read.md"

class TestSetupReviewBlindRead(unittest.TestCase):
    def test_audit_file_exists(self):
        self.assertTrue(AUDIT_FILE.exists(), f"Audit file {AUDIT_FILE} does not exist")

    def test_table_rows_validity(self):
        self.assertTrue(AUDIT_FILE.exists(), f"Audit file {AUDIT_FILE} does not exist")
        text = AUDIT_FILE.read_text(encoding="utf-8")
        lines = text.splitlines()

        # Find table header
        table_lines = []
        in_table = False
        for line in lines:
            if line.startswith("|") and "Verdict" in line:
                in_table = True
                continue
            if in_table:
                if line.startswith("|---"):
                    continue
                if line.startswith("|"):
                    table_lines.append(line)
                else:
                    in_table = False

        self.assertGreater(len(table_lines), 20, f"Expected > 20 audit table rows, found {len(table_lines)}")

        valid_verdicts = {"FOUND", "DIFF", "NOT_IN_DATA"}
        for idx, row in enumerate(table_lines):
            cols = [c.strip() for c in row.split("|")[1:-1]]
            # Expected columns: Sheet Line | Section | Item Description | Cited File:Line | Cited Number / Text | Actual Content Found | Verdict | Notes
            self.assertGreaterEqual(len(cols), 7, f"Row {idx+1} has fewer than 7 columns: {row}")
            cited_ref = cols[3]
            verdict_raw = cols[6].replace("*", "").strip()
            self.assertIn(verdict_raw, valid_verdicts, f"Row {idx+1} invalid verdict '{verdict_raw}' in {row}")
            # Every row must have a file:line or command or explicit cite
            self.assertTrue(
                bool(re.search(r"(\.[\w]+:\d+|git |python |CAT:\d+|:[0-9]+)", cited_ref)),
                f"Row {idx+1} cited ref '{cited_ref}' does not contain file:line or command: {row}"
            )

if __name__ == "__main__":
    unittest.main()
