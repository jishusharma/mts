"""Tests for the Fable run 4 pack. Run: python -m unittest test_pack  (from build/), pack must be built.
1. leak check passes on the real pack and FAILS on planted rows (csv date, csv epoch, md date).
2. Profile builder reproduces the FORMULAS 18.1 worked examples A, B, C (numbers copied from FORMULAS.md, not code).
3. One hand-picked week (2022-06-13) POC/VAH/VAL from the pack equals an independent bin-by-bin computation
   (different loop order than build_pack.profile) on the saved 1m fixture."""
import csv, gzip, os, shutil, tempfile, unittest
import numpy as np
import build_pack as bp
import leak_check as lc

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "..", "pack")


class Leak(unittest.TestCase):
    def test_real_pack_clean(self):
        self.assertEqual(lc.scan(PACK), [])

    def _planted(self, fn, fix):
        d = tempfile.mkdtemp()
        try:
            shutil.copytree(PACK, os.path.join(d, "pack"))
            fix(os.path.join(d, "pack"))
            return lc.scan(os.path.join(d, "pack"))
        finally:
            shutil.rmtree(d)

    def test_planted_csv_date_fails(self):
        def fix(p):
            with open(os.path.join(p, "ohlcv_4h.csv"), "a") as f:
                f.write("2023-07-01 00:00,1,1,1,1,1,1\n")
        self.assertTrue(self._planted("x", fix))

    def test_planted_epoch_fails(self):
        def fix(p):
            with open(os.path.join(p, "ohlcv_1d.csv"), "a") as f:
                f.write("1688169600000,1,1,1,1,1,1\n")  # 2023-07-01 00:00 UTC in ms
        self.assertTrue(self._planted("x", fix))

    def test_planted_text_fails(self):
        def fix(p):
            with open(os.path.join(p, "README.md"), "a") as f:
                f.write("\nBTC closed 2023-08-15 at 29000\n")
        self.assertTrue(self._planted("x", fix))

    def test_last_in_window_row_passes(self):
        def fix(p):
            with open(os.path.join(p, "ohlcv_4h.csv"), "a") as f:
                f.write("2023-06-30 20:00,1,1,1,1,1,1\n")
        self.assertEqual(self._planted("x", fix), [])


class Formulas181(unittest.TestCase):
    def prof(self, bars, w):
        h = np.array([b[1] for b in bars], float); l = np.array([b[0] for b in bars], float); v = np.array([b[2] for b in bars], float)
        return bp.profile(h, l, v, w=w)

    def test_worked_A(self):  # FORMULAS 18.1 Worked A: poc_price 1.5, val 1.0, vah 2.0
        self.assertEqual(self.prof([(0, 2, 6), (1, 3, 4), (1, 2, 10)], 1.0), (1.5, 1.0, 2.0))

    def test_worked_B(self):  # bin volumes [1,2,10,4,3] as point masses at bin centres: poc 2.5, val 2.0, vah 4.0
        bars = [(k + 0.5, k + 0.5, v) for k, v in enumerate([1, 2, 10, 4, 3])]
        self.assertEqual(self.prof(bars, 1.0), (2.5, 2.0, 4.0))

    def test_worked_C(self):  # tie [3,10,3]: lower side first -> val 0.0, vah 2.0
        bars = [(k + 0.5, k + 0.5, v) for k, v in enumerate([3, 10, 3])]
        self.assertEqual(self.prof(bars, 1.0)[1:], (0.0, 2.0))


def ref_profile(rows, w=10.0):
    """Independent reference: iterate bins, then bars (FORMULAS 18.1 text, no numpy)."""
    lo_k = int(min(r[2] for r in rows) // w); hi_k = int(max(r[1] for r in rows) // w)
    vol = {}
    for k in range(lo_k, hi_k + 1):
        a, b = k * w, (k + 1) * w
        t = 0.0
        for _, h, l, v in rows:
            if h == l:
                t += v if int(l // w) == k else 0.0
            else:
                ov = min(h, b) - max(l, a)
                if ov > 0:
                    t += v * ov / (h - l)
        vol[k] = t
    total = sum(vol.values())
    poc = min(k for k in vol if vol[k] == max(vol.values()))
    lo = hi = poc; acc = vol[poc]
    while acc < 0.70 * total and (lo > lo_k or hi < hi_k):
        vl = vol[lo - 1] if lo > lo_k else -1
        vh = vol[hi + 1] if hi < hi_k else -1
        if vl >= vh and lo > lo_k:
            lo -= 1; acc += vol[lo]
        else:
            hi += 1; acc += vol[hi]
    return poc * w + w / 2, (hi + 1) * w, lo * w  # poc, vah, val


class HandWeek(unittest.TestCase):
    def setUp(self):
        with gzip.open(os.path.join(HERE, "fixtures", "week_2022-06-13_1m.csv.gz"), "rt") as f:
            r = list(csv.reader(f))[1:]
        self.rows = [(int(x[0]), float(x[2]), float(x[3]), float(x[5])) for x in r]  # t,h,l,v

    def test_week_poc_vah_val(self):
        self.assertEqual(len(self.rows), 10080)
        ref = ref_profile([(t, h, l, v) for t, h, l, v in self.rows])
        with open(os.path.join(PACK, "levels_weekly.csv")) as f:
            row = next(x for x in csv.DictReader(f) if x["period_open_utc"] == "2022-06-13 00:00")
        got = (float(row["poc"]), float(row["vah"]), float(row["val"]))
        self.assertEqual(got, ref)

    def test_day_poc_vah_val(self):
        day = [(t, h, l, v) for t, h, l, v in self.rows if 86400000 * 1 <= t - self.rows[0][0] < 86400000 * 2]
        self.assertEqual(len(day), 1440)
        ref = ref_profile(day)
        with open(os.path.join(PACK, "levels_daily.csv")) as f:
            row = next(x for x in csv.DictReader(f) if x["period_open_utc"] == "2022-06-14 00:00")
        self.assertEqual((float(row["poc"]), float(row["vah"]), float(row["val"])), ref)


if __name__ == "__main__":
    unittest.main()
