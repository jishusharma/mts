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


class BlockedStudy(unittest.TestCase):
    SENT = "FAIL/INCONCLUSIVE: stop; this BLOCK covers only 1m and 5m cells counted here."

    def test_blocked_md_without_result_is_blocked_with_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "demo_2026-02-02"
            d.mkdir()
            (d / "PRE_REG.md").write_text("# PRE-REGISTRATION: Demo count, BTCUSDT\n", encoding="utf-8")
            (d / "BLOCKED.md").write_text("# BLOCKED\n" + self.SENT + "\n", encoding="utf-8")
            rows = V.parse_study(d)
        self.assertEqual((rows[0]["verdict"], rows[0]["kill_scope"]), ("BLOCKED", self.SENT))

    def test_blocked_without_sentence_is_scope_none_and_never_blocks_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "demo_2026-02-02"
            d.mkdir()
            (d / "BLOCKED.md").write_text("# BLOCKED\nnothing frozen\n", encoding="utf-8")
            rows = V.parse_study(d)
            self.assertEqual((rows[0]["verdict"], rows[0]["kill_scope"]), ("BLOCKED", "none"))
            csvp = Path(tmp) / "v.csv"
            V.save(csvp, rows)

            class A:
                words, csv = "demo", str(csvp)
            self.assertEqual(V.cmd_check(A), 0)

    def test_real_kurisko_row_is_blocked_with_scope_and_check_passes(self):
        rows = [r for r in V.load(V.CSV_PATH) if r["study_dir"].startswith("kurisko_2026-10-18")]
        self.assertEqual(rows[0]["verdict"], "BLOCKED")
        self.assertIn("1m and 5m", rows[0]["kill_scope"])

        class A:
            words, csv = "kurisko quad rotation", str(V.CSV_PATH)
        self.assertEqual(V.cmd_check(A), 0)


class LedgerCount(unittest.TestCase):
    def test_ledger_union_per_study_max_no_double_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            vc = Path(tmp) / "v.csv"
            cols = V.COLS
            def vrow(study, arm):
                r = {c: "x" for c in cols}
                r.update(study_dir=study, arm=arm, split_read="DEV")
                return [r[c] for c in cols]
            write_csv(vc, cols, [vrow("s1", "a"), vrow("s1", "b"), vrow("s2", "(study)")])
            lc = Path(tmp) / "l.csv"
            lcols = ["study", "variant", "run_utc", "split", "data_source", "description", "status"]
            write_csv(lc, lcols, [["s1", "V1", "d", "DEV", "x", "x", "x"],       # s1 already has 2 arms: no extra
                                  ["s3", "K1", "d", "DEV", "x", "x", "count-only-blocked"],
                                  ["s3", "K2", "d", "DEV", "x", "x", "count-only-blocked"],
                                  ["s4", "H1", "d", "VALIDATION", "x", "x", "x"]])  # other split: ignored

            class A:
                csv, ledger_csv, split, ledger = str(vc), str(lc), "DEV", True
            seen, _ = V.count_variants(vc, "DEV")
            self.assertEqual(len(seen), 3)                                       # plain count unchanged
            self.assertEqual(V.count_with_ledger(vc, lc, "DEV")[0], 5)           # s1 2 + s2 1 + s3 2
            self.assertEqual(V.cmd_count(A), 0)

    def test_real_ledger_has_kurisko_cells_and_pit_arms(self):
        per = V.ledger_per_study(RESEARCH_LEDGER, "DEV")
        self.assertEqual(len(per["kurisko_2026-10-18"]), 8)
        self.assertEqual(len(per["pit_levels_2026-10-16"]), 2)


RESEARCH_LEDGER = V.RESEARCH / "TRIAL_LEDGER.csv"


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


class PowerLine(unittest.TestCase):
    def test_power_line_g1_low_power(self):
        # SOURCED gap-g1-prereg-power.json:50
        # n=400, se_pct=0.10, gross 0.20, cost 0.05
        # expected MDE80 0.28016, net 0.15 below it so LOW-POWER,
        # n for 80 percent = 400*(0.28016/0.15)^2 = 1395
        row = {"n": "400", "se_pct": "0.10", "gross_mean_pct": "0.20", "cost_pct": "0.05"}
        line = V.power_line(row)
        self.assertIsNotNone(line)
        self.assertIn("0.28016", line)
        self.assertIn("0.15", line)
        self.assertIn("LOW-POWER", line)
        self.assertIn("1395", line)

    def test_power_line_adequate_power(self):
        # OURS: gross 0.40, cost 0.05 -> net 0.35 >= MDE80 0.28016 -> no LOW-POWER flag
        # trades for 80%: round(400 * (0.28016 / 0.35)**2) = 256
        row = {"n": "400", "se_pct": "0.10", "gross_mean_pct": "0.40", "cost_pct": "0.05"}
        line = V.power_line(row)
        self.assertIsNotNone(line)
        self.assertIn("0.28016", line)
        self.assertNotIn("LOW-POWER", line)
        self.assertIn("256", line)

    def test_power_line_unparsed(self):
        # When se_pct is UNPARSED, power_line cannot compute MDE and returns None
        row = {"n": "400", "se_pct": "UNPARSED", "gross_mean_pct": "0.20", "cost_pct": "0.05"}
        self.assertIsNone(V.power_line(row))


if __name__ == "__main__":
    unittest.main()

