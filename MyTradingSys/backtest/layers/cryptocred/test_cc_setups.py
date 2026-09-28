import unittest

from MyTradingSys.backtest.layers.cryptocred import cc_setups as cs


def bar(t, l, c, h=None, o=None):
    if h is None:
        h = max(l, c) + 1
    if o is None:
        o = c
    return {"t": t, "o": o, "c": c, "h": h, "l": l}


def filler(n):
    """n neutral filler bars (indices 0..n-1) that don't affect any scan window."""
    return [bar(i, l=1000 + i, c=1000 + i, h=1000 + i) for i in range(n)]


class _PatchMixin:
    """Monkeypatch cc_setups's imported names (find_swings/classify_msb/find_retest) for
    the duration of a test, restoring the originals afterward."""

    def patch(self, **funcs):
        originals = {name: getattr(cs, name) for name in funcs}
        for name, fn in funcs.items():
            setattr(cs, name, fn)
        self.addCleanup(lambda: [setattr(cs, name, orig) for name, orig in originals.items()])


class TestSetup1SrFlip(unittest.TestCase, _PatchMixin):
    def test_u1_bull(self):
        events = [{"direction": "bull", "broken_level": 95, "i": 5, "confirm_i": 6, "broken_swing_i": 3}]
        retest = {"t": 10, "i": 10, "level": 95, "bars_since_break": 4}
        self.patch(
            find_swings=lambda *a, **k: [],
            classify_msb=lambda *a, **k: events,
            find_retest=lambda *a, **k: retest,
        )
        got = cs.setup1_sr_flip([], stop_buffer_pct=0.001, target_r=1.5)
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["side"], "long")
        self.assertAlmostEqual(sig["entry_price"], 95)
        self.assertEqual(sig["entry_t"], 10)
        self.assertAlmostEqual(sig["stop"], 94.905)
        self.assertEqual(len(sig["targets"]), 1)
        self.assertAlmostEqual(sig["targets"][0][0], 95.1425)
        self.assertEqual(sig["targets"][0][1], 1.0)
        self.assertEqual(sig["meta"], {"setup": "sr_flip", "rule_id": "C10-E01", "msb_i": 5, "target_r": 1.5})

    def test_u2_bear(self):
        events = [{"direction": "bear", "broken_level": 50, "i": 9, "confirm_i": 6, "broken_swing_i": 3}]
        retest = {"t": 10, "i": 10, "level": 50, "bars_since_break": 4}
        self.patch(
            find_swings=lambda *a, **k: [],
            classify_msb=lambda *a, **k: events,
            find_retest=lambda *a, **k: retest,
        )
        got = cs.setup1_sr_flip([], stop_buffer_pct=0.001, target_r=1.5)
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["side"], "short")
        self.assertAlmostEqual(sig["entry_price"], 50)
        self.assertEqual(sig["entry_t"], 10)
        self.assertAlmostEqual(sig["stop"], 50.05)
        self.assertEqual(len(sig["targets"]), 1)
        self.assertAlmostEqual(sig["targets"][0][0], 49.925)
        self.assertEqual(sig["targets"][0][1], 1.0)
        self.assertEqual(sig["meta"], {"setup": "sr_flip", "rule_id": "C10-E01", "msb_i": 9, "target_r": 1.5})

    def test_u3_no_retest_skipped(self):
        events = [{"direction": "bull", "broken_level": 95, "i": 5, "confirm_i": 6, "broken_swing_i": 3}]
        self.patch(
            find_swings=lambda *a, **k: [],
            classify_msb=lambda *a, **k: events,
            find_retest=lambda *a, **k: None,
        )
        got = cs.setup1_sr_flip([], stop_buffer_pct=0.001, target_r=1.5)
        self.assertEqual(got, [])


