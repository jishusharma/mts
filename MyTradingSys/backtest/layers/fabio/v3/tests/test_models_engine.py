"""Fabio v3 models (spec section 4) and the engine. Bars are hand-built; EXPECT values hand-derived from the spec rules.
T58 is the spec's own worked example; the model A/B/C cases use our own bars with the arithmetic in the comments."""
import random

import pytest

from MyTradingSys.backtest.layers.fabio.v3 import d_and_stop, model_a_trade, model_b, model_c, model_d_trade
from MyTradingSys.backtest.layers.fabio.v3 import engine


def mk(rows, b99=None):
    out = []
    for k, (o, h, l, c) in enumerate(rows):
        out.append({"t": k * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": 0.0, "sell_vol": 0.0, "delta": 0.0,
                    "b99_buy_vol": (b99 or {}).get(k, 0.0), "b99_sell_vol": 0.0, "b999_buy_vol": 0.0,
                    "b999_sell_vol": 0.0, "thr_days": 30, "fp": ""})
    return out


def test_d_and_stop_dmax_rule():                                       # spec 4 Common: no arm if D > Dmax * entry
    assert d_and_stop(1, 100.0, 0.5, 0.003, 0.01) == (pytest.approx(0.5), pytest.approx(99.5))
    assert d_and_stop(1, 100.0, 1.5, 0.003, 0.01) is None
    assert d_and_stop(1, 100.0, 0.1, 0.003, 0.01)[0] == pytest.approx(0.3)   # floor f * entry wins


# ---- model A: armed at the close of bar 0, limit 104 (LVN*), O 100 -> D = max(0.312, 4.0 + 0.1) = 4.1
A_BARS = [(105, 105.5, 104.5, 105), (105, 105, 103.9, 104.2), (104.2, 108.3, 104.1, 108.0), (108.0, 108.1, 103.9, 104.0)]


def test_model_a_rest_be_exit():
    r = model_a_trade(mk(A_BARS), 0, 1, 100.0, 104.0, 0.003, 0.05, mgmt="dist", be_k=1.0, end_idx=3)
    t = r["trades"][0]
    assert (r["arms"], r["fills"]) == (1, 1) and t["fill_idx"] == 1
    assert t["D"] == pytest.approx(4.1) and t["stop0"] == pytest.approx(99.9)
    assert t["reason"] == "be" and t["exit"] == pytest.approx(104.0)           # fav 4.3 >= 4.1 on bar 2
    assert t["fee_r"] == pytest.approx(0.0005 * 104 / 4.1) and t["net_r"] == pytest.approx(-0.0005 * 104 / 4.1)


def test_model_a_no_arm_when_d_exceeds_dmax():
    r = model_a_trade(mk(A_BARS), 0, 1, 100.0, 104.0, 0.003, 0.01, end_idx=3)    # 4.1 > 1.04
    assert r["arms"] == 0 and r["trades"] == []


def test_model_a_entry_cutoff_blocks_late_decision():                          # spec 2: no entries at/after open+330
    r = model_a_trade(mk(A_BARS), 0, 1, 100.0, 104.0, 0.003, 0.05, end_idx=3, last_entry_idx=-1)
    assert r["arms"] == 0


# ---- model B: balance H 100 / L 98; probe bar 1 (c 100.5, absorbed), reclaim bar 2 (c 99.9 < H) -> short
B_BARS = [(99, 99.5, 98.8, 99.0), (99.0, 100.8, 99.0, 100.5), (100.5, 100.6, 99.5, 99.9), (99.9, 100.0, 99.0, 99.4),
          (99.4, 99.6, 97.8, 98.2)]


