import sys
sys.dont_write_bytecode = True
"""PRE_REG_TEMPLATE.md has 12 numbered items; any HOME_FIT_AUDIT_*.md has all 12 answered."""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = HERE / "PRE_REG_TEMPLATE.md"
ITEM = re.compile(r"^## (\d+)\. ", re.M)


def item_numbers(path):
    return [int(n) for n in ITEM.findall(path.read_text(encoding="utf-8"))]


class PreRegTemplate(unittest.TestCase):
    def test_template_exists(self):
        self.assertTrue(TEMPLATE.exists(), "PRE_REG_TEMPLATE.md missing")

    def test_twelve_numbered_items(self):
        # section 0 is the pre-build gate (q13, 2026-10-14); 1-12 are the checklist
        self.assertEqual(item_numbers(TEMPLATE), list(range(0, 13)))

    def test_every_item_has_answer_and_evidence_slot(self):
        t = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(t.count("Answer:"), 12)
        self.assertEqual(t.count("Evidence (file:line):"), 12)

    def test_home_fit_audits_fully_answered(self):
        for p in ROOT.rglob("HOME_FIT_AUDIT_*.md"):
            with self.subTest(audit=p.name):
                self.assertEqual(item_numbers(p), list(range(1, 13)))
                txt = p.read_text(encoding="utf-8")
                self.assertNotIn("Answer: TODO", txt)
                self.assertNotIn("NOT_ANSWERED", txt)


if __name__ == "__main__":
    unittest.main()
