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
        self.assertEqual(chart_verify.TFS, set(capture.TF_MINUTES))

    def test_alert_rate_check_keys_in_capture_tf_minutes(self):
        for k, v in alert_rate_check.TF_MIN.items():
            self.assertIn(k, capture.TF_MINUTES)
            self.assertEqual(v, capture.TF_MINUTES[k])


if __name__ == "__main__":
    unittest.main()
