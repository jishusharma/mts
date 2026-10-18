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

    def test_home_fit_audits_have_verdict_answer_evidence_per_item(self):
        # every numbered item of an audit carries a FAIR/UNFAIR verdict, an Answer and an Evidence line
        for p in ROOT.rglob("HOME_FIT_AUDIT_*.md"):
            with self.subTest(audit=p.name):
                parts = re.split(r"(?m)^## (?=\d+\. )", p.read_text(encoding="utf-8"))[1:]
                self.assertEqual(len(parts), 12)
                for sec in parts:
                    n = sec.split(".", 1)[0]
                    self.assertRegex(sec, r"(?m)^Verdict: (FAIR|UNFAIR)\b", "item %s: no verdict" % n)
                    self.assertRegex(sec, r"(?m)^Answer: \S", "item %s: no answer" % n)
                    self.assertRegex(sec, r"(?m)^Evidence \(file:line\): \S", "item %s: no evidence" % n)

    def test_malkan_home_fit_audit_present(self):
        p = ROOT / "research" / "tom_transfer_2026-10-11" / "HOME_FIT_AUDIT_MALKAN.md"
        self.assertTrue(p.exists(), "HOME_FIT_AUDIT_MALKAN.md missing")
        self.assertEqual(item_numbers(p), list(range(1, 13)))


POSITIONING_AUDIT = ROOT / "research" / "tom_transfer_2026-10-11" / "HOME_FIT_AUDIT_POSITIONING.md"
VERDICT = re.compile(r"^Verdict: (FAIR|UNFAIR)", re.M)


class PositioningHomeFitAudit(unittest.TestCase):
    """Card positioning-home-fit-audit: the file must exist (the rglob test above passes vacuously without it)."""

    def test_file_exists(self):
        self.assertTrue(POSITIONING_AUDIT.exists(), "HOME_FIT_AUDIT_POSITIONING.md missing")

    def test_twelve_items_each_with_verdict_and_evidence(self):
        txt = POSITIONING_AUDIT.read_text(encoding="utf-8")
        self.assertEqual(item_numbers(POSITIONING_AUDIT), list(range(1, 13)))
        self.assertEqual(len(VERDICT.findall(txt)), 12)
        self.assertEqual(txt.count("Evidence (file:line):"), 12)

    def test_has_follow_up_cards_section(self):
        txt = POSITIONING_AUDIT.read_text(encoding="utf-8")
        self.assertIn("## Tally and order of cards", txt)


MALKAN_LEDGER_PARITY = ROOT / "research" / "malkan_ledger_2026-10" / "LEDGER_PARITY.md"


class MalkanLedgerParity(unittest.TestCase):
    """Card malkan-ledger-parity-feasibility: the file must exist, have counts, and a verdict line."""

    def test_file_exists(self):
        self.assertTrue(MALKAN_LEDGER_PARITY.exists(), "LEDGER_PARITY.md missing")

    def test_has_counts_and_verdict(self):
        txt = MALKAN_LEDGER_PARITY.read_text(encoding="utf-8")
        self.assertRegex(txt, r"(?m)^-?\s*Verdict:\s*(SCORABLE|HYPOTHESIS)\b", "no valid Verdict line")
        self.assertRegex(txt, r"(?m)^-?\s*Dated calls:\s*\d+\b", "no Dated calls count line")
        self.assertRegex(txt, r"(?m)^-?\s*RSI parity points:\s*\d+\b", "no RSI parity points count line")


CRYPTOCRED_HTF_PRE_REG = ROOT / "research" / "cryptocred_htf_2026-10" / "PRE_REG_CRYPTOCRED_HTF.md"


class CryptoCredHtfPreReg(unittest.TestCase):
    """Card cryptocred-prereg-4h-1d: PRE_REG_CRYPTOCRED_HTF.md readiness check."""

    def test_file_exists(self):
        files = list(ROOT.rglob("PRE_REG_CRYPTOCRED_HTF.md"))
        self.assertTrue(len(files) > 0, "PRE_REG_CRYPTOCRED_HTF.md missing")

    def test_items_1_to_12_present_and_answered(self):
        files = list(ROOT.rglob("PRE_REG_CRYPTOCRED_HTF.md"))
        self.assertTrue(len(files) > 0, "PRE_REG_CRYPTOCRED_HTF.md missing")
        for p in files:
            with self.subTest(prereg=p.name):
                nums = item_numbers(p)
                for i in range(1, 13):
                    self.assertIn(i, nums, f"item {i} missing from {p.name}")
                txt = p.read_text(encoding="utf-8")
                self.assertNotIn("Answer: TODO", txt)
                self.assertNotIn("Evidence (file:line): TODO", txt)
                self.assertNotIn("NOT_ANSWERED", txt)
                parts = re.split(r"(?m)^## (?=\d+\. )", txt)[1:]
                self.assertGreaterEqual(len(parts), 12, "fewer than 12 numbered sections")
                item_secs = [s for s in parts if re.match(r"^([1-9]|1[0-2])\.", s)]
                self.assertEqual(len(item_secs), 12, "must have all 12 items")
                for sec in item_secs:
                    n = sec.split(".", 1)[0]
                    self.assertRegex(sec, r"(?m)^Answer:\s*\S", f"item {n}: no answer")
                    self.assertRegex(sec, r"(?m)^Evidence.*:\s*\S", f"item {n}: no evidence")

    def test_gates_0a_to_0f_answered(self):
        files = list(ROOT.rglob("PRE_REG_CRYPTOCRED_HTF.md"))
        self.assertTrue(len(files) > 0, "PRE_REG_CRYPTOCRED_HTF.md missing")
        for p in files:
            with self.subTest(prereg=p.name):
                txt = p.read_text(encoding="utf-8")
                for g in ["0a", "0b", "0c", "0d", "0e", "0f"]:
                    match = re.search(rf"(?m)^-\s*{g}\b[^\n]*:\s*(.+)$", txt)
                    self.assertIsNotNone(match, f"gate {g} missing from {p.name}")
                    ans = match.group(1).strip()
                    self.assertGreater(len(ans), 10, f"gate {g} answer too short")
                    self.assertNotIn("TODO", ans)
                    self.assertNotIn("NOT_ANSWERED", ans)


if __name__ == "__main__":
    unittest.main()

