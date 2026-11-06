import datetime as dt
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import count_10sym as c

DATE = dt.date(2023, 3, 1)       # US standard time: open 14:30 UTC
MIN = 60000


def lows_with_min_at(off_min, gap=None):
    o = int(c.ny_open_utc(DATE).timestamp() * 1000)
    start = int(dt.datetime(2023, 3, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    d = {t: 100.0 for t in range(start, o + 180 * MIN, MIN)}
    d[o + off_min * MIN] = 90.0
    if gap is not None:
        del d[o + gap * MIN]
    return d


def test_low_in_window_is_event():
    assert c.day_event(DATE, lows_with_min_at(130)) is True


def test_low_too_early_or_late_is_not():
    assert c.day_event(DATE, lows_with_min_at(60)) is False
    assert c.day_event(DATE, lows_with_min_at(110)) is False  # low set at open+110 counts 0
    assert c.day_event(DATE, lows_with_min_at(170)) is False   # set after open+150: not held 30 min inside the window


def test_gap_drops_day_and_weekend_is_none():
    assert c.day_event(DATE, lows_with_min_at(130, gap=10)) is None
    assert c.day_event(dt.date(2023, 3, 4), {}) is None


def test_btc_dev_count_equals_35():
    if not (c.DATA_DIR / "klines").exists():
        pytest.skip("1m kline cache absent (CI)")
    res = c.count("BTCUSDT", dt.date(2022, 1, 1), dt.date(2024, 7, 1))
    assert res is not None
    assert res["events"] == 35

