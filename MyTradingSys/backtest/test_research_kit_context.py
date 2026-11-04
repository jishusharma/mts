"""research_kit context harness: regime / phase / session tags, retest-entry mode, regime-mix line.
Every expectation is hand arithmetic (shown per test), never read from an existing implementation.
Series are (t_close, value) pairs: the bar is known at t_close (seconds, UTC)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest import research_kit as K  # noqa: E402

DAY = 86400


def daily(closes):
    """daily bars k=1..n closing at k * DAY."""
    closes = list(closes)
    return [(k * DAY) for k in range(1, len(closes) + 1)], closes


def test_regime_bull_all_three_agree():
    # closes 1..200: SMA200 at the last bar = (1+200)/2 = 100.5; close 200 > 100.5 -> above.
    d = daily(range(1, 201))
    t = 200 * DAY
    wk = ([t - 500, t - 300, t + 300], [65.0, 61.0, 35.0])   # last closed at t: 61 (>= 60)
    mo = ([t - 400, t + 100], [62.0, 38.0])                  # last closed at t: 62
    r = K.regime_tag(t, d, wk, mo)
    assert r == {"side": "above", "band": "bull", "regime": "bull"}


def test_regime_bear_and_range_and_boundaries():
    # closes 200..1: SMA200 = 100.5, last close 1 -> below.
    d = daily(range(200, 0, -1))
    t = 200 * DAY
    # weekly exactly 40 and monthly 38: both <= 40 -> bear band (boundary inclusive)
    r = K.regime_tag(t, d, ([t - 10], [40.0]), ([t - 10], [38.0]))
    assert r == {"side": "below", "band": "bear", "regime": "bear"}
    # weekly exactly 60 and monthly 61 on a below-SMA tape: bull band but side disagrees -> range
    r = K.regime_tag(t, d, ([t - 10], [60.0]), ([t - 10], [61.0]))
    assert r == {"side": "below", "band": "bull", "regime": "range"}
    # weekly 45 -> neither band
    r = K.regime_tag(t, d, ([t - 10], [45.0]), ([t - 10], [61.0]))
    assert r["band"] == "mid" and r["regime"] == "range"


def test_regime_none_when_history_short():
    # 150 daily bars < 200 needed for SMA200
    d = daily(range(1, 151))
    t = 150 * DAY
    r = K.regime_tag(t, d, ([t - 10], [65.0]), ([t - 10], [65.0]))
    assert r["side"] is None and r["regime"] is None
    # no weekly bar closed yet at t
    d = daily(range(1, 201))
    r = K.regime_tag(200 * DAY, d, ([200 * DAY + 5], [65.0]), ([1], [65.0]))
    assert r["band"] is None and r["regime"] is None


def test_regime_ema_side_differs_from_sma():
    # closes 10, 40, 31 with n=2. SMA2 = 35.5 -> 31 below. EMA2 (alpha 2/3, seed first value): e1 = 30, e2 = 20.667+10 = 30.667
    # -> 31 above.
    d = daily([10, 40, 31])
    t = 3 * DAY
    wk, mo = ([1], [65.0]), ([1], [65.0])
    assert K.regime_tag(t, d, wk, mo, ma="sma", ma_n=2)["side"] == "below"
    assert K.regime_tag(t, d, wk, mo, ma="ema", ma_n=2)["side"] == "above"


def test_regime_as_of_planted_future_bar_changes_nothing():
    d = daily(range(1, 201))
    t = 200 * DAY
    wk = ([t - 500, t - 300], [65.0, 61.0])
    mo = ([t - 400], [62.0])
    before = K.regime_tag(t, d, wk, mo)
    # plant a future daily bar (huge down move), a future weekly and monthly bar (bear values)
    d2 = (d[0] + [201 * DAY], d[1] + [-1000.0])
    wk2 = (wk[0] + [t + 1], wk[1] + [10.0])
    mo2 = (mo[0] + [t + 1], mo[1] + [10.0])
    assert K.regime_tag(t, d2, wk2, mo2) == before
    # control: the same planted bar becomes visible once t reaches it (the test can fail)
    assert K.regime_tag(201 * DAY, d2, wk2, mo2)["side"] == "below"


def test_phase_from_tf_break_classes():
    # tf_break: W1 = wick sweep (closed back inside, still range), H = close beyond held (break), R = reclaimed inside (retest)
    assert [K.phase_tag(c) for c in ("W1", "H", "R")] == ["range", "break", "retest"]
    with pytest.raises(ValueError):
        K.phase_tag("X")


def test_session_tag_cutoffs():
    base = 5 * DAY

    def h(hh, mm=0):
        return base + hh * 3600 + mm * 60

    # cutoffs 08:00, 13:00, 21:00 UTC (OURS): asia < 8 <= london < 13 <= ny < 21 <= late
    got = [K.session_tag(h(0)), K.session_tag(h(7, 59)), K.session_tag(h(8)), K.session_tag(h(12, 59)),
           K.session_tag(h(13)), K.session_tag(h(20, 59)), K.session_tag(h(21)), K.session_tag(h(23, 59))]
    assert got == ["asia", "asia", "london", "london", "ny", "ny", "late", "late"]


# bars are (o, h, l, c). signal bar index 0; its own range never counts.
LONG_BARS = [(100, 101, 99, 100.5),   # 0 signal bar (low 99 would touch level 100: must be ignored)
             (102, 105, 101, 104),    # 1 no touch (low 101 > 100)
             (104, 104, 99.5, 103),   # 2 touch: low 99.5 <= 100, open 104 > 100 -> limit fills at 100
             (103, 110, 90, 95)]      # 3 irrelevant


def test_retest_entry_first_pullback_fills_at_level():
    assert K.retest_entry(LONG_BARS, 0, 100.0, +1, 3) == (2, 100.0)


def test_retest_entry_window_and_no_retest():
    # N = 1 sees only bar 1 -> no pullback -> None (trade skipped, not taken at the signal bar)
    assert K.retest_entry(LONG_BARS, 0, 100.0, +1, 1) is None
    # level well below every low -> never touched
    assert K.retest_entry(LONG_BARS, 0, 50.0, +1, 3) is None


def test_retest_entry_gap_through_level_fills_at_open():
    bars = [(100, 101, 99, 100.5), (98, 99, 97, 98.5)]   # bar 1 opens 98 < level 100: long limit fills at the open
    assert K.retest_entry(bars, 0, 100.0, +1, 1) == (1, 98.0)


def test_retest_entry_short_mirror():
    # short, level 100: touch when high >= 100; fills at max(open, level)
    bars = [(100, 101, 99, 99.5), (97, 99, 96, 98), (98, 100.5, 97, 99), (99, 120, 80, 90)]
    assert K.retest_entry(bars, 0, 100.0, -1, 3) == (2, 100.0)
    bars2 = [(100, 101, 99, 99.5), (102, 103, 101, 102)]  # gap above: short fills at open 102
    assert K.retest_entry(bars2, 0, 100.0, -1, 1) == (1, 102.0)


def test_retest_entry_ignores_bars_after_fill_and_after_window():
    mutated = LONG_BARS[:3] + [(1, 1e9, -1e9, 1)] + [(1, 1e9, -1e9, 1)]
    assert K.retest_entry(mutated, 0, 100.0, +1, 3) == (2, 100.0)
    # a touch only on bar 3 is outside N = 2
    bars = [LONG_BARS[0], LONG_BARS[1], (104, 105, 101, 103), (103, 104, 99, 100)]
    assert K.retest_entry(bars, 0, 100.0, +1, 2) is None
    assert K.retest_entry(bars, 0, 100.0, +1, 3) == (3, 100.0)


def test_regime_mix_line_counts_sum_to_weeks():
    tags = ["bull", "bull", "bear", "range", "range", None]
    # 6 weeks: bull 2 = 33.3 %, bear 1 = 16.7 %, range 2 = 33.3 %, n/a 1 = 16.7 %
    assert K.regime_mix_line(tags) == "6 weeks: bull 2 (33%) | bear 1 (17%) | range 2 (33%) | n/a 1 (17%)"
    assert K.regime_mix_line([]) == "0 weeks: no data"
    with pytest.raises(ValueError):
        K.regime_mix_line(["bull", "sideways"])


def test_weekly_regimes_feeds_mix_line():
    d = daily(range(1, 201))
    t = 200 * DAY
    wk = ([t - 700000], [65.0])
    mo = ([t - 700000], [65.0])
    weeks = [t, t + 7 * DAY]   # second week: no new daily bar, SMA side unchanged (as of last closed bar)
    tags = K.weekly_regimes(weeks, d, wk, mo)
    assert tags == ["bull", "bull"]
    assert K.regime_mix_line(tags).startswith("2 weeks: bull 2")
