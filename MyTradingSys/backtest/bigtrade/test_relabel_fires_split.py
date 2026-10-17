import csv, os, sys, tempfile, unittest, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relabel_fires_split as rf


def ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


class T(unittest.TestCase):
    def test_relabel(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "fires_x.csv")
            rows = [("2024-06-30", "TRAIN"), ("2024-07-01", "TRAIN"), ("2024-12-31", "TRAIN"), ("2025-01-01", "VALIDATE"),
                    ("2025-07-01", "HOLDOUT")]
            with open(p, "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["layer", "t_fire_ms", "split", "extra"])
                for dte, old in rows:
                    w.writerow(["x", ms(dte), old, "keep"])
            b, a, n = rf.relabel_file(p, os.path.join(d, "bk"))
            self.assertEqual(n, 5)
            self.assertEqual(dict(b), {"TRAIN": 3, "VALIDATE": 1, "HOLDOUT": 1})
            self.assertEqual(dict(a), {"TRAIN": 1, "VALIDATE": 3, "HOLDOUT": 1})
            got = list(csv.DictReader(open(p, newline="")))
            self.assertEqual([r["split"] for r in got], ["TRAIN", "VALIDATE", "VALIDATE", "VALIDATE", "HOLDOUT"])
            self.assertTrue(all(r["extra"] == "keep" for r in got))
            bk = list(csv.DictReader(open(os.path.join(d, "bk", "fires_x.csv"), newline="")))
            self.assertEqual(bk[1]["split"], "TRAIN")  # original preserved
            rf.relabel_file(p, os.path.join(d, "bk"))  # idempotent, backup not overwritten
            bk = list(csv.DictReader(open(os.path.join(d, "bk", "fires_x.csv"), newline="")))
            self.assertEqual(bk[1]["split"], "TRAIN")


if __name__ == "__main__":
    unittest.main()
