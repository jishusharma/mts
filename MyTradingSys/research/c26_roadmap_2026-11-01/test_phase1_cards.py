"""The Phase 1 design looks (Q5, Q7-Q10) are on the simulator: one result card each, no prices, schema the page build accepts."""
import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RESULTS = os.path.join(REPO, "MyTradingSys", "research", "sim_desk", "results")
CARDS = {"c26-q5-touch-factors": "phase1_touch_look.py", "c26-q7-liquidation-bands": "phase1_liq_look.py",
         "c26-q8-cvd-divergence": "phase1_cvd_div.py", "c26-q9-footprint": "phase1_fp_look.py",
         "c26-q10-path-distribution": "phase1_dist_look.py"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CARD = load("phase1_card", os.path.join(HERE, "phase1_card.py"))
BUILD = load("build_artifact", os.path.join(REPO, "MyTradingSys", "research", "sim_desk", "artifact", "build_artifact.py"))


class CardWriter(unittest.TestCase):
    def test_table_drops_price_columns(self):
        t = CARD.table("t", ["take-out (UTC)", "H1", "short band above", "net"], [["10-29 11:00", "100000", "100400", "+0.5"]])
        self.assertEqual(t["cols"], ["take-out (UTC)", "net"])
        self.assertEqual(t["rows"], [["10-29 11:00", "+0.5"]])

    def test_card_fits_the_page_schema(self):
        c = CARD.card("x", "t", [CARD.P("a", "b"), CARD.FEE], "how", "v", "info", ["w"], [], [], ["phase1_card.py"])
        self.assertTrue(set(BUILD.REQUIRED) <= set(c))
        self.assertTrue(all(w["label"] in ("SOURCED", "OURS") for w in c["what"]))
        self.assertEqual(c["source_files"], [CARD.SRC + "phase1_card.py"])


class CardsOnTheSimulator(unittest.TestCase):
    def test_every_look_has_a_card_the_page_build_accepts(self):
        ids = {r["id"] for r in BUILD.collect(RESULTS)}  # raises on any malformed file, like the real build
        for id_, script in CARDS.items():
            with self.subTest(id_):
                self.assertIn(id_, ids)
                c = json.load(open(os.path.join(RESULTS, id_ + ".json"), encoding="utf-8"))
                self.assertIn(CARD.SRC + script, c["source_files"])
                self.assertTrue(c["examples"], "a look card carries its tables")
                for ex in c["examples"]:
                    self.assertFalse(set(ex["cols"]) & set(CARD.NO_PRICE), "no price column on the public page")
                    self.assertTrue(ex["rows"])


if __name__ == "__main__":
    unittest.main()
