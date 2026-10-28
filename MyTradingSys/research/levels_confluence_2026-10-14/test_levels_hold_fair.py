"""LC1 fair control (T05-F5): touched-only, distance-matched. Expected numbers are worked by hand in the comments."""
import random

from levels_hold import DAY_MS, analyze, fair_control_prices, legacy_control_prices


def _bar(t, o, h, lo, c):
    return {'t': t, 'o': o, 'h': h, 'l': lo, 'c': c, 'v': 1.0}


def _hold_day(day):
    """Midnight open 100, stop width max(.004*100, .001*101)=0.4.
    b1 touches 101 from below (prev close 100 < 101 => side -1, resistance); b2 trades down to 100.5 <= 101-0.4 => HOLD.
    The range 99.9..101.2 never reaches 99, so a control line at 99 is never touched."""
    t0 = day * DAY_MS
    return [_bar(t0, 100, 100.2, 99.9, 100), _bar(t0 + 60000, 100.5, 101.2, 100.4, 101),
            _bar(t0 + 120000, 101, 101.1, 100.5, 100.6)]


def test_fair_control_excludes_real_level():
    # Pool of 200 distinct distances; real distance 37.  Legacy draws are mid +/- the real distance, so half of them ARE the
    # real level (expected share 1/2).  Fair draws pick one of 200 distances and a sign, so the share is 1/(2*200) = 0.0025.
    mid, real_dist, n = 100.0, 37.0, 20000
    pool = [float(i) for i in range(1, 201)]
    legacy = legacy_control_prices(mid, real_dist, n, random.Random(1))
    fair = fair_control_prices(pool, mid, n, random.Random(1))
    assert len(legacy) == len(fair) == n
    eq = lambda xs: sum(abs(p - (mid + real_dist)) < 1e-9 for p in xs) / n
    assert eq(legacy) > .45
    assert eq(fair) < .01


def test_untouched_control_lines_leave_the_denominator():
    # 30 January days, each with one level at 101 (distance 1) that touches and HOLDs: real hold rate 30/30 = 1.
    # Every pool distance is 1, so a control line sits at 101 (touched, HOLD) or at 99 (never touched).
    days = list(range(19723, 19753))
    bars = [b for d in days for b in _hold_day(d)]
    levels = {d: [{'family': 'f', 'price': 101.0}] for d in days}
    row = analyze(bars, levels)['families']['f']
    assert row['n'] == 30 and row['hold_rate'] == 1.0
    # fair: only the ~half of 600 lines at 101 are touched, all HOLD => rate exactly 1.0, difference exactly 0 => DROP.
    assert 0 < row['fair_control_touches'] < 600
    assert row['random_hold_rate'] == 1.0
    assert row['difference'] == 0.0 and row['verdict'] == 'DROP'
    # legacy: lines at 99 count as non-holds in the denominator => random rate near 0.5, a spurious positive gap, KEEP.
    assert 0.3 < row['legacy_random_hold_rate'] < 0.7
    assert row['legacy_ci95'][0] > 0 and row['legacy_verdict'] == 'KEEP'
