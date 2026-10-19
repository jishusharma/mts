import sys
sys.dont_write_bytecode = True
"""Simulator validation (operator q16): planted edge, fee-including null, trade-list diff for tom_bt.run_variant.

Expected numbers are derived by hand from FORMULAS.md 18.5 (net_R = (side*(exit-L) - fee_in*L - fee_out*exit) / R) and the
fee rates in fees.py (Deribit BTC-PERPETUAL: maker 0.0, taker 0.0005, fees.py:23-24), never from run_variant.

Parameters (label: SOURCED = trader's words / verified exchange figure, OURS = synthetic design choice):
  fee rates                      SOURCED  fees.py:23-24 (verified 2026-09-26 public/get_instrument)
  rules (stop first, fill-bar    SOURCED  tom_bt.py docstring + FORMULAS.md 18.5 (conservative resolution)
   stop only, gap -> open)
  geometry long 100/99/103       OURS     risk 1, target 3R; short 200/202/194 risk 2, target 3R (mirror)
  12 target / 8 stop, 2 of the 8 OURS     planted by construction (card simulator-validation-planted-edge)
   stops are both-touch bars
  block length 100 bars          OURS     > fill window 40 and hold 40 for a 5m zone (8 x 5 bars)
  null noise +-0.3, close +-0.1  OURS     stays strictly inside stop/target, symmetric so gross cancels

PLANTED EDGE, hand arithmetic (maker entry and target = 0 fee, taker stop = 0.0005):
  long  target: gross = +(103-100)/1 = +3.0, fee = 0                       -> net +3.0
  long  stop  : gross = -(100-99)/1  = -1.0, fee = 0.0005*99/1  = 0.0495   -> net -1.0495
  short target: gross = +(200-194)/2 = +3.0, fee = 0                       -> net +3.0
  short stop  : gross = -(202-200)/2 = -1.0, fee = 0.0005*202/2 = 0.0505   -> net -1.0505
  trades: 12 target (6 long + 6 short), 4 long stop, 4 short stop (2 of the 8 stops are both-touch bars)
  sum net = 12*3.0 + 4*(-1.0495) + 4*(-1.0505) = 36 - 4.198 - 4.202 = 27.6 ; mean = 27.6/20 = 1.38
  (stop_first=False would turn both-touch bars into targets: 14 x 3.0 - 6 stops -> mean differs, mutation test below)

NULL, hand arithmetic (flat noise, every order fills on bar 0 and times out at the close of bar 40, gross cancels):
  long : fee = 0.0005*100/1 = 0.05 R round turn (entry maker 0 + exit taker 0.0005) -> mean net -0.05
  short: fee = 0.0005*200/2 = 0.05 R                                                 -> mean net -0.05
  all-taker profile (0.0005 + 0.0005): long 0.0010*100/1 = 0.10 R, short 0.0010*200/2 = 0.10 R -> mean net -0.10
"""
import importlib.util
import random
import types
import unittest
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tom_bt as T  # noqa: E402
from MyTradingSys.backtest.fees import DERIBIT_MAKER, DERIBIT_TAKER  # noqa: E402

BLOCK = 100          # bars per signal block (OURS)
ZTYPE = "5m_swing_low"  # zone_tf -> "5m": fill window 8*5 = 40 bars, hold 8*5 = 40 bars (tom_bt.zone_tf)
FILL_HOLD = 40
LONG_G = dict(dir="long", entry=100.0, stop=99.0, target=103.0)
SHORT_G = dict(dir="short", entry=200.0, stop=202.0, target=194.0)

# 20 planted signals: (side, outcome). "both" = the stop and the target are both inside one bar -> stop (stop_first=True).
PLAN = [("long", "target"), ("short", "target"), ("long", "stop"), ("short", "stop"), ("long", "target"),
        ("short", "target"), ("long", "both"), ("short", "target"), ("long", "target"), ("short", "stop"),
        ("long", "target"), ("short", "both"), ("long", "stop"), ("short", "target"), ("long", "target"),
        ("short", "stop"), ("long", "stop"), ("short", "target"), ("long", "target"), ("short", "target")]
