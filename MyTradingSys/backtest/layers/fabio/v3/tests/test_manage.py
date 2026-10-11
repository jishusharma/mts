"""Fabio v3 management (spec 5.2): stop helpers, adds, and the single-leg walk. Expected values from spec T31-T34,
T51-T54, T62 (hand-derived there); T34 inputs are not in the spec, so the inputs here are our own with hand arithmetic."""
import unittest
import pytest

from MyTradingSys.backtest.layers.fabio.v3 import (add_allowed, add_size, be_update, defended_level, opp_stop,
                                                   simulate_trade, trail_update)


def mk(rows):
    """rows of (o, h, l, c) -> order-flow bar dicts with zero volumes (spec section 1 columns)."""
    out = []
    for k, (o, h, l, c) in enumerate(rows):
        out.append({"t": k * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": 0.0, "sell_vol": 0.0, "delta": 0.0,
                    "b99_buy_vol": 0.0, "b99_sell_vol": 0.0, "b999_buy_vol": 0.0, "b999_sell_vol": 0.0,
                    "thr_days": 30, "fp": ""})
    return out


class TestFabioV3Manage(unittest.TestCase):
    def ap(self, a, b, places=6):
        self.assertAlmostEqual(a, b, places=places)

    # ---- stop helpers
    def test_t34_trail_update_long_and_short(self):
        self.ap(trail_update(1, 100.0, 101.0, 102.0), 100.9)            # cand = 101 - 0.1
        self.assertEqual(trail_update(1, 100.0, 101.0, 100.9), 100.0)   # c not beyond cand
        self.ap(trail_update(1, 100.0, 102.0, 103.0), 101.9)
        self.assertEqual(trail_update(1, 101.5, 101.0, 102.0), 101.5)   # cand would loosen the stop
        self.ap(trail_update(-1, 100.0, 99.0, 98.0), 99.1)              # short mirror
        self.assertEqual(trail_update(1, 100.0, None, 102.0), 100.0)    # S6 None: unchanged

    def test_t51_opp_stop(self):
        self.ap(opp_stop(1, 100, 99, 99.9, 100.6), 100.0)               # cands 100.0, 99.8
        self.ap(opp_stop(1, 100, 100.4, 100.8, 101.3), 100.7)
        self.ap(opp_stop(1, 100, 99, 99.5, 99.8), 99.4)                 # 100.0 not below c
        self.ap(opp_stop(1, 100, 100.7, 100.5, 101.0), 100.7)           # 100.4 would loosen
        self.ap(opp_stop(-1, 100, 101, 100.3, 99.5), 100.0)             # short: min of 100.0, 100.4

    def test_be_update_moves_to_entry_once_distance_reached(self):                          # spec 5.2 dist
        self.assertEqual(be_update(1, 100.0, 1.0, 99.0, 101.0, 1.0), 100.0)
        self.assertEqual(be_update(1, 100.0, 1.0, 99.0, 100.9, 1.0), 99.0)         # fav 0.9 < be_k * D
        self.assertEqual(be_update(1, 100.0, 1.0, 100.0, 105.0, 1.0), 100.0)       # already at BE: no loosening

    def test_t52_defended_level(self):
        bars = mk([(100, 100, 100, 100)] * 6)
        bars[3]["h"], bars[4]["l"] = 101.6, 100.8
        absb = [0, 0, 0, 1, -1, 0]
        self.assertEqual(defended_level(bars, absb, 0, 5, 1), 101.6)
        self.assertIsNone(defended_level(bars, absb, 0, 2, 1))
        self.assertIsNone(defended_level(bars, absb, 3, 5, 1))         # a exclusive
        self.assertEqual(defended_level(bars, absb, 0, 5, -1), 100.8)

    # ---- adds
    def test_t32_add_size_budget_zero(self):
        self.ap(add_size(1, [(1, 100)], 102, 104, 1, 0.0), 1.0)
        self.ap(add_size(1, [(1, 100)], 101, 104, 1, 0.0), 1 / 3)
        self.assertEqual(add_size(1, [(1, 100)], 100.5, 104, 1, 0.0), 0.0)
        self.assertEqual(add_size(1, [(1, 100)], 100, 104, 1, 0.0), 0.0)

    def test_t62_add_size_day_budget(self):
        self.ap(add_size(1, [(1, 100)], 99, 101, 1, 3.0), 1.0)
        self.ap(add_size(1, [(1, 100)], 99, 101, 1, 1.5), 0.25)
        self.assertEqual(add_size(1, [(1, 100)], 99, 101, 1, 1.0), 0.0)

    def test_t33_t62_add_allowed_gates(self):
        base = dict(s=1, e1=100.0, stop=100.0, n_adds=0, i=100, open_idx=0, control=1, push_ok=True, curve_state="fair")
        self.assertTrue(add_allowed(**base))
        self.assertFalse(add_allowed(**{**base, "curve_state": "premium"}))
        self.assertFalse(add_allowed(**{**base, "n_adds": 2}))
        self.assertTrue(add_allowed(**{**base, "n_adds": 1}))
        self.assertFalse(add_allowed(**{**base, "i": 330}))
        self.assertTrue(add_allowed(**{**base, "i": 329}))
        self.assertFalse(add_allowed(**{**base, "control": 0}))
        self.assertFalse(add_allowed(**{**base, "push_ok": False}))
        self.assertFalse(add_allowed(**{**base, "stop": 99.0}))                    # be mode: stop below e1
        self.assertTrue(add_allowed(**{**base, "stop": 99.0, "add_mode": "day"}))
        self.assertTrue(add_allowed(**{**base, "curve_state": "premium", "s7": False}))
        short = {**base, "s": -1, "control": -1, "stop": 100.0}
        self.assertFalse(add_allowed(**{**short, "curve_state": "discount"}))
        self.assertTrue(add_allowed(**{**short, "curve_state": "premium"}))
        self.assertFalse(add_allowed(**{**base, "curve_state": None}))             # fail closed

    def test_add_allowed_rejects_unknown_add_mode(self):
        with self.assertRaises(ValueError):
            add_allowed(1, 100.0, 100.0, 0, 1, 0, 1, True, "fair", add_mode="x")

    # ---- the walk
    @staticmethod
    def _get_t53_data():
        return ([(100.2, 100.6, 99.8, 100.3), (100.3, 100.8, 99.9, 100.6), (100.6, 101.5, 100.5, 101.4),
                (101.4, 101.6, 101.0, 101.1), (101.1, 101.5, 100.8, 101.3), (101.3, 102.0, 101.2, 101.9),
                (101.9, 102.1, 101.0, 101.5)],
                [0, 0, 1, 0, 0, 1, 0],
                [0, -1, 0, 1, -1, 0, 0])

    @staticmethod
    def _moves(t):
        return [(i, round(p, 6), k) for i, p, k in t["moves"]]

    def test_t31_dist_break_even_exit(self):
        bars = mk([(100, 100.2, 99.5, 100.1), (100.1, 101.0, 99.5, 100.5), (100.2, 100.4, 99.9, 100.0)])
        t = simulate_trade(bars, 0, 1, 100.0, 1.0, 99.0, mgmt="dist", be_k=1.0)
        self.ap(t["exit"], 100.0)
        self.assertEqual(t["reason"], "be")
        self.ap(t["fee_r"], 0.05)
        self.ap(t["net_r"], -0.05)

    def test_t53_event_management_end_to_end(self):
        t53, ctrl, absb = self._get_t53_data()
        t = simulate_trade(mk(t53), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=ctrl, absorbed=absb)
        self.assertEqual(self._moves(t), [(1, 100.0, "opp"), (3, 100.4, "own"), (4, 100.7, "opp"), (5, 101.1, "trail")])
        self.assertEqual(t["exit_idx"], 6)
        self.assertEqual(t["reason"], "trail")
        self.ap(t["exit"], 101.1)
        self.ap(t["gross_r"], 1.1)
        self.ap(t["fee_r"], 0.05)
        self.ap(t["net_r"], 1.05)

    def test_t53_same_bars_dist_mode(self):
        t53, ctrl, absb = self._get_t53_data()
        t = simulate_trade(mk(t53), 0, 1, 100.0, 1.0, 99.0, mgmt="dist", be_k=1.0, ctrl=ctrl, absorbed=absb)
        self.assertEqual(self._moves(t), [(2, 100.0, "be"), (2, 100.4, "trail"), (5, 101.1, "trail")])
        self.ap(t["exit"], 101.1)

    def test_t54_event_no_events_runs_to_window_end(self):
        t53, _, _ = self._get_t53_data()
        t = simulate_trade(mk(t53), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=[0] * 7, absorbed=[0] * 7)
        self.assertEqual(t["moves"], [])
        self.assertEqual(t["reason"], "window_end")
        self.ap(t["exit"], 101.5)
        self.ap(t["gross_r"], 1.5)
        self.ap(t["net_r"], 1.45)

    def test_t54_own_absorption_alone_never_exits(self):
        t53, _, _ = self._get_t53_data()
        ab = [0, 0, 0, 1, 0, 0, 0]
        t = simulate_trade(mk(t53), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=[0] * 7, absorbed=ab)
        self.assertEqual(t["moves"], [])
        self.assertEqual(t["reason"], "window_end")
        self.ap(t["net_r"], 1.45)

    def test_stop_gap_exits_at_open_and_stop_first_beats_target(self):                     # spec 5.2
        bars = mk([(100, 100.2, 99.9, 100.1), (98.0, 98.5, 97.0, 98.0)])
        t = simulate_trade(bars, 0, 1, 100.0, 1.0, 99.0, mgmt="dist")
        self.assertEqual(t["exit"], 98.0)
        self.assertEqual(t["exit_idx"], 1)
        both = mk([(100, 100.2, 99.9, 100.1), (100.0, 103.0, 98.0, 100.0)])
        t = simulate_trade(both, 0, 1, 100.0, 1.0, 99.0, mgmt="dist", target=102.0)
        self.assertNotEqual(t["reason"], "target")
        self.ap(t["exit"], 99.0)
        t = simulate_trade(both, 0, 1, 100.0, 1.0, 99.0, mgmt="dist", target=102.0, stop_first=False)
        self.assertEqual(t["reason"], "target")

    def test_walk_rejects_bad_mgmt(self):
        t53, _, _ = self._get_t53_data()
        with self.assertRaises(ValueError):
            simulate_trade(mk(t53), 0, 1, 100.0, 1.0, 99.0, mgmt="x")


