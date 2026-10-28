"""Auto-trader ages a lagged layer alert from t_confirm (the bar it was first seen), not from its own bar."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402

BAR = 3600
T_EVENT = 1790000000000 // 3600000 * 3600000          # 1h bar open, ms
NOW = datetime.fromtimestamp(T_EVENT / 1000 + 3 * BAR + 60, timezone.utc)   # 1 min after the 2-bars-later bar closed


def _cfg():
    import json
    c = json.loads(json.dumps(at.DEFAULT_CONFIG))
    c["pre_pipeline_sources"] = {"layer:": {"reason": "test fixture", "review_by": "2026-10-23"}, "tom": {"reason": "test fixture", "review_by": "2026-10-23"}}   # fable H1: not testing the promotion gate here
    return c


class TestConfirmAge(unittest.TestCase):
    def test_lagged_alert_fresh_by_t_confirm(self):
        a = {"layer": "fabio", "sub": "volume_fvg", "event": "e", "side": "long", "tf": "1h",
             "t_close": T_EVENT, "t_confirm": T_EVENT + 2 * BAR * 1000}
        self.assertNotIn("reject", at.layer_signal(a, _cfg(), NOW))

    def test_same_alert_without_t_confirm_is_stale(self):
        a = {"layer": "fabio", "sub": "volume_fvg", "event": "e", "side": "long", "tf": "1h", "t_close": T_EVENT}
        self.assertIn("stale", at.layer_signal(a, _cfg(), NOW)["reject"])

    def test_old_t_confirm_still_stale(self):
        a = {"layer": "fabio", "sub": "volume_fvg", "event": "e", "side": "long", "tf": "1h",
             "t_close": T_EVENT, "t_confirm": T_EVENT + 2 * BAR * 1000}
        late = datetime.fromtimestamp(NOW.timestamp() + 2 * BAR, timezone.utc)
        self.assertIn("stale", at.layer_signal(a, _cfg(), late)["reject"])


if __name__ == "__main__":
    unittest.main()
