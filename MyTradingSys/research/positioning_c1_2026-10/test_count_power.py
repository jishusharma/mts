"""
Unit tests for count_power.py (card positioning-c1-longwindow-count-power).
Tests that the count script reproduces len(funding_cvd_fade_events(...)) on a fixed fixture
and refuses any bar dated 2024-07-01 or later.
Fails before count_power.py exists.
"""

import math
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure repo root and research dir are importable
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import count_power as cp
from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import (
    funding_cvd_fade_events,
)

CUTOFF_MS = cp.CUTOFF_MS  # 1719792000000 ms = 2024-07-01 00:00:00 UTC


def _synthetic_fixture():
    """Build a deterministic fixture of 15m bars and 8h funding records before 2024-07-01."""
    # Start at 2023-01-01 00:00:00 UTC (1672531200000 ms)
    start_ms = 1672531200000
    funding = []
    # 120 8-hour funding records
    for k in range(120):
        t_f = start_ms + k * 8 * 3600 * 1000
        rate = 0.0001 * math.sin(k * 0.2)
        funding.append((t_f, rate))

    bars = []
    # 500 15m bars starting at 100th funding record time
    t0 = funding[95][0]
    p = 20000.0
    for i in range(500):
        t_b = t0 + i * 15 * 60 * 1000
        # synthetic price and volume
        p_c = p + 50.0 * math.sin(i * 0.1)
        v = 100.0 + 10.0 * math.cos(i * 0.15)
        # tbv determines cvd
        tbv = 0.5 * v + 5.0 * math.sin(i * 0.2)
        bars.append({
            "t": t_b,
            "o": p_c - 5.0,
            "h": p_c + 10.0,
            "l": p_c - 10.0,
            "c": p_c,
            "v": v,
            "tbv": tbv,
        })
    return bars, funding


def test_reproduces_len_funding_cvd_fade_events_on_fixed_fixture():
    bars, funding = _synthetic_fixture()
    params = {
        "lookback": 60,
        "n": 20,
        "hi": 0.90,
        "lo": 0.10,
        "use_divergence": True,
    }
    expected_events = funding_cvd_fade_events(bars, funding, **params)
    expected_len = len(expected_events)

    # count_power must reproduce this exact length
    counted = cp.count_events_for_cell(bars, funding, params)
    assert counted == expected_len

    # Also test with use_divergence=False
    params_nodiv = dict(params, use_divergence=False)
    expected_events_nodiv = funding_cvd_fade_events(bars, funding, **params_nodiv)
    counted_nodiv = cp.count_events_for_cell(bars, funding, params_nodiv)
    assert counted_nodiv == len(expected_events_nodiv)


def test_refuses_any_bar_dated_2024_07_01_or_later():
    # A bar at exactly CUTOFF_MS (2024-07-01 00:00:00 UTC) must be refused
    bad_bar = {"t": CUTOFF_MS, "o": 1.0, "h": 2.0, "l": 0.5, "c": 1.5, "v": 10.0, "tbv": 5.0}
    with pytest.raises(ValueError, match="2024-07-01"):
        cp.validate_dev_bars([bad_bar])

    # A bar strictly after CUTOFF_MS must also be refused
    future_bar = {"t": CUTOFF_MS + 60000, "o": 1.0, "h": 2.0, "l": 0.5, "c": 1.5, "v": 10.0, "tbv": 5.0}
    with pytest.raises(ValueError, match="2024-07-01"):
        cp.validate_dev_bars([future_bar])


def test_loader_refuses_kline_csv_with_bars_at_or_after_2024_07_01():
    with tempfile.TemporaryDirectory() as tmp:
        csv_file = Path(tmp) / "BTCUSDT-1m-2024-06.csv"
        # Row 1 is DEV, Row 2 is 2024-07-01 00:00:00 UTC
        csv_file.write_text(
            f"open_time,open,high,low,close,volume,close_time,quote_volume,count,tbv,tbqv,ignore\n"
            f"{CUTOFF_MS - 60000},100,101,99,100,10,123,123,1,5,5,0\n"
            f"{CUTOFF_MS},100,101,99,100,10,123,123,1,5,5,0\n",
            newline="\n",
            encoding="utf-8"
        )
        with pytest.raises(ValueError, match="2024-07-01"):
            cp.load_dev_1m_klines(tmp)


def test_inconclusive_flag_when_n_less_than_100():
    # If N < 100, power verdict must be marked INCONCLUSIVE in advance
    assert cp.evaluate_power_verdict(99) == "INCONCLUSIVE (N < 100)"
    assert cp.evaluate_power_verdict(0) == "INCONCLUSIVE (N < 100)"
    assert "INCONCLUSIVE" not in cp.evaluate_power_verdict(100)