AMBIGUOUS_IDX = [i for i, (_, o) in enumerate(PLAN) if o == "both"]  # [6, 11]
assert len(PLAN) == 20 and sum(1 for _, o in PLAN if o == "target") == 12 and sum(1 for _, o in PLAN if o != "target") == 8
assert len(AMBIGUOUS_IDX) == 2


def geom(side):
    return LONG_G if side == "long" else SHORT_G


def bars_for(side, outcome):
    """Bars of one block as (o,h,l,c). Bar 0 touches the entry (fill, stop untouched); bar 1 is the decisive bar."""
    g = geom(side)
    if side == "long":
        b0 = (100.5, 100.8, 100.0, 100.4)
        b1 = {"target": (100.4, 103.5, 100.2, 103.0),      # high >= 103, low > 99
              "stop": (100.4, 100.6, 98.8, 99.0),          # low <= 99, high < 103
              "both": (100.4, 103.5, 98.8, 100.0)}[outcome]  # low <= 99 AND high >= 103
        flat = (100.5, 100.6, 100.4, 100.5)
    else:
        b0 = (199.5, 200.0, 199.2, 199.6)
        b1 = {"target": (199.6, 199.8, 193.5, 194.0),      # low <= 194, high < 202
              "stop": (199.6, 202.5, 199.0, 202.0),        # high >= 202, low > 194
              "both": (199.6, 202.5, 193.5, 199.0)}[outcome]
        flat = (199.5, 199.6, 199.4, 199.5)
    assert g["entry"] is not None
    return [b0, b1] + [flat] * (BLOCK - 2)


def mk(blocks):
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for blk in blocks:
        for a, b, d, e in blk:
            o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    return T.Bars1m(0, o, h, l, c, v, tbv)


def signal(k, side):
    g = geom(side)
    return dict(t=float(k * BLOCK * 60), verdict="SETUP_FORMING", proof=5, dir=side, setup="planted", zone="z%d" % k,
                zprice=g["entry"], ztype=ZTYPE, stop=g["stop"], target=g["target"])


def planted_inputs():
    b = mk([bars_for(s, o) for s, o in PLAN])
    return [signal(k, s) for k, (s, _) in enumerate(PLAN)], b


def net_r_hand(side, entry, exit_px, risk, fee_in, fee_out):
    """FORMULAS.md 18.5: net_R = (side*(exit-L) - fee_in*L - fee_out*exit) / R."""
    sgn = 1.0 if side == "long" else -1.0
    return (sgn * (exit_px - entry) - fee_in * entry - fee_out * exit_px) / risk


def expected_planted():
    """Hand-built expected list; exit prices are the stop / target prices from the geometry, not read from the sim."""
    out = []
    for k, (side, outcome) in enumerate(PLAN):
        g = geom(side)
        risk = abs(g["entry"] - g["stop"])
        reason = "target" if outcome == "target" else "stop"
        px = g["target"] if reason == "target" else g["stop"]
        fee_out = DERIBIT_MAKER if reason == "target" else DERIBIT_TAKER   # maker target, taker stop
        sgn = 1.0 if side == "long" else -1.0
        out.append(dict(filled=True, reason=reason, gross_r=sgn * (px - g["entry"]) / risk,
                        net_r=net_r_hand(side, g["entry"], px, risk, DERIBIT_MAKER, fee_out),
                        fee_r=(DERIBIT_MAKER * g["entry"] + fee_out * px) / risk,
                        fill_i=k * BLOCK, exit_i=k * BLOCK + 1, bars_held=1,
                        ambiguous=1 if outcome == "both" else 0, zone_tf="5m"))
    return out


def trade_diff(actual, expected, tol=1e-9):
    """Trade-list diff: list of (trade index, field, expected, actual); [] = lists identical."""
    diffs = []
    if len(actual) != len(expected):
        diffs.append((-1, "len", len(expected), len(actual)))
    for i, (a, e) in enumerate(zip(actual, expected)):
        for f, ev in e.items():
            av = a.get(f)
            same = (abs(av - ev) <= tol) if isinstance(ev, float) and isinstance(av, (int, float)) else av == ev
            if not same:
                diffs.append((i, f, ev, av))
    return diffs


