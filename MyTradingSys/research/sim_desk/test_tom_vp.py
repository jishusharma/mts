"""Tom volume-profile study on the desk (research/sim_desk/studies/tom_vp.py).

Verifies: plug-in discovery and labelling, date lock; the period profile uses the period's own bars (FORMULAS 18.1 worked
example B); the three trade ideas fire on a hand-built 5m series exactly where the concept check says; the migration
filter skips the trade against the shift; planted-leak causality; the acceptance exit; a hand-checked fee-net trade;
a DEV run when the bars are on disk.
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
D0 = 19083   # 2022-04-01 UTC, a Friday (inside DEV)


def study():
    found = desk.load_studies()
    assert 'tom_vp' in found
    return found['tom_vp']


def test_plugged_in_labelled_and_date_locked():
    s = study()
    assert s.ID == 'tom_vp' and 'volume profile' in s.TITLE.lower()
    for f in s.params():
        if f.get('date'):
            continue
        for t in (list(f['choices'].values()) if f.get('choices') else [f['label']]):
            assert '(trader' in t or '(ours' in t or 'fee' in t.lower(), t
    for bad in ({'end': '2024-07-01'}, {'start': '2022-03-31'}, {'anchor': 'cash_session'}, {'setup': 'POC_TOUCH'},
                {'setup': 'ACCEPT', 'accept_n': 0}, {'stop_atr': 'x'}, {'accept_n': 99}):
        with pytest.raises(ValueError):
            s.normalize(bad)
    q = s.normalize({})
    assert q['target_r'] is None and q['accept_n'] == 6
    d = s.describe(q)
    for word in ('70 % value area', 'point of control', 'development window only'):
        assert word in d, word
    assert 'n6' in s.label(q)


def _minute_bars(day, prices, vol=1.0):
    """1m bars for one UTC day: point-mass bars (o=h=l=c) at the given prices, repeated to fill the day."""
    n = 1440
    px = np.resize(np.asarray(prices, float), n)
    t = day * DAY + np.arange(n) * MIN
    return np.column_stack([t, px, px, px, px, np.full(n, vol)])


def test_period_profile_is_the_periods_own_bars_worked_example_b():
    """FORMULAS 18.1 worked B: bin volumes [1,2,10,4,3] (w = 1) -> POC 2.5, VAL 2.0, VAH 4.0; keyed by its own day."""
    s = study()
    prices = [0.5] * 1 + [1.5] * 2 + [2.5] * 10 + [3.5] * 4 + [4.5] * 3
    a = _minute_bars(D0, prices)
    a = a[:20]                                       # exactly the 20 point-mass bars of the example
    prof = s.period_profiles(a, 'prior_day', w=1.0)
    assert set(prof) == {D0}
    assert prof[D0] == {'poc_price': 2.5, 'vah': 4.0, 'val': 2.0}
    # weekly key: D0 (a Friday) and the next Monday fall in different Monday-weeks
    assert s.period_index(np.array([D0 * DAY]), 'prior_week')[0] + 1 == s.period_index(np.array([(D0 + 3) * DAY]), 'prior_week')[0]
    assert s.period_start_ms(s.period_index(np.array([D0 * DAY]), 'prior_week')[0], 'prior_week') == (D0 - 4) * DAY   # Monday 2022-03-28


def _five(day, ohlc):
    """5m bars (t, o, h, l, c) for one day from a list of (o, h, l, c); the rest of the day repeats the last bar."""
    rows = list(ohlc) + [ohlc[-1]] * (288 - len(ohlc))
    t = day * DAY + np.arange(288) * 5 * MIN
    return np.column_stack([t, np.asarray(rows, float)])


PROF = {D0 - 1: {'poc_price': 105.0, 'vah': 110.0, 'val': 100.0}}
SERIES = [(104, 106, 103, 105), (105, 111, 104, 109),   # bar 1: touches VAH from inside, closes back in -> FADE short
          (109, 112, 108, 112),                         # bar 2: first close above VAH -> RETURN short
          (112, 113, 111, 113), (113, 114, 112, 114),   # bar 4: third consecutive close outside -> ACCEPT n3 long
          (114, 115, 109, 109), (109, 110, 99, 99),     # bar 6: first close below VAL -> RETURN long; touches VAH but closes outside value: no FADE
          (99, 101, 98, 98), (98, 99, 97, 97)]


def test_three_ideas_fire_where_the_concept_check_says():
    s = study()
    a5 = _five(D0, SERIES)
    ret = s.signals(a5, PROF, 'prior_day', 'RETURN', 6, 'OFF')
    assert [(x['i'], x['side'], x['level']) for x in ret] == [(2, -1, 110.0), (6, 1, 100.0)]
    fade = s.signals(a5, PROF, 'prior_day', 'FADE', 6, 'OFF')
    assert [(x['i'], x['side'], x['level']) for x in fade] == [(1, -1, 110.0)]
    acc = s.signals(a5, PROF, 'prior_day', 'ACCEPT', 3, 'OFF')
    assert [(x['i'], x['side']) for x in acc] == [(4, 1), (8, -1)]
    assert s.signals(a5, {}, 'prior_day', 'RETURN', 6, 'OFF') == []          # no profile for yesterday: nothing fires


def test_migration_filter_skips_the_trade_against_the_shift():
    s = study()
    a5 = _five(D0, SERIES)
    up = {**PROF, D0 - 2: {'poc_price': 90.0, 'vah': 95.0, 'val': 85.0}}            # yesterday's value entirely above the day before's
    assert s.migration(up, D0) == 1 and s.migration(PROF, D0) == 0
    ret = s.signals(a5, up, 'prior_day', 'RETURN', 6, 'WITH')
    assert [(x['i'], x['side']) for x in ret] == [(6, 1)]                            # the short against the up-shift is skipped
    acc = s.signals(a5, up, 'prior_day', 'ACCEPT', 3, 'WITH')
    assert [(x['i'], x['side']) for x in acc] == [(4, 1)]


def test_acceptance_exit_and_planted_leak():
    s = study()
    a5 = _five(D0, SERIES)
    # RETURN short from bar 2 against VAH 110: closes 113, 114 are outside -> n=2 exits at the open after bar 4
    assert s.accept_exit(a5, 2, -1, 110.0, 100.0, 2) == int(a5[5, 0])
    assert s.accept_exit(a5, 2, -1, 110.0, 100.0, 0) is None
    assert s.accept_exit(a5, 2, -1, 110.0, 100.0, 3) is None                         # the run breaks at bar 5 (close 109)
    base = s.signals(a5, PROF, 'prior_day', 'RETURN', 6, 'OFF')
    junk = a5.copy()
    junk[4:, 1:] = 1e6
    cut = s.signals(junk, PROF, 'prior_day', 'RETURN', 6, 'OFF')
    assert [x for x in cut if x['i'] <= 3] == [x for x in base if x['i'] <= 3]


def test_hand_checked_fee_net_trade():
    """RETURN short at 112 after bar 2; ATR 2 -> stop 114, target POC 105. Fill at the open of bar 3 (112); the stop 114
    is hit on bar 4 (high 114): gross -1 R, fees (0.07 % x 112 + 0.07 % x 114) / 2 = 0.0791 R, net -1.0791 R."""
    s = study()
    q = s.normalize({'stop_atr': 1.0, 'maker_pct': 0.02, 'taker_pct': 0.05, 'slip_pct': 0.02})
    a5 = _five(D0, SERIES)
    minute = np.repeat(a5, 5, axis=0)
    minute[:, 0] = D0 * DAY + np.arange(len(minute)) * MIN
    sig = {'i': 2, 'side': -1, 'level': 110.0, 'poc': 105.0, 'vah': 110.0, 'val': 100.0, 'p': D0}

    def make(sg):
        close = float(a5[sg['i'], 4]); t0 = int(a5[sg['i'], 0]) + 5 * MIN
        return [-1, t0, None, close + 2.0, 105.0, t0 + 5 * MIN, None, (D0 + 1) * DAY, 110.0]
    res = _bars.collect([sig], minute, q, make)
    assert res['filled'].tolist() == [True] and res['exit'].tolist() == ['STOP']
    assert res['gross'][0] == pytest.approx(-1.0) and res['net'][0] == pytest.approx(-1.0791, abs=1e-4)


@pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on disk')
def test_dev_run_writes_ledger_row(tmp_path):
    s = study()
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    r = desk.run_setting(s, {'start': '2023-01-01', 'end': '2023-03-31'}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert r['n'] > 20 and r['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA')
    assert '| sim-desk tom_vp prior_day RETURN n6' in trials.read_text(encoding='utf-8')
    for t in r['trades']['t']:
        assert 1672531200000 <= t < 1680307200000          # every filled trade inside the chosen dates
