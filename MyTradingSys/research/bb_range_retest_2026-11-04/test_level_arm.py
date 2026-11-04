"""Wiring tests for bb_range_retest_2026-11-04: ATR is causal, the session-range tag is as-of (planted future bar changes nothing),
the level arm needs a re-entry close BEFORE any touch (so it is not the next-open fill), touch within k ATR, fill rule, no read of
bars at/before the signal or re-entry bar."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("bb_retest_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

M15 = 900000
DAY = 86400000


def _flat(n, px=100.0, h=0.5):
    return [(px, px + h, px - h, px)] * n


def test_atr14_uses_only_bars_up_to_i():
    o = _flat(30)
    a1 = study.atr14(o, 20)
    o2 = o + [(100.0, 500.0, 1.0, 100.0)]
    assert study.atr14(o2, 20) == a1 and abs(a1 - 1.0) < 1e-9     # TR = 1.0 on flat bars with h=0.5


def _session_bars(days, base=100.0, big_day=None):
    """15m bars from epoch day 100: per day 96 bars; the london session (08-13 UTC, bars closing 08:15..13:00) of `big_day` is wide."""
    bars = []
    for d in range(days):
        for k in range(96):
            t = (100 + d) * DAY + k * M15
            amp = 5.0 if (big_day == d and 32 <= k < 52) else 0.5
            bars.append({"t": t, "o": base, "h": base + amp, "l": base - amp, "c": base})
    return bars


def test_session_range_tag_is_as_of_and_needs_history():
    bars = _session_bars(14, big_day=13)
    tags = study.session_range_tags(bars, M15)
    assert len(tags) == len(bars)
    first_days = [t for t in tags[:96 * 5]]
    assert not any(first_days)                       # fewer than 10 prior same-name sessions: never tagged
    last = 13 * 96
    # london of the last day: wide bars from k=32; once the running range exceeds the median of prior sessions the tag is on
    assert tags[last + 40] is True
    assert tags[last + 10] is False                  # asia of that day: normal range
    # planted future bar changes no earlier tag
    more = bars + [{"t": bars[-1]["t"] + M15, "o": 100.0, "h": 1000.0, "l": 1.0, "c": 100.0}]
    assert study.session_range_tags(more, M15)[:len(bars)] == tags


def test_level_arm_needs_reentry_close_then_touch():
    # long at lower band 100 (signal bar 5). Price stays BELOW the band afterwards: the old retest filled here, the level arm must not.
    o = _flat(30, 98.0, 0.2)
    assert study.level_arm_fill(o, 5, 1, 100.0, 0.5, 1.0) is None
    # re-entry close above the band at bar 7, no pullback afterwards: no fill
    o = _flat(30, 98.0, 0.2)
    o[7] = (98.0, 103.0, 98.0, 102.0)
    for k in range(8, 30):
        o[k] = (103.0, 104.0, 102.5, 103.5)
    assert study.level_arm_fill(o, 5, 1, 100.0, 0.5, 1.0) is None
    # pullback to level + 0.5 ATR (=100.5) at bar 9: fills at the limit
    o[9] = (103.0, 103.5, 100.4, 101.0)
    assert study.level_arm_fill(o, 5, 1, 100.0, 0.5, 1.0) == (9, 100.5)
    # gap down through the limit fills at the open
    o[9] = (100.2, 100.5, 99.0, 100.0)
    assert study.level_arm_fill(o, 5, 1, 100.0, 0.5, 1.0) == (9, 100.2)


def test_level_arm_never_reads_signal_or_reentry_bar_and_short_mirror():
    o = _flat(30, 102.0, 0.2)
    o[5] = (102.0, 102.0, 1.0, 102.0)           # signal bar dip must not matter
    o[7] = (102.0, 102.0, 97.0, 98.0)           # re-entry close (below the short level 100): its own range must not fill
    o[7] = (102.0, 102.0, 99.5, 98.0) if False else o[7]
    # short: level 100, price above it before: re-entry = close < 100
    o = _flat(30, 102.0, 0.2)
    o[7] = (102.0, 102.0, 97.0, 98.0)
    for k in range(8, 30):
        o[k] = (97.0, 97.5, 96.5, 97.0)
    assert study.level_arm_fill(o, 5, -1, 100.0, 0.5, 1.0) is None
    o[10] = (97.0, 99.6, 96.8, 98.0)             # high reaches level - 0.5 = 99.5
    assert study.level_arm_fill(o, 5, -1, 100.0, 0.5, 1.0) == (10, 99.5)


def test_level_arm_windows():
    o = _flat(40, 98.0, 0.2)
    o[18] = (98.0, 103.0, 98.0, 102.0)          # re-entry at 18 > 5 + 10: too late
    assert study.level_arm_fill(o, 5, 1, 100.0, 0.5, 1.0, 10, 10) is None
    o = _flat(40, 98.0, 0.2)
    o[7] = (98.0, 103.0, 98.0, 102.0)
    for k in range(8, 40):
        o[k] = (103.0, 104.0, 102.5, 103.5)
    o[18] = (103.0, 103.5, 100.0, 101.0)        # touch at 18 > 7 + 10: too late
    assert study.level_arm_fill(o, 5, 1, 100.0, 0.5, 1.0, 10, 10) is None
