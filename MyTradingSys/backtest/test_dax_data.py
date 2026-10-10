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


if __name__ == "__main__":
    unittest.main()
