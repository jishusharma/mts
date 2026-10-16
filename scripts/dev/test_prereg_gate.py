"""Tests for scripts/dev/prereg_gate.py: count-only MDE gate before a PRE_REG freeze (FABLE_RUNS_AUDIT E1)."""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "prereg_gate.py"


def run(*a):
    p = subprocess.run([sys.executable, str(GATE), *a], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


class PreRegGate(unittest.TestCase):
    def test_pit_count_mde_about_015_and_exit_follows_limit(self):
        # n=1835 sd=1.46 m=42: z_holm = Phi^-1(1-0.05/84) = 3.241, MDE = (3.241+0.84)*1.46/sqrt(1835) = 0.1391
        code, out = run("--n", "1835", "--sd", "1.46", "--cost", "0.10", "--m", "42")
        self.assertEqual(code, 0, out)
        self.assertIn("MDE 0.139", out)
        code, out = run("--n", "1835", "--sd", "1.46", "--cost", "0.179", "--m", "42")  # 0.139 + 0.179 = 0.318 > 0.30
        self.assertEqual(code, 1, out)
        self.assertIn("BLOCK", out)

    def test_small_n_blocks(self):
        code, out = run("--n", "200", "--sd", "1.46", "--cost", "0.179", "--m", "42")
        self.assertEqual(code, 1, out)

    def test_limit_override_and_input_errors(self):
        self.assertEqual(run("--n", "200", "--sd", "1.46", "--cost", "0.1", "--m", "42", "--max-gross", "0.6")[0], 0)
        self.assertEqual(run("--n", "0", "--sd", "1", "--cost", "0", "--m", "1")[0], 2)


if __name__ == "__main__":
    unittest.main()
