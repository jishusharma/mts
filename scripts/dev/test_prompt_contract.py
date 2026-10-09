"""Tests for prompt_contract.py (B155). Expected outcomes come from DSA_SESSION_PROMPT.md section 5d, not from the code:
30 lines max; opening Session ID / Mode / Repo root / TASK; three named blocks; no unstated restriction; no restated
hard rules or state; screen only."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prompt_contract as pc  # noqa: E402

GOOD = """Session ID: MTS-2026-10-10-0100Z-APP-BLD-x
Mode: App
Repo root: C:/repo
TASK: fix B999 with a failing test first.
DSA-side work already done: read BUGS.md row B999.
Collision check: disjoint from in-flight sessions.
Registry work DSA will do after: flip B999 in BUGS.md."""
NOREF = set()


def fails(text, **kw):
    return pc.check_prompt(text, reference=NOREF, **kw)


class TestPromptContract(unittest.TestCase):
    def test_good_prompt_passes(self):
        self.assertEqual(fails(GOOD), [])

    def test_31_lines_fail_30_pass(self):
        base = GOOD.splitlines()
        ok = "\n".join(base + ["x"] * (30 - len(base)))
        self.assertEqual(len(ok.splitlines()), 30)
        self.assertEqual(fails(ok), [])
        self.assertTrue(any(f.startswith("lines:") for f in fails(ok + "\nx")))

    def test_each_named_block_is_required(self):
        for name in ("DSA-side work already done", "Collision check", "Registry work DSA will do after"):
            txt = GOOD.replace(name, "Other heading")
            self.assertTrue(any(f.startswith("blocks:") and name.lower() in f for f in fails(txt)), name)

    def test_opening_sequence_order_matters(self):
        l = GOOD.splitlines()
        swapped = "\n".join([l[1], l[0]] + l[2:])
        self.assertTrue(any(f.startswith("opening:") for f in fails(swapped)))
        self.assertTrue(any(f.startswith("opening:") for f in fails(GOOD.replace("TASK:", "Goal:"))))

    def test_blank_lines_before_opening_are_ignored(self):
        self.assertEqual(fails("\n\n" + GOOD), [])

    def test_restriction_word_fails_unless_operator_set(self):
        bad = GOOD + "\nDo not read the .secrets folder."
        self.assertTrue(any(f.startswith("restrict:") for f in fails(bad)))
        self.assertEqual([f for f in fails(GOOD + "\nNever touch mainnet. OPERATOR-SET") if f.startswith("restrict:")], [])
        self.assertEqual([f for f in fails(GOOD + '\n"never touch mainnet", operator 2026-10-08') if f.startswith("restrict:")], [])

    def test_restated_rule_line_fails(self):
        rule = "Testnet only (Deribit test); never mainnet; never read the secrets folder"
        ref = {rule}
        out = pc.check_prompt(GOOD + "\n- " + rule, reference=ref)
        self.assertTrue(any(f.startswith("restated:") for f in out))

    def test_short_lines_are_not_treated_as_restated(self):
        self.assertEqual(pc.check_prompt(GOOD, reference={"Mode: App"}), [])

    def test_prompt_file_inside_repo_is_refused_outside_is_fine(self):
        self.assertTrue(any(f.startswith("screen:") for f in fails(GOOD, source_path=pc.REPO / "tmp_prompt.txt")))
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(fails(GOOD, source_path=Path(d) / "p.txt"), [])

    def test_real_reference_files_load(self):
        self.assertGreater(len(pc._reference_lines()), 20)


if __name__ == "__main__":
    unittest.main()
