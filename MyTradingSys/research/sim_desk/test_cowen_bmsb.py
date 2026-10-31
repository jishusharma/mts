"""Cowen bull-market-support-band study on the desk (research/sim_desk/studies/cowen_bmsb.py).

Verifies: plug-in discovery, labelling and date lock; the band from completed weekly closes (hand-computed 20-week SMA and
21-week EMA, expected numbers worked out on paper, not taken from the code); the unfinished week never enters the band
(planted leak); the four ideas fire on a hand-built daily series exactly where the concept check says; the band exit; the
other-coin catch-down; a hand-checked fee-net trade; a DEV run when the bars are on disk.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402
from studies import _bars  # noqa: E402

DAY, MIN = _bars.DAY, _bars.MIN
D0 = 19083       # 2022-04-01 UTC, a Friday (inside DEV)
MON = 19079      # 2022-03-28 UTC, a Monday


def study():
    found = desk.load_studies()
    assert 'cowen_bmsb' in found
    return found['cowen_bmsb']


def test_plugged_in_labelled_and_date_locked():
    s = study()
    assert s.ID == 'cowen_bmsb' and 'support band' in s.TITLE.lower()
    for f in s.params():
        if f.get('date'):
            continue
        for t in (list(f['choices'].values()) if f.get('choices') else [f['label']]):
            assert '(trader' in t or '(ours' in t or 'fee' in t.lower(), t
    for bad in ({'end': '2024-07-01'}, {'start': '2022-03-31'}, {'setup': 'MIDTERM'}, {'target': 'BAND'},
                {'setup': 'BOUNCE', 'target': 'BAND'}, {'exit_n': 99}, {'stop_atr': 'x'}, {'hold_days': 0}):
        with pytest.raises(ValueError):
            s.normalize(bad)
    q = s.normalize({'setup': 'FAKEOUT', 'target': 'BAND'})
    assert q['target_r'] is None and q['gap_pct'] == 0.0
    d = s.describe(s.normalize({}))
    for word in ('20-week SMA and 21-week EMA', 'completed weeks', 'development window only'):
        assert word in d, word
    assert 'BOUNCE' in s.label(s.normalize({}))


def _weekly_const(n_weeks, close_of=lambda w: w + 1.0):
    """Daily bars (t, o, h, l, c) from Monday MON: every day of week w closes at close_of(w)."""
    n = 7 * n_weeks
    t = (MON + np.arange(n)) * DAY
    c = np.array([close_of(i // 7) for i in range(n)], float)
    return np.column_stack([t, c, c, c, c])


def test_band_is_sma20_and_ema21_of_completed_weeks_hand_computed():
    """Weekly closes c_w = w + 1. By hand: SMA20 at week k = mean(c[k-19..k]) = k - 8.5 + 1 ... worked per row below;
    EMA21 seed = mean(c[0..20]) = 11 at k = 20, then each week adds (c - ema) * 2/22 = +1, so ema_k = c_k - 10."""
    s = study()
    d = _weekly_const(27)
    top, bot = s.band(d[:, 0], d[:, 4])
    wk = lambda w: slice(7 * w, 7 * w + 7)                       # noqa: E731
    assert np.isnan(top[wk(0)]).all() and np.isnan(top[wk(20)]).all()    # week 20 would need EMA at week 19: not defined
    # week 21 uses week 20: SMA20 = mean(2..21) = 11.5, EMA21 = mean(1..21) = 11
    assert top[wk(21)] == pytest.approx([11.5] * 7) and bot[wk(21)] == pytest.approx([11.0] * 7)
    # week 25 uses week 24: SMA20 = mean(6..25) = 15.5, EMA21 = 25 - 10 = 15
    assert top[wk(25)] == pytest.approx([15.5] * 7) and bot[wk(25)] == pytest.approx([15.0] * 7)


def test_unfinished_week_never_enters_the_band_planted_leak():
    s = study()
    base = _weekly_const(27)
    top0, bot0 = s.band(base[:, 0], base[:, 4])
    junk = _weekly_const(27, lambda w: 1000.0 if w == 25 else w + 1.0)    # week 25 closes at 1000
    top1, bot1 = s.band(junk[:, 0], junk[:, 4])
    w25 = slice(7 * 25, 7 * 25 + 7)
    assert top1[w25] == pytest.approx(top0[w25]) and bot1[w25] == pytest.approx(bot0[w25])   # same band while the week runs
    w26 = slice(7 * 26, 7 * 26 + 7)
    assert top1[w26][0] > 100 and top0[w26][0] < 20                                           # one week later it counts


def _feat(rows, top=100.0, bottom=90.0, sma=None, t0=D0):
    """Feature dict from (o, h, l, c) rows, a constant band, and an optional 50-day average list."""
    d = np.column_stack([(t0 + np.arange(len(rows))) * DAY, np.asarray(rows, float)])
    n = len(rows)
    return {'d': d, 'top': np.full(n, float(top)), 'bottom': np.full(n, float(bottom)),
            'sma50': np.full(n, np.nan) if sma is None else np.asarray(sma, float), 'atr': np.full(n, 2.0)}


ROWS = [(110, 112, 109, 110), (110, 111, 99, 108),     # bar 1: dips to the top (99 <= 100) from above, closes above 90 -> BOUNCE long
        (108, 109, 94, 95),                            # bar 2: again from above (previous close 108)
        (95, 96, 87, 88),                              # bar 3: first close below the bottom 90 -> LOSE short
        (88, 89, 84, 85), (85, 103, 84, 102),          # bar 5: back above the top
        (102, 106, 101, 105),                          # bar 6: low 101 never reaches the top: no bounce
        (105, 106, 100.5, 101)]                        # bar 7: below the 50-day 103 while above the band top -> FAKEOUT short
SMA = [np.nan] * 5 + [103.0] * 3


def test_four_ideas_fire_where_the_concept_check_says():
    s = study()
    f = _feat(ROWS, sma=SMA)
    got = lambda setup: [(x['i'], x['side']) for x in s.signals(f, setup)]    # noqa: E731
    assert got('BOUNCE') == [(1, 1), (2, 1)]
    assert got('LOSE') == [(3, -1)]
    assert got('FAKEOUT') == [(7, -1)]
    assert s.signals(f, 'CATCHDOWN') == []                                     # no other coin given: nothing fires
    assert s.signals(_feat(ROWS), 'FAKEOUT') == []                             # no 50-day average yet: nothing fires
    nan_band = _feat(ROWS, top=np.nan, bottom=np.nan)
    assert all(s.signals(nan_band, k) == [] for k in ('BOUNCE', 'LOSE'))        # no band yet: nothing fires


def test_level_exit_counts_consecutive_closes_on_the_wrong_side():
    s = study()
    f = _feat(ROWS, sma=SMA)
    t = f['d'][:, 0].astype(np.int64)
    # long from bar 1: closes below 90 at bars 3 (88) and 4 (85) -> 2 in a row ends it at the open of bar 5
    assert s.exit_after(f, 1, 1, 2, f['bottom']) == t[4] + DAY and s.exit_after(f, 1, 1, 0, f['bottom']) is None
    assert s.exit_after(f, 1, 1, 3, f['bottom']) is None                                    # bar 5 closes back above 90: the run breaks
    # LOSE short from bar 3, level = band bottom 90: closes above 90 at bars 5 (102), 6 (105), 7 (101); bar 4 (85) is not
    assert s.exit_after(f, 3, -1, 2, f['bottom']) == t[6] + DAY and s.exit_after(f, 3, -1, 3, f['bottom']) == t[7] + DAY
    # FAKEOUT short with level = the 50-day (103) and CATCHDOWN with a number: only closes above count, never the band
    assert s.exit_after(f, 3, -1, 1, f['sma50']) == t[6] + DAY       # 50-day 103: bar 5 closes 102 (no), bar 6 closes 105 (yes)
    assert s.exit_after(f, 4, -1, 1, 101.5) == t[5] + DAY            # bar 5 closes 102 > 101.5
    assert s.exit_after(f, 4, -1, 2, 101.5) == t[6] + DAY            # bar 6 closes 105 > 101.5, a second in a row
    assert s.exit_after(f, 6, -1, 1, 101.5) is None                  # bar 7 closes 101 < 101.5


def test_catchdown_needs_the_other_coin_at_its_band_and_a_gap_above_its_own():
    s = study()
    main = _feat([(c, c, c, c) for c in (100, 104, 105, 102, 106, 107)])
    other = _feat([(l, l, l, l) for l in (101, 101, 95, 95, 101, 95)], top=98.0)     # at its band (low <= 98) on bars 2, 3, 5
    got = [(x['i'], x['side']) for x in s.signals(main, 'CATCHDOWN', 3.0, other)]
    # gap 3 %: close must exceed 103. Bar 2 (105, other at band) fires; bar 3 (102) fails the gap; bar 5 (107) fires again
    assert got == [(2, -1), (5, -1)]
    assert [x['i'] for x in s.signals(main, 'CATCHDOWN', 5.0, other)] == [5]       # 105 is not above 105: only bar 5 (107) fires
    assert s.signals(main, 'CATCHDOWN', 8.0, other) == []


def test_hand_checked_fee_net_trade():
    """LOSE short, entry at the next day's open 100, stop 102 hit by a high of 102: gross -1 R, fees
    (0.07 % x 100 + 0.07 % x 102) / 2 = 0.0707 R, net -1.0707 R."""
    s = study()
    q = s.normalize({'maker_pct': 0.02, 'taker_pct': 0.05, 'slip_pct': 0.02, 'start': '2022-04-01', 'end': '2022-04-05'})
    n = 3 * 1440
    t = D0 * DAY + np.arange(n) * MIN
    px = np.full(n, 100.0)
    a = np.column_stack([t, px, px, px, px])
    k = 1440 + 1000
    a[k, 2] = 102.0
    t0 = (D0 + 1) * DAY
    res = _bars.collect([{'x': 1}], a, q, lambda sg: [-1, t0, None, 102.0, 90.0, t0 + DAY, None, t0 + DAY, 100.0])
    assert res['filled'].tolist() == [True] and res['exit'].tolist() == ['STOP']
    assert res['gross'][0] == pytest.approx(-1.0) and res['net'][0] == pytest.approx(-1.0707, abs=1e-4)


@pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on disk')
def test_dev_run_writes_ledger_row(tmp_path):
    s = study()
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    r = desk.run_setting(s, {'setup': 'BOUNCE'}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert r['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA')
    assert '| sim-desk cowen_bmsb BOUNCE' in trials.read_text(encoding='utf-8')
    lo, hi = 1648771200000, 1719791999999                       # 2022-04-01 .. 2024-06-30
    for t_ in r['trades']['t']:
        assert lo <= t_ <= hi
