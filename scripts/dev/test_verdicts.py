"""verdicts.py overrides: derived from the cards correct-verdict-registry-one-run-for-eur*, resolve-missing-orderflow-divergence-kil*,
backfill-t090-7h-split-and-inconclusive-* (sourced hand corrections that survive `verdicts.py backfill`)."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verdicts as V  # noqa: E402

REPO = V.REPO


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        w.writerows(rows)


def make_root(tmp):
    d = Path(tmp) / "research" / "demo_2026-01-01"
    d.mkdir(parents=True)
    (d / "RESULT.md").write_text("# Demo study\nVerdict: FAIL\n", encoding="utf-8")
    return Path(tmp) / "research"


class Args:
    def __init__(self, root, csvp, ov):
        self.root, self.csv, self.overrides = str(root), str(csvp), str(ov)


class OverrideMechanism(unittest.TestCase):
    def run_backfill(self, ov_rows):
        tmp = tempfile.mkdtemp()
        root = make_root(tmp)
        ov = Path(tmp) / "ov.csv"
        write_csv(ov, V.OVERRIDE_COLS, ov_rows)
        out = Path(tmp) / "v.csv"
        V.cmd_backfill(Args(root, out, ov))
        return V.load(out)

    def test_override_changes_backfilled_row(self):
        rows = self.run_backfill([["demo_2026-01-01", "*", "one_run", "yes", "x/RESULT.md:8"]])
        self.assertEqual(rows[0]["one_run"], "yes")

    def test_without_override_row_is_no(self):
        self.assertEqual(self.run_backfill([])[0]["one_run"], "no")

    def test_empty_source_rejected(self):
        with self.assertRaises(ValueError):
            self.run_backfill([["demo_2026-01-01", "*", "one_run", "yes", ""]])

    def test_unknown_column_rejected(self):
        with self.assertRaises(ValueError):
            self.run_backfill([["demo_2026-01-01", "*", "nope", "yes", "x:1"]])

    def test_inconclusive_override_sets_scope_none(self):
        rows = self.run_backfill([["demo_2026-01-01", "*", "verdict", "INCONCLUSIVE", "x:1"]])
        self.assertEqual(rows[0]["verdict"], "INCONCLUSIVE")
        self.assertEqual(rows[0]["kill_scope"], "none")


class RealRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = V.load(V.CSV_PATH)
        cls.ov = V.load_overrides(V.OVERRIDES_PATH)

    def row(self, name):
        return [r for r in self.rows if r["study_dir"] == name]

    def test_eur_one_run_yes(self):
        self.assertTrue(self.row("eur_low_us_sweep_2026-10-14"))
        for r in self.row("eur_low_us_sweep_2026-10-14"):
            self.assertEqual(r["one_run"], "yes")

    def test_orderflow_kill_scope_resolved(self):
        for r in self.row("orderflow_views_2026-10-14"):
            self.assertNotEqual(r["kill_scope"], V.UNP)
            self.assertIn("price-vs-CVD divergence", r["kill_scope"])

    def test_t090_split_and_verdict(self):
        for r in self.row("t090_7h_2026-10-09"):
            self.assertTrue(r["split_read"].startswith("ALL"))
            self.assertEqual(r["verdict"], "INCONCLUSIVE")
            self.assertEqual(r["kill_scope"], "none")

    def test_every_override_has_source_and_it_exists(self):
        for o in self.ov:
            self.assertTrue(o["source"].strip())
            f, _, ln = o["source"].partition(":")
            p = REPO / f
            self.assertTrue(p.is_file(), o["source"])
            nums = [int(x) for x in ln.replace("-", ":").split(":") if x.strip().isdigit()]
            n = len(p.read_text(encoding="utf-8").split("\n"))
            self.assertTrue(nums and all(1 <= x <= n for x in nums), o["source"])

    def test_overridden_rows_in_csv_have_sources(self):
        names = {o["study_dir"] for o in self.ov}
        for o in self.ov:
            self.assertTrue(o["source"].strip(), o)
        self.assertTrue(names)


if __name__ == "__main__":
    unittest.main()
