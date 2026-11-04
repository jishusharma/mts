"""Independent spec checks for the live Malkan/Krown confluence wiring."""

import pytest

from MyTradingSys.backtest.layers.alerts import live_confluence_feed as feed


def _bars(pivot_b, close_b, wick_low=None):
    """Two close pivots at 3 and pivot_b, with a later confirmation bar."""
    close = [100.0] * max(pivot_b + 3, feed.MIN_BARS_NEEDED)
    close[3] = 90.0
    close[pivot_b] = close_b
    bars = []
    for i, c in enumerate(close):
        lo = min(c - 1, (wick_low or {}).get(i, c - 1))
        bars.append({"t": i * 3_600_000, "o": c, "h": c + 1, "l": lo, "c": c})
    return bars


def _fixed_rsi(monkeypatch, pivot_b, rsi_a, rsi_b):
    def values(closes, period):
        result = [50.0] * len(closes)
        result[3] = rsi_a
        result[pivot_b] = rsi_b
        return result

    monkeypatch.setattr(feed, "rsi_core", values)


@pytest.mark.parametrize(
    ("pivot_b", "window", "expected_class"),
    [(14, 12, "STRONG"), (20, 18, "OK")],
)
def test_malkan_primary_12_and_secondary_18_windows(monkeypatch, pivot_b, window, expected_class):
    _fixed_rsi(monkeypatch, pivot_b, 30.0, 40.0)
    events = feed.confluence_feed_layer(_bars(pivot_b, 85.0))

    match = [e for e in events if e["code"] == "R-BULL" and e["column"] == "primary"]
    assert len(match) == 1
    assert match[0]["bars"] == window  # A and B are both counted.
    assert match[0]["window_class"] == expected_class
    assert match[0]["basis"] == "close"


def test_malkan_over_18_is_weak_and_not_emitted(monkeypatch):
    # A/B are 20 bars apart (inclusive), beyond the 18-bar maximum.
    _fixed_rsi(monkeypatch, 22, 30.0, 40.0)
    events = feed.confluence_feed_layer(_bars(22, 85.0))

    assert not [e for e in events if e["code"] == "R-BULL" and e["column"] == "primary"]
    assert feed.window_class(20) == "WEAK"


def test_malkan_uses_close_pivots_and_ignores_wick_extremes(monkeypatch):
    _fixed_rsi(monkeypatch, 14, 30.0, 40.0)
    close_pivot = feed.confluence_feed_layer(_bars(14, 85.0))
    wick_only = feed.confluence_feed_layer(
        _bars(14, 85.0, wick_low={5: 20.0, 10: 15.0})
    )

    def malkan_primary(events):
        return [(e["code"], e["t"], e["bars"]) for e in events if e.get("column") == "primary"]

    assert malkan_primary(wick_only) == malkan_primary(close_pivot)
    assert any(e["code"] == "R-BULL" and e["basis"] == "close" for e in wick_only)


def test_krown_hidden_bullish_is_separate_close_only_flag(monkeypatch):
    _fixed_rsi(monkeypatch, 7, 40.0, 30.0)
    bars = _bars(7, 95.0, wick_low={4: 10.0})
    events = feed.confluence_feed_layer(bars)

    hidden = [e for e in events if e["code"] == "K-HBULL"]
    assert len(hidden) == 1
    assert hidden[0]["source"] == "KROWN-CONFLUENCE"
    assert hidden[0]["basis"] == "close"
    assert hidden[0]["bars"] == 5
    assert hidden[0]["collection_only"] is True
    assert "side" not in hidden[0]
