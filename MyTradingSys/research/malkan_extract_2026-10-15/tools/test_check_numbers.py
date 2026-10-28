"""Offline test for the Malkan number gate (tools/check_numbers.py): a range "80-90" must read as 80 and 90, not as a stray "0".

Run (repo root):  python -I MyTradingSys/research/malkan_extract_2026-10-15/tools/test_check_numbers.py
The same assertions fail on the unmodified Krown checker (research/krown_ta101_2026-10-13/tools/check_numbers.py):
run with env CHECKER=krown to see all 3 tests fail (checked 2026-10-15: 3 failures on Krown, OK on the Malkan wrapper).
"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TARGET = ROOT / "MyTradingSys" / "research" / ("krown_ta101_2026-10-13" if os.environ.get("CHECKER") == "krown" else "malkan_extract_2026-10-15") / "tools" / "check_numbers.py"


def load(path):
    spec = importlib.util.spec_from_file_location("chk_under_test", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class RangeAndIds(unittest.TestCase):
    def run_check(self, line):
        m = load(TARGET)
        kc = getattr(m, "kc", m)  # the Malkan wrapper keeps the Krown module as `kc`
        kc.body = lambda vid: kc.norm("seventy 80 and 90 and 60 and 40")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "extract_x.md"
            f.write_text("- Video ID: abcdefghijk\n" + line + "\n", encoding="utf-8", newline="\n")
            return kc.check(f)

    def test_range_reads_as_two_numbers(self):
        vid, total, bad = self.run_check("- Stated mechanics: daily RSI 80-90 then 60 to 40")
        self.assertEqual(bad, [], bad)
        self.assertEqual(total, 4)

    def test_missing_number_still_flagged(self):
        vid, total, bad = self.run_check("- Stated mechanics: RSI 80-91")
        self.assertEqual([b[1] for b in bad], ["91"])

    def test_concept_id_is_not_a_number(self):
        vid, total, bad = self.run_check("- Inferred: INFERRED: as in M-abcdefghijk-22 the level is 60")
        self.assertEqual(bad, [], bad)


if __name__ == "__main__":
    unittest.main()
