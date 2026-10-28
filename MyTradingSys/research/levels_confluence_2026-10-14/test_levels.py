from levels import DAY_MS, _profile, levels_by_day
from levels_hold import outcome


def bar(t, o, h, l, c, v):
    return {'t': t, 'o': o, 'h': h, 'l': l, 'c': c, 'v': v}


def test_day_two_value_area_matches_hand_calculation():
    # Point masses in 10 USD bins: [1, 2, 10, 4, 3], per FORMULAS.md 18.1.
    volumes = [1, 2, 10, 4, 3]
    day1 = [bar(i * 60_000, 1005 + i * 10, 1005 + i * 10, 1005 + i * 10,
                1005 + i * 10, v) for i, v in enumerate(volumes)]
    day2_start = DAY_MS
    day2 = [bar(day2_start, 1011, 1012, 1010, 1011, 1)]
    result = levels_by_day(day1 + day2)[1]
    profile = {x['family']: x['price'] for x in result}
    assert profile['prior_day_poc'] == 1025
    assert profile['prior_day_val'] == 1020
    assert profile['prior_day_vah'] == 1040


def test_levels_day_two_do_not_read_bars_at_or_after_midnight():
    day1 = [bar(i * 60_000, 100, 110, 90, 100, 1) for i in range(4)]
    day2 = [bar(DAY_MS, 101, 105, 99, 102, 1)]
    baseline = levels_by_day(day1 + day2)[1]
    # Alter the exact midnight bar and every later day-2 bar.
    future = [bar(DAY_MS + i * 60_000, 800 + i, 900 + i, 700 + i, 850 + i, 999)
              for i in range(20)]
    mutated = levels_by_day(day1 + future)[1]
    assert baseline == mutated


def test_break_before_favorable_move_is_break():
    # A touch at 100, then price penetrates to 99 before a one-width reaction to 101.
    bars = [bar(0, 100, 100, 100, 100, 1), bar(1, 100, 100, 99, 99, 1)]
    assert outcome(bars, 100, 1) == 'BREAK'


# --- Q79: touch-bar look-ahead (side from previous close, no touch-bar target credit) ---

def test_touch_bar_close_does_not_set_side_or_credit_target():
    # Previous close 105 is above level 100 -> long side (support). The touch bar dips to 99.5,
    # spikes to 101.5 (>= level+width) and closes at 101: old code read close>=level => long and
    # credited the in-bar spike as HOLD. New rule: no favourable credit inside the touch bar.
    touch = bar(1, 105, 101.5, 99.5, 101, 1)
    nxt = bar(2, 101, 100.8, 100.2, 100.5, 1)
    assert outcome([touch, nxt], 100, 1, prev_close=105) == 'NEITHER'


def test_side_comes_from_previous_close_not_touch_close():
    # Prev close 95 below level -> short side. Touch bar closes ABOVE level (old code: long).
    # A later bar falls to 98.9 (favourable for a short, width 1) -> HOLD only under the new side.
    touch = bar(1, 95, 100.5, 94.9, 100.2, 1)
    later = bar(2, 100.2, 100.3, 98.9, 99.0, 1)
    assert outcome([touch, later], 100, 1, prev_close=95) == 'HOLD'


def test_touch_bar_adverse_still_counts_as_break():
    touch = bar(1, 105, 105, 98.9, 101, 1)
    later = bar(2, 101, 102, 100.5, 101.5, 1)
    assert outcome([touch, later], 100, 1, prev_close=105) == 'BREAK'
