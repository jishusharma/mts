import sys, pathlib, unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "MyTradingSys" / "observation"))
sys.path.insert(0, str(REPO / "scripts" / "dev"))

import capture
import chart_verify
import alert_rate_check


class TestTimeframeMap(unittest.TestCase):
    def test_chart_verify_tfs_equals_capture_tf_minutes(self):
        self.assertEqual(chart_verify.TFS, set(capture.TF_MINUTES) - chart_verify.FAPI_UNSUPPORTED)
        self.assertTrue(chart_verify.FAPI_UNSUPPORTED <= set(capture.TF_MINUTES))
        self.assertNotIn("4m", chart_verify.TFS)
        self.assertIn("1w", chart_verify.TFS)

    def test_alert_rate_check_keys_in_capture_tf_minutes(self):
        for k, v in alert_rate_check.TF_MIN.items():
            self.assertIn(k, capture.TF_MINUTES)
            self.assertEqual(v, capture.TF_MINUTES[k])

    def test_multiday_frames_in_capture_map(self):
        for tf, mins in {"2d": 2880, "3d": 4320, "4d": 5760, "5d": 7200}.items():
            self.assertEqual(capture.TF_MINUTES[tf], mins)
        self.assertLess(capture.TF_MINUTES["1d"], capture.TF_MINUTES["2d"])
        self.assertLess(capture.TF_MINUTES["5d"], capture.TF_MINUTES["1w"])

    def test_multiday_frames_in_chart_verify(self):
        self.assertIn("3d", chart_verify.TFS)  # exchange candle
        for tf in ("2d", "4d", "5d"):  # built from 1d, fapi has no such interval
            self.assertIn(tf, chart_verify.FAPI_UNSUPPORTED)
            self.assertNotIn(tf, chart_verify.TFS)

    def test_multiday_frames_in_timeframe_registry(self):
        import json
        reg = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text())["timeframes"]
        for tf, n in {"2d": 2, "3d": 3, "4d": 4, "5d": 5}.items():
            self.assertEqual(reg[tf]["unit"], "days")
            self.assertEqual(reg[tf]["days"], n)
            self.assertEqual(reg[tf]["days"] * 1440, __import__("capture").TF_MINUTES[tf])


if __name__ == "__main__":
    unittest.main()
