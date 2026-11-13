import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from census_lib import percentiles, episode_starts, band, bucket_of


def test_percentiles_known():
    p = percentiles(list(range(101)), [1, 50, 99])
    assert p[1] == 1.0 and p[50] == 50.0 and p[99] == 99.0


def test_percentiles_skip_none_nan():
    p = percentiles([None, float("nan"), 10.0, 20.0], [50])
    assert p[50] == 15.0


def test_episodes_count_runs_not_bars():
    v = [50, 29, 28, 31, 29, None, 29, 29, 40]
    assert episode_starts(v, 30) == [1, 4, 6]


def test_episodes_strict_vs_equal():
    v = [31, 30, 30, 31]
    assert episode_starts(v, 30) == []
    assert episode_starts(v, 30, include_equal=True) == [1]


def test_band_words():
    assert band(10, 20, 30) == "rarely hit"
    assert band(25, 20, 30) == "sometimes hit"
    assert band(30, 20, 30) == "sometimes hit"
    assert band(31, 20, 30) == "common"


def test_bucket_edges():
    e = [25, 30, 35]
    assert bucket_of(24.9, e) == 0 and bucket_of(25, e) == 1 and bucket_of(36, e) == 3
