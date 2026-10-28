"""Kurisko quad rotation tests. Expected numbers come from FORMULAS.md section 24 (hand values; make_golden.py, which does
not import the module) and from OHLC fixtures whose values are derived by hand in the comments, never from module output."""
import csv
import json
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3]))   # repo root, for MyTradingSys.backtest.layers.rsi.rsi_core
import quad_rotation as qr  # noqa: E402
import stoch_core as sc  # noqa: E402

TF = 60000
NAN = math.nan


def mk(hlc, t0=0):
    return [(t0 + i * TF, h, l, c) for i, (h, l, c) in enumerate(hlc)]


# Fixtures A/B (hand-derived). Bars 0-5 fall one point per bar with close = low and high = low + 1:
# bar i: low 100-i, high 101-i, close 100-i. For k=2..5 the raw %K of every bar with a full window is 0 (close is the
# window low), so with d=1 all four lines are 0 from bar 4 on (k=5 needs five bars): episode start s = 4.
FALL = [(101 - i, 100 - i, 100 - i) for i in range(6)]
# Fixture A bar 6 (h 97, l 94.5, c 96.5): k=2 HH 97 LL 94.5 -> 2/2.5 = 80; k=3: 80; k=4: HH 98 -> 2/3.5 = 57.142857;
# k=5: HH 99 -> 2/4.5 = 44.444444. Fast 80 > 0 with all four < 20 on bars 4..5: event at t=6.
FIX_A = mk(FALL + [(97, 94.5, 96.5)])
# Fixture B bar 6 (h 96, l 94, c 94.2): k=2 0.2/2 = 10; k=3 HH 97 -> 0.2/3 = 6.666667; k=4 0.2/4 = 5; k=5 0.2/5 = 4.
# Bar 7 (h 95, l 93, c 93.5): k=2 HH 96 LL 93 -> 0.5/3 = 16.666667; k=3 same 16.666667; k=4 HH 97 -> 0.5/4 = 12.5;
# k=5 HH 98 -> 0.5/5 = 10. All four stay under 20 while the fast line ticks up again: still the same episode.
FIX_B = mk(FALL + [(96, 94, 94.2), (95, 93, 93.5)])
BANDS = ((2, 1), (3, 1), (4, 1), (5, 1))   # (k, d); d = 1 means the line is the raw %K


def mirror(bars):
    return [(t, 200 - l, 200 - h, 200 - c) for (t, h, l, c) in bars]


