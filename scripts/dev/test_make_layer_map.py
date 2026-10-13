"""Layer map generator: curated rows are consistent and the page renders."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CFG = REPO / "MyTradingSys" / "system" / "layer_map.json"


class LayerMapTest(unittest.TestCase):
    def test_rows_reference_known_layers_and_reports(self):
        cfg = json.loads(CFG.read_text(encoding="utf-8"))
        ids = {l["id"] for l in cfg["layers"]}
        self.assertEqual(len(ids), len(cfg["layers"]), "duplicate layer id")
        for b in cfg["backtests"]:
            self.assertTrue(set(b["layers"]) <= ids, b["id"])
            self.assertTrue((REPO / b["report"]).exists(), b["report"])
            self.assertIn(b.get("read"), ("summary", "header"), b["id"])

    def test_generator_writes_page(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "m.html"
            r = subprocess.run([sys.executable, str(REPO / "scripts" / "dev" / "make_layer_map.py"), "--out", str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("cannot run a backtest", html)
            self.assertNotIn("__DATA__", html)


if __name__ == "__main__":
    unittest.main()
