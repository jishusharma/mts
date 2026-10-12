"""Guard: every pointer in MyTradingSys/system/layer_index.json exists, and every family has a spec and a status.
Run: python -m unittest tests.test_layers_index   (repo root)
"""
import json
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import make_layers_md as m  # noqa: E402


class LayersIndex(unittest.TestCase):
    def setUp(self):
        self.idx = json.loads(m.IDX.read_text(encoding="utf-8"))

    def test_no_dead_pointers(self):
        self.assertEqual(m.missing_paths(self.idx), [])

    def test_every_family_has_spec_and_status(self):
        for f in self.idx["families"]:
            self.assertTrue(f["spec"] and f["status"], f["id"])

    def test_claude_md_links_layers(self):
        self.assertIn("system/LAYERS.md", (REPO / "CLAUDE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
