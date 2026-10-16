import importlib.util
from pathlib import Path


MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("oi_delta_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def test_four_state_and_forward_excursions_are_hand_computed():
    rows = event_table.build_event_table(
        [
            {"timestamp": 1, "price_change_pct": 1.0, "oi_change_pct": 2.0, "entry": 100, "stop": 98},
            {"timestamp": 2, "price_change_pct": 1.0, "oi_change_pct": -2.0, "entry": 100, "stop": 102},
            {"timestamp": 3, "price_change_pct": -1.0, "oi_change_pct": 2.0, "entry": 100, "stop": 102},
            {"timestamp": 4, "price_change_pct": -1.0, "oi_change_pct": -2.0, "entry": 100, "stop": 98},
        ],
        [
            {"timestamp": 1, "high": 100, "low": 100, "close": 100},
            {"timestamp": 2, "high": 104, "low": 99, "close": 102},
            {"timestamp": 3, "high": 102, "low": 99, "close": 101},
            {"timestamp": 4, "high": 103, "low": 97, "close": 99},
            {"timestamp": 5, "high": 101, "low": 98, "close": 100},
        ],
        horizon=2,
        dev_start_ms=0,
        dev_end_ms=100,
    )
    assert [row["state"] for row in rows] == [
        "aggressive_long", "divergence_bearish", "divergence_bullish", "aggressive_short"
    ]
    assert rows[0]["forward_return_R"] == 0.5
    assert rows[0]["mfe_R"] == 2.0
    assert rows[0]["mae_R"] == 0.5


def test_missing_oi_is_not_in_data_not_zero_and_no_future_label():
    rows = event_table.build_event_table(
        [{"timestamp": 1, "price_change_pct": 1.0, "oi_change_pct": None, "entry": 100, "stop": 98}],
        [{"timestamp": 1, "high": 100, "low": 100, "close": 100},
         {"timestamp": 2, "high": 102, "low": 99, "close": 101}],
        horizon=1,
        dev_start_ms=0,
        dev_end_ms=100,
    )
    assert rows[0]["status"] == "NOT_IN_DATA"
    assert rows[0]["state"] == "NOT_IN_DATA"
    assert rows[0]["forward_return_R"] == ""


def test_event_label_uses_only_asof_oi_and_price_inputs():
    row = event_table.build_event_table(
        [{"timestamp": 1, "price_change_pct": -1, "oi_change_pct": 1, "entry": 100, "stop": 98}],
        [{"timestamp": 1, "high": 100, "low": 100, "close": 100},
         {"timestamp": 2, "high": 103, "low": 99, "close": 101}],
        horizon=1,
        dev_start_ms=0,
        dev_end_ms=100,
    )[0]
    assert row["state"] == "divergence_bullish"
