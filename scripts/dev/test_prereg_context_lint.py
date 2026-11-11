"""Tests for scripts/dev/prereg_context_lint.py on a fixture tree (a gate: exit 1 on an offender).
Written 2026-11-04 before the lint existed: `test_new_prereg_without_context_fails` failed with ImportError on the pre-change tree."""
import tempfile
import unittest
from pathlib import Path

import prereg_context_lint as lint

GOOD_CONTEXT = ("# PRE_REG x\n\n## Context\n- Regime: daily close vs SMA200 side; weekly RSI band (SOURCED Malkan)\n"
                "- Phase: retest after a 15m break (tf_break class R)\n- Session: none, because the rule is daily\n"
                "- Entry: first pullback to the signal level within 8 bars\n\n## Rules\n...\n")


def put(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


class PreRegContextLint(unittest.TestCase):
    def test_new_prereg_without_context_fails(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            put(root, "MyTradingSys/research/old_2026-10/PRE_REG.md", "# frozen before the rule\n")
            put(root, "MyTradingSys/research/new_2026-11/PRE_REG.md", "# PRE_REG\n## Rules\nbuy the cross\n")
            allow = {"MyTradingSys/research/old_2026-10/PRE_REG.md"}
            offenders, stale = lint.lint(root, allow)
            self.assertEqual(stale, [])
            self.assertEqual([o[0] for o in offenders], ["MyTradingSys/research/new_2026-11/PRE_REG.md"])
            self.assertIn("Regime:, Phase:, Session:, Entry:", offenders[0][1])
            self.assertEqual(lint.main(["--root", str(root), "--allow", str(root / "none.tsv")]), 1)

    def test_plain_prereg_md_without_context_is_an_offender(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            put(root, "MyTradingSys/research/s_1112/PREREG.md", "# PREREG" + chr(10) + "## Rules" + chr(10) + "buy" + chr(10))
            put(root, "MyTradingSys/research/ok_1112/PREREG.md", GOOD_CONTEXT)
            offenders, _ = lint.lint(root, set())
            self.assertEqual([o[0] for o in offenders], ["MyTradingSys/research/s_1112/PREREG.md"])
            self.assertEqual(lint.main(["--root", str(root), "--allow", str(root / "none.tsv")]), 1)

    def test_partial_context_names_the_missing_lines(self):
        text = "# p\n## Context\nRegime: none, because daily\nPhase: break\n## Rules\n"
        self.assertEqual(lint.context_missing(text), ["Session:", "Entry:"])
        self.assertEqual(lint.context_missing(GOOD_CONTEXT), [])
        self.assertEqual(lint.context_missing("# p\n## Context\nRegime:\n"), ["Regime:", "Phase:", "Session:", "Entry:"])  # empty value

    def test_result_needs_regime_mix(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            put(root, "MyTradingSys/research/new/PRE_REG.md", GOOD_CONTEXT)
            put(root, "MyTradingSys/research/new/RESULT.md", "# result\nmean +0.1\n")
            offenders, _ = lint.lint(root, set())
            self.assertEqual([o[0] for o in offenders], ["MyTradingSys/research/new/RESULT.md"])
            put(root, "MyTradingSys/research/new/RESULT.md", "# result\n**Regime mix:** 40% bear / 35% range / 25% bull weeks\n")
            offenders, _ = lint.lint(root, set())
            self.assertEqual(offenders, [])
            self.assertEqual(lint.main(["--root", str(root), "--allow", str(root / "none.tsv")]), 0)

    def test_allowlist_round_trip_and_stale(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            put(root, "MyTradingSys/research/a/PRE_REG_v2.md", "# no context, frozen earlier\n")
            put(root, "MyTradingSys/research/_archive/b/PRE_REG.md", "# archived, never scanned\n")
            allow = root / "allow.tsv"
            self.assertEqual(lint.main(["--root", str(root), "--allow", str(allow), "--write-allow"]), 0)
            self.assertEqual(lint.read_allow(allow), {"MyTradingSys/research/a/PRE_REG_v2.md"})
            self.assertEqual(lint.main(["--root", str(root), "--allow", str(allow)]), 0)
            _, stale = lint.lint(root, lint.read_allow(allow) | {"MyTradingSys/research/gone/PRE_REG.md"})
            self.assertEqual(stale, ["MyTradingSys/research/gone/PRE_REG.md"])


if __name__ == "__main__":
    unittest.main()
