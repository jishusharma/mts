import sys
sys.dont_write_bytecode = True
"""trade_sanity: a fill shifted by one bar fails the log sanity check; year and long/short lines add up."""
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trade_sanity as T  # noqa: E402

T0 = 1640995200000  # 2022-01-01 00:00 UTC
Y23 = 1672531200000  # 2023-01-01 00:00 UTC


def klines(start, n=200):
    return {start + i * T.MS: (100.0 + i, 101.0 + i, 99.0 + i, 100.5 + i) for i in range(n)}


def trade(i, side=1, start=T0, ret=1.0, hold=10):
    e, x = start + i * T.MS, start + (i + hold) * T.MS
    return dict(side=side, entry_ms=e, exit_ms=x, entry_px=100.0 + i, exit_px=100.0 + i + hold, ret=ret)


class LogSanity(unittest.TestCase):
    def test_matching_fills_pass_and_print_five(self):
        k, tr = klines(T0), [trade(i * 12) for i in range(8)]
        k.update(klines(T0 + 200 * T.MS, 120))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rows = T.log_sanity(tr, k)
        self.assertEqual(len(rows), 5)
        self.assertEqual(buf.getvalue().count("OK  "), 5)
        self.assertEqual(rows[-1]["entry_ms"], tr[-1]["entry_ms"])   # the 5 LATEST

    def test_fill_shifted_one_bar_fails(self):
        k = klines(T0, 300)
        tr = [trade(i * 12) for i in range(8)]
        tr[-1]["entry_ms"] += T.MS            # logged time one bar late, price unchanged
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(T.LogSanityError):
                T.log_sanity(tr, k)

    def test_exit_shifted_and_missing_bar_fail(self):
        k, tr = klines(T0), [trade(0), trade(20)]
        tr[-1]["exit_ms"] -= T.MS
        with redirect_stdout(io.StringIO()), self.assertRaises(T.LogSanityError):
            T.log_sanity(tr, k)
        tr = [trade(0)]
        tr[0]["exit_ms"] = T0 + 10 ** 7 * T.MS   # no kline there
        with redirect_stdout(io.StringIO()), self.assertRaises(T.LogSanityError):
            T.log_sanity(tr, k)

    def test_close_leg(self):
        k = klines(T0)
        t = trade(3)
        t["entry_px"] = 100.5 + 3
        rows = T.check_trades([t], k, entry_leg="close")
        self.assertTrue(rows[0]["entry_ok"])
        self.assertFalse(T.check_trades([t], k)[0]["entry_ok"])


class YearSide(unittest.TestCase):
    def test_rows_split_and_sum(self):
        tr = [trade(0, 1, T0, 2.0), trade(1, -1, T0, -1.0), trade(2, 1, Y23, 4.0)]
        lines = T.year_side_lines(tr)
        self.assertIn("| year 2022 | 2 | 0.5000 | 1.0000 |", lines)
        self.assertIn("| year 2023 | 1 | 4.0000 | 4.0000 |", lines)
        self.assertIn("| long | 2 | 3.0000 | 6.0000 |", lines)
        self.assertIn("| short | 1 | -1.0000 | -1.0000 |", lines)

    def test_empty_side_is_nan_not_crash(self):
        lines = T.year_side_lines([trade(0, 1, T0, 1.0)])
        self.assertIn("| short | 0 | nan | 0.0000 |", lines)


class Template(unittest.TestCase):
    def test_template_carries_rows(self):
        t = (Path(__file__).resolve().parent / "PRE_REG_TEMPLATE.md").read_text(encoding="utf-8")
        for w in ("Log sanity", "Per-year rows", "Long/short rows", "trade_sanity.py"):
            self.assertIn(w, t)


if __name__ == "__main__":
    unittest.main()
