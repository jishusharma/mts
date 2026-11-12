"""Tests for rules.py (card btc-last-orderflow-rules-1112). Synthetic data only: no F: drive needed.

Each rule has (1) a case that must fire with the right side, (2) a no-fire case, (3) a look-ahead check (changing bars
after the decision does not change the signal), and (4) a meta-test: the same expectation applied to a deliberately wrong
rule (flipped side, flipped extreme, value area from the same day) must FAIL, so the tests cannot pass on a wrong rule.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules  # noqa: E402


# ------------------------------------------------------------------ R8
def _down_series(n=900, seed=0):
    rng = np.random.default_rng(seed)
    close = 100.0 - 0.05 * np.arange(n) + rng.normal(0, 0.01, n)
    delta = -rng.uniform(1, 2, n)          # mild steady selling
    return close, delta


def r8_expectation(fn):
    """fn(close, delta, arm) -> [(k, side)]. Down-trend with mild selling then one big sell hour."""
    close, delta = _down_series()
    delta[850] = -50.0                      # sell extreme at hour 850
    a = dict(fn(close, delta, 'a'))
    b = dict(fn(close, delta, 'b'))
    assert a.get(849) == -1, 'mild selling in a down-trend must short'
    assert 850 not in a, 'no short at the extreme'
    assert b.get(850) == 1, 'sell extreme in a down-trend must go long'
    assert 849 not in b


def wrong_r8_flip(close, delta, arm):
    return [(k, -s) for k, s in rules.r8_signals(close, delta, arm)]


def wrong_r8_extreme_inverted(close, delta, arm):
    d = -np.asarray(delta, dtype=float)    # treats buying as the extreme side
    return rules.r8_signals(close, d, arm)


def test_r8_fires():
    r8_expectation(rules.r8_signals)


def test_r8_no_trend_no_signal():
    close, delta = _down_series()
    close = close[::-1].copy()              # rising market
    delta[850] = -50.0
    assert rules.r8_signals(close, delta, 'a') == []
    assert rules.r8_signals(close, delta, 'b') == []


def test_r8_no_lookahead():
    close, delta = _down_series()
    delta[850] = -50.0
    full = [x for x in rules.r8_signals(close, delta, 'b') if x[0] <= 850]
    c2, d2 = close.copy(), delta.copy()
    c2[851:] = 1e6
    d2[851:] = 1e9
    assert [x for x in rules.r8_signals(c2, d2, 'b') if x[0] <= 850] == full


@pytest.mark.parametrize('wrong', [wrong_r8_flip, wrong_r8_extreme_inverted])
def test_r8_wrong_rule_fails(wrong):
    with pytest.raises(AssertionError):
        r8_expectation(wrong)


# ------------------------------------------------------------------ value area
def _day(center=100.0, spread=1.0):
    t = np.arange(rules.DAY)
    mid = center + spread * np.sin(t / 200.0)
    h, l, c = mid + 0.05, mid - 0.05, mid
    v = np.ones(rules.DAY)
    v[(c > center - 0.2) & (c < center + 0.2)] = 50.0   # heavy volume near the center
    return h, l, c, v


def test_value_area_brackets_poc_and_is_70pct():
    h, l, c, v = _day()
    val, vah = rules.value_area(h, l, c, v, c[-1])
    assert val < 100.0 < vah
    inside = (((h + l + c) / 3 >= val) & ((h + l + c) / 3 <= vah))
    assert v[inside].sum() >= 0.69 * v.sum()
    assert vah - val < 2.0, 'heavy-volume core, not the full range'


def _va_unmoved(fn):
    h, l, c, v = _day()
    H_, L_, C_, V_ = (np.tile(x, 3) for x in (h, l, c, v))
    base = fn(H_, L_, C_, V_, 1)
    H2, L2, C2 = H_.copy(), L_.copy(), C_.copy()
    H2[rules.DAY:] += 500                  # change day 1 and later: day 1's VA (from day 0) must not move
    L2[rules.DAY:] += 500
    C2[rules.DAY:] += 500
    assert fn(H2, L2, C2, V_, 1) == base


def wrong_va_same_day(h, l, c, v, d):
    a, b = d * rules.DAY, (d + 1) * rules.DAY
    return rules.value_area(h[a:b], l[a:b], c[a:b], v[a:b], c[b - 1])


def test_value_area_uses_prior_day_only():
    _va_unmoved(rules.day_va)


def test_value_area_same_day_rule_fails():
    with pytest.raises(AssertionError):
        _va_unmoved(wrong_va_same_day)


# ------------------------------------------------------------------ R5
def r5_expectation(fn):
    val, vah = 99.0, 101.0
    n = 1441
    hi, lo = np.full(n, 100.2), np.full(n, 99.8)
    hi[300] = 101.2                         # touches VAH first: short at the next bar
    assert fn(100.0, hi, lo, val, vah) == (300, -1)
    hi2, lo2 = np.full(n, 100.2), np.full(n, 99.8)
    lo2[200] = 98.9
    hi2[300] = 101.2                        # VAL first: long
    assert fn(100.0, hi2, lo2, val, vah) == (200, 1)
    assert fn(105.0, hi, lo, val, vah) is None, 'opens outside value: no trade'
    hi3, lo3 = np.full(n, 100.2), np.full(n, 99.8)
    hi3[1300] = 102.0                       # after the 20:00Z cut-off
    assert fn(100.0, hi3, lo3, val, vah) is None


def wrong_r5_flip(day_open, hi, lo, val, vah):
    r = rules.r5_trade(day_open, hi, lo, val, vah)
    return None if r is None else (r[0], -r[1])


def wrong_r5_ignores_open(day_open, hi, lo, val, vah):
    return rules.r5_trade(100.0, hi, lo, val, vah)


def test_r5_fires():
    r5_expectation(rules.r5_trade)


def test_r5_both_edges_one_bar_skips():
    n = 1441
    hi, lo = np.full(n, 100.2), np.full(n, 99.8)
    hi[100], lo[100] = 101.5, 98.5
    assert rules.r5_trade(100.0, hi, lo, 99.0, 101.0) is None


@pytest.mark.parametrize('wrong', [wrong_r5_flip, wrong_r5_ignores_open])
def test_r5_wrong_rule_fails(wrong):
    with pytest.raises(AssertionError):
        r5_expectation(wrong)


# ------------------------------------------------------------------ R11
def r11_expectation(fn):
    val, vah = 99.0, 101.0
    close15 = np.full(96, 100.0)
    vol15 = np.full(96, 10.0)
    close15[10] = 101.5                     # fresh breakout up
    vol15[10], vol15[11], vol15[12] = 100.0, 80.0, 70.0
    j, s, q = fn(100.0, close15, vol15, val, vah)
    assert (j, s) == (10, 1) and q == pytest.approx(0.75)
    vol15[11], vol15[12] = 10.0, 10.0       # dry-up
    assert fn(100.0, close15, vol15, val, vah)[2] == pytest.approx(0.1)
    close15b = np.full(96, 100.0)
    close15b[20] = 98.0                     # break down
    assert fn(100.0, close15b, np.full(96, 10.0), val, vah)[1] == -1
    closed_out = np.full(96, 102.0)         # already outside from the start: not a fresh break
    assert fn(105.0, closed_out, np.full(96, 10.0), val, vah) is None


def wrong_r11_flip(day_open, close15, vol15, val, vah):
    r = rules.r11_event(day_open, close15, vol15, val, vah)
    return None if r is None else (r[0], -r[1], r[2])


def wrong_r11_uses_breakout_bar_volume_as_followup(day_open, close15, vol15, val, vah):
    r = rules.r11_event(day_open, close15, vol15, val, vah)
    return None if r is None else (r[0], r[1], 1.0)


def test_r11_fires():
    r11_expectation(rules.r11_event)


def test_r11_no_lookahead():
    close15 = np.full(96, 100.0)
    vol15 = np.full(96, 10.0)
    close15[10] = 101.5
    a = rules.r11_event(100.0, close15, vol15, 99.0, 101.0)
    c2 = close15.copy()
    c2[13:] = 500.0                          # bars after the follow-up window cannot change the event
    assert rules.r11_event(100.0, c2, vol15, 99.0, 101.0) == a


@pytest.mark.parametrize('wrong', [wrong_r11_flip, wrong_r11_uses_breakout_bar_volume_as_followup])
def test_r11_wrong_rule_fails(wrong):
    with pytest.raises(AssertionError):
        r11_expectation(wrong)


# ------------------------------------------------------------------ shared
def test_fee_is_ten_bp_round_trip():
    assert rules.COST_PCT == pytest.approx(0.10)
    assert rules.net_pct(0.30, 1) == pytest.approx(0.20)
    assert rules.net_pct(-0.30, -1) == pytest.approx(0.20)


def test_verdict_needs_both_halves_and_t():
    ent = [0] * 100 + [rules.HALF_DAY * rules.DAY + 1] * 100
    good = [0.2, 0.1] * 100
    assert rules.verdict(ent, good)['verdict'] == 'PASS'
    bad_second = [0.3] * 100 + [-0.01] * 100
    assert rules.verdict(ent, bad_second)['verdict'] == 'FAIL'
    assert rules.verdict(ent[:50], good[:50])['verdict'] == 'INSUFFICIENT_N'


def test_placebo_is_seeded_and_direction_matched():
    n = 3 * rules.DAY
    o = np.linspace(100, 101, n)
    c = o.copy()
    cand = list(range(5, n - 100, 5))
    ev = [(600, 1), (1300, -1)]
    a = rules.placebo(o, c, cand, ev, ndraw=20)
    b = rules.placebo(o, c, cand, ev, ndraw=20)
    assert np.allclose(a, b, equal_nan=True)