class TestSetup2FibPullback(unittest.TestCase, _PatchMixin):
    def test_u4_bull(self):
        # Impulse leg: prior swing low P_low=60 (list-index 1) -> swing high H=100 broken
        # (list-index 3, matching broken_swing_i so setup2's positional lookup finds it).
        swings = [
            {"i": 0, "t": 0, "price": 10, "kind": "low", "confirmed_i": 0},
            {"i": 1, "t": 1, "price": 60, "kind": "low", "confirmed_i": 1},
            {"i": 2, "t": 2, "price": 40, "kind": "high", "confirmed_i": 2},
            {"i": 3, "t": 3, "price": 100, "kind": "high", "confirmed_i": 3},
        ]
        events = [{"direction": "bull", "broken_level": 100, "broken_swing_i": 3, "confirm_i": 3, "i": 7}]
        self.patch(
            find_swings=lambda *a, **k: swings,
            classify_msb=lambda *a, **k: events,
        )
        # zone = [100-0.786*40, 100-0.618*40] = [68.56, 75.28]; scan starts at confirm_i+1=4.
        bars = filler(4) + [bar(4, l=80, c=81), bar(5, l=70, c=71)]
        got = cs.setup2_fib_pullback(bars, fib_lo=0.618, fib_hi=0.786, stop_buffer_pct=0.001, target_r=1.5)
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["side"], "long")
        self.assertAlmostEqual(sig["entry_price"], 75.28)
        self.assertAlmostEqual(sig["stop"], 68.49144)
        self.assertEqual(len(sig["targets"]), 1)
        self.assertAlmostEqual(sig["targets"][0][0], 85.46284)
        self.assertEqual(sig["targets"][0][1], 1.0)
        self.assertEqual(sig["meta"]["setup"], "fib_pullback")
        self.assertEqual(sig["meta"]["rule_id"], "C10-E04")
        self.assertEqual(sig["meta"]["msb_i"], 7)
        self.assertEqual(sig["meta"]["target_r"], 1.5)

    def test_u4b_bull_swing_list_index_ne_bar_index(self):
        # Regression for the bug where broken_swing_i (a BAR index, per cc_structure's
        # classify_msb) was used directly as an index into the `swings` LIST. Here the
        # swings occur at bar indices 10-13 (several non-swing bars precede the first
        # swing), so list position != bar index: swings[3] has i=13, not i=3.
        #
        # By TEST_PLAN.md's setup2 definition, prev_low = "most recent swing of the
        # opposite kind before the broken swing" -> scanning backward from the swing
        # immediately preceding the broken high (list position 2) we find list
        # position 1: price=60, kind=low. That is the same impulse leg as U4
        # (P_low=60 -> H=100), so the expected numbers are identical to U4:
        #   zone = [100 - 0.786*40, 100 - 0.618*40] = [68.56, 75.28]
        #   entry_price = 75.28, stop = 68.56*(1-0.001) = 68.49144
        #   target = 75.28 + 1.5*(75.28-68.49144) = 85.46284
        #
        # On the buggy code, broken_swing_i=13 is used as `swings[i]` for
        # i in range(12, -1, -1) against a 4-element list -> IndexError immediately
        # at swings[12]. Confirmed: this test raises IndexError on the pre-fix code.
        swings = [
            {"i": 10, "t": 10, "price": 10, "kind": "low", "confirmed_i": 10},
            {"i": 11, "t": 11, "price": 60, "kind": "low", "confirmed_i": 11},
            {"i": 12, "t": 12, "price": 40, "kind": "high", "confirmed_i": 12},
            {"i": 13, "t": 13, "price": 100, "kind": "high", "confirmed_i": 13},
        ]
        events = [{"direction": "bull", "broken_level": 100, "broken_swing_i": 13, "confirm_i": 15, "i": 20}]
        self.patch(
            find_swings=lambda *a, **k: swings,
            classify_msb=lambda *a, **k: events,
        )
        # bars[0..15] filler (index 15 = confirm bar), scan starts at confirm_i+1=16.
        bars = filler(16) + [bar(16, l=80, c=81), bar(17, l=70, c=71)]
        got = cs.setup2_fib_pullback(bars, fib_lo=0.618, fib_hi=0.786, stop_buffer_pct=0.001, target_r=1.5)
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["side"], "long")
        self.assertAlmostEqual(sig["entry_price"], 75.28)
        self.assertEqual(sig["entry_t"], 17)
        self.assertAlmostEqual(sig["stop"], 68.49144)
        self.assertEqual(len(sig["targets"]), 1)
        self.assertAlmostEqual(sig["targets"][0][0], 85.46284)
        self.assertEqual(sig["targets"][0][1], 1.0)
        self.assertEqual(sig["meta"]["msb_i"], 20)


class TestSetup3FailedMsbReversal(unittest.TestCase, _PatchMixin):
    def test_u5_bull_msb_fails(self):
        # broken_level=95 confirmed at c=7; structure extreme over [5..7] (max h) = 98.
        # failure_lookback=2 -> window = bars[8:10]: idx8 h=96 (<=98, no new high),
        # idx9 h=94, c=93 (<95 -> failed/reversed).
        bars = filler(5) + [
            bar(5, l=94, c=95, h=95),
            bar(6, l=74, c=75, h=75),
            bar(7, l=94, c=98, h=98),
            bar(8, l=93, c=96, h=96),
            bar(9, l=92, c=93, h=94),
        ]
        events = [{"direction": "bull", "broken_level": 95, "broken_swing_i": 5, "confirm_i": 7, "i": 7}]
        self.patch(
            find_swings=lambda *a, **k: [],
            classify_msb=lambda *a, **k: events,
        )
        got = cs.setup3_failed_msb_reversal(bars, failure_lookback=2, stop_buffer_pct=0.001, target_r=2.0)
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["side"], "short")
        self.assertAlmostEqual(sig["entry_price"], 93)
        self.assertEqual(sig["entry_t"], 9)
        self.assertAlmostEqual(sig["stop"], 95.095)
        self.assertEqual(len(sig["targets"]), 1)
        self.assertAlmostEqual(sig["targets"][0][0], 88.81)
        self.assertEqual(sig["targets"][0][1], 1.0)
        self.assertEqual(sig["meta"], {"setup": "failed_msb_reversal", "rule_id": "C10-E05", "msb_i": 7, "target_r": 2.0})

    def test_u6_not_enough_bars_skipped(self):
        # len(bars)-1 < c + failure_lookback -> undetermined, no signal.
        bars = filler(5) + [
            bar(5, l=94, c=95, h=95),
            bar(6, l=74, c=75, h=75),
            bar(7, l=94, c=98, h=98),
            bar(8, l=93, c=96, h=96),
        ]  # len(bars)=9, len(bars)-1=8; c=7, failure_lookback=2 -> need >=9, only have 8
        events = [{"direction": "bull", "broken_level": 95, "broken_swing_i": 5, "confirm_i": 7, "i": 7}]
        self.patch(
            find_swings=lambda *a, **k: [],
            classify_msb=lambda *a, **k: events,
        )
        got = cs.setup3_failed_msb_reversal(bars, failure_lookback=2, stop_buffer_pct=0.001, target_r=2.0)
        self.assertEqual(got, [])


if __name__ == "__main__":
    unittest.main()
