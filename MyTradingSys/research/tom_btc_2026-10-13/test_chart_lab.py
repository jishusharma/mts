from datetime import datetime, timezone

import importlib.util

import pytest

# chart_lab draws with Pillow; gate machines without it skip the tests (a module-level skip collects nothing: pytest exit 5)
HAS_PIL = importlib.util.find_spec("PIL") is not None
pytestmark = pytest.mark.skipif(not HAS_PIL, reason="Pillow not installed")
if HAS_PIL:
    from chart_lab import detect_bo, detect_candidates, detect_tc, plot_chart


def _bar(ts, high, low=None, close=None, volume=1.0, delta=0.0, fp=""):
    low = high if low is None else low
    close = high if close is None else close
    return {"t": int(ts.timestamp() * 1000), "o": close, "h": high, "l": low, "c": close,
            "buy_vol": volume, "sell_vol": 0.0, "delta": delta, "fp": fp or "100:1:0"}


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


def test_tc_and_bo_candidates():
    day = datetime(2025, 1, 22, tzinfo=timezone.utc)
    tc_rows = []
    # 30 rising minutes establish a VWAP trend. The pullback touches VWAP,
    # then the last high volume close reclaims the prior bar high.
    for minute in range(30):
        px = 100 + minute * 0.1
        tc_rows.append(_bar(day.replace(minute=minute), px + .1, px - .1, px, volume=1))
    for minute, px, lo, vol in ((30, 101.6, 101.3, 1), (31, 101.5, 101.2, 1),
                                (32, 101.8, 101.4, 1), (33, 102.2, 101.7, 3)):
        tc_rows.append(_bar(day.replace(minute=minute), px + .05, lo, px, volume=vol))
    tc = detect_tc(tc_rows, anchors=("00:00",))
    assert len(tc) == 1
    tc_chart = plot_chart(tc_rows, tc[0])
    assert max(b["end_t"] for b in tc_chart["bars"]) == tc[0]["decision_t"]

    bo_rows = []
    for minute in range(60):
        bo_rows.append(_bar(day.replace(minute=minute), 100.5, 99.5, 100, volume=1))
    bo_rows.append(_bar(day + __import__("datetime").timedelta(hours=1), 102, 100.2, 101.5, volume=3))
    bo = detect_bo(bo_rows, anchors=("00:00",))
    assert len(bo) == 1
    bo_chart = plot_chart(bo_rows, bo[0])
    assert max(b["end_t"] for b in bo_chart["bars"]) == bo[0]["decision_t"]


@pytest.mark.skipif(not __import__("pathlib").Path(r"F:\MTS\data\orderflow_1m").exists(), reason="DEV input absent")
def test_fade_unchanged():
    from chart_lab import load_dev
    rows = load_dev(r"F:\MTS\data\orderflow_1m")
    assert len(detect_candidates(rows)) == 105
