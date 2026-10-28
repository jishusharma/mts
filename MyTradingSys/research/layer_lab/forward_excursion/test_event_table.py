import importlib.util
from pathlib import Path


MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("forward_excursion_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def _bars(side):
    if side == "long":
        ranges = [(100, 100), (101, 99), (103, 100), (104, 100), (102, 99), (101, 100)]
    else:
        ranges = [(100, 100), (101, 99), (100, 97), (100, 96), (101, 98), (100, 99)]
    return [
        {"t": i, "o": 100, "h": high, "l": low, "c": 100}
        for i, (high, low) in enumerate(ranges)
    ]


def test_long_forward_excursion_is_measured_in_r():
    result = event_table.forward_excursion(_bars("long"), 0, "long", 2, 5)
    assert result == {"mfe_r": 2.0, "mae_r": 0.5, "first_hit": "target_1R", "truncated": False}


def test_short_mirrors_long_excursion():
    result = event_table.forward_excursion(_bars("short"), 0, "short", 2, 5)
    assert result == {"mfe_r": 2.0, "mae_r": 0.5, "first_hit": "target_1R", "truncated": False}


def test_same_bar_touching_both_levels_counts_stop_first():
    bars = _bars("long")
    bars[1].update(h=103, l=97)
    assert event_table.forward_excursion(bars, 0, "long", 2, 1)["first_hit"] == "stop_1R"


def test_horizon_past_available_data_uses_available_bars_and_marks_truncated():
    result = event_table.forward_excursion(_bars("long"), 0, "long", 2, 20)
    assert result["mfe_r"] == 2.0
    assert result["mae_r"] == 0.5
    assert result["truncated"] is True


def test_nonpositive_r_price_raises_value_error():
    for invalid in (0, -1):
        try:
            event_table.forward_excursion(_bars("long"), 0, "long", invalid, 2)
        except ValueError:
            continue
        raise AssertionError("r_price <= 0 must raise ValueError")
