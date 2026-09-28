"""Edge-case tests for prob_table, derived from spec 033 (Dirichlet: (count+alpha)/(n+3*alpha)); numbers by hand."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prob_table as pt

F = ("vp_shape", "price_vs_va", "cvd_slope")


def rec(ts, ret, v="A"):
    return {"ts": ts, "vp_shape": v, "price_vs_va": "P", "cvd_slope": "C", "fwd_return_pct": {"60m": ret}}


class TestProbTableEdges(unittest.TestCase):
    def test_outcome_boundaries_are_flat(self):
        self.assertEqual(pt.outcome(0.2, 0.2), "FLAT")
        self.assertEqual(pt.outcome(-0.2, 0.2), "FLAT")
        self.assertEqual(pt.outcome(0.2000001, 0.2), "UP")
        self.assertEqual(pt.outcome(-0.2000001, 0.2), "DOWN")

    def test_empty_records_baseline_uniform(self):
        t = pt.build_table([], F, "60m", 0.2, 1.0)
        self.assertEqual(t["__baseline__"]["n"], 0)
        for k in ("UP", "FLAT", "DOWN"):
            self.assertAlmostEqual(t["__baseline__"][k], 1 / 3)

    def test_single_record_smoothing(self):
        t = pt.build_table([rec("2026-01-01", 1.0)], F, "60m", 0.2, 1.0)
        c = t[("A", "P", "C")]
        self.assertEqual(c["n"], 1)
        self.assertAlmostEqual(c["UP"], 2 / 4)
        self.assertAlmostEqual(c["FLAT"], 1 / 4)
        self.assertAlmostEqual(c["DOWN"], 1 / 4)

    def test_alpha_zero_gives_raw_frequencies(self):
        recs = [rec("1", 1.0), rec("2", 1.0), rec("3", -1.0), rec("4", 0.0)]
        c = pt.build_table(recs, F, "60m", 0.2, 0.0)[("A", "P", "C")]
        self.assertAlmostEqual(c["UP"], 0.5)
        self.assertAlmostEqual(c["DOWN"], 0.25)
        self.assertAlmostEqual(c["FLAT"], 0.25)

    def test_nan_none_and_missing_horizon_skipped(self):
        recs = [rec("1", float("nan")), rec("2", None),
                {"ts": "3", "vp_shape": "A", "price_vs_va": "P", "cvd_slope": "C",
                 "fwd_return_pct": {"30m": 1.0}},
                rec("4", 1.0)]
        t = pt.build_table(recs, F, "60m", 0.2, 1.0)
        self.assertEqual(t["__baseline__"]["n"], 1)

    def test_probabilities_sum_to_one(self):
        recs = [rec(str(i), r) for i, r in enumerate([1, -1, 0, 1, 1, 0.1])]
        c = pt.build_table(recs, F, "60m", 0.2, 1.0)[("A", "P", "C")]
        self.assertAlmostEqual(c["UP"] + c["FLAT"] + c["DOWN"], 1.0)

    def test_evaluate_empty_test_set(self):
        r = pt.evaluate([rec("1", 1.0)], [], min_n=1)
        self.assertEqual(r["n_test"], 0)
        self.assertEqual(r["improvement"], 0.0)

    def test_evaluate_falls_back_to_baseline_below_min_n(self):
        # train: 1 record UP -> cell n=1 < min_n=100 -> table probs == baseline probs -> improvement 0
        r = pt.evaluate([rec("1", 1.0)], [rec("2", 1.0)], min_n=100)
        self.assertAlmostEqual(r["improvement"], 0.0, places=12)
        self.assertEqual(r["cells_ge_min_n"], 0)
        # baseline UP prob = (1+1)/(1+3)=0.5 -> logloss = -ln 0.5
        self.assertAlmostEqual(r["logloss_baseline"], -math.log(0.5), places=9)

    def test_evaluate_mean_over_scored_records_only(self):
        # one scorable test record and one NaN return; mean log-loss must be over the scored one only
        r = pt.evaluate([rec("1", 1.0)], [rec("2", 1.0), rec("3", float("nan"))], min_n=100)
        self.assertAlmostEqual(r["logloss_baseline"], -math.log(0.5), places=9)


if __name__ == "__main__":
    unittest.main()
