"""RSI (Malkan 40/60) and WaveTrend (LazyBear cross) studies on the desk. Hand-computed trade numbers for the shared
1m trade simulator; data tests run only when the 1m bars are on this machine."""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402
from studies import _bars  # noqa: E402

TAKER, MAKER = 0.0005, 0.0002


def flat(n=100):
    a = np.zeros((n, 5))
    a[:, 0] = np.arange(n) * 60000.
    a[:, 1:] = 100.
    return a


def run(a, side=1, trig=101., stop=99., target=105., window=50, t_exit=None, hold=90):
    return _bars.run_trade(a, side, 0, trig, stop, target, window * 60000, t_exit, hold * 60000, TAKER, MAKER)


def test_long_breakout_fill_then_target():
    a = flat()
    a[3, 2] = 101.5
    a[10, 2] = 105.2
    r = run(a)
    assert r['filled'] and r['entry'] == (180000, 101.)
    assert r['exit'][1:] == (105., 'T1')
    assert r['net_r'] == pytest.approx(2 - .0005 * 101 / 2 - .0002 * 105 / 2)      # 1.96425


def test_long_stop_and_gap_through_stop():
    a = flat()
    a[3, 2] = 101.5
    a[5, 3] = 98.5
    assert run(a)['net_r'] == pytest.approx(-1 - .0005 * 101 / 2 - .0005 * 99 / 2)  # -1.05
    a[5, 1], a[5, 3] = 98., 97.9                                                   # opens below the stop
    r = run(a)
    assert r['exit'][1] == 98. and r['net_r'] == pytest.approx(-1.5 - .0005 * 101 / 2 - .0005 * 98 / 2)


def test_same_bar_stop_and_target_counts_the_stop():
    a = flat()
    a[3, 2] = 101.5
    a[6, 2], a[6, 3] = 106., 98.
    assert run(a)['exit'][2] == 'STOP'


def test_no_fill_when_trigger_never_reached_in_window():
    a = flat()
    a[60, 2] = 102.                     # after the window
    r = run(a)
    assert r['filled'] is False and r['net_r'] == 0.


def test_indicator_exit_at_bar_close_and_open_at_end_dropped():
    a = flat()
    a[3, 2] = 101.5
    a[19, 4] = 102.
    r = run(a, t_exit=20 * 60000)
    assert r['exit'] == (19 * 60000, 102., 'SIGNAL')
    assert r['net_r'] == pytest.approx(.5 - .0005 * 101 / 2 - .0005 * 102 / 2)     # 0.44975
    assert run(a, hold=500) is None                                                # never resolved inside the data


def test_short_mirror_and_market_entry():
    a = flat()
    a[3, 3] = 98.9
    a[8, 3] = 94.9
    r = run(a, side=-1, trig=99., stop=101., target=95.)
    assert r['entry'][1] == 99. and r['net_r'] == pytest.approx(2 - .0005 * 99 / 2 - .0002 * 95 / 2)
    m = run(flat(), side=1, trig=None, stop=99., target=None, t_exit=30 * 60000)
    assert m['entry'] == (0, 100.) and m['exit'][2] == 'SIGNAL'


def test_resample_hour_bars():
    a = flat(180)
    a[:, 1:] = np.arange(180)[:, None] + np.array([0., 1., -1., .5])
    h = _bars.resample(a, 60)
    assert h.shape == (3, 5)
    assert list(h[1]) == [3600000., 60., 120., 59., 119.5]


def test_rsi_and_wavetrend_found_and_labelled():
    found = desk.load_studies()
    assert {'levels', 'rsi', 'wavetrend'} <= set(found)
    for sid in ('rsi', 'wavetrend'):
        s = found[sid]
        for f in s.params():
            if f.get('date'):
                continue
            texts = list(f['choices'].values()) if f.get('choices') else [f['label']]
            for t in texts:
                assert '(trader' in t or '(ours' in t or 'fee' in t.lower(), (sid, t)
        with pytest.raises(ValueError):
            s.normalize({'end': '2024-07-01'})


needs_data = pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on this machine')


@needs_data
@pytest.mark.parametrize('sid,p,min_n', [('rsi', {}, 1), ('rsi', {'tf': '1h'}, 20), ('wavetrend', {}, 20)])
def test_run_end_to_end(sid, p, min_n, tmp_path):
    s = desk.load_studies()[sid]
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    out = desk.run_setting(s, p, trials_path=trials, cache_dir=tmp_path / 'c', charts=True)
    assert out['n'] >= min_n and out['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA')
    assert f'| sim-desk {sid} ' in trials.read_text(encoding='utf-8')
    assert 1 <= len(out['charts']) <= 6
    q = s.normalize(p)
    for c in out['charts']:
        tr = s.chart_trade(c['ref'], q)
        assert tr['stop'] == c['ref'][3] and 'UTC' in c['svg'] and len(c['svg'].encode()) < 10240


@pytest.mark.parametrize('sid', ['rsi', 'wavetrend'])
def test_symbol_box(sid):
    s = desk.load_studies()[sid]
    assert s.params()[0]['name'] == 'symbol' and set(s.params()[0]['choices']) == {'BTCUSDT', 'ETHUSDT'}
    assert s.normalize({})['symbol'] == 'BTCUSDT' and 'ETH' not in s.label(s.normalize({}))   # BTC ledger names unchanged
    assert 'ETHUSDT' in s.label(s.normalize({'symbol': 'ETHUSDT'})) and 'ETH' in s.describe(s.normalize({'symbol': 'ETHUSDT'}))
    with pytest.raises(ValueError):
        s.normalize({'symbol': 'DOGEUSDT'})


@pytest.mark.skipif(not _bars.data_ready('ETHUSDT'), reason='ETH 1m bars not on this machine')
def test_eth_bars_are_eth_and_stay_inside_dev():
    a, b = _bars.load_1m(symbol='ETHUSDT'), _bars.load_1m(symbol='BTCUSDT')
    assert 500 < a[:, 4].mean() < 5000 < b[:, 4].mean() and a[-1, 0] < _bars.day_ms('2024-07-01')


@pytest.mark.skipif(not _bars.data_ready('ETHUSDT'), reason='ETH 1m bars not on this machine')
def test_eth_run_end_to_end(tmp_path):
    s = desk.load_studies()['rsi']
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    out = desk.run_setting(s, {'symbol': 'ETHUSDT', 'tf': '1h'}, trials_path=trials, cache_dir=tmp_path / 'c')
    assert out['n'] >= 20 and 'ETH' in out['describe'] and 'ETHUSDT' in trials.read_text(encoding='utf-8')
