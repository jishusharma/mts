from datetime import datetime, timezone

import importlib.util

import pytest

# chart_lab draws with Pillow; gate machines without it skip the tests (a module-level skip collects nothing: pytest exit 5)
HAS_PIL = importlib.util.find_spec("PIL") is not None
pytestmark = pytest.mark.skipif(not HAS_PIL, reason="Pillow not installed")
if HAS_PIL:
    from chart_lab import detect_candidates, plot_chart


def _bar(ts, high, low=None, close=None, volume=1.0, delta=0.0, fp=""):
    low = high if low is None else low
    close = high if close is None else close
    return {"t": int(ts.timestamp() * 1000), "o": close, "h": high, "l": low, "c": close,
            "buy_vol": volume, "sell_vol": 0.0, "delta": delta, "fp": fp}


def test_oversized_leg_decides_on_third_stall_and_plot_has_no_future():
    day = datetime(2025, 1, 22, tzinfo=timezone.utc)
    rows = []
    # Twenty prior completed same-anchor legs have size 5; candidate clears VAH=100.
    for offset in range(1, 21):
        prior_day = day - __import__("datetime").timedelta(days=offset)
        for minute, high in enumerate([100, 102, 105, 105, 105, 105]):
            rows.append(_bar(prior_day.replace(hour=0, minute=minute), high, 90, 95,
                             fp="90:3:0|100:2:0"))
    for minute, high in enumerate([100, 101, 105, 110, 115, 120, 120, 120, 120]):
        rows.append(_bar(day.replace(hour=0, minute=minute), high, high - 2, high - 1,
                         fp="90:3:0|100:2:0"))
    candidates = detect_candidates(rows, anchors=("00:00",), prior_legs=20, va_days=1)
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["decision_t"] == rows[-1]["t"]
    chart = plot_chart(rows, candidate, output_path=None)
    assert max(b["end_t"] for b in chart["bars"]) == candidate["decision_t"]
    assert all(b["end_t"] <= candidate["decision_t"] for b in chart["bars"])
