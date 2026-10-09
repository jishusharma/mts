"""make_groups.py: a registry row gets exactly one group (assign > title keywords > evidence keywords > UNGROUPED),
a file goes to the group with the longest path claim, and the real groups.json is internally consistent."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_groups as mg

CFG = {
    "asof": "2026-10-09",
    "groups": [
        {"code": "EXEC", "name": "Exec", "keywords": ["fee", "daily-loss", "auto_trader"], "paths": ["MyTradingSys/execution/"]},
        {"code": "DATA", "name": "Data", "keywords": ["snapshot", "open interest"], "paths": ["src/", "scripts/dev/refresh_klines.py"]},
        {"code": "OPS", "name": "Ops", "keywords": ["supervisor log", "worker"], "paths": ["scripts/dev/", "scripts/"]},
        {"code": "VIS", "name": "Vis", "keywords": ["screenshot"], "paths": ["scripts/dev/shot.py"]},
    ],
    "assign": {"B900": "OPS"},
}


def row(i, title, evidence="", status="OPEN", sev="MED"):
    return {"id": i, "opened": "2026-10-09", "status": status, "sev": sev, "title": title, "evidence": evidence}


class ClassifyTest(unittest.TestCase):
    def test_assign_beats_keywords(self):
        self.assertEqual(mg.classify(row("B900", "fee on every daily-loss event"), CFG)[0], "OPS")

    def test_title_beats_evidence(self):
        r = row("B901", "Daily-loss monitor re-authenticates as MAIN", "see supervisor log, worker restart, supervisor log")
        self.assertEqual(mg.classify(r, CFG)[0], "EXEC")

    def test_whole_words_only(self):
        # 'fee' must not fire inside 'feed', 'snapshot' must not fire inside 'snapshots_old'
        self.assertEqual(mg.classify(row("B902", "Binance feed drops"), CFG)[0], "UNGROUPED")
        self.assertEqual(mg.classify(row("B903", "snapshots_old pruned"), CFG)[0], "UNGROUPED")
        self.assertEqual(mg.classify(row("B904", "Open interest is stepped"), CFG)[0], "DATA")

    def test_nothing_matches_is_ungrouped_never_guessed(self):
        self.assertEqual(mg.classify(row("B905", "something unrelated"), CFG)[0], "UNGROUPED")

    def test_tie_goes_to_the_earlier_group(self):
        r = row("B906", "fee and snapshot")
        self.assertEqual(mg.classify(r, CFG)[0], "EXEC")


class OwnerTest(unittest.TestCase):
    def test_longest_prefix_wins(self):
        self.assertEqual(mg.owner_of("scripts/dev/shot.py", CFG), "VIS")
        self.assertEqual(mg.owner_of("scripts/dev/other.py", CFG), "OPS")
        self.assertEqual(mg.owner_of("scripts/dev/refresh_klines.py", CFG), "DATA")
        self.assertEqual(mg.owner_of("scripts/core/x.ps1", CFG), "OPS")

    def test_exact_file_claim_does_not_claim_siblings(self):
        self.assertIsNone(mg.owner_of("src2/x.java", CFG))
        self.assertEqual(mg.owner_of("scripts/dev/shot.pyc", CFG), "OPS")  # falls to the folder claim, not the file claim

    def test_unclaimed_is_none(self):
        self.assertIsNone(mg.owner_of("elsewhere/file.txt", CFG))


class CountsTest(unittest.TestCase):
    def test_open_includes_in_fix_and_blocked(self):
        items = [row("B1", "a", status="OPEN", sev="HIGH"), row("B2", "b", status="IN-FIX"), row("B3", "c", status="BLOCKED"),
                 row("B4", "d", status="CLOSED"), row("B5", "e", status="WONTFIX")]
        self.assertEqual(mg.counts(items), {"open": 3, "high": 1, "closed": 1, "wontfix": 1, "total": 5})


class RealConfigTest(unittest.TestCase):
    """Internal consistency of the checked-in groups.json. Not a gate on new bug rows: those show as UNGROUPED in --check."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = mg.load_cfg()
        cls.rows = mg.load_rows()

    def test_codes_unique_and_ten(self):
        codes = [g["code"] for g in self.cfg["groups"]]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(codes, ["DATA", "SRC", "CORE", "LAYR", "EVID", "EXEC", "VIS", "DESK", "OPS", "INFRA"])

    def test_assignments_point_at_real_groups_and_real_rows(self):
        codes = {g["code"] for g in self.cfg["groups"]}
        ids = {r["id"] for r in self.rows}
        for rid, code in self.cfg["assign"].items():
            self.assertIn(code, codes, rid)
            self.assertIn(rid, ids, rid)

    def test_every_group_has_what_the_map_prints(self):
        for g in self.cfg["groups"]:
            for k in ("name", "scope", "operator_words", "front", "surface", "live_path", "paths", "keywords", "focus", "tracker"):
                self.assertIn(k, g, g["code"])
            self.assertTrue(g["paths"] and g["keywords"] and g["front"], g["code"])

    def test_every_open_row_is_placed(self):
        # the registry as checked in must be fully grouped; a NEW row added later is reported by --check, not here
        for r in self.rows:
            if r["status"] in mg.OPEN:
                self.assertNotEqual(mg.classify(r, self.cfg)[0], "UNGROUPED", r["id"])

    def test_the_screenshot_tool_lives_in_vis(self):
        self.assertEqual(mg.owner_of("scripts/dev/shot.py", self.cfg), "VIS")
        self.assertEqual(mg.owner_of("MyTradingSys/execution/auto_trader.py", self.cfg), "EXEC")
        self.assertEqual(mg.owner_of("src/main/java/datafeed/MarketDataSnapshot.java", self.cfg), "DATA")


class RenderTest(unittest.TestCase):
    def test_map_names_every_group_and_lists_open_items_worst_first(self):
        rows = [row("B1", "snapshot low", sev="LOW"), row("B2", "snapshot high", sev="HIGH")]
        by = {"DATA": [{**r, "group": "DATA"} for r in rows]}
        cfg = {**CFG, "groups": [{**g, "name": g["name"], "scope": "s", "operator_words": "w", "front": ["f"], "surface": "x",
                                  "live_path": False, "focus": "f", "tracker": "t"} for g in CFG["groups"]]}
        text = mg.render(cfg, by, {"DATA": 2}, {})
        for code in ("EXEC", "DATA", "OPS", "VIS"):
            self.assertIn(f"## {code} - ", text)
        self.assertLess(text.index("B2 | HIGH"), text.index("B1 | LOW"))
        self.assertIn("UNGROUPED registry rows: 0", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