class TestStochCore(unittest.TestCase):
    def test_golden_k5_d3(self):
        with open(HERE / "golden_stoch_k5d3.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        h = [float(r["high"]) for r in rows]
        l = [float(r["low"]) for r in rows]
        c = [float(r["close"]) for r in rows]
        raw = sc.raw_k(h, l, c, 5)
        line = sc.stoch_line(h, l, c, 5, 3)
        for i, r in enumerate(rows):
            for got, key in ((raw[i], "raw_k"), (line[i], "line")):
                if r[key] == "":
                    self.assertTrue(math.isnan(got), f"{key} bar {i}")
                else:
                    self.assertAlmostEqual(got, float(r[key]), delta=1e-9, msg=f"{key} bar {i}")

    def test_hand_value_bar4(self):
        # bar 4 window bars 0..4: HH 107, LL 98, close 104 -> 100*6/9 = 66.666667
        h = [102, 104, 105, 106, 107]
        l = [98, 99, 101, 102, 103]
        c = [100, 103, 102, 105, 104]
        self.assertAlmostEqual(sc.raw_k(h, l, c, 5)[4], 66.6666666667, delta=1e-9)

    def test_flat_input_is_nan_never_zero_or_hundred(self):
        p = [100.0] * 12
        self.assertTrue(all(math.isnan(v) for v in sc.raw_k(p, p, p, 3)))
        self.assertTrue(all(math.isnan(v) for v in sc.stoch_line(p, p, p, 3, 2)))

    def test_nan_in_smoothing_window_gives_nan(self):
        h = [10, 10, 10, 12, 13]
        l = [10, 10, 10, 9, 9]
        c = [10, 10, 10, 12, 11]
        line = sc.stoch_line(h, l, c, 3, 2)
        # raw K_3: bar 2 NaN (flat window); bar 3 window 1..3 HH 12 LL 9 close 12 -> 100; bar 4 window 2..4 HH 13 LL 9 close 11 -> 50
        self.assertTrue(math.isnan(line[3]))
        self.assertAlmostEqual(line[4], 75.0, delta=1e-9)

    def test_slowing_variant(self):
        h = [10] * 5
        l = [0] * 5
        c = [0, 10, 0, 10, 10]
        # raw K_2 = [nan, 100, 0, 100, 100]; slow 2: [nan, nan, 50, 50, 100]; d 2: [.., .., nan, 50, 75]
        line = sc.stoch_line(h, l, c, 2, 2, 2)
        self.assertTrue(math.isnan(line[2]))
        self.assertAlmostEqual(line[3], 50.0, delta=1e-9)
        self.assertAlmostEqual(line[4], 75.0, delta=1e-9)

    def test_future_bars_do_not_change_past(self):
        h = [102, 104, 105, 106, 107, 108]
        l = [98, 99, 101, 102, 103, 104]
        c = [100, 103, 102, 105, 104, 107]
        base = sc.stoch_line(h, l, c, 3, 2)
        h2, l2, c2 = h[:], l[:], c[:]
        h2[5], l2[5], c2[5] = 500, -500, 400
        pois = sc.stoch_line(h2, l2, c2, 3, 2)
        for i in range(5):
            self.assertTrue(base[i] == pois[i] or (math.isnan(base[i]) and math.isnan(pois[i])))


def ev_key(ev):
    return [(e.t, e.side, e.episode_start) for e in ev]


class TestDetect(unittest.TestCase):
    """detect() on hand-supplied line values: the event rule only."""

    def test_first_uptick_one_event_then_none_in_episode(self):
        fast = [NAN, 5, 5, 8, 12, 9, 15]       # bar 1 episode start; bar 2 equal; bar 3 uptick -> event; bar 4 uptick: none
        o = [NAN, 5, 5, 5, 5, 5, 5]
        self.assertEqual(ev_key(qr.detect([fast, o, o, o])), [(3, "long", 1)])

    def test_equal_is_not_a_turn(self):
        self.assertEqual(qr.detect([[5, 5, 5, 5], [5] * 4, [5] * 4, [5] * 4]), [])

    def test_episode_ends_at_any_line_ge_20_then_new_episode(self):
        fast = [5, 4, 6, 25, 5, 4, 7]
        o = [5] * 7
        self.assertEqual(ev_key(qr.detect([fast, o, o, o])), [(2, "long", 0), (6, "long", 4)])

    def test_other_line_leaving_blocks_event(self):
        fast = [5, 5, 5, 6]
        slow = [5, 30, 5, 5]                   # bar 1 slow >= 20: episode restarts at 2; t=3 uptick fires with s=2
        o = [5] * 4
        self.assertEqual(ev_key(qr.detect([fast, o, o, slow])), [(3, "long", 2)])
        slow2 = [5, 5, 30, 5]                  # slow >= 20 at bar 2 ends the episode: t=3 uptick has no live episode
        self.assertEqual(qr.detect([[5, 5, 4, 6], o, o, slow2]), [])

    def test_exactly_20_is_not_under_20(self):
        self.assertEqual(qr.detect([[20, 20, 21], [5] * 3, [5] * 3, [5] * 3]), [])

    def test_event_bar_may_itself_leave_the_zone(self):
        self.assertEqual(ev_key(qr.detect([[5, 5, 50], [5] * 3, [5] * 3, [5] * 3])), [(2, "long", 0)])

    def test_short_mirror_all_above_80_and_falling(self):
        fast = [95, 95, 92, 97, 90]
        o = [95] * 5
        self.assertEqual(ev_key(qr.detect([fast, o, o, o])), [(2, "short", 0)])

    def test_exactly_80_is_not_over_80(self):
        self.assertEqual(qr.detect([[80, 80, 70], [90] * 3, [90] * 3, [90] * 3]), [])

    def test_nan_mid_episode_ends_it(self):
        o = [5] * 4
        self.assertEqual(qr.detect([[5, 5, NAN, 6], o, o, o]), [])

    def test_unknown_arm_rejected(self):
        with self.assertRaises(ValueError):
            qr.compute(FIX_A, TF, arm="rsii")

    def test_nan_line_is_never_in_an_episode(self):
        self.assertEqual(qr.detect([[NAN, 6], [5] * 2, [5] * 2, [5] * 2]), [])


class TestComputeStoch(unittest.TestCase):
    def test_fixture_a_long_event_values(self):
        rows = qr.compute(FIX_A, TF, arm="stoch", bands=BANDS)
        ev = [r for r in rows if r.side]
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e.side, e.kind, e.t_close, e.episode_start_t), ("long", "quad_rotation_stoch", 7 * TF, 5 * TF))
        for got, exp in zip(e.values, (80.0, 80.0, 57.142857, 44.444444)):
            self.assertAlmostEqual(got, exp, delta=1e-6)

    def test_fixture_b_one_event_second_uptick_is_not_one(self):
        rows = qr.compute(FIX_B, TF, arm="stoch", bands=BANDS)
        ev = [r for r in rows if r.side]
        self.assertEqual([(r.t_close, r.episode_start_t) for r in ev], [(7 * TF, 5 * TF)])
        self.assertIsNone(rows[7].side)
        for got, exp in zip(rows[6].values, (10.0, 6.666667, 5.0, 4.0)):
            self.assertAlmostEqual(got, exp, delta=1e-6)
        for got, exp in zip(rows[7].values, (16.666667, 16.666667, 12.5, 10.0)):
            self.assertAlmostEqual(got, exp, delta=1e-6)

    def test_all_four_under_20_bar(self):
        rows = qr.compute(FIX_B, TF, arm="stoch", bands=BANDS)
        for v in rows[4].values + rows[5].values:
            self.assertEqual(v, 0.0)

    def test_short_mirror_fixture_b(self):
        rows = qr.compute(mirror(FIX_B), TF, arm="stoch", bands=BANDS)
        ev = [r for r in rows if r.side]
        self.assertEqual([(r.side, r.t_close, r.episode_start_t) for r in ev], [("short", 7 * TF, 5 * TF)])
        for got, exp in zip(rows[6].values, (90.0, 93.333333, 95.0, 96.0)):
            self.assertAlmostEqual(got, exp, delta=1e-6)

    def test_flat_input_gives_no_events_and_nan_values(self):
        rows = qr.compute(mk([(100, 100, 100)] * 15), TF, arm="stoch", bands=BANDS)
        self.assertTrue(all(r.side is None for r in rows))
        self.assertTrue(all(math.isnan(v) for r in rows for v in r.values))

    def test_available_at_is_bar_close(self):
        for r in qr.compute(FIX_A, TF, arm="stoch", bands=BANDS):
            self.assertEqual(r.available_at, r.open_time + TF)

    def test_gap_resets_windows(self):
        bars = FIX_A[:5] + [(t + TF, h, l, c) for (t, h, l, c) in FIX_A[5:]]   # one missing bar before index 5
        rows = qr.compute(bars, TF, arm="stoch", bands=BANDS)
        self.assertTrue(all(r.side is None for r in rows))
        self.assertTrue(all(math.isnan(v) for v in rows[5].values))

    def test_future_spike_changes_nothing_at_or_before_t(self):
        base = qr.compute(FIX_B, TF, arm="stoch", bands=BANDS)
        for t in range(len(FIX_B) - 1):
            pois = [b if j <= t else (b[0], 1e6, -1e6, 5e5) for j, b in enumerate(FIX_B)]
            got = qr.compute(pois, TF, arm="stoch", bands=BANDS)
            for i in range(t + 1):
                self.assertEqual(got[i].side, base[i].side, f"t={t} i={i}")
                for a, b in zip(got[i].values, base[i].values):
                    self.assertTrue(a == b or (math.isnan(a) and math.isnan(b)), f"t={t} i={i}")

    def test_default_params_labels(self):
        p = json.loads((HERE / "params" / "kurisko_default.json").read_text())["params"]
        for k, v in p.items():
            self.assertIn(v["label"], {"SOURCED", "OURS", "OPERATOR-HYPOTHESIS"}, k)
            self.assertTrue(v.get("source"), k)
        self.assertIs(p["enabled"]["value"], False)
        self.assertEqual(p["bands"]["value"], [[9, 3], [14, 3], [40, 4], [60, 10]])
        self.assertEqual((p["level_lo"]["value"], p["level_hi"]["value"]), (20, 80))
        self.assertEqual(p["rsi_bands"]["label"], "OPERATOR-HYPOTHESIS")


