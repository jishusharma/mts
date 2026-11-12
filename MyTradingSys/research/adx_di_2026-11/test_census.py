"""test_census.py - synthetic cross: hand-built bars, expected rows computed by hand."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402


def bars_from(h, l, c, t0=0):
    return [{"t": t0 + i * 2 * 86400000, "h": h[i], "l": l[i], "c": c[i]} for i in range(len(c))]


class TestCensus(unittest.TestCase):
    def test_red_cross_depth_and_whipsaw(self):
        # n = 1 collapses Wilder smoothing to the raw bar: DI+ = 100*+DM/TR, DI- = 100*-DM/TR.
        # bar1 up (+DM 2, TR 2) -> DI+ > DI-; bar2 down (-DM 3, TR 3) -> red cross at i=2; bar3 up -> green (whipsaw1 yes)
        h = [10, 12, 11, 13, 13, 13]
        l = [8, 10, 8, 11, 11, 11]
        c = [9, 11, 9, 12, 12, 12]
        rows = census.cross_rows(bars_from(h, l, c), n=1, fwd=3, slope=1)
        self.assertEqual([(r["i"], r["dir"]) for r in rows], [(2, "red"), (3, "green")])
        r = rows[0]
        self.assertTrue(r["ws1"])
        # forward window bars 3..5, lowest low 11 at offset 1: depth 11/9 - 1
        self.assertEqual(r["bars_to"], 1)
        self.assertAlmostEqual(r["depth"], 11 / 9 - 1)
        self.assertIsNone(rows[1]["depth"])   # only 2 bars after the green cross, fwd = 3

    def test_bucket(self):
        self.assertEqual([census.bucket(v) for v in (19.9, 20, 40, 40.1)], ["<20", "20-40", "20-40", ">40"])

    def test_cascade_median_lead_is_days_not_percent(self):
        with open(census.REGISTRY) as f:
            registry = census.json.load(f)
        daily = census.load_daily()
        b2 = census.to_2d(daily, registry)
        out = census.render(daily, b2, census.cross_rows(b2), census.cross_rows(daily), daily)
        cells = [ln.split("|")[5].strip() for ln in out.splitlines()
                 if ln.startswith(("| DEV |", "| VALIDATION |", "| RECENT |"))]
        self.assertEqual(len(cells), 3)
        for c in cells:
            self.assertNotIn("%", c)


if __name__ == "__main__":
    unittest.main()