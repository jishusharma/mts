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


H = 3_600_000
CUT = 1719792000000  # 2024-07-01 UTC


def _npz(tmp_path, times, volumes=None, name="k.npz"):
    import numpy as np
    n = len(times)
    path = tmp_path / name
    np.savez(path, t=np.array(times, dtype=np.int64), o=np.full(n, 100.0), h=np.full(n, 102.0),
             l=np.full(n, 98.0), c=np.full(n, 101.0),
             v=np.array(volumes if volumes is not None else [10.0] * n))
    return path


def test_loader_drops_bars_with_open_at_or_after_cutoff(tmp_path):
    times = [CUT - 2 * H, CUT - H, CUT, CUT + H]
    bars = event_table.load_dev_npz(_npz(tmp_path, times), "1h")
    assert [b["timestamp"] for b in bars] == [CUT - 2 * H, CUT - H]


def test_loader_four_hour_skips_bucket_with_missing_1h_bar(tmp_path):
    base = CUT - 24 * H  # 00:00 UTC aligned
    times = [base + i * H for i in range(8)]
    del times[5]  # second bucket (04..07) loses 09:00? bucket 2 is hours 4..7; index 5 = 05:00
    bars = event_table.load_dev_npz(_npz(tmp_path, times, [1, 2, 3, 4, 5, 7, 8][:7]), "4h")
    assert [b["timestamp"] for b in bars] == [base]
    assert bars[0]["volume"] == 10.0
    assert bars[0]["high"] == 102.0 and bars[0]["open"] == 100.0 and bars[0]["close"] == 101.0


def test_loader_four_hour_ignores_unaligned_partial_start(tmp_path):
    base = CUT - 24 * H
    times = [base + i * H for i in range(1, 9)]  # starts 01:00; first full bucket is 04..07
    bars = event_table.load_dev_npz(_npz(tmp_path, times), "4h")
    assert [b["timestamp"] for b in bars] == [base + 4 * H]


def test_loader_to_table_known_spike_hand_forward_excursions(tmp_path):
    import numpy as np
    start = 1640995200000
    n = 338
    times = [start + i * H for i in range(n)]
    vol = [10.0] * n
    vol[168], vol[336] = 20.0, 30.0
    path = _npz(tmp_path, times, vol)
    d = dict(np.load(path))
    d["h"][337], d["l"][337], d["c"][337] = 106.0, 97.0, 104.0
    np.savez(path, **d)
    rows = event_table.build_event_table(event_table.load_dev_npz(path, "1h"), "1h", n_weeks=2, horizon=1)
    row = rows[336]
    assert row["is_spike"] is True and row["relative_volume"] == 2.0
    assert (row["mfe_R"], row["mae_R"], row["forward_return_R"]) == (1.5, 0.75, 1.0)


def test_baseline_excludes_current_bar_hand_ratio():
    volumes = [10.0] * 338
    volumes[168] = 20.0
    volumes[336] = 1000.0
    row = event_table.build_event_table(_bars(volumes), "1h", n_weeks=2, horizon=1)[336]
    assert row["baseline_volume"] == 15.0
    assert row["relative_volume"] == 1000.0 / 15.0


def test_summarize_counts_and_means():
    rows = [{"is_spike": True, "status": "OK", "mfe_R": 2.0, "mae_R": 1.0},
            {"is_spike": True, "status": "OK", "mfe_R": 4.0, "mae_R": 3.0},
            {"is_spike": True, "status": "NOT_IN_DATA", "mfe_R": "", "mae_R": ""},
            {"is_spike": False, "status": "OK", "mfe_R": "", "mae_R": ""},
            {"is_spike": False, "status": "NOT_IN_DATA", "mfe_R": "", "mae_R": ""}]
    s = event_table.summarize(rows)
    assert s == {"rows": 5, "rows_ok": 3, "rows_not_in_data": 2, "spikes": 3, "spikes_ok": 2,
                 "spikes_not_in_data": 1, "mean_mfe_R": 3.0, "mean_mae_R": 2.0}