def test_model_b_edge_target():
    r = model_b(mk(B_BARS), 0, {"H": 100.0, "L": 98.0}, [0, 1, 0, 0, 0], 0.003, 0.05, target_mode="edge")
    t = r["trades"][0]
    # Xp = 100.8 (probe extreme incl. the reclaim bar), entry c[2] = 99.9 -> structural |100.8-99.9|+0.1 = 1.0, D 1.0
    assert t["s"] == -1 and t["entry"] == pytest.approx(99.9) and t["D"] == pytest.approx(1.0)
    assert t["stop0"] == pytest.approx(100.9) and t["fill_idx"] == 3
    assert t["reason"] == "target" and t["exit"] == pytest.approx(98.0)
    assert t["gross_r"] == pytest.approx(1.9) and t["fee_r"] == 0.0           # maker entry, maker target


def test_model_b_requires_absorption_in_the_probe():
    r = model_b(mk(B_BARS), 0, {"H": 100.0, "L": 98.0}, [0] * 5, 0.003, 0.05)
    assert r["arms"] == 0 and r["trades"] == []


def test_model_b_trail_variant_has_no_target():
    r = model_b(mk(B_BARS), 0, {"H": 100.0, "L": 98.0}, [0, 1, 0, 0, 0], 0.003, 0.05, target_mode="trail")
    assert r["trades"][0]["target"] is None


def test_model_b_rejects_bad_modes():
    with pytest.raises(ValueError):
        model_b(mk(B_BARS), 0, {"H": 100.0, "L": 98.0}, [0] * 5, 0.003, 0.05, target_mode="x")


# ---- model C: IB = bars 0-2 (H 103, L 99, mid 101); bar 3 closes 103.8 with a big push; limit 103 -> D 2.1
C_ROWS = [(100, 103, 99, 101)] * 3 + [(102.5, 104.0, 102.8, 103.8), (103.5, 103.6, 102.9, 103.2),
                                      (103.2, 103.3, 100.5, 101.5), (101.5, 101.6, 101.0, 101.2)]


def test_model_c_ivb_stop_out_is_minus_one_r():
    r = model_c(mk(C_ROWS, b99={3: 2.0}), 0, 3, 1, 0.003, 0.05, entry_mode="rest", tier="99")
    t = r["trades"][0]
    assert t["entry"] == pytest.approx(103.0) and t["D"] == pytest.approx(2.1) and t["stop0"] == pytest.approx(100.9)
    assert t["reason"] == "stop" and t["gross_r"] == pytest.approx(-1.0)


def test_model_c_gate_closed_no_arm_and_no_push_no_arm():
    assert model_c(mk(C_ROWS, b99={3: 2.0}), 0, 3, 1, 0.003, 0.05, gate_open=False)["arms"] == 0
    assert model_c(mk(C_ROWS), 0, 3, 1, 0.003, 0.05)["arms"] == 0                 # S4 false: no big push


# ---- model D: the spec's T58 example
D_ROWS = [(101, 102.8, 100.9, 102.5), (102.5, 102.9, 102.0, 102.6), (102.6, 102.7, 101.9, 102.4),
          (102.4, 105.2, 102.3, 105.0), (104.0, 104.2, 102.1, 102.5)]
D_CTRL = [0, 0, 0, 1, 0]


def d_trade():
    return model_d_trade(mk(D_ROWS), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="rest", ctrl=D_CTRL, mgmt="dist",
                         be_k=1.0)


def test_t58_rest_fill_be_then_trail():
    t = d_trade()["trades"][0]
    assert t["fill_idx"] == 2 and t["entry"] == pytest.approx(102.0)           # bar 1 does not fill (l 102.0 > 101.9)
    assert t["D"] == pytest.approx(3.1) and t["stop0"] == pytest.approx(98.9)
    assert t["reason"] == "trail" and t["exit"] == pytest.approx(102.2) and t["exit_idx"] == 4
    assert t["gross_r"] == pytest.approx(0.064516, abs=1e-6)
    assert t["fee_r"] == pytest.approx(0.016452, abs=1e-6) and t["net_r"] == pytest.approx(0.048065, abs=1e-6)