def null_inputs():
    """Same 20 signals, flat noise: bar 0 touches the entry, then 99 bars of seeded noise inside +-0.3 of the entry; bar 40
    (the timeout bar, fill_i + 40) closes at entry +-0.1, alternating per side so the gross R of the timeouts cancels."""
    rng = random.Random(20261020)
    blocks, close_off = [], {"long": 0, "short": 0}
    for k, (side, _) in enumerate(PLAN):
        g = geom(side)
        e = g["entry"]
        blk = [(e + 0.2, e + 0.3, e, e + 0.1)]  # fill bar: low == entry (touch), high far below target, stop untouched
        for _ in range(BLOCK - 1):
            m = e + rng.uniform(-0.3, 0.3)
            blk.append((m, m + 0.05, m - 0.05, m))
        n = close_off[side]
        close_off[side] += 1
        off = 0.1 if n % 2 == 0 else -0.1   # long: 10 trades -> 5 x +0.1, 5 x -0.1 ; same for short
        blk[FILL_HOLD] = (e, e + 0.15, e - 0.15, e + off)
        blocks.append(blk)
    return [signal(k, s) for k, (s, _) in enumerate(PLAN)], mk(blocks)


# ---------------------------------------------------------------- mutants: scratch copies of tom_bt with one line changed
def mutant(old, new):
    src_path = HERE / "tom_bt.py"
    src = src_path.read_text(encoding="utf-8")
    assert src.count(old) == 1, "mutation anchor drifted: %r" % old
    mod = types.ModuleType("tom_bt_mutant")
    mod.__file__ = str(src_path)  # tom_bt resolves scripts/dev relative to __file__
    exec(compile(src.replace(old, new), str(src_path), "exec"), mod.__dict__)
    return mod


STOP_FIRST_OLD = "def run_variant(sigs, b, fees=FEES_DERIBIT, stop_first=True,"
STOP_FIRST_NEW = "def run_variant(sigs, b, fees=FEES_DERIBIT, stop_first=False,"
EXIT_FEE_OLD = 'fee_r = (fees["entry"] * entry + fees[kind] * px) / risk'
EXIT_FEE_NEW = 'fee_r = (fees["entry"] * entry) / risk'


def mean_net(trades):
    return sum(t["net_r"] for t in trades) / len(trades)


class TestPlantedEdge(unittest.TestCase):
    def test_hand_values_are_the_literals_in_the_docstring(self):
        # Guards the helper against the docstring arithmetic (and fee profile) so the oracle cannot drift silently.
        self.assertEqual((DERIBIT_MAKER, DERIBIT_TAKER), (0.0, 0.0005))
        self.assertAlmostEqual(net_r_hand("long", 100, 99, 1, 0, 0.0005), -1.0495, places=12)
        self.assertAlmostEqual(net_r_hand("short", 200, 202, 2, 0, 0.0005), -1.0505, places=12)
        self.assertAlmostEqual(net_r_hand("long", 100, 103, 1, 0, 0), 3.0, places=12)
        exp = expected_planted()
        self.assertAlmostEqual(sum(t["net_r"] for t in exp), 27.6, places=9)
        self.assertAlmostEqual(mean_net(exp), 1.38, places=9)

    def test_trade_list_matches_hand_built_20_of_20(self):
        sigs, b = planted_inputs()
        got = T.run_variant(sigs, b)
        diffs = trade_diff(got, expected_planted())
        self.assertEqual(diffs, [], "trade-list diff: %r" % diffs)
        matched = len(got) - len({d[0] for d in diffs})
        self.assertEqual((matched, len(got)), (20, 20))  # trades matched 20 of 20
        self.assertEqual([t["reason"] for t in got].count("target"), 12)
        self.assertEqual([t["reason"] for t in got].count("stop"), 8)

    def test_both_touch_bars_resolve_to_the_stop(self):
        sigs, b = planted_inputs()
        got = T.run_variant(sigs, b)
        for i in AMBIGUOUS_IDX:
            self.assertEqual(got[i]["reason"], "stop", i)
            self.assertEqual(got[i]["ambiguous"], 1, i)
            self.assertAlmostEqual(got[i]["gross_r"], -1.0, places=12)
        self.assertEqual(sum(t["ambiguous"] for t in got), 2)

    def test_recovered_mean_net_r_equals_hand_value(self):
        sigs, b = planted_inputs()
        got = T.run_variant(sigs, b)
        self.assertAlmostEqual(mean_net(got), 1.38, delta=1e-9)  # (12*3 - 4*1.0495 - 4*1.0505)/20
        s = T.summarize(got)
        self.assertEqual((s["n_signals"], s["n_filled"]), (20, 20))
        self.assertAlmostEqual(s["mean_net"], 1.38, delta=1e-9)
        self.assertAlmostEqual(s["win"], 0.6, delta=1e-12)
        self.assertEqual(s["ambiguous"], 2)


