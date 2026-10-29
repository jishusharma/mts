"""Tests for eagle_gaps.py on a synthetic repo (each kind must fire on a planted gap)."""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import eagle_gaps


def mk(root):
    s = root / "MyTradingSys" / "system"; (s / "tasks").mkdir(parents=True)
    (root / "a.py").write_text("x", encoding="utf-8")
    (s / "layer_index.json").write_text(json.dumps({"families": [
        {"id": "f1", "code": ["a.py"], "spec": ["missing/spec.md"], "layers": ["l1"]},
        {"id": "f2", "layers": []}]}), encoding="utf-8")
    (s / "layer_map.json").write_text(json.dumps({"layers": [
        {"id": "l1", "module": "a.py"}, {"id": "l2", "module": "gone/b.py"}],
        "backtests": [{"id": "B1", "layers": ["l1", "zz"], "report": None, "verdict": None,
                       "fees": None, "split": "x", "n": "1"}]}), encoding="utf-8")
    (s / "tasks" / "c1.json").write_text(json.dumps({"id": "c1", "state": "open", "layers": ["f1", "nofam"]}), encoding="utf-8")
    (s / "tasks" / "c2.json").write_text(json.dumps({"id": "c2", "state": "done", "layers": ["f2"]}), encoding="utf-8")


class T(unittest.TestCase):
    def test_kinds(self):
        with tempfile.TemporaryDirectory() as d:
            mk(Path(d)); got = {(k, o) for k, o, _ in eagle_gaps.gaps(d)}
        for want in [("PATH_MISSING", "family:f1"), ("PATH_MISSING", "layer:l2"), ("LAYER_NO_BACKTEST", "layer:l2"),
                     ("LAYER_NO_FAMILY", "layer:l2"), ("BT_UNKNOWN_LAYER", "backtest:B1"), ("BT_NO_REPORT", "backtest:B1"),
                     ("BT_NO_VERDICT", "backtest:B1"), ("BT_FIELD_NULL", "backtest:B1"), ("FAMILY_NO_CODE", "family:f2"),
                     ("FAMILY_NO_CARD", "family:f2"), ("CARD_DEAD_LAYER", "card:c1")]:
            self.assertIn(want, got)
        self.assertNotIn(("FAMILY_NO_CARD", "family:f1"), got)
        self.assertNotIn(("LAYER_NO_BACKTEST", "layer:l1"), got)


if __name__ == "__main__":
    unittest.main()
