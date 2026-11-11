"""Tests for call_paper_log.py. Synthetic bars only; no network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import call_paper_log as m  # noqa: E402

T0 = 1_800_000_000_000 - 1_800_000_000_000 % m.STEP


def bar(i, o, h, l, c, d=-1.0):
    return {"t": T0 + i * m.STEP, "o": o, "h": h, "l": l, "c": c, "d": d}


def flat(n, px=100.0, d=-1.0):
    return [bar(i, px, px + 0.05, px - 0.05, px, d) for i in range(n)]


def call(side="long", lo=98.0, hi=98.5, logged=5, life=400, cid="c1"):
    return {"id": cid, "analyst": "X", "side": side, "lo": lo, "hi": hi, "t_logged": T0 + logged * m.STEP,
            "expires": T0 + life * m.STEP}


class Base(unittest.TestCase):
    def setUp(self):
        self.j = str(Path(tempfile.mkdtemp()) / "j.jsonl")
        self._div = m.div_map
        m.div_map = lambda bars: {}

    def tearDown(self):
        m.div_map = self._div

    def run_step(self, bars, calls):
        return m.step(bars, calls, self.j, min_bars=10)


class SimTests(unittest.TestCase):
    def test_stop_moved_out_to_40bp_and_target_2r(self):
        bars = [bar(0, 100, 100.1, 99.95, 100), bar(1, 100, 100.9, 99.9, 100.8)]
        r = m.simulate(1, bars, 0, 99.9)          # raw stop 10 bp away -> 40 bp
        self.assertAlmostEqual(r["stop"], 99.6)
        self.assertAlmostEqual(r["target"], 100.8)
        self.assertEqual(r["why"], "target")
        self.assertAlmostEqual(r["gross_r"], 2.0)
        self.assertAlmostEqual(r["net_r"], 2.0 - m.cost_frac("target") / 0.004)

    def test_same_bar_stop_first_and_short_mirror(self):
        r = m.simulate(1, [bar(0, 100, 102, 99, 100)], 0, 99.5)
        self.assertEqual(r["why"], "stop")
        self.assertLess(r["net_r"], -1.0)
        s = m.simulate(-1, [bar(0, 100, 100.1, 98.9, 99)], 0, 100.5)
        self.assertEqual(s["why"], "target")

    def test_open_until_horizon_then_time_exit(self):
        self.assertIsNone(m.simulate(1, flat(50), 0, 99.5))
        r = m.simulate(1, flat(120), 0, 99.5)
        self.assertEqual((r["why"], r["t_exit_bar"]), ("time", T0 + 95 * m.STEP))

    def test_costs_from_fees_module(self):
        self.assertAlmostEqual(m.cost_frac("stop"), m.fees.FEES_ALL_TAKER["entry"] + m.fees.FEES_ALL_TAKER["stop"]
                               + m.fees.SLIPPAGE_RT_S13)


class SlotTests(Base):
    def bars_with_touch(self, touch=20, turn=None, n=160):
        b = flat(n)
        b[touch] = bar(touch, 100, 100.05, 98.4, 99.0)              # dips into the 98.0-98.5 zone
        for k in range(touch + 1, n):
            b[k] = bar(k, 99.0, 99.05, 98.95, 99.0)
        if turn is not None:
            b[turn] = bar(turn, 99.0, 99.3, 98.95, 99.2, d=5.0)     # positive delta, up body
            for k in range(turn + 1, n):
                b[k] = bar(k, 99.2, 99.25, 99.15, 99.2)
        return b

    def test_flow_turn_inside_window_trades_the_setup(self):
        new = self.run_step(self.bars_with_touch(turn=23), [call()])
        s = [r for r in new if r["arm"] == "setup"]
        self.assertEqual([(r["kind"], r["trigger"]) for r in s], [("outcome", "T2")])
        self.assertEqual(s[0]["t_fill"], T0 + 24 * m.STEP)
        self.assertAlmostEqual(s[0]["stop"], 98.0)                  # zone lo is below the touch low 98.4
        self.assertEqual(s[0]["why"], "time")

    def test_trigger_after_window_is_no_trigger(self):
        new = self.run_step(self.bars_with_touch(turn=20 + m.WINDOW), [call()])
        self.assertEqual([r["kind"] for r in new if r["arm"] == "setup"], ["no_trigger"])

    def test_divergence_trigger_t1(self):
        m.div_map = lambda bars: {T0 + 22 * m.STEP: {1}}
        new = self.run_step(self.bars_with_touch(), [call()])
        self.assertEqual([r.get("trigger") for r in new if r["arm"] == "setup"], ["T1"])

    def test_touch_before_logging_does_not_count(self):
        new = self.run_step(self.bars_with_touch(touch=20, turn=23, n=60)[:22] + flat(138)[22:], [call(logged=30)])
        self.assertEqual([r for r in new if r["arm"] in ("setup", "placebo_a")], [])

    def test_placebo_a_enters_after_touch(self):
        new = self.run_step(self.bars_with_touch(), [call()])
        a = [r for r in new if r["arm"] == "placebo_a"]
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]["t_fill"], T0 + 21 * m.STEP)

    def test_placebo_b_only_away_from_zone(self):
        b = flat(160)
        b[40] = bar(40, 100, 100.3, 99.95, 100.2, d=5.0)
        for k in range(41, 160):
            b[k] = bar(k, 100.2, 100.25, 100.15, 100.2)
        near = self.run_step(b, [call(lo=99.8, hi=100.0)])          # close 100.2 is inside 1 % of the zone
        self.assertEqual([r for r in near if r["arm"] == "placebo_b"], [])
        self.j = str(Path(tempfile.mkdtemp()) / "j2.jsonl")
        far = self.run_step(b, [call(lo=90.0, hi=91.0)])
        pb = [r for r in far if r["arm"] == "placebo_b"]
        self.assertEqual((len(pb), pb[0]["trigger"], pb[0]["side"]), (1, "T2", "long"))

    def test_one_setup_trade_at_a_time(self):
        calls = [call(cid="c1"), call(cid="c2")]
        new = self.run_step(self.bars_with_touch(turn=23), calls)
        self.assertEqual(sorted(r["kind"] for r in new if r["arm"] == "setup"), ["outcome", "skipped_busy"])

    def test_second_poll_writes_nothing(self):
        b = self.bars_with_touch(turn=23)
        self.assertTrue(self.run_step(b, [call()]))
        self.assertEqual(self.run_step(b, [call()]), [])

    def test_fails_closed_on_bad_bars(self):
        b = self.bars_with_touch(turn=23)
        b[10]["c"] = float("nan")
        self.assertEqual(self.run_step(b, [call()]), [])
        self.assertFalse(Path(self.j).exists())

    def test_stop_rule_and_readout(self):
        rows = [{"arm": "setup", "kind": "outcome", "status": "closed", "net_r": -0.1, "t_exit_bar": 0}] * 30
        Path(self.j).write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        self.assertEqual(m.verdict(rows), "STOP")
        self.assertEqual(m.verdict(rows[:29]), "RUNNING")
        self.assertIn("| Call + trigger (the setup) | 30 | -0.100 |", m.readout(self.j))
        good = [dict(r, net_r=0.3) for r in rows]
        self.assertTrue(m.verdict(good).startswith("RUNNING (does not"))
        pl = [{"arm": a, "kind": "outcome", "status": "closed", "net_r": 0.1} for a in ("placebo_a", "placebo_b")]
        self.assertEqual(m.verdict(good + pl), "EDGE-CANDIDATE")


class CallFileTests(unittest.TestCase):
    def test_level_becomes_zone_and_bad_rows_dropped(self):
        p = Path(tempfile.mkdtemp()) / "calls.jsonl"
        p.write_text(json.dumps({"id": "a", "side": "long", "level": 100.0, "t_logged": 1}) + "\n"
                     + json.dumps({"id": "b", "side": "up", "level": 100.0, "t_logged": 1}) + "\nnot json\n")
        c = m.load_calls(p)
        self.assertEqual(len(c), 1)
        self.assertAlmostEqual(c[0]["lo"], 99.75)
        self.assertEqual(c[0]["expires"], 1 + m.LIFE_MS)


if __name__ == "__main__":
    unittest.main()