class TestFeeNull(unittest.TestCase):
    def test_null_mean_is_minus_round_turn_fee(self):
        sigs, b = null_inputs()
        got = T.run_variant(sigs, b)
        self.assertEqual(len(got), 20)
        self.assertTrue(all(t["filled"] and t["reason"] == "timeout" for t in got))
        self.assertTrue(all(t["bars_held"] == FILL_HOLD for t in got))
        gross = sum(t["gross_r"] for t in got) / 20
        self.assertAlmostEqual(gross, 0.0, delta=1e-9)       # noise has no edge
        self.assertAlmostEqual(mean_net(got), -0.05, delta=0.01)   # spec tolerance; hand value 0.0005*100/1 = 0.0005*200/2
        self.assertAlmostEqual(mean_net(got), -0.05, delta=1e-9)   # the construction makes it exact

    def test_null_all_taker_profile_is_minus_ten_bps_in_r(self):
        sigs, b = null_inputs()
        got = T.run_variant(sigs, b, fees=T.FEES_ALL_TAKER)
        self.assertAlmostEqual(mean_net(got), -0.10, delta=1e-9)  # 0.0010*100/1 and 0.0010*200/2

    def test_null_per_trade_fee_matches_hand_formula(self):
        sigs, b = null_inputs()
        got = T.run_variant(sigs, b)
        for t in got:
            side, e = t["dir"], float(t["zprice"])
            risk = abs(e - float(t["stop"]))
            exit_px = b.c[t["exit_i"]]
            self.assertAlmostEqual(t["net_r"], net_r_hand(side, e, exit_px, risk, DERIBIT_MAKER, DERIBIT_TAKER), delta=1e-9)


class TestPlantedDefects(unittest.TestCase):
    """The checks above must catch a one-line defect in a scratch copy of tom_bt.py (the real file is never edited)."""

    def test_stop_first_flipped_fails_on_exactly_the_both_touch_bars(self):
        M = mutant(STOP_FIRST_OLD, STOP_FIRST_NEW)
        sigs, b = planted_inputs()
        diffs = trade_diff(M.run_variant(sigs, b), expected_planted())
        self.assertNotEqual(diffs, [])
        self.assertEqual(sorted({d[0] for d in diffs}), AMBIGUOUS_IDX)
        self.assertEqual({d[1] for d in diffs} >= {"reason", "net_r"}, True)
        # 14 targets and 6 stops: mean = (14*3 - 3*1.0495 - 3*1.0505)/20 = (42 - 6.3)/20 = 1.785, not 1.38
        self.assertAlmostEqual(mean_net(M.run_variant(sigs, b)), 1.785, delta=1e-9)

    def test_documented_stop_first_false_option_differs_on_the_same_bars(self):
        sigs, b = planted_inputs()
        diffs = trade_diff(T.run_variant(sigs, b, stop_first=False), expected_planted())
        self.assertEqual(sorted({d[0] for d in diffs}), AMBIGUOUS_IDX)

    def test_dropping_the_exit_fee_fails_the_null_and_the_planted_mean(self):
        M = mutant(EXIT_FEE_OLD, EXIT_FEE_NEW)
        sigs, b = null_inputs()
        self.assertAlmostEqual(mean_net(M.run_variant(sigs, b)), 0.0, delta=1e-9)  # fee-free: net == gross == 0
        self.assertGreater(abs(mean_net(M.run_variant(sigs, b)) - (-0.05)), 0.01)  # the null assertion would fail
        sigs, b = planted_inputs()
        self.assertNotEqual(trade_diff(M.run_variant(sigs, b), expected_planted()), [])  # stop-leg fee_r/net_r differ


if __name__ == "__main__":
    unittest.main()
