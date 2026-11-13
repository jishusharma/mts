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
