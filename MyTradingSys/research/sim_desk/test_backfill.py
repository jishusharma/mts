"""Backfill: every catalogue row has a result card, reachable from the desk list; nothing is invented."""
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "artifact"))

import backfill_results as bf  # noqa: E402
import build_artifact as ba  # noqa: E402
import runs_view  # noqa: E402

RESULTS = os.path.join(HERE, "results")


def cat():
    return json.load(open(os.path.join(RESULTS, "_catalogue.json"), encoding="utf-8"))


def result_ids():
    return {f[:-5] for f in os.listdir(RESULTS) if f.endswith(".json") and not f.startswith("_")}


class Counts(unittest.TestCase):
    def test_exported_count_equals_result_files(self):
        c = cat()
        self.assertEqual(c["exported"], len(result_ids()))
        self.assertEqual(c["count"], len(c["rows"]))
        self.assertEqual(c["count"], c["exported"], "every catalogued test needs a result card")

    def test_every_row_reachable_from_desk_list_and_card(self):
        listed = {r["id"] for r in runs_view.list_tests(RESULTS)}
        for r in cat()["rows"]:
            self.assertIn(r["id"], listed)
            doc = runs_view.get_test(RESULTS, r["id"])
            self.assertIsNotNone(doc, r["id"])
            self.assertIn("verdict", doc)

    def test_list_is_newest_first_and_unknown_id_refused(self):
        dates = [str(r.get("date") or "") for r in runs_view.list_tests(RESULTS)]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertIsNone(runs_view.get_test(RESULTS, "../_catalogue"))
        self.assertIsNone(runs_view.get_test(RESULTS, "not-in-catalogue"))

    def test_artifact_lists_every_catalogue_row(self):
        html = open(os.path.join(HERE, "artifact", "index.html"), encoding="utf-8").read()
        blob = re.search(r"const CAT=(\[.*?\]);\n", html, re.S).group(1)
        self.assertEqual({r["id"] for r in json.loads(blob)}, {r["id"] for r in cat()["rows"]})
        for need in ('id="kf"', 'id="vf"', 'id="ff"'):
            self.assertIn(need, html)

    def test_desk_page_has_all_tests_section(self):
        page = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
        for need in ('id="alltests"', "/api/tests", 'id="atk"', 'id="atv"', 'id="atf"'):
            self.assertIn(need, page)


class NothingInvented(unittest.TestCase):
    def setUp(self):
        bf.FILES.add("x/none.md")

    def row(self, **kw):
        r = {"id": "st-x", "family": "f", "title": "T", "kind": "backtest", "verdict": "FAIL", "status": "FAILED",
             "source": "x/none.md", "date": "2026-01-01"}
        r.update(kw)
        return r

    def test_missing_source_gives_nulls_with_reasons(self):
        res = bf.build(self.row())
        self.assertIsNone(res["window"])
        self.assertEqual(res["kpis"], [])
        for k in ("n_trades", "net_r", "window", "parameters", "why"):
            self.assertIn(k, res["missing"])
        self.assertEqual(res["provenance"], "source-extracted")

    def test_all_backfilled_files_are_valid_and_labelled(self):
        for t in ba.collect(RESULTS):
            if t.get("provenance") == "source-extracted":
                self.assertIn("missing", t)
                for e in t["evidence"]:
                    self.assertTrue(e["quote"])
                for w in t["what"]:
                    self.assertIn(w["label"], ("SOURCED", "OURS"))


if __name__ == "__main__":
    unittest.main()
