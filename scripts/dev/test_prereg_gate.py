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

    def test_sd_at_or_below_one_needs_a_source(self):
        # gate-fix-1: sd 1.0 is the unmeasured placeholder (GATE_AUDIT Q1); the sd must be the sd of per-event R
        code, out = run("--n", "678", "--sd", "1", "--cost", "0.597", "--m", "8")
        self.assertEqual(code, 2, out)
        code, out = run("--n", "678", "--sd", "1", "--cost", "0.597", "--m", "8", "--sd-source", "x.md:1")
        self.assertEqual(code, 1, out)  # sourced: runs, cost 0.597 > 0.30 blocks
        code, out = run("--n", "678", "--sd", "1.4", "--cost", "0.597", "--m", "8")
        self.assertEqual(code, 1, out)
        # z_holm(8) = 2.734; MDE = 3.574 * 1.4 / sqrt(678) = 0.192 R
        self.assertIn("MDE 0.192 R", out)

    def test_m_auto_counts_dev_rows_plus_new_cells(self):
        # gate-fix-3: 3 distinct DEV (study, arm) rows + 2 new cells = m 5; z_holm(5) = Phi^-1(0.995) = 2.576
        import tempfile
        nl = chr(10)
        lines = ["study_dir,family,arm,split_read,n,gross_mean_pct,se_pct,cost_pct,verdict,kill_scope,one_run,commit,date",
                 "s1,f,a,DEV,1,0,0,0,FAIL,none,no,c,d", "s1,f,b,DEV+VALIDATION,1,0,0,0,FAIL,none,no,c,d",
                 "s2,f,(study),DEV,1,0,0,0,FAIL,none,no,c,d", "s3,f,(study),VALIDATION,1,0,0,0,FAIL,none,no,c,d"]
        with tempfile.TemporaryDirectory() as d:
            fx = Path(d) / "v.csv"
            fx.write_text(nl.join(lines) + nl, newline=nl, encoding="utf-8")
            code, out = run("--n", "678", "--sd", "1.4", "--cost", "0.1", "--m", "auto", "--new-cells", "2", "--verdicts-csv", str(fx))
            self.assertIn("m 5 ", out)
            self.assertIn("z_holm 2.576", out)
            code, out = run("--n", "678", "--sd", "1.4", "--cost", "0.1", "--m", "auto", "--verdicts-csv", str(fx))
            self.assertIn("m 3 ", out)
            self.assertEqual(run("--n", "678", "--sd", "1.4", "--cost", "0.1", "--m", "7")[0], 0)


if __name__ == "__main__":
    unittest.main()