if __name__ == "__main__":
    unittest.main()


# ---- the walk
T53 = [(100.2, 100.6, 99.8, 100.3), (100.3, 100.8, 99.9, 100.6), (100.6, 101.5, 100.5, 101.4),
       (101.4, 101.6, 101.0, 101.1), (101.1, 101.5, 100.8, 101.3), (101.3, 102.0, 101.2, 101.9),
       (101.9, 102.1, 101.0, 101.5)]
CTRL = [0, 0, 1, 0, 0, 1, 0]
ABSB = [0, -1, 0, 1, -1, 0, 0]


def _moves(t):
    return [(i, round(p, 6), k) for i, p, k in t["moves"]]


def test_t31_dist_break_even_exit():
    bars = mk([(100, 100.2, 99.5, 100.1), (100.1, 101.0, 99.5, 100.5), (100.2, 100.4, 99.9, 100.0)])
    t = simulate_trade(bars, 0, 1, 100.0, 1.0, 99.0, mgmt="dist", be_k=1.0)
    assert t["exit"] == pytest.approx(100.0) and t["reason"] == "be"
    assert t["fee_r"] == pytest.approx(0.05) and t["net_r"] == pytest.approx(-0.05)


def test_t53_event_management_end_to_end():
    t = simulate_trade(mk(T53), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=CTRL, absorbed=ABSB)
    assert _moves(t) == [(1, 100.0, "opp"), (3, 100.4, "own"), (4, 100.7, "opp"), (5, 101.1, "trail")]
    assert t["exit_idx"] == 6 and t["reason"] == "trail" and t["exit"] == pytest.approx(101.1)
    assert t["gross_r"] == pytest.approx(1.1) and t["fee_r"] == pytest.approx(0.05) and t["net_r"] == pytest.approx(1.05)


