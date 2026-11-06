"""ci.yml flake floor (SHIP_TRAIN.md card 1): failed shards rerun once; docs-only pushes get the docs-integrity lane."""
import re
import subprocess
import unittest
from pathlib import Path

CI = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


class FlakeFloorTest(unittest.TestCase):
    def setUp(self):
        self.s = CI.read_text(encoding="utf-8")

    def test_gate_step_reruns_a_failed_shard_once(self):
        run = "python scripts/dev/run_all_tests.py --shard ${{ matrix.shard }}"
        self.assertEqual(self.s.count(run), 2, "first try plus exactly one rerun")
        self.assertRegex(self.s, re.escape(run) + r" \|\| \{")

    def test_docs_only_lane_exists_and_gates_the_full_gate(self):
        self.assertIn("docs-integrity:", self.s)
        self.assertIn("MyTradingSys/tests/docs", self.s)
        self.assertIn("needs.changes.outputs.docs_only != 'true'", self.s)
        self.assertIn("'**/*.md'", self.s)

    def test_green_needs_either_lane_and_no_failure(self):
        for job in ("auto-merge", "mark-green"):
            block = self.s.split("\n  %s:\n" % job)[1].split("\n  # ")[0]
            self.assertIn("needs: [offline-gate, docs-integrity]", block)
            self.assertIn("!contains(needs.*.result, 'failure')", block)
            self.assertIn("needs.docs-integrity.result == 'success'", block)

    def test_docs_only_regexp_matches_every_code_path_filter(self):
        paths = re.search(r"push:\n    branches.*?paths:\n(.*?)\n  pull_request", self.s, re.S).group(1)
        code = re.search(r"code='(.*?)'\n", self.s).group(1)
        for line in paths.splitlines():
            p = line.split("#")[0].strip().lstrip("- ").strip("'")
            if not p or p.startswith("**/") or p == "MyTradingSys/system/**":
                continue                                            # the docs lane's own triggers
            sample = p.replace("**/*.py", "x.py").replace("**", "x")
            self.assertTrue(re.search(code, sample), "docs-only regexp would call %s docs-only" % p)

    def test_docs_only_regexp_passes_a_doc_and_fails_code(self):
        code = re.search(r"code='(.*?)'\n", self.s).group(1)
        self.assertFalse(re.search(code, "MyTradingSys/system/ROUTING.md"))
        self.assertFalse(re.search(code, "README.md"))
        self.assertTrue(re.search(code, "scripts/dev/sync.py"))
        self.assertTrue(re.search(code, "MyTradingSys/system/tasks/a.md"))


if __name__ == "__main__":
    unittest.main()