class TestComputeRsi(unittest.TestCase):
    # Closes fall 10,9,8,7,6 then 7. RSI periods (2,3,3,3). Falling closes: no gains, RSI = 0 once seeded (idx = period).
    # idx5, period 2: avg gain (0*1+1)/2 = 0.5, avg loss (1*1+0)/2 = 0.5 -> RS 1 -> 50.
    # idx5, period 3: avg gain (0*2+1)/3 = 1/3, avg loss (1*2+0)/3 = 2/3 -> RS 0.5 -> 100-100/1.5 = 33.333333.
    # Episode start s = 3 (period-3 RSI first exists at idx 3); idx 4 fast 0 == 0 no turn; idx 5 turn -> event.
    CLOSES = [10, 9, 8, 7, 6, 7]

    def bars(self):
        return [(i * TF, c, c, c) for i, c in enumerate(self.CLOSES)]

    def test_rsi_arm_event(self):
        rows = qr.compute(self.bars(), TF, arm="rsi", bands=((2, 0), (3, 0), (3, 0), (3, 0)))
        ev = [r for r in rows if r.side]
        self.assertEqual([(r.side, r.kind, r.t_close, r.episode_start_t) for r in ev],
                         [("long", "quad_rotation_rsi", 6 * TF, 4 * TF)])
        for got, exp in zip(ev[0].values, (50.0, 33.333333, 33.333333, 33.333333)):
            self.assertAlmostEqual(got, exp, delta=1e-6)

    def test_rsi_short_series_is_nan_not_an_error(self):
        rows = qr.compute(self.bars()[:3], TF, arm="rsi", bands=((9, 0), (14, 0), (40, 0), (60, 0)))
        self.assertTrue(all(r.side is None and all(math.isnan(v) for v in r.values) for r in rows))


if __name__ == "__main__":
    unittest.main()
