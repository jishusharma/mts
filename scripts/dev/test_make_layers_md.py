"""make_layers_md.py: the per-layer index has no dead pointer, every layer_map layer has exactly one family, and
cards, backtests and Codex lab reports land under the right family. Run: python scripts/dev/test_make_layers_md.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_layers_md as M

REPO = M.REPO


def fixture(root):
    s = Path(root) / M.SYS
    (s / "tasks").mkdir(parents=True)
    (Path(root) / M.LAB).mkdir(parents=True)
    (Path(root) / "spec.md").write_text("x", encoding="utf-8")
    (Path(root) / "bt.md").write_text("x", encoding="utf-8")
    idx = {"families": [{"id": "tom", "name": "Tom", "status": "redefining", "tracks": "Claude", "layers": ["tom_core"],
                         "spec": ["spec.md"], "code": [], "ledger": [], "results": ["bt.md"], "roadmap": [], "cards": ["lab-dax-*"]},
                        {"id": "rsi", "name": "RSI", "status": "closed", "tracks": "Claude", "layers": ["rsi_div"],
                         "spec": ["spec.md"], "code": [], "ledger": [], "results": [], "roadmap": [], "cards": []}],
           "cross_cutting": []}
    lmap = {"layers": [{"id": "tom_core", "status": "STOP", "module": "a.java"}, {"id": "rsi_div", "status": "no edge", "module": "r.py"}],
            "backtests": [{"id": "TOM-1", "date": "2026-10-07", "layers": ["tom_core"], "verdict": "no edge", "report": "bt.md"}]}
    (s / "layer_index.json").write_text(json.dumps(idx), encoding="utf-8")
    (s / "layer_map.json").write_text(json.dumps(lmap), encoding="utf-8")
    for c in ({"id": "spike-fade", "state": "ready", "prio": 1, "lane": "SONNET", "title": "Spike fade", "layers": ["tom"]},
              {"id": "lab-dax-gate", "state": "ready", "prio": 1, "lane": "CODEX", "title": "Gate"},
              {"id": "old-rsi", "state": "done", "prio": 2, "lane": "SONNET", "title": "Old", "layers": ["rsi"]}):
        (s / "tasks" / f"{c['id']}.json").write_text(json.dumps(c), encoding="utf-8")
    (Path(root) / M.LAB / "2026-10-12_lab-dax-gate.md").write_text("r", encoding="utf-8")
    return idx, lmap


class RealIndexTest(unittest.TestCase):
    def test_repo_index_has_no_dead_pointer_and_owns_every_layer(self):
        idx, lmap, _, _ = M.load(REPO)
        self.assertEqual(M.problems(idx, lmap, REPO), [])

    def test_claude_md_and_codex_lab_link_the_page(self):
        for doc in ("CLAUDE.md", "MyTradingSys/system/LAYER_LAB.md"):
            self.assertIn("LAYERS.md", (REPO / doc).read_text(encoding="utf-8"), doc)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)
        self.idx, self.lmap = fixture(self.root)

    def tearDown(self):
        self.d.cleanup()

    def section(self, text, fid):
        return text.split(f"(`{fid}`)")[1].split("\n## ")[0]

    def test_cards_backtests_and_lab_reports_land_in_their_family(self):
        self.assertEqual(M.write(self.root), [])
        text = (self.root / M.SYS / "LAYERS.md").read_text(encoding="utf-8")
        tom, rsi = self.section(text, "tom"), self.section(text, "rsi")
        self.assertIn("`spike-fade`", tom)                    # by the card's layers field
        self.assertIn("`lab-dax-gate`", tom)                  # Codex card without the field: id glob
        self.assertIn("2026-10-12_lab-dax-gate.md", tom)      # its lab report through the card id
        self.assertIn("`TOM-1`: no edge", tom)                # layer_map backtest row
        self.assertNotIn("Other results", tom)                # bt.md already listed as a backtest: not twice
        self.assertIn("Open cards: none", rsi)                # done cards are not open
        self.assertNotIn("old-rsi", text)

    def test_unowned_layer_double_owner_and_dead_pointer_are_errors(self):
        self.lmap["layers"].append({"id": "volume", "status": "?", "module": "v.py"})
        self.idx["families"][1]["layers"].append("tom_core")
        self.idx["families"][0]["spec"].append("gone.md")
        bad = " | ".join(M.problems(self.idx, self.lmap, self.root))
        for want in ("volume has no family", "tom_core is in more than one family", "missing gone.md"):
            self.assertIn(want, bad)


if __name__ == "__main__":
    unittest.main()
