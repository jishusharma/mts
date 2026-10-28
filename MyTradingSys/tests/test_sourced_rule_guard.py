"""sourced-rule-guard: check_sourced_params.py flags unlabelled / unquoted / unledgered layer params."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import check_sourced_params as c  # noqa: E402

LEDGER = {"Wvq1TZh8aF0"}
RULES = {"KR-Z02"}


def run(d):
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "x.json"
        p.write_text(json.dumps(d), encoding="utf8")
        return c.check_file(p, LEDGER, RULES)


def P(**v):
    return {"params": {"a": v}}


class Guard(unittest.TestCase):
    def test_good(self):
        self.assertEqual(run(P(value=1, label="SOURCED", source="KR-Z02 two is a memory")), [])
        self.assertEqual(run(P(value=1, label="SOURCED", source="x", quote="he said so")), [])
        self.assertEqual(run(P(value=1, label="OURS", source="judgement")), [])

    def test_no_label(self):
        self.assertEqual(run(P(value=1, source="KR-Z02")), [("a", "no-label")])
        self.assertEqual(run(P(value=1, label="MAYBE", source="s")), [("a", "no-label")])

    def test_no_source(self):
        self.assertEqual(run(P(value=1, label="OURS", source=" ")), [("a", "no-source")])

    def test_sourced_without_quote(self):
        self.assertEqual(run(P(value=1, label="SOURCED", source="trust me")), [("a", "sourced-no-quote")])

    def test_unknown_rule_and_ledger(self):
        self.assertEqual(run(P(value=1, label="SOURCED", source="KR-Z99 x")), [("a", "unknown-rule")])
        self.assertEqual(run(P(value=1, label="SOURCED", source="extract_AAAAAAAAAAA.md")), [("a", "not-in-ledger")])
        self.assertEqual(run(P(value=1, label="SOURCED", source="extract_Wvq1TZh8aF0.md")), [])

    def test_flat_shape(self):
        self.assertEqual(run({"source": "operator"}), [])
        self.assertEqual(run({"source": "somebody"}), [("*", "sourced-no-quote")])
        self.assertEqual(run({"source": "somebody", "min_bars_quote": "q"}), [])
        self.assertEqual(run({"note": "x"}), [("*", "no-source")])

    def test_allowlist_expiry_and_stale(self):
        item = ("f.json", "a", "no-label")
        old = c.ALLOWLIST
        try:
            c.ALLOWLIST = {item: ("owner", "2999-01-01")}
            self.assertEqual(c.evaluate(1, [item]), ([], 1))
            self.assertEqual(c.evaluate(1, [])[0][0][:5], "STALE")
            c.ALLOWLIST = {item: ("owner", "2000-01-01")}
            self.assertTrue(c.evaluate(1, [item], date(2026, 10, 28))[0][0].startswith("EXPIRED"))
        finally:
            c.ALLOWLIST = old

    def test_real_tree_clean_and_counted(self):
        n, res = c.scan(ROOT)
        self.assertGreaterEqual(n, 50)
        fails, allowed = c.evaluate(n, res)
        self.assertEqual(fails, [])
        self.assertEqual(allowed, len(c.ALLOWLIST))   # allowlist size is in the commit message
        self.assertEqual(len(c.ALLOWLIST), 0)

    def test_cli_exit_code(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/dev/check_sourced_params.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
