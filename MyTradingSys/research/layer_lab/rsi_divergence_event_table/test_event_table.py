import importlib.util
from pathlib import Path


MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("rsi_divergence_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def fixture():
    # Close pivots at 2 and 6: 102 -> 100, while RSI rises 20 -> 30.
    close = [104, 103, 102, 103, 104, 102, 100, 101, 102, 103, 104, 105, 106, 107]
    rsi =   [40,  30,  20,  30,  40,  25,  30,  40,  50,  60,  70,  80,  90,  95]
    n = len(close)
    return {"t": [i * 3_600_000 for i in range(n)], "o": [close[i] + 1 for i in range(n)],
            "h": [close[i] + 2 for i in range(n)], "l": [close[i] - 2 for i in range(n)],
            "c": close, "rsi": rsi, "atr": [2.0] * n}


def test_bullish_event_entry_and_forward_excursion_are_hand_computed():
    bars = fixture()
    row, = event_table.build_event_table(bars, timeframe="1h", horizon=3)
    assert (row["a_i"], row["b_i"]) == (2, 6)
    assert row["entry_i"] == 8 and row["entry"] == bars["o"][8]
    # Entry 103, R=2; bars 8..10 have max high 106 and min low 100.
    assert row["mfe_R"] == 1.5
    assert row["mae_R"] == 1.5
    assert row["bars_forward"] == 3


def test_bars_after_horizon_do_not_enter_excursion():
    bars = fixture()
    base, = event_table.build_event_table(bars, timeframe="1h", horizon=3)
    bars["h"][11:] = [10000] * 3
    bars["l"][11:] = [-10000] * 3
    later, = event_table.build_event_table(bars, timeframe="1h", horizon=3)
    assert (base["mfe_R"], base["mae_R"]) == (later["mfe_R"], later["mae_R"])


def test_empty_input_returns_no_rows():
    assert event_table.build_event_table({"t": [], "o": [], "h": [], "l": [], "c": [], "atr": [], "rsi": []}) == []


def test_incomplete_forward_window_is_not_in_data():
    bars = fixture()
    bars = {key: value[:10] for key, value in bars.items()}
    row, = event_table.build_event_table(bars, timeframe="1h", horizon=3)
    assert row["status"] == "NOT_IN_DATA"
    assert row["mfe_R"] == ""
