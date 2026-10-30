import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import splits


def test_guard_passes_dev():
    splits.assert_dev_only('2022-01-01', '2024-06-30 23:59')


@pytest.mark.parametrize('bad', ['2024-07-01', '2025-09-15', '2026-01-01'])
def test_guard_raises_on_validation_and_holdout(bad):
    with pytest.raises(splits.SplitViolation):
        splits.assert_dev_only('2022-01-01', bad)


def test_guard_raises_before_dev():
    with pytest.raises(splits.SplitViolation):
        splits.assert_dev_only('2021-12-31', '2022-02-01')


def test_dev_only_filter():
    idx = pd.DatetimeIndex([pd.Timestamp(x) for x in ['2021-12-31', '2022-01-01', '2024-06-30 23:59', '2024-07-01', '2025-08-01']])
    df = pd.DataFrame({'x': range(5)}, index=idx)
    assert list(splits.dev_only(df)['x']) == [1, 2]


def test_windows():
    assert splits.window_of('2024-06-30') == 'DEV'
    assert splits.window_of('2025-06-30') == 'VALIDATION'
    assert splits.window_of('2025-07-01') == 'HOLDOUT'


def test_read_holdout_logs(tmp_path):
    p = tmp_path / 'h.csv'
    splits.read_holdout('s', 'me', 'why', log_path=str(p))
    splits.read_holdout('s2', 'me', 'why', log_path=str(p))
    lines = p.read_text().splitlines()
    assert lines[0].startswith('timestamp_utc') and len(lines) == 3 and ',s2,' in lines[2]