def test_t58_dmax_one_percent_does_not_arm():
    r = model_d_trade(mk(D_ROWS), 0, 1, 102.0, 99.0, 0.003, 0.01, entry_mode="rest", ctrl=D_CTRL, mgmt="dist")
    assert r["arms"] == 0


def test_t58_rest_order_expires_after_three_bars():
    rows = list(D_ROWS)
    rows[2] = (102.6, 102.7, 102.0, 102.4)           # bar 2 l 102.0: no fill
    rows[4] = (104.0, 104.2, 101.8, 102.5)           # bar 4 l 101.8 would fill, but the order expired after bar 3
    r = model_d_trade(mk(rows), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="rest", ctrl=D_CTRL, mgmt="dist")
    assert (r["arms"], r["fills"], r["missed_winners"]) == (1, 0, 0)


def test_t58_confirm_is_taker_at_next_open():
    r = model_d_trade(mk(D_ROWS), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="confirm", ctrl=D_CTRL, mgmt="dist")
    t = r["trades"][0]
    assert t["fill_idx"] == 1 and t["entry"] == pytest.approx(102.5) and t["D"] == pytest.approx(3.6)
    assert t["stop0"] == pytest.approx(98.9) and t["reason"] == "window_end" and t["exit"] == pytest.approx(102.5)
    assert t["gross_r"] == pytest.approx(0.0) and t["net_r"] == pytest.approx(-0.028472, abs=1e-6)


def test_model_d_rejects_bad_entry_mode():
    with pytest.raises(ValueError):
        model_d_trade(mk(D_ROWS), 0, 1, 102.0, 99.0, 0.003, 0.05, entry_mode="x")


# ---- engine
CFG = dict(N=20, p=0.05, z_hi=2.5, m_c=5, f=0.003, g="off", entry_mode="rest", mgmt="event")
VERDICTS = {"IDLE", "IMPULSE", "PROBE", "ARMED", "SIGNAL", "IN_TRADE", "DONE"}


def rand_bars(n=140, seed=3):
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


@pytest.mark.parametrize("key", ["N", "p", "z_hi", "m_c", "f", "g", "entry_mode", "mgmt"])
def test_engine_grid_params_are_required(key):                       # prompt: NS-grid params REQUIRED, no defaults
    cfg = {k: v for k, v in CFG.items() if k != key}
    with pytest.raises(ValueError):
        engine.run(rand_bars(), cfg)


def test_engine_dist_mgmt_requires_be_k():
    with pytest.raises(ValueError):
        engine.run(rand_bars(), {**CFG, "mgmt": "dist"})


def test_engine_rejects_unknown_model_and_bad_modes():
    with pytest.raises(ValueError):
        engine.run(rand_bars(), {**CFG, "models": ("Z",)})
    with pytest.raises(ValueError):
        engine.run(rand_bars(), {**CFG, "entry_mode": "x"})


def test_engine_output_contract_and_vocabulary():
    out = engine.run(rand_bars(), CFG)
    assert set(out) == {"verdict", "model", "side", "entry", "stop", "target", "management", "diagnostics"}
    assert out["verdict"] in VERDICTS
    assert set(out["diagnostics"]) == {"A", "B", "C", "D"}
    assert all(v["state"] in VERDICTS for v in out["diagnostics"].values())


def test_engine_flat_window_is_idle():
    out = engine.run(mk([(100, 100, 100, 100)] * 80), CFG)
    assert out["verdict"] == "IDLE" and out["model"] is None and out["entry"] is None


def test_engine_causal_as_of_ignores_later_bars():                   # spec 2 / T49: deleting bars > i changes nothing
    bars = rand_bars()
    for i in (60, 100, 139):
        full = engine.run(bars, {**CFG, "as_of": i})
        cut = engine.run(bars[:i + 1], CFG)
        assert {k: v for k, v in full.items() if k != "diagnostics"} == {k: v for k, v in cut.items() if k != "diagnostics"}
        assert {m: d["state"] for m, d in full["diagnostics"].items()} == {m: d["state"] for m, d in cut["diagnostics"].items()}
