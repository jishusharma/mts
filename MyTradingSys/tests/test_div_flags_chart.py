"""Spec tests for rsi/div_flags_chart.py (card gpt-spec-tests-div-flags-chart-1104, D11 feeder check).

Window classes (STRONG <=12, OK 13..18, WEAK >18, bars counted A..B inclusive) are OURS, not SOURCED
(HINDI_CONCEPTS.md: 18 NOT_IN_DATA). Expected spans come from how the series is BUILT (index of A and B),
never from the code under test. Pivots are strict local extremes of the CLOSE; wicks are never read.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from MyTradingSys.backtest.layers.rsi.div_flags_chart import detect_all

DAY = 86400000


def _bars(closes, wick=0.0):
    out = []
    for i, c in enumerate(closes):
        out.append({"t": i * DAY, "o": c, "h": c + 0.1 + wick, "l": c - 0.1 - wick, "c": c})
    return out


def _bullish_closes(span):
    """Steep fall to A (index a), bounce, slow lower low at B = a+span-1. Pivots (lows) are exactly A and B."""
    c = [200.0 - 4.0 * i for i in range(20)]            # steep fall, last index 19 is the low A
    a = 19
    up = (span - 1) // 2                                # bars rising after A
    for k in range(1, up + 1):
        c.append(c[a] + 1.0 * k)
    peak = c[-1]
    down = span - 1 - up                                # bars falling to B
    b_close = c[a] - 0.5
    step = (peak - b_close) / down
    for k in range(1, down + 1):
        c.append(peak - step * k)
    assert abs(c[-1] - b_close) < 1e-9
    c.append(c[-1] + 1.0)                               # bar after B so B is a confirmed pivot
    c.append(c[-1] + 1.0)
    return c, a, a + span - 1


def _bull_events(closes):
    evs, _ = detect_all(_bars(closes))
    return [e for e in evs if e["kind"] == "bullish"]


def _check(span, cls):
    closes, a, b = _bullish_closes(span)
    ev = _bull_events(closes)
    assert len(ev) == 1, ev
    e = ev[0]
    assert (e["a_i"], e["b_i"]) == (a, b)
    assert e["bars"] == span
    assert e["window_class"] == cls
    assert e["close_a"] == closes[a] and e["close_b"] == closes[b]


def test_span_12_strong_boundary():
    _check(12, "STRONG")


def test_span_13_ok_lower_edge():
    _check(13, "OK")


def test_span_18_ok_upper_edge():
    _check(18, "OK")


def test_span_19_weak_not_emitted():
    closes, a, b = _bullish_closes(19)
    assert _bull_events(closes) == []


def test_span_short_inside_strong():
    _check(5, "STRONG")


def test_wicks_ignored_when_closes_do_not_diverge():
    # Closes: higher low at B (no divergence). Wicks make B's LOW far lower than A's low: a wick-based reader
    # would see a lower low. Close-only reading must give no bullish event.
    closes, a, b = _bullish_closes(8)
    closes[b] = closes[a] + 0.5                       # B close now a higher low than A
    bars = _bars(closes)
    bars[b]["l"] = closes[a] - 50.0                   # huge wick below
    evs, _ = detect_all(bars)
    assert [e for e in evs if e["kind"] == "bullish"] == []


def test_wicks_do_not_move_pivots_when_closes_diverge():
    closes, a, b = _bullish_closes(8)
    bars = _bars(closes, wick=30.0)
    bars[b]["l"] = closes[b] + 5.0                    # wick low of B ABOVE A's wick low: wick reader sees no divergence
    evs, _ = detect_all(bars)
    ev = [e for e in evs if e["kind"] == "bullish"]
    assert len(ev) == 1 and (ev[0]["a_i"], ev[0]["b_i"]) == (a, b)
