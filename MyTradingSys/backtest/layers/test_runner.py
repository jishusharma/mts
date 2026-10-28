import unittest

from MyTradingSys.backtest.layers.runner import forward_return_stats, baseline_return_stats, build_manifest


class TestForwardReturnStats(unittest.TestCase):
    """layers/TEST_PLAN_runner.md Case R1/R2."""

    def test_r1_mixed_long_short_horizon_runs_out(self):
        closes = [100, 102, 101, 104, 103, 105, 108, 107, 110, 112]
        events = [{"i": 2, "side": "long"}, {"i": 5, "side": "short"}]
        got = forward_return_stats(events, closes, horizons=(1, 3, 5, 10, 20))

        self.assertEqual(got[1]["n"], 2)
        self.assertAlmostEqual(got[1]["mean_return"], 0.000566, delta=1e-4)
        self.assertAlmostEqual(got[1]["hit_rate"], 0.5, delta=1e-9)
        self.assertAlmostEqual(got[1]["mae"], 0.000566, delta=1e-4)

        self.assertEqual(got[3]["n"], 2)
        self.assertAlmostEqual(got[3]["mean_return"], -0.004008, delta=1e-4)
        self.assertAlmostEqual(got[3]["hit_rate"], 0.5, delta=1e-9)
        self.assertAlmostEqual(got[3]["mae"], -0.013909, delta=1e-4)

        self.assertEqual(got[5]["n"], 1)
        self.assertAlmostEqual(got[5]["mean_return"], 0.059406, delta=1e-4)
        self.assertAlmostEqual(got[5]["hit_rate"], 1.0, delta=1e-9)
        self.assertAlmostEqual(got[5]["mae"], 0.019802, delta=1e-4)

        for h in (10, 20):
            self.assertEqual(got[h]["n"], 0)
            self.assertIsNone(got[h]["mean_return"])
            self.assertIsNone(got[h]["hit_rate"])
            self.assertIsNone(got[h]["mae"])

    def test_r2_empty_events(self):
        closes = [100, 102, 101, 104, 103, 105, 108, 107, 110, 112]
        got = forward_return_stats([], closes, horizons=(1, 3))
        self.assertEqual(got, {
            1: {"n": 0, "mean_return": None, "hit_rate": None, "mae": None},
            3: {"n": 0, "mean_return": None, "hit_rate": None, "mae": None},
        })


class TestBaselineReturnStats(unittest.TestCase):
    """Case R3."""

    def test_r3_long_only_over_every_bar_h1(self):
        closes = [100, 102, 101, 104, 103, 105, 108, 107, 110, 112]
        got = baseline_return_stats(closes, horizons=(1,))
        self.assertEqual(got[1]["n"], 9)
        self.assertAlmostEqual(got[1]["mean_return"], 0.012804, delta=1e-4)
        self.assertAlmostEqual(got[1]["hit_rate"], 0.666667, delta=1e-4)


class TestBuildManifest(unittest.TestCase):
    """Case R4/R5."""

    def test_r4_required_fields_plus_run_id(self):
        manifest = build_manifest(
            revision_hash="abc123",
            params_id="rsi_default_2026-09-28",
            data_file_hashes={"BTCUSDT_1m.csv": "sha256:deadbeef"},
            command="python layers/runner.py --tf 1h",
            start="2026-09-28T00:00:00Z",
            end="2026-09-28T00:05:00Z",
            row_counts={"BTCUSDT_1m.csv": 43200},
        )
        self.assertEqual(manifest["revision_hash"], "abc123")
        self.assertEqual(manifest["params_id"], "rsi_default_2026-09-28")
        self.assertEqual(manifest["data_file_hashes"], {"BTCUSDT_1m.csv": "sha256:deadbeef"})
        self.assertEqual(manifest["command"], "python layers/runner.py --tf 1h")
        self.assertEqual(manifest["start"], "2026-09-28T00:00:00Z")
        self.assertEqual(manifest["end"], "2026-09-28T00:05:00Z")
        self.assertEqual(manifest["row_counts"], {"BTCUSDT_1m.csv": 43200})
        self.assertIn("run_id", manifest)
        self.assertTrue(manifest["run_id"])

    def test_r5_missing_required_field_raises(self):
        with self.assertRaises(Exception):
            build_manifest(revision_hash="abc123")


if __name__ == "__main__":
    unittest.main()
