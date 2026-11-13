import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_1113 as r

H = 3600000
COST = 2 * 0.0005 + 0.0002  # round trip as a fraction of entry price (fees.BINANCE_TAKER, SLIPPAGE_RT_S13), computed by hand


def mk(rows, skip=()):
    """rows: (open, high, low, close) per bar; bar i opens at i*H (indices in `skip` are removed to make gaps)."""
    return [[i * H, o, h, l, c, 1.0] for i, (o, h, l, c) in enumerate(rows) if i not in skip]


def flat(c, wick=0.1):
    return (c, c + wick, c - wick, c)


def r03_rows():
    # closes 10,12,11,9,10,13,12: A=idx1 (12), C=idx3 (9, lowest close between), B=idx5 (13 > A), red confirm candle idx6
    rows = [flat(10), (10, 20.0, 9.9, 12), flat(11), flat(9), flat(10), (10, 13.2, 9.9, 13), (13, 13.5, 11.9, 12)]
    return rows  # bar1 has a 20.0 wick: on wicks B (13.2) is NOT a higher high than A (20.0); on closes it is


RSI_R03 = [None, 70, 60, 50, 55, 60, 55]
RSI_R04 = [None, 30, 40, 50, 45, 40, 45]


def test_rsi_wilder_hand_value():
    # n=3 closes 10,11,10,12,13: avg gain 1, avg loss 1/3 -> RSI 75; next gain 1 -> gain 1, loss 2/9 -> RSI 100-100/5.5
    out = r.rsi_wilder([10, 11, 10, 12, 13], 3)
    assert out[:3] == [None, None, None]
    assert abs(out[3] - 75.0) < 1e-9
    assert abs(out[4] - (100 - 100 / 5.5)) < 1e-9


def test_r03_detects_on_closes_only_not_wicks():
    bars = mk(r03_rows())
    rsi = [None, 70, 0, 0, 0, 60, 0]  # RSI lower high at B (60 < 70)
    sig = r.find_signals(bars, 12, "R03", rsi=rsi)
    assert len(sig) == 1
    s = sig[0]
    assert (s["t"], s["a"], s["b"]) == (6, 1, 5)
    assert s["entry"] == 12 and s["stop"] == 13.5 and s["target"] == 9
    # RSI higher at B: no divergence, no signal
    assert r.find_signals(bars, 12, "R03", rsi=[None, 60, 0, 0, 0, 70, 0]) == []
    # lookback shorter than the A-B distance (4 bars): no signal
    assert r.find_signals(bars, 3, "R03", rsi=rsi) == []


def r04_rows():
    # closes 20,18,19,21,20,17,18: A=idx1 (18), C=idx3 (21 highest close), B=idx5 (17 < A), green confirm idx6
    return [flat(20), (20, 20.1, 10.0, 18), flat(19), flat(21), flat(20), (20, 20.1, 16.8, 17), (17, 18.2, 16.5, 18)]


def test_r04_stop_below_signal_low_target_point_c():
    bars = mk(r04_rows())
    sig = r.find_signals(bars, 12, "R04", rsi=[None, 30, 0, 0, 0, 40, 0])
    assert len(sig) == 1
    s = sig[0]
    assert (s["t"], s["a"], s["b"]) == (6, 1, 5)
    assert s["entry"] == 18 and s["stop"] == 16.5 and s["target"] == 21
    # target hit: risk 1.5, reward 3 -> gross 2R; cost 0.0012*18/1.5 = 0.0144R
    t = r.simulate(mk(r04_rows() + [(18, 21.1, 17.9, 20)]), sig, 12, H)
    assert len(t) == 1 and t[0]["reason"] == "target"
    assert abs(t[0]["net_r"] - (2 - COST * 18 / 1.5)) < 1e-9
    # a bar touching both stop and target counts as the stop: gross -1R
    t = r.simulate(mk(r04_rows() + [(18, 21.5, 16.0, 20)]), sig, 12, H)
    assert t[0]["reason"] == "stop" and abs(t[0]["net_r"] - (-1 - COST * 18 / 1.5)) < 1e-9


