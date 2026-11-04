"""Independent specs for the research context tags and causal retest fills."""

import pytest

from MyTradingSys.backtest import research_kit as rk


@pytest.mark.parametrize(
    ("weekly", "monthly", "expected"),
    [
        (60, 60, "bull"),       # sourced thresholds are inclusive
        (40, 40, "bear"),
        (60, 59.99, "mid"),     # both timeframes must agree
        (40, 40.01, "mid"),
        (75, 25, "mid"),
        (None, 80, None),
        (80, None, None),
    ],
)
def test_rsi_band_requires_both_closed_timeframes_at_inclusive_thresholds(weekly, monthly, expected):
    assert rk.rsi_band(weekly, monthly) == expected


@pytest.mark.parametrize(
    ("band", "side", "expected"),
    [("bull", "above", "bull"), ("bear", "below", "bear"),
     ("bull", "below", "range"), ("bear", "above", "range"),
     ("mid", "above", "range")],
)
def test_regime_requires_rsi_agreement_and_matching_ma_side(monkeypatch, band, side, expected):
    monkeypatch.setattr(rk, "_last_closed", lambda series, t: 70 if band == "bull" else 30 if band == "bear" else 50)
    monkeypatch.setattr(rk, "ma_side", lambda closes, n, ma: side)
    daily = ([10, 20], [100, 101])
    result = rk.regime_tag(20, daily, ([10], [0]), ([10], [0]), ma_n=2)
    assert result == {"side": side, "band": band, "regime": expected}


def test_regime_uses_only_daily_closes_at_or_before_query_time(monkeypatch):
    seen = []
    monkeypatch.setattr(rk, "ma_side", lambda closes, n, ma: seen.append(list(closes)) or "above")
    monkeypatch.setattr(rk, "_last_closed", lambda series, t: 65)
    rk.regime_tag(20, ([10, 20, 30], [100, 101, 999]), ([1], [0]), ([1], [0]), ma_n=2)
    assert seen == [[100, 101]]


def test_regime_does_not_use_rsi_values_timestamped_after_query_time():
    daily = ([10, 20, 30], [98, 99, 101])
    weekly = ([30, 31], [70, 20])
    monthly = ([30, 31], [75, 20])
    before_close = rk.regime_tag(30, daily, weekly, monthly, ma_n=2)
    at_close = rk.regime_tag(31, daily, weekly, monthly, ma_n=2)
    assert before_close["band"] == "bull"
    assert before_close["regime"] == "bull"
    assert at_close["band"] == "bear"
    assert at_close["regime"] == "range"  # MA side stayed above; bear needs a below side


def test_regime_is_unavailable_until_ma_history_and_rsi_state_exist():
    result = rk.regime_tag(100, ([10], [101]), ([200], [70]), ([200], [70]), ma_n=2)
    assert result == {"side": None, "band": None, "regime": None}


@pytest.mark.parametrize(
    ("hour", "expected"),
    [(0, "asia"), (7, "asia"), (8, "london"), (12, "london"),
     (13, "ny"), (20, "ny"), (21, "late"), (23, "late")],
)
def test_session_tags_switch_at_utc_hour_boundaries(hour, expected):
    assert rk.session_tag(hour * 3600) == expected


def test_session_tag_uses_utc_day_rollover_and_integer_minute_resolution():
    assert rk.session_tag(23 * 3600 + 59 * 60 + 59) == "late"
    assert rk.session_tag(24 * 3600) == "asia"


def test_phase_mapping_and_unknown_class_boundary():
    assert [rk.phase_tag(x) for x in ("W1", "H", "R")] == ["range", "break", "retest"]
    with pytest.raises(ValueError, match="unknown tf_break class"):
        rk.phase_tag("unknown")


def test_regime_mix_counts_missing_weeks_in_denominator_and_rejects_unknown_tags():
    assert rk.regime_mix_line(["bull", "bear", "range", None]) == (
        "4 weeks: bull 1 (25%) | bear 1 (25%) | range 1 (25%) | n/a 1 (25%)"
    )
    assert rk.regime_mix_line([]) == "0 weeks: no data"
    with pytest.raises(ValueError, match="unknown regime"):
        rk.regime_mix_line(["sideways"])


def test_long_retest_ignores_signal_bar_and_fills_first_later_touch():
    bars = [(90, 120, 80, 110), (110, 115, 105, 112), (112, 114, 100, 103), (103, 110, 95, 98)]
    assert rk.retest_entry(bars, 0, 100, +1, 3) == (2, 100.0)


def test_retest_entry_does_not_fill_from_signal_bar_range_or_beyond_window():
    signal_bar_touches_level = [(100, 110, 90, 105), (105, 115, 104, 112), (112, 120, 101, 118)]
    assert rk.retest_entry(signal_bar_touches_level, 0, 100, +1, 1) is None
    assert rk.retest_entry(signal_bar_touches_level, 0, 100, +1, 0) is None


@pytest.mark.parametrize(
    ("side", "bars", "expected"),
    [(+1, [(105, 110, 98, 100)], (1, 100.0)),  # ordinary long touch
     (+1, [(95, 103, 90, 92)], (1, 95.0)),     # long gap through limit
     (-1, [(95, 102, 90, 100)], (1, 100.0)),   # ordinary short touch
     (-1, [(105, 110, 99, 108)], (1, 105.0))], # short gap through limit
)
def test_retest_limit_fill_price_and_direction(side, bars, expected):
    full = [(100, 101, 99, 100)] + bars
    assert rk.retest_entry(full, 0, 100, side, 1) == expected


def test_retest_window_includes_bar_i_plus_n_but_never_i_plus_n_plus_one():
    bars = [(100, 101, 99, 100), (101, 110, 101, 108), (108, 111, 99, 100)]
    assert rk.retest_entry(bars, 0, 100, +1, 1) is None
    assert rk.retest_entry(bars, 0, 100, +1, 2) == (2, 100.0)


def test_retest_does_not_read_future_bars_after_first_fill():
    class Bars:
        def __len__(self):
            return 4

        def __getitem__(self, index):
            if index == 1:
                return (105, 110, 99, 102)
            if index > 1:
                raise AssertionError("retest scan read beyond its first fill")
            return (100, 101, 99, 100)

    assert rk.retest_entry(Bars(), 0, 100, +1, 3) == (1, 100.0)
