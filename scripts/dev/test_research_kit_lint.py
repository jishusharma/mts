"""Tests for scripts/dev/research_kit_lint.py on a fixture tree (report-only, exits 0)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LINT = Path(__file__).resolve().parent / "research_kit_lint.py"


def put(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def run_lint(root, allow):
    p = subprocess.run([sys.executable, str(LINT), "--root", str(root), "--allow", str(allow)],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


class LintTest(unittest.TestCase):
    def test_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            put(root, "MyTradingSys/backtest/research_kit.py", "def holm(p):\n    return p\n")
            put(root, "MyTradingSys/research/a/old.py", "def holm_p(p):\n    return p\n")
            put(root, "MyTradingSys/research/a/new.py", "def cluster_se(v, days):\n    return 0\n")
            put(root, "MyTradingSys/research/a/good.py",
                "from research_kit import holm\n\ndef holm_wrap(p):\n    return holm(p)\n")
            put(root, "MyTradingSys/research/a/test_x.py", "def holm_fake():\n    pass\n")
            put(root, "MyTradingSys/research/a/pivots.py", "def _cluster(pivots, tol):\n    return pivots\n")
            put(root, "MyTradingSys/backtest/bt.py", "def day_cluster_mean(x):\n    return x\n")
            put(root, "allow.tsv",
                "path\tfunctions\tnote\nMyTradingSys/research/a/old.py\tholm_p\texisting\n"
                "MyTradingSys/research/a/gone.py\tholm\tstale\n")
            rc, out = run_lint(root, root / "allow.tsv")
            self.assertEqual(rc, 0)
            self.assertIn("NEW", out)
            self.assertIn("MyTradingSys/research/a/new.py", out)
            self.assertIn("MyTradingSys/backtest/bt.py", out)
            new_part = out.split("ALLOWED")[0]
            self.assertNotIn("old.py", new_part)
            self.assertNotIn("good.py", out)
            self.assertNotIn("test_x.py", out)
            self.assertNotIn("pivots.py", out)
            self.assertIn("old.py", out.split("ALLOWED")[1])
            self.assertIn("STALE", out)
            self.assertIn("gone.py", out)

    def test_missing_allowlist_exits_zero(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            put(root, "MyTradingSys/research/a/new.py", "def holm(p):\n    return p\n")
            rc, out = run_lint(root, root / "nope.tsv")
            self.assertEqual(rc, 0)
            self.assertIn("new.py", out)


if __name__ == "__main__":
    unittest.main()
