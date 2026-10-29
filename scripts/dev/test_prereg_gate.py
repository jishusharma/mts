"""Tests for scripts/dev/prereg_gate.py: count-only MDE gate before a PRE_REG freeze (FABLE_RUNS_AUDIT E1)."""
import subprocess
import sys
import unittest
from statistics import NormalDist
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "prereg_gate.py"


def run(*a):
    p = subprocess.run([sys.executable, str(GATE), *a], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


def independent_z(m):
    """Spec-derived two-sided Holm critical z, independent of prereg_gate.py."""
    return NormalDist().inv_cdf(1 - 0.05 / (2 * m))


def independent_mde(n, sd, m):
    return (independent_z(m) + 0.84) * sd / n**0.5


def independent_need_n(sd, m, cost, max_gross=0.30):
    return ((independent_z(m) + 0.84) * sd / (max_gross - cost)) ** 2


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

    def test_z_holm_m1_matches_independent_quantile(self):
        expected = independent_z(1)
        code, out = run("--n", "100000", "--sd", "1.5", "--cost", "0", "--m", "1")
        self.assertEqual(code, 0, out)
        self.assertIn(f"z_holm {expected:.3f}", out)

    def test_z_holm_m5_matches_independent_quantile(self):
        expected = independent_z(5)
        code, out = run("--n", "100000", "--sd", "1.5", "--cost", "0", "--m", "5")
        self.assertEqual(code, 0, out)
        self.assertIn(f"z_holm {expected:.3f}", out)

    def test_z_holm_m9_matches_independent_quantile(self):
        expected = independent_z(9)
        code, out = run("--n", "100000", "--sd", "1.5", "--cost", "0", "--m", "9")
        self.assertEqual(code, 0, out)
        self.assertIn(f"z_holm {expected:.3f}", out)

    def test_mde_independent_point_small_n(self):
        expected = independent_mde(100, 1.2, 1)
        code, out = run("--n", "100", "--sd", "1.2", "--cost", "0", "--m", "1")
        self.assertEqual(code, 1, out)
        self.assertIn(f"MDE {expected:.3f} R", out)

    def test_mde_independent_point_mid_n(self):
        expected = independent_mde(1000, 2, 5)
        code, out = run("--n", "1000", "--sd", "2", "--cost", "0", "--m", "5")
        self.assertEqual(code, 0, out)
        self.assertIn(f"MDE {expected:.3f} R", out)

    def test_mde_independent_point_large_n(self):
        expected = independent_mde(5000, 3, 9)
        code, out = run("--n", "5000", "--sd", "3", "--cost", "0", "--m", "9")
        self.assertEqual(code, 0, out)
        self.assertIn(f"MDE {expected:.3f} R", out)

    def test_exact_gross_limit_passes(self):
        n, sd, m = 100, 1.05, 1
        expected = independent_mde(n, sd, m)
        cost = 0.30 - expected
        code, out = run("--n", str(n), "--sd", str(sd), "--cost", format(cost, ".17g"), "--m", str(m))
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)
        self.assertIn("= 0.300 vs max plausible gross 0.3", out)

    def test_just_above_gross_limit_blocks(self):
        n, sd, m = 100, 1.05, 1
        cost = 0.30 - independent_mde(n, sd, m) + 1e-6
        code, out = run("--n", str(n), "--sd", str(sd), "--cost", format(cost, ".17g"), "--m", str(m))
        self.assertEqual(code, 1, out)
        self.assertIn("BLOCK", out)

    def test_sd_one_requires_source_but_just_above_one_is_valid(self):
        code, out = run("--n", "10000", "--sd", "1", "--cost", "0", "--m", "1")
        self.assertEqual(code, 2, out)
        code, out = run("--n", "10000", "--sd", "1.0001", "--cost", "0", "--m", "1")
        self.assertEqual(code, 0, out)
        self.assertIn("MDE", out)

    def test_cost_at_or_above_limit_has_infinite_n_needed(self):
        for cost in ("0.30", "0.31"):
            with self.subTest(cost=cost):
                code, out = run("--n", "100", "--sd", "2", "--cost", cost, "--m", "1")
                self.assertEqual(code, 1, out)
                self.assertIn("n needed inf", out)

    def test_finite_n_needed_matches_independent_formula(self):
        expected = independent_need_n(sd=1.2, m=5, cost=0.05)
        code, out = run("--n", "200", "--sd", "1.2", "--cost", "0.05", "--m", "5")
        self.assertEqual(code, 1, out)
        self.assertIn(f"n needed {expected:.0f}", out)


if __name__ == "__main__":
    unittest.main()
