"""T05-F5: the LC1 verdict must use the touched-only, distance-matched fair control.

Hand fixture (two UTC days in one calendar month, family 'x', midnight open 100 both days):
  day 0: real level 102 (distance 2); bars span 99.5..103.3
  day 1: real level 97  (distance 3); bars span 97.5..100.3
Distance pool for ('x', month) = {2, 3}, so a control line is one of 97, 98, 102, 103.
Excluding the real level itself: day 0 lines are in {97, 98, 103}, day 1 lines in {98, 102, 103}.
Outcomes worked by hand from levels_hold.outcome (width = max(0.4% of 100, 0.1% of level) = 0.4 for all of these):
  day 0, line 103: first touch bar 2 (prev close 101.9 < 103 -> side -1); bar 3 low 102.5 <= 102.6 and high 103.3 < 103.4 -> HOLD
  day 0, lines 97 / 98: low of the day 99.5 -> never touched
  day 0, real 102: touch bar 1 (prev close 100.2 < 102 -> side -1); bar 2 high 103.2 >= 102.4 -> BREAK
  day 1, line 98: touch bar 1 (prev close 100.0 > 98 -> side +1); bar 2 low 97.5 <= 97.6 -> BREAK
  day 1, lines 102 / 103: high of the day 100.3 -> never touched
  day 1, real 97: low of the day 97.5 -> never touched
"""
import pytest

from levels import DAY_MS
from levels_hold import analyze


def bar(t, o, h, l, c):
    return {'t': t, 'o': o, 'h': h, 'l': l, 'c': c, 'v': 1}


DAY0 = [bar(0, 100, 100.5, 99.5, 100.2),
        bar(60_000, 100.2, 102.1, 100.1, 101.9),
        bar(120_000, 101.9, 103.2, 101.8, 103.1),
        bar(180_000, 103.1, 103.3, 102.5, 102.6)]
DAY1 = [bar(DAY_MS, 100, 100.3, 99.8, 100.0),
        bar(DAY_MS + 60_000, 100.0, 100.1, 97.9, 98.0),
        bar(DAY_MS + 120_000, 98.0, 98.2, 97.5, 97.8)]
LEVELS = {0: [{'family': 'x', 'price': 102.0}], 1: [{'family': 'x', 'price': 97.0}]}
HAND = {(0, 103.0): 'HOLD', (0, 97.0): None, (0, 98.0): None,
        (1, 98.0): 'BREAK', (1, 102.0): None, (1, 103.0): None}


def test_fair_control_excludes_real_level():
    res = analyze(DAY0 + DAY1, LEVELS)
    lines = res['fair_events']
    assert len(lines) == 2                                  # every candidate level draws controls, touched or not
    holds = touches = 0
    for ev in lines:
        assert len(ev['controls']) == 20
        for price, out in ev['controls']:
            assert price != pytest.approx(ev['level'])      # a control line is never the real level
            assert out == HAND[(ev['day'], round(price, 6))]
            if out is not None:                             # untouched lines leave the denominator
                touches += 1
                holds += out == 'HOLD'
    fam = res['families']['x']
    assert touches > 0 and fam['fair_ctl_touches'] == touches
    assert fam['fair_ctl_hold_rate'] == pytest.approx(holds / touches)
    assert fam['n'] == 1 and fam['hold_rate'] == 0.0        # real: day 0 BREAK, day 1 untouched
    assert fam['fair_difference'] == pytest.approx(0.0 - holds / touches)
    assert fam['verdict'] == fam['fair_verdict']            # the published verdict is the fair one
    assert 'legacy_verdict' in fam and 'random_hold_rate' in fam   # published control kept as a labelled legacy column
