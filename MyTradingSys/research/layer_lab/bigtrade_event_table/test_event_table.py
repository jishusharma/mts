import importlib.util
from pathlib import Path


MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("bigtrade_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def test_known_fire_mfe_mae_and_first_hit_are_hand_computed():
    fire = {"key": "alpha", "tf": "1m", "side": "long", "t_fire_ms": 1640995320000,
            "price": 100, "stop": 98, "split": "TRAIN"}
    bars = {"t": [1640995200000, 1640995260000, 1640995320000, 1640995380000, 1640995440000],
            "h": [100, 101, 102, 104, 103], "l": [100, 99, 99, 99, 97],
            "c": [100, 100, 100, 102, 101]}
    row = event_table.measure_fire(fire, bars, horizon=2)
    assert row["mfe_R"] == 2.0
    assert row["mae_R"] == 1.5
    assert row["first_hit"] == "target_1R"
    assert row["bars_forward"] == 2


def test_forward_data_does_not_enter_fire_features_or_dev_window():
    fire = {"key": "alpha", "tf": "1m", "side": "long", "t_fire_ms": 1640995320000,
            "price": 100, "stop": 98, "split": "TRAIN"}
    bars = {"t": [1640995200000, 1640995260000, 1640995320000, 1640995380000, 1640995440000],
            "h": [100, 101, 102, 140, 150], "l": [100, 99, 99, 90, 80],
            "c": [100, 100, 100, 110, 90]}
    one = event_table.measure_fire(fire, bars, horizon=1)
    two = event_table.measure_fire(fire, bars, horizon=2)
    assert one["fire_price"] == two["fire_price"] == 100
    assert one["mfe_R"] == 20.0
    assert two["mfe_R"] == 25.0


def test_missing_klines_produce_not_in_data_row():
    fire = {"key": "alpha", "tf": "1m", "side": "long", "t_fire_ms": 1640995320000,
            "price": 100, "stop": 98, "split": "TRAIN"}
    rows = event_table.build_event_table([fire], {})
    assert len(rows) == 1
    assert rows[0]["status"] == "NOT_IN_DATA"
    assert rows[0]["mfe_R"] == ""


def test_first_hit_ambiguity_prefers_stop_conservatively():
    fire = {"key": "alpha", "tf": "1m", "side": "long", "t_fire_ms": 1640995200000,
            "price": 100, "stop": 98, "split": "TRAIN"}
    bars = {"t": [1640995200000, 1640995260000], "h": [100, 103], "l": [100, 97], "c": [100, 100]}
    assert event_table.measure_fire(fire, bars, horizon=1)["first_hit"] == "stop_1R"


def test_dev_end_is_2024_07_01_and_no_fire_or_bar_at_or_after_it():
    cut = 1719792000000  # 2024-07-01 00:00 UTC, computed independently
    assert event_table.DEV_END_MS == cut
    m = 60000
    bars = {"t": [cut - 2 * m, cut - m, cut, cut + m, cut + 2 * m],
            "h": [100, 101, 500, 500, 500], "l": [100, 99, 1, 1, 1], "c": [100] * 5}
    fire = {"key": "a", "tf": "1m", "side": "long", "t_fire_ms": cut - 2 * m,
            "price": 100, "stop": 98, "split": "TRAIN"}
    row = event_table.measure_fire(fire, bars, horizon=5)
    assert row["status"] == "OK" and row["bars_forward"] == 1  # only the bar before the cut
    assert row["mfe_R"] == 0.5 and row["mae_R"] == 0.5
    late = dict(fire, t_fire_ms=cut)
    assert event_table.measure_fire(late, bars, horizon=5)["status"] == "NOT_IN_DATA"
    assert event_table.build_event_table([late, dict(fire, t_fire_ms=cut + m)], {"1m": bars}) == []