def test_t53_same_bars_dist_mode():
    t = simulate_trade(mk(T53), 0, 1, 100.0, 1.0, 99.0, mgmt="dist", be_k=1.0, ctrl=CTRL, absorbed=ABSB)
    assert _moves(t) == [(2, 100.0, "be"), (2, 100.4, "trail"), (5, 101.1, "trail")]
    assert t["exit"] == pytest.approx(101.1)


def test_t54_event_no_events_runs_to_window_end():
    t = simulate_trade(mk(T53), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=[0] * 7, absorbed=[0] * 7)
    assert t["moves"] == [] and t["reason"] == "window_end" and t["exit"] == pytest.approx(101.5)
    assert t["gross_r"] == pytest.approx(1.5) and t["net_r"] == pytest.approx(1.45)


def test_t54_own_absorption_alone_never_exits():
    ab = [0, 0, 0, 1, 0, 0, 0]
    t = simulate_trade(mk(T53), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=[0] * 7, absorbed=ab)
    assert t["moves"] == [] and t["reason"] == "window_end" and t["net_r"] == pytest.approx(1.45)


def test_stop_gap_exits_at_open_and_stop_first_beats_target():                     # spec 5.2
    bars = mk([(100, 100.2, 99.9, 100.1), (98.0, 98.5, 97.0, 98.0)])
    t = simulate_trade(bars, 0, 1, 100.0, 1.0, 99.0, mgmt="dist")
    assert t["exit"] == 98.0 and t["exit_idx"] == 1
    both = mk([(100, 100.2, 99.9, 100.1), (100.0, 103.0, 98.0, 100.0)])
    t = simulate_trade(both, 0, 1, 100.0, 1.0, 99.0, mgmt="dist", target=102.0)
    assert t["reason"] != "target" and t["exit"] == pytest.approx(99.0)
    t = simulate_trade(both, 0, 1, 100.0, 1.0, 99.0, mgmt="dist", target=102.0, stop_first=False)
    assert t["reason"] == "target"


def test_walk_rejects_bad_mgmt():
    with pytest.raises(ValueError):
        simulate_trade(mk(T53), 0, 1, 100.0, 1.0, 99.0, mgmt="x")
