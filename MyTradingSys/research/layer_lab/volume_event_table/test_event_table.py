import importlib.util
from pathlib import Path


MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("volume_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def _bars(volumes):
    start = 1640995200000
    return [{"timestamp": start + i * 3_600_000, "open": 100, "high": 102, "low": 98,
             "close": 101, "volume": v} for i, v in enumerate(volumes)]


def test_same_hour_of_week_median_excludes_current_bar_and_flags_spike():
    volumes = [10.0] * 338
    volumes[168] = 20.0
    volumes[336] = 30.0
    rows = event_table.build_event_table(_bars(volumes), "1h", n_weeks=2, horizon=1)
    row = rows[336]
    assert row["baseline_volume"] == 15.0
    assert row["relative_volume"] == 2.0
    assert row["is_spike"] is True
    assert row["status"] == "OK"


def test_known_spike_forward_excursions_are_in_range_r():
    bars = _bars([10.0] * 337)
    bars[336]["volume"] = 20.0
    bars.append({"timestamp": bars[336]["timestamp"] + 3_600_000, "open": 100,
                 "high": 106, "low": 97, "close": 104, "volume": 10})
    row = event_table.build_event_table(bars, "1h", n_weeks=2, horizon=1)[336]
    assert row["forward_return_R"] == 1.0
    assert row["mfe_R"] == 1.5
    assert row["mae_R"] == 0.75


def test_fewer_than_n_prior_weeks_is_not_in_data():
    rows = event_table.build_event_table(_bars([20.0] * 168), "1h", n_weeks=2, horizon=1)
    assert rows[-1]["status"] == "NOT_IN_DATA"
    assert rows[-1]["baseline_volume"] == ""
    assert rows[-1]["is_spike"] is False


def test_bearish_spike_excursions_are_directionally_correct():
    bars = _bars([10.0] * 337)
    bars[336]['open'] = 100
    bars[336]['close'] = 99
    bars[336]['volume'] = 20.0
    bars.append({'timestamp': bars[336]['timestamp'] + 3_600_000, 'open': 100,
                 'high': 103, 'low': 94, 'close': 96, 'volume': 10})
    row = event_table.build_event_table(bars, '1h', n_weeks=2, horizon=1)[336]
    assert row['direction'] == 'down'
    assert row['forward_return_R'] == 1.0
    assert row['mfe_R'] == 1.5
    assert row['mae_R'] == 0.75


def test_four_hour_same_week_slot_baseline():
    start = 1640995200000
    bars = [{'timestamp': start + i * 14_400_000, 'open': 100, 'high': 102, 'low': 98,
             'close': 101, 'volume': 10.0} for i in range(86)]
    bars[42]['volume'] = 20.0
    bars[84]['volume'] = 40.0
    rows = event_table.build_event_table(bars, '4h', n_weeks=2, horizon=1)
    row = rows[84]
    assert row['baseline_volume'] == 15.0
    assert row['relative_volume'] == 40.0 / 15.0
    assert row['is_spike'] is True
