"""Fabio v3 models (spec section 4) and the engine. Bars are hand-built; EXPECT values hand-derived from the spec rules.
T58 is the spec's own worked example; the model A/B/C cases use our own bars with the arithmetic in the comments."""
import random
import unittest

from MyTradingSys.backtest.layers.fabio.v3 import d_and_stop, model_a_trade, model_b, model_c, model_d_trade
from MyTradingSys.backtest.layers.fabio.v3 import engine


def mk(rows, b99=None):
    out = []
    for k, (o, h, l, c) in enumerate(rows):
        out.append({"t": k * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": 0.0, "sell_vol": 0.0, "delta": 0.0,
                    "b99_buy_vol": (b99 or {}).get(k, 0.0), "b99_sell_vol": 0.0, "b999_buy_vol": 0.0,
                    "b999_sell_vol": 0.0, "thr_days": 30, "fp": ""})
    return out


class TestFabioV3ModelsEngine(unittest.TestCase):
    def ap(self, a, b, places=6):
        self.assertAlmostEqual(a, b, places=places)

    def test_d_and_stop_dmax_rule(self):                                       # spec 4 Common: no arm if D > Dmax * entry
        d, s = d_and_stop(1, 100.0, 0.5, 0.003, 0.01)
        self.ap(d, 0.5)
        self.ap(s, 99.5)
        self.assertIsNone(d_and_stop(1, 100.0, 1.5, 0.003, 0.01))
        d, s = d_and_stop(1, 100.0, 0.1, 0.003, 0.01)
        self.ap(d, 0.3)   # floor f * entry wins

    # ---- model A: armed at the close of bar 0, limit 104 (LVN*), O 100 -> D = max(0.312, 4.0 + 0.1) = 4.1
    @staticmethod
    def _get_a_bars():
        return [(105, 105.5, 104.5, 105), (105, 105, 103.9, 104.2), (104.2, 108.3, 104.1, 108.0), (108.0, 108.1, 103.9, 104.0)]

    def test_model_a_rest_be_exit(self):
        a_bars = self._get_a_bars()
        r = model_a_trade(mk(a_bars), 0, 1, 100.0, 104.0, 0.003, 0.05, mgmt="dist", be_k=1.0, end_idx=3)
        t = r["trades"][0]
        self.assertEqual(r["arms"], 1)
        self.assertEqual(r["fills"], 1)
        self.assertEqual(t["fill_idx"], 1)
        self.ap(t["D"], 4.1)
        self.ap(t["stop0"], 99.9)
        self.assertEqual(t["reason"], "be")
        self.ap(t["exit"], 104.0)           # fav 4.3 >= 4.1 on bar 2
        self.ap(t["fee_r"], 0.0005 * 104 / 4.1)
        self.ap(t["net_r"], -0.0005 * 104 / 4.1)

    def test_model_a_no_arm_when_d_exceeds_dmax(self):
        a_bars = self._get_a_bars()
        r = model_a_trade(mk(a_bars), 0, 1, 100.0, 104.0, 0.003, 0.01, end_idx=3)    # 4.1 > 1.04
        self.assertEqual(r["arms"], 0)
        self.assertEqual(r["trades"], [])

    def test_model_a_entry_cutoff_blocks_late_decision(self):                          # spec 2: no entries at/after open+330
        a_bars = self._get_a_bars()
        r = model_a_trade(mk(a_bars), 0, 1, 100.0, 104.0, 0.003, 0.05, end_idx=3, last_entry_idx=-1)
        self.assertEqual(r["arms"], 0)

    # ---- model B: balance H 100 / L 98; probe bar 1 (c 100.5, absorbed), reclaim bar 2 (c 99.9 < H) -> short
    @staticmethod
    def _get_b_bars():
        return [(99, 99.5, 98.8, 99.0), (99.0, 100.8, 99.0, 100.5), (100.5, 100.6, 99.5, 99.9), (99.9, 100.0, 99.0, 99.4),
                (99.4, 99.6, 97.8, 98.2)]

    def test_model_b_edge_target(self):
        b_bars = self._get_b_bars()
        r = model_b(mk(b_bars), 0, {"H": 100.0, "L": 98.0}, [0, 1, 0, 0, 0], 0.003, 0.05, target_mode="edge")
        t = r["trades"][0]
        # Xp = 100.8 (probe extreme incl. the reclaim bar), entry c[2] = 99.9 -> structural |100.8-99.9|+0.1 = 1.0, D 1.0
        self.assertEqual(t["s"], -1)
        self.ap(t["entry"], 99.9)
        self.ap(t["D"], 1.0)
        self.ap(t["stop0"], 100.9)
        self.assertEqual(t["fill_idx"], 3)
        self.assertEqual(t["reason"], "target")
        self.ap(t["exit"], 98.0)
        self.ap(t["gross_r"], 1.9)
        self.assertEqual(t["fee_r"], 0.0)           # maker entry, maker target

    def test_model_b_requires_absorption_in_the_probe(self):
        b_bars = self._get_b_bars()
        r = model_b(mk(b_bars), 0, {"H": 100.0, "L": 98.0}, [0] * 5, 0.003, 0.05)
        self.assertEqual(r["arms"], 0)
        self.assertEqual(r["trades"], [])

    def test_model_b_trail_variant_has_no_target(self):
        b_bars = self._get_b_bars()
        r = model_b(mk(b_bars), 0, {"H": 100.0, "L": 98.0}, [0, 1, 0, 0, 0], 0.003, 0.05, target_mode="trail")
        self.assertIsNone(r["trades"][0]["target"])

    def test_model_b_rejects_bad_modes(self):
        b_bars = self._get_b_bars()
        with self.assertRaises(ValueError):
            model_b(mk(b_bars), 0, {"H": 100.0, "L": 98.0}, [0] * 5, 0.003, 0.05, target_mode="x")

    # ---- model C: IB = bars 0-2 (H 103, L 99, mid 101); bar 3 closes 103.8 with a big push; limit 103 -> D 2.1
    @staticmethod
    def _get_c_rows():
        return [(100, 103, 99, 101)] * 3 + [(102.5, 104.0, 102.8, 103.8), (103.5, 103.6, 102.9, 103.2),
                                            (103.2, 103.3, 100.5, 101.5), (101.5, 101.6, 101.0, 101.2)]

    def test_model_c_ivb_stop_out_is_minus_one_r(self):
        c_rows = self._get_c_rows()
        r = model_c(mk(c_rows, b99={3: 2.0}), 0, 3, 1, 0.003, 0.05, entry_mode="rest", tier="99")
        t = r["trades"][0]
        self.ap(t["entry"], 103.0)
        self.ap(t["D"], 2.1)
        self.ap(t["stop0"], 100.9)
        self.assertEqual(t["reason"], "stop")
        self.ap(t["gross_r"], -1.0)

    def test_model_c_gate_closed_no_arm_and_no_push_no_arm(self):
        c_rows = self._get_c_rows()
        self.assertEqual(model_c(mk(c_rows, b99={3: 2.0}), 0, 3, 1, 0.003, 0.05, gate_open=False)["arms"], 0)
        self.assertEqual(model_c(mk(c_rows), 0, 3, 1, 0.003, 0.05)["arms"], 0)                 # S4 false: no big push

    # ---- model D: the spec's T58 example
    @staticmethod
    def _get_d_rows():
        return [(101, 102.8, 100.9, 102.5), (102.5, 102.9, 102.0, 102.6), (102.6, 102.7, 101.9, 102.4),
                (102.4, 105.2, 102.3, 105.0), (104.0, 104.2, 102.1, 102.5)]

    @staticmethod
    def _get_d_ctrl():
        return [0, 0, 0, 1, 0]

    def _d_trade(self):
        d_rows = self._get_d_rows()
        d_ctrl = self._get_d_ctrl()
        return model_d_trade(mk(d_rows), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="rest", ctrl=d_ctrl, mgmt="dist",
                             be_k=1.0)

    def test_t58_rest_fill_be_then_trail(self):
        t = self._d_trade()["trades"][0]
        self.assertEqual(t["fill_idx"], 2)
        self.ap(t["entry"], 102.0)           # bar 1 does not fill (l 102.0 > 101.9)
        self.ap(t["D"], 3.1)
        self.ap(t["stop0"], 98.9)
        self.assertEqual(t["reason"], "trail")
        self.ap(t["exit"], 102.2, places=5)
        self.assertEqual(t["exit_idx"], 4)
        self.ap(t["gross_r"], 0.064516, places=6)
        self.ap(t["fee_r"], 0.016452, places=6)
        self.ap(t["net_r"], 0.048065, places=6)

    def test_t58_dmax_one_percent_does_not_arm(self):
        d_rows = self._get_d_rows()
        d_ctrl = self._get_d_ctrl()
        r = model_d_trade(mk(d_rows), 0, 1, 102.0, 99.0, 0.003, 0.01, entry_mode="rest", ctrl=d_ctrl, mgmt="dist")
        self.assertEqual(r["arms"], 0)

    def test_t58_rest_order_expires_after_three_bars(self):
        d_rows = list(self._get_d_rows())
        d_ctrl = self._get_d_ctrl()
        d_rows[2] = (102.6, 102.7, 102.0, 102.4)           # bar 2 l 102.0: no fill
        d_rows[4] = (104.0, 104.2, 101.8, 102.5)           # bar 4 l 101.8 would fill, but the order expired after bar 3
        r = model_d_trade(mk(d_rows), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="rest", ctrl=d_ctrl, mgmt="dist")
        self.assertEqual((r["arms"], r["fills"], r["missed_winners"]), (1, 0, 0))

    def test_t58_confirm_is_taker_at_next_open(self):
        d_rows = self._get_d_rows()
        d_ctrl = self._get_d_ctrl()
        r = model_d_trade(mk(d_rows), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="confirm", ctrl=d_ctrl, mgmt="dist")
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 1)
        self.ap(t["entry"], 102.5)
        self.ap(t["D"], 3.6)
        self.ap(t["stop0"], 98.9)
        self.assertEqual(t["reason"], "window_end")
        self.ap(t["exit"], 102.5)
        self.ap(t["gross_r"], 0.0)
        self.ap(t["net_r"], -0.028472, places=6)

    def test_model_d_rejects_bad_entry_mode(self):
        d_rows = self._get_d_rows()
        with self.assertRaises(ValueError):
            model_d_trade(mk(d_rows), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="x")

    # ---- engine
    @staticmethod
    def _get_cfg():
        return dict(N=20, p=0.05, z_hi=2.5, m_c=5, f=0.003, g="off", entry_mode="rest", mgmt="event")

    @staticmethod
    def _get_verdicts():
        return {"IDLE", "IMPULSE", "PROBE", "ARMED", "SIGNAL", "IN_TRADE", "DONE"}

    @staticmethod
    def _rand_bars(n=140, seed=3):
        rng, bars, px = random.Random(seed), [], 100.0
        for k in range(n):
            o = px
            c = o + rng.uniform(-0.6, 0.6)
            h, l = max(o, c) + rng.uniform(0, 0.3), min(o, c) - rng.uniform(0, 0.3)
            buy, sell = rng.uniform(1, 9), rng.uniform(1, 9)
            bars.append({"t": k * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": buy, "sell_vol": sell,
                         "delta": buy - sell, "b99_buy_vol": rng.choice([0, 0, 3]), "b99_sell_vol": rng.choice([0, 0, 3]),
                         "b999_buy_vol": 0.0, "b999_sell_vol": 0.0, "thr_days": 30, "fp": "%d:%.2f:%.2f" % (int(l), buy, sell)})
            px = c
        return bars

    def test_engine_grid_params_are_required(self):                       # prompt: NS-grid params REQUIRED, no defaults
        cfg = self._get_cfg()
        for key in ["N", "p", "z_hi", "m_c", "f", "g", "entry_mode", "mgmt"]:
            cfg_missing = {k: v for k, v in cfg.items() if k != key}
            with self.assertRaises(ValueError):
                engine.run(self._rand_bars(), cfg_missing)

    def test_engine_dist_mgmt_requires_be_k(self):
        cfg = self._get_cfg()
        with self.assertRaises(ValueError):
            engine.run(self._rand_bars(), {**cfg, "mgmt": "dist"})

    def test_engine_rejects_unknown_model_and_bad_modes(self):
        cfg = self._get_cfg()
        with self.assertRaises(ValueError):
            engine.run(self._rand_bars(), {**cfg, "models": ("Z",)})
        with self.assertRaises(ValueError):
            engine.run(self._rand_bars(), {**cfg, "entry_mode": "x"})

    def test_engine_output_contract_and_vocabulary(self):
        cfg = self._get_cfg()
        out = engine.run(self._rand_bars(), cfg)
        self.assertEqual(set(out), {"verdict", "model", "side", "entry", "stop", "target", "management", "diagnostics"})
        verdicts = self._get_verdicts()
        self.assertIn(out["verdict"], verdicts)
        self.assertEqual(set(out["diagnostics"]), {"A", "B", "C", "D"})
        for v in out["diagnostics"].values():
            self.assertIn(v["state"], verdicts)

    def test_engine_flat_window_is_idle(self):
        cfg = self._get_cfg()
        out = engine.run(mk([(100, 100, 100, 100)] * 80), cfg)
        self.assertEqual(out["verdict"], "IDLE")
        self.assertIsNone(out["model"])
        self.assertIsNone(out["entry"])

    def test_engine_causal_as_of_ignores_later_bars(self):                   # spec 2 / T49: deleting bars > i changes nothing
        cfg = self._get_cfg()
        bars = self._rand_bars()
        for i in (60, 100, 139):
            full = engine.run(bars, {**cfg, "as_of": i})
            cut = engine.run(bars[:i + 1], cfg)
            full_diag = {k: v for k, v in full.items() if k != "diagnostics"}
            cut_diag = {k: v for k, v in cut.items() if k != "diagnostics"}
            self.assertEqual(full_diag, cut_diag)
            full_states = {m: d["state"] for m, d in full["diagnostics"].items()}
            cut_states = {m: d["state"] for m, d in cut["diagnostics"].items()}
            self.assertEqual(full_states, cut_states)


if __name__ == "__main__":
    unittest.main()
