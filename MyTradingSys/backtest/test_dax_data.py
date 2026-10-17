import sys
sys.dont_write_bytecode = True
"""Tests for dax_data.py. Expected values are computed by hand from the feed format in the module docstring."""
import datetime as dt
import lzma
import struct
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dax_data as D  # noqa: E402

DAY = dt.date(2025, 3, 30)          # CET -> CEST switch day: the feed is UTC, so no hour may shift
DAY_MS = 1743292800000              # 2025-03-30T00:00:00Z = 1735689600 (2025-01-01) + 88 days * 86400, in ms


def blob(recs):
    return lzma.compress(b"".join(struct.pack(">5if", *r) for r in recs), format=lzma.FORMAT_ALONE)


class TestParse(unittest.TestCase):
    def test_utc_scale_and_filler(self):
        recs = [(0, 22000000, 22010500, 21990000, 22015250, 2.5),        # 00:00Z: o, c, l, h in price*1000
                (3600, 22100000, 22100000, 22100000, 22100000, 0.0),     # closed-market filler: dropped
                (7200, 22200000, 22250000, 22190000, 22260000, 1.0)]     # 02:00Z = 04:00 CEST, still 02:00Z
        rows = D.parse_bi5(blob(recs), DAY)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], (DAY_MS, 22000.0, 22015.25, 21990.0, 22010.5, 2.5))
        self.assertEqual(rows[1][0], DAY_MS + 7200 * 1000)
        self.assertEqual(rows[1][1:5], (22200.0, 22260.0, 22190.0, 22250.0))

    def test_empty_day(self):
        self.assertEqual(D.parse_bi5(b"", DAY), [])

    def test_ask_blob_uses_same_price_decode_and_filler_drop(self):
        recs = [(0, 22001500, 22002500, 22001000, 22003000, 2.5),
                (60, 22100000, 22100000, 22100000, 22100000, 0.0)]
        self.assertEqual(D.parse_bi5(blob(recs), DAY, side="ASK"),
                         [(DAY_MS, 22001.5, 22003.0, 22001.0, 22002.5, 2.5)])

    def test_ask_url_and_side_fetch(self):
        self.assertTrue(D.day_url(DAY, side="ASK").endswith("/ASK_candles_min_1.bi5"))

    def test_spreads_join_exact_open_ms_without_forward_fill(self):
        bid = [(1000, 100.0, 101.0, 99.0, 100.0, 1.0),
               (3000, 101.0, 102.0, 100.0, 101.0, 1.0)]
        ask = [(1000, 100.5, 101.5, 99.5, 100.25, 1.0),
               (2000, 100.5, 101.5, 99.5, 100.75, 1.0)]
        self.assertEqual(D.spreads(bid, ask), [(1000, 0.25)])

    def test_convert_neutral_taker_split(self):
        with tempfile.TemporaryDirectory() as td:
            raw, out = Path(td) / "raw", Path(td) / "out"
            raw.mkdir()
            (raw / "2025-03-30.bi5").write_bytes(blob([(60, 20000000, 20002000, 19999000, 20004000, 4.0)]))
            (raw / "2025-03-29.bi5").write_bytes(b"")
            self.assertEqual(D.convert(raw, out, "GER40"), 1)
            line = (out / "klines" / "GER40-1m-2025-03.csv").read_text().strip().split(",")
            self.assertEqual(int(line[0]), DAY_MS + 60000)
            self.assertEqual([float(x) for x in line[1:6]], [20000.0, 20004.0, 19999.0, 20002.0, 4.0])
            self.assertEqual(int(line[6]), DAY_MS + 60000 + 59999)
            self.assertEqual(float(line[9]), 2.0)                       # taker-buy = half of 4.0: delta 0

    def test_convert_delta_is_exactly_zero_for_micro_volumes(self):
        # volume 0.001335: half is 0.0006675, which 6 decimals round to 0.000668 (the old format), so the engine's
        # delta = 2 * 0.000668 - 0.001335 = +1e-6: a phantom aggressor split. 7 decimals keep delta exactly 0.
        with tempfile.TemporaryDirectory() as td:
            raw, out = Path(td) / "raw", Path(td) / "out"
            raw.mkdir()
            recs = [(60 * k, 20000000, 20002000, 19999000, 20004000, v) for k, v in enumerate((0.001335, 0.00102, 3.141593))]
            (raw / "2025-03-30.bi5").write_bytes(blob(recs))
            D.convert(raw, out, "GER40")
            lines = (out / "klines" / "GER40-1m-2025-03.csv").read_text().strip().splitlines()
            self.assertEqual(len(lines), 3)
            for line in lines:
                f = line.split(",")
                self.assertEqual(2 * float(f[9]) - float(f[5]), 0.0)


    def test_convert_end_ms_decodes_only_complete_development_bars(self):
        # cutoff = DAY_MS + 120000: the bar opening at +60 s closes at +120 s (kept); the +120 s bar closes at +180 s (dropped).
        with tempfile.TemporaryDirectory() as td:
            raw, out = Path(td) / "raw", Path(td) / "out"
            raw.mkdir()
            recs = [(60, 20000000, 20002000, 19999000, 20004000, 4.0), (120, 20000000, 20002000, 19999000, 20004000, 4.0)]
            (raw / "2025-03-30.bi5").write_bytes(blob(recs))
            (raw / "2025-03-31.bi5").write_bytes(b"not lzma: a later day must never be decoded")
            self.assertEqual(D.convert(raw, out, "GER40", end_ms=DAY_MS + 120000), 1)
            lines = (out / "klines" / "GER40-1m-2025-03.csv").read_text().strip().splitlines()
            self.assertEqual([int(x.split(",")[0]) for x in lines], [DAY_MS + 60000])

    def test_convert_end_ms_refuses_leftover_future_month_file(self):
        with tempfile.TemporaryDirectory() as td:
            raw, out = Path(td) / "raw", Path(td) / "out"
            raw.mkdir()
            (out / "klines").mkdir(parents=True)
            (out / "klines" / "GER40-1m-2025-04.csv").write_text("1,2,3\n", newline="\n")
            with self.assertRaisesRegex(ValueError, "authorized cutoff"):
                D.convert(raw, out, "GER40", end_ms=DAY_MS + 120000)


if __name__ == "__main__":
    unittest.main()
