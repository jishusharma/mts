"""Spec: card bb-top-reversal-candle-backtest (E2): prior 15m candle green with its high at/near the upper BB(20,2),
next candle red, closes below the prior green open and back inside the band -> "short" only (card defines no long).
Expected numbers are hand-computed here (population stdev), not read from the code."""
import math

from MyTradingSys.backtest.layers.alerts import live_bb_top_reversal as m

Q = 900000
T0 = 1_700_000_100_000 // Q * Q


def _flat(n, px=100.0):
    return [{"t": T0 + k * Q, "o": px, "h": px, "l": px, "c": px, "v": 1.0, "tbv": 0.5} for k in range(n)]


def _bar(k, o, h, l, c):
    return {"t": T0 + k * Q, "o": o, "h": h, "l": l, "c": c, "v": 1.0, "tbv": 0.5}


def _scenario(prior_h=101.0, prior_c=101.0, prior_o=100.0, last_c=99.5, last_o=101.0):
    bars = _flat(19)
    bars.append(_bar(19, prior_o, prior_h, min(prior_o, prior_c), prior_c))
    bars.append(_bar(20, last_o, last_o, min(last_o, last_c), last_c))
    return bars


def test_bollinger_values_hand_computed():
    # closes 1..20: mean 10.5, population var (20^2-1)/12 = 33.25, sd 5.766281297..., bands 10.5 +/- 2 sd
    up, lo = m.bollinger([float(x) for x in range(1, 21)])
    sd = math.sqrt(33.25)
    assert abs(up[19] - (10.5 + 2 * sd)) < 1e-9 and abs(lo[19] - (10.5 - 2 * sd)) < 1e-9
    assert up[18] is None
    # 19 closes of 100 then 101: mean 100.05, var (19*0.05^2 + 0.95^2)/20 = 0.0475
    up, _ = m.bollinger([100.0] * 19 + [101.0])
    assert abs(up[19] - (100.05 + 2 * math.sqrt(0.0475))) < 1e-9   # 100.485890...


def test_fires_short_on_e2_reversal():
    ev = m.bb_top_reversal_layer(_scenario())
    assert len(ev) == 1 and ev[0]["side"] == "short" and ev[0]["sampling"] is True
    assert ev[0]["t"] == T0 + 20 * Q and ev[0]["event"] == "bb_top_reversal_short"
    assert abs(ev[0]["upper"] - 100.49) < 1e-9   # round(100.48589, 2)


def test_no_event_when_close_not_below_prior_open():
    assert m.bb_top_reversal_layer(_scenario(last_c=100.5)) == []   # red but above prior green open 100


def test_no_event_when_prior_not_green_or_no_touch():
    assert m.bb_top_reversal_layer(_scenario(prior_c=99.9, prior_o=100.0, prior_h=101.0)) == []  # prior red
    # touch threshold = upper - 0.05*bandwidth; high 100.2 is below it -> no touch
    assert m.bb_top_reversal_layer(_scenario(prior_h=100.2)) == []


def test_cushion_boundary():
    # bw = 2*2*sd = 0.87178; threshold = 100.48589 - 0.05*0.87178 = 100.44230
    assert len(m.bb_top_reversal_layer(_scenario(prior_h=100.45))) == 1
    assert m.bb_top_reversal_layer(_scenario(prior_h=100.43)) == []


def test_no_long_mirror():
    # a bottom reversal (green after red at the lower band) produces nothing: card defines the top only
    bars = _flat(19)
    bars.append(_bar(19, 100.0, 100.0, 99.0, 99.0))
    bars.append(_bar(20, 99.0, 100.6, 99.0, 100.5))
    assert m.bb_top_reversal_layer(bars) == []


def test_empty_short_nan_input():
    assert m.bb_top_reversal_layer([]) == []
    assert m.bb_top_reversal_layer(_flat(20)) == []
    bars = _scenario()
    bars[10]["c"] = float("nan")          # NaN inside the band window: bands undefined -> no event, no crash
    assert m.bb_top_reversal_layer(bars) == []
    bars = _scenario()
    bars[20]["c"] = float("nan")
    assert m.bb_top_reversal_layer(bars) == []


def test_truncation_no_lookahead():
    bars = _scenario() + _flat(5, 99.5)
    for k, b in enumerate(bars[21:], 21):
        b["t"] = T0 + k * Q
    full = m.bb_top_reversal_layer(bars)
    assert m.bb_top_reversal_layer(bars[:21]) == full[:1]
    assert m.bb_top_reversal_layer(bars[:20]) == []      # the signal bar not yet closed
    assert m.bb_top_reversal_layer(bars[:21] + [_bar(21, 1, 1e9, 1, 1e9)])[:1] == full[:1]


def test_restart_determinism():
    bars = _scenario()
    assert m.bb_top_reversal_layer(bars) == m.bb_top_reversal_layer([dict(b) for b in bars])
    # a restart that only has the last 21 bars sees the same event
    long = _flat(10) + [dict(b, t=b["t"] + 10 * Q) for b in bars]
    assert [e["t"] for e in m.bb_top_reversal_layer(long)] == [T0 + 30 * Q]
