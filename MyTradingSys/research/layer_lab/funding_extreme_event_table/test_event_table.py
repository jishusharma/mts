import importlib.util
from pathlib import Path

import numpy as np


MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("funding_extreme_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def test_trailing_percentile_excludes_current_and_flags_spike():
    # 90 baseline magnitudes 1..90; with linear quantile q95 = 85.55.
    rates = [(event_table.DEV_START_MS + i * 8 * 60 * 60 * 1000, i / 10000) for i in range(90)]
    rates += [(event_table.DEV_START_MS + 90 * 8 * 60 * 60 * 1000, 0.20)]
    rows = event_table.build_event_table(rates, {})
    assert rows[89]["status"] == "NOT_IN_DATA"  # only 89 prior prints
    spike = rows[90]
    assert spike["baseline_q95"] == 0.008455
    assert spike["is_extreme"] is True
    assert spike["side"] == "short"


def test_forward_24h_uses_only_24_bars_and_fade_side():
    t0 = event_table.DEV_START_MS + 1000 * 60 * 60 * 1000
    rate = [(t0, 0.01)]
    # A full baseline before the event, then price bars at hourly opens.
    rate = [(t0 - (90 - i) * 8 * 60 * 60 * 1000, 0.001) for i in range(90)] + rate
    bars_t = np.arange(t0 - 60 * 60 * 1000, t0 + 25 * 60 * 60 * 1000, 60 * 60 * 1000, dtype=np.int64)
    bars = {"t": bars_t, "o": np.full(len(bars_t), 100.0), "h": np.full(len(bars_t), 102.0),
            "l": np.full(len(bars_t), 98.0), "c": np.full(len(bars_t), 100.0),
            "atr": np.full(len(bars_t), 2.0)}
    bars["h"][25] = 150.0
    rows = event_table.build_event_table(rate, bars)
    row = rows[-1]
    assert row["status"] == "OK"
    assert row["side"] == "short"
    assert row["mfe_R"] == 1.0
    assert row["mae_R"] == 1.0
    assert row["bars_forward"] == 24


def test_entry_reference_uses_last_completed_bar_not_current_bar_close():
    t0 = event_table.DEV_START_MS + 1000 * 60 * 60 * 1000
    funding = [(t0 - (90 - i) * 8 * 60 * 60 * 1000, 0.001) for i in range(90)] + [(t0, 0.01)]
    ts = np.arange(t0 - 60 * 60 * 1000, t0 + 25 * 60 * 60 * 1000, 60 * 60 * 1000, dtype=np.int64)
    bars = {"t": ts, "h": np.full(len(ts), 102.0), "l": np.full(len(ts), 98.0),
            "c": np.full(len(ts), 100.0), "atr": np.full(len(ts), 2.0)}
    bars["c"][0] = 90.0
    bars["c"][1] = 500.0  # This bar is still open at the funding print.
    row = event_table.build_event_table(funding, bars)[-1]
    assert row["entry_price"] == 90.0


def test_initial_prints_missing_baseline_and_missing_klines_are_not_in_data():
    rates = [(event_table.DEV_START_MS + i * 8 * 60 * 60 * 1000, 0.01) for i in range(90)]
    rows = event_table.build_event_table(rates, {})
    assert len(rows) == 90
    assert all(row["status"] == "NOT_IN_DATA" for row in rows)


def test_extreme_with_missing_klines_is_not_in_data():
    t0 = event_table.DEV_START_MS + 1000 * 60 * 60 * 1000
    funding = [(t0 - (90 - i) * 8 * 60 * 60 * 1000, 0.001) for i in range(90)]
    funding.append((t0, 0.01))
    row = event_table.build_event_table(funding, {})[-1]
    assert row["is_extreme"] is True
    assert row["status"] == "NOT_IN_DATA"
