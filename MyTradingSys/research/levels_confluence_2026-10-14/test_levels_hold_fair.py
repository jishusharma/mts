"""T05-F5: the LC1 control must be touched-only and distance-matched without ever being the real level.
Red on the old control (analyze_fair does not exist there; the legacy figure below is the defect), green on the fair one."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import levels_hold as LH  # noqa: E402
from levels_hold import DAY_MS  # noqa: E402


def _bar(t, o, h, l, c):
    return {'t': t, 'o': o, 'h': h, 'l': l, 'c': c, 'v': 1}


def _day(day, mid=100.0):
    # 30 one-minute bars inside [98, 102]; nothing beyond is ever touched.
    return [_bar(day * DAY_MS + i * 60_000, mid, mid + 2, mid - 2, mid) for i in range(30)]


def test_fair_control_excludes_real_level():
    mid = 100.0
    pool = [0.5, 1.0, 1.5, 40.0]
    rng = random.Random(1)
    for _ in range(200):
        lines = LH.fair_control_prices(rng, pool, mid, real_price=mid + 1.0, k=20, skip_real=True)
        assert all(abs(p - (mid + 1.0)) > 1e-9 for p in lines)
    # Same rng stream with or without the skip: only collided draws differ.
    a = LH.fair_control_prices(random.Random(7), pool, mid, mid + 1.0, 50, False)
    b = LH.fair_control_prices(random.Random(7), pool, mid, mid + 1.0, 50, True)
    assert [p for p in a if abs(p - (mid + 1.0)) > 1e-9] == b
    assert len(a) == 50


def test_untouched_control_lines_leave_the_denominator():
    # 3 days, 1 level each at +-1 from open; the pool also holds a 40 USD distance whose lines are never touched.
    bars, levels = [], {}
    for day, off in ((1, 1.0), (2, -1.0), (3, 1.0)):
        bars += _day(day)
        levels[day] = [{'family': 'f', 'price': 100.0 + off}]
    bars += _day(4)
    levels[4] = [{'family': 'f', 'price': 140.0}]
    res = LH.analyze_fair(bars, levels, k=20, skip_real=True)['f']
    total_draws = 20 * 4
    assert res['n_touch'] == 3                          # the 140 level is untouched: absent, not a non-hold
    assert 0 < res['fair_ctl_touches'] < total_draws    # the 40 USD lines left the denominator
    assert res['fair_ctl_touches'] <= total_draws * 3 / 4 + 20   # independent bound: only 1 of 4 pool distances is far


def test_legacy_control_is_defective():
    # Documents the defect the fair control removes: in the legacy control about half the five lines ARE the real level.
    bars, levels = [], {}
    for day in range(1, 41):
        bars += _day(day)
        levels[day] = [{'family': 'f', 'price': 101.0}, {'family': 'f', 'price': 140.0}]
    res = LH.analyze_fair(bars, levels, k=20, skip_real=False)['f']
    assert 0.4 < res['orig_ctl_equal_real_share'] < 0.6
    assert res['orig_ctl_untouched_share'] > 0.3     # the 140 level's lines are all untouched => counted as non-holds
