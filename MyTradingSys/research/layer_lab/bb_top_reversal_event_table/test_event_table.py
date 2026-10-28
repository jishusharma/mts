import importlib.util
import math
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("bb_top_reversal_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def _setup_bars():
    # Twenty closes are flat at 100, so the green-bar upper band is exactly 100.
    bars = [{"t": 1640995200000 + i * 900_000, "o": 100.0, "h": 100.5, "l": 99.5, "c": 100.0}
            for i in range(20)]
    bars.append({"t": 1640995200000 + 20 * 900_000, "o": 100.0, "h": 102.0, "l": 99.8, "c": 101.0})
    bars.append({"t": 1640995200000 + 21 * 900_000, "o": 101.0, "h": 101.5, "l": 98.5, "c": 99.0})
    # Entry is this bar's open. Its extremes are included in the 16-bar forward window.
    bars.append({"t": 1640995200000 + 22 * 900_000, "o": 100.0, "h": 103.0, "l": 97.0, "c": 99.0})
    for i in range(23, 38):
        bars.append({"t": 1640995200000 + i * 900_000, "o": 99.0, "h": 101.0, "l": 98.0, "c": 99.0})
    return bars


def test_hand_built_setup_uses_hand_computed_upper_band_and_forward_r():
    bars = _setup_bars()
    row = event_table.build_event_table(bars)[0]
    # Green window closes: nineteen 100s followed by 101. mean=100.05;
    # population variance=.0475; upper=100.05 + 2*sqrt(.0475).
    upper = 100.05 + 2 * math.sqrt(0.0475)
    assert row["green_upper"] == upper
    assert row["event_index"] == 21
    assert row["entry"] == 100.0
    assert row["risk_r"] == 1.5  # red high 101.5 minus entry 100
    assert row["mfe_R"] == 2.0  # (entry 100 - minimum 97) / 1.5
    assert row["mae_R"] == 2.0  # (maximum 103 - entry 100) / 1.5
    assert row["bars_forward"] == 16
    assert row["status"] == "OK"


def test_red_candle_closing_above_green_open_is_not_a_setup():
    bars = _setup_bars()
    bars[21]["c"] = 100.5
    assert event_table.build_event_table(bars) == []


def test_green_candle_below_upper_band_is_not_a_setup():
    bars = _setup_bars()
    bars[20]["h"] = 99.9
    assert event_table.build_event_table(bars) == []


def test_bars_after_red_do_not_change_setup_flags():
    bars = _setup_bars()
    rows = event_table.build_event_table(bars)
    altered = [dict(bar) for bar in bars]
    altered[22]["o"] = -500.0
    altered[22]["c"] = 500.0
    assert event_table.build_event_table(altered)[0]["event_index"] == rows[0]["event_index"]