def test_r03_short_target_and_cap_and_gap():
    sig = r.find_signals(mk(r03_rows()), 12, "R03", rsi=[None, 70, 0, 0, 0, 60, 0])
    # target 9 hit: risk 1.5, reward 3 -> 2R gross, cost 0.0012*12/1.5 = 0.0096R
    t = r.simulate(mk(r03_rows() + [(12, 12.1, 8.9, 9)]), sig, 12, H)
    assert t[0]["reason"] == "target" and abs(t[0]["net_r"] - (2 - COST * 12 / 1.5)) < 1e-9
    # neither level touched for 2*lookback = 24 bars: exit at the close of bar t+24 (=11.0): gross (12-11)/1.5
    quiet = [(12, 12.2, 11.8, 12)] * 23 + [(11.5, 11.9, 10.9, 11.0)]
    t = r.simulate(mk(r03_rows() + quiet), sig, 12, H)
    assert t[0]["reason"] == "cap" and t[0]["exit"] == 30 and abs(t[0]["net_r"] - (1 / 1.5 - COST * 12 / 1.5)) < 1e-9
    # a missing bar inside the trade window: the trade is dropped, not repaired
    assert r.simulate(mk(r03_rows() + [(12, 12.1, 8.9, 9)], skip={7}), sig, 12, H) == []


def test_placebo_same_trade_count():
    import numpy as np
    pools = {"A": np.array([1.0, 2.0, 3.0]), "B": np.array([-5.0, -6.0])}
    out = r.placebo_draw(pools, {"A": 3, "B": 2}, np.random.default_rng(1))
    assert len(out) == 5                                   # exactly the observed trade count
    assert sorted(out)[:2] and all(x in (1.0, 2.0, 3.0) for x in out[:3]) and all(x in (-5.0, -6.0) for x in out[3:])
    # observed mean far above every possible placebo mean -> p = 1/(B+1); far below -> p = 1
    assert r.placebo_p(pools, {"A": 3, "B": 2}, 99.0, np.random.default_rng(2), b=19) == 1 / 20
    assert r.placebo_p(pools, {"A": 3, "B": 2}, -99.0, np.random.default_rng(2), b=19) == 1.0


def test_bh_and_verdict_rules():
    # hand BH q=0.10, m=4: sorted p .01 .02 .5 .9 vs thresholds .025 .05 .075 .10 -> largest k with p<=thr is 2
    assert list(r.bh([0.5, 0.01, 0.9, 0.02])) == [False, True, False, True]
    base = dict(n=40, mean_r=0.1, lo=0.01, placebo_p=0.03)
    assert r.verdict_cell(base, True, False) == "PASS"
    assert r.verdict_cell(base, True, True) == "FAIL"                       # ONE-REGIME cannot carry a PASS
    assert r.verdict_cell(dict(base, lo=-0.01), True, False) == "FAIL"      # CI includes 0
    assert r.verdict_cell(dict(base, n=29), True, False) == "UNDERPOWERED"
    assert r.overall(["UNDERPOWERED", "FAIL"]) == "FAIL" and r.overall(["UNDERPOWERED"] * 8) == "UNDERPOWERED"
    assert r.overall(["FAIL", "PASS"]) == "PASS"


def test_summary_json_schema_and_trials_null():
    cells = [dict(rule="R03", tf="1h", lookback=12, split=s, n=5, mean_r=0.1, verdict="UNDERPOWERED" if s == "VALIDATION" else None)
             for s in ("DEV", "VALIDATION", "RECENT")]
    s = r.build_summary(cells)
    assert s["trials"] is None and s["overall"] == "UNDERPOWERED" and s["n_pass"] == 0 and len(s["cells"]) == 3
    s.update(effects="e", n_text="n", verdict_text="v")
    row = r.layer_map_row(s, "MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md")
    assert row["trials"] is None and row["layers"] == ["rsi_divergence"] and row["verdict"].startswith("UNDERPOWERED")
    for k in ("id", "title", "date", "market", "params", "split", "fees", "interaction", "effects", "n", "verdict", "report", "read"):
        assert k in row
