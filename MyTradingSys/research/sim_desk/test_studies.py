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


def test_resample_gapped_minutes():
    # hand-worked: hour 0 has only minutes 5, 20, 50; hour 1 only minute 61; hour 2 absent; hour 3 only minute 180
    M = 60000
    a = np.array([[5 * M, 10, 12, 9, 11], [20 * M, 11, 15, 8, 14], [50 * M, 14, 13, 10, 12],
                  [61 * M, 20, 21, 19, 20], [180 * M, 30, 31, 29, 30.5]])
    h = _bars.resample(a, 60)
    assert h.shape == (3, 5)
    assert list(h[0]) == [0., 10., 15., 8., 12.]           # open of first, max high, min low, close of last present minute
    assert list(h[1]) == [3600000., 20., 21., 19., 20.]
    assert list(h[2]) == [3 * 3600000., 30., 31., 29., 30.5]   # empty hour 2 is not invented


def test_resample_empty_input():
    h = _bars.resample(np.zeros((0, 5)), 60)
    assert h.shape == (0, 5)


def test_levels_rejects_other_symbol():
    # levels has no coin choice (BTC data only); a non-BTC symbol must be refused, never silently run on BTC
    lv = desk.load_studies()['levels']
    with pytest.raises(ValueError, match='symbol'):
        lv.normalize({'symbol': 'ETHUSDT'})
    with pytest.raises(ValueError, match='symbol'):
        lv.normalize({'symbol': 'DOGEUSDT'})
    assert lv.normalize({'symbol': 'BTCUSDT'}) == lv.normalize({})
    assert lv.normalize({'symbol': ''}) == lv.normalize({})


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


# ---- 11-09 census page rows (card sim-desk-edge-hunt-census-1109): numbers hand-read from the RESULT files, never recomputed ----
import json  # noqa: E402
import census_1109 as c9  # noqa: E402

RES = HERE / 'results' / '_census_1109.json'
EXPECT = {  # id: (chip, n, mean net R)
    'census-5m-15m-session-ladder': ('FAIL', 698, -0.372), 'eh-h1-T01': ('FAIL', 108, -0.217),
    'eh-h2-T02': ('INCONCLUSIVE', 7, 1.06), 'eh-h2-T03': ('INCONCLUSIVE', 8, 0.07), 'eh-h3-T04': ('FAIL', 1150, -0.221),
    'eh-h4-T05': ('FAIL', 300, -0.086), 'eh-h5-T06': ('INCONCLUSIVE', 1322, 0.048), 'eh-s2-T09': ('FAIL', 41, -0.581),
    'eh-s2-T10': ('FAIL', 47, -0.804), 'eh-s3-T11': ('FAIL', 1588, -0.146), 'eh-s3-T12': ('FAIL', 1477, -0.133),
    'malkan-level-short-best-arm': ('INCONCLUSIVE', 126, 0.10), 'malkan-level-short-full-stack': ('INCONCLUSIVE', 37, 0.13)}


def test_census_rows_cover_every_1109_study_with_chip_n_mean():
    d = c9.build_rows()
    rows = {r['id']: r for r in d['rows']}
    assert set(EXPECT) | {'malkan-operator-5-points'} == set(rows)
    for rid, (chip, n, mean) in EXPECT.items():
        r = rows[rid]
        assert (r['chip'], r['n']) == (chip, n) and r['mean_net_r'] == pytest.approx(mean), rid
        assert r['tone'] == {'FAIL': 'bad', 'INCONCLUSIVE': 'warn', 'PASS': 'good'}[chip]
    assert len(rows['census-5m-15m-session-ladder']['cells']) == 10


def test_census_why_is_a_quote_from_the_result_file():
    for r in c9.build_rows()['rows']:
        assert r['why'] and r['why_src'] and r['why_quote'], r['id']
        assert r['why_quote'] in (c9.RESEARCH / r['why_src']).read_text(encoding='utf-8'), r['id']


def test_census_says_when_a_study_saved_no_per_trade_file():
    rows = {r['id']: r for r in c9.build_rows()['rows']}
    assert rows['eh-h3-T04']['per_trade']['status'] == 'not_saved' and 'not saved' in rows['eh-h3-T04']['per_trade']['note']
    h2 = rows['eh-h2-T02']
    assert h2['per_trade']['status'] == 'file' and len(h2['trades']) == 7 and sum(1 for t in h2['trades'] if t['r'] > 0) == 4
    assert len(rows['eh-h2-T03']['trades']) == 8 and rows['eh-h2-T03']['trades'][2]['r'] == pytest.approx(1.9478)


def test_malkan_operator_five_points_are_own_row_with_five_trades():
    r = {r['id']: r for r in c9.build_rows()['rows']}['malkan-operator-5-points']
    assert [t['name'] for t in r['trades']] == ['C1', 'C2', 'V1', 'V2', 'C3']
    c1 = r['trades'][0]
    assert c1['side'] == 'short' and c1['stop_pct'] == pytest.approx(2.385, abs=0.001) and c1['best_pct'] == pytest.approx(4.3)
    assert c1['exit_note'].startswith('stop hit 09-03') and r['chip'] == 'INCONCLUSIVE'


def test_check_next_is_at_most_five_ideas_each_quoted_from_its_file():
    ck = c9.build_rows()['check_next']
    assert 1 <= len(ck) <= 5
    for c in ck:
        assert c['idea'] and c['quote'] in (c9.RESEARCH / c['file']).read_text(encoding='utf-8'), c


def test_committed_census_file_has_candles_for_all_five_malkan_trades():
    d = json.loads(RES.read_text(encoding='utf-8'))
    tr = {r['id']: r for r in d['rows']}['malkan-operator-5-points']['trades']
    assert len(tr) == 5
    for t in tr:
        assert len(t['c']) >= 20 and 0 <= t['entry_i'] < len(t['c']) and t['stop_pct'] > 0 and t['best_pct'] > 0, t['name']
        assert all(len(k) == 4 for k in t['c'])
    assert tr[0]['exit_i'] is not None and tr[0]['exit_t'].startswith('2026-09-03')
    assert d['rows'] == c9.with_candles(c9.build_rows(), d)['rows']      # the committed file is the builder output, not hand-edited


def test_page_gets_the_census_tab_and_data():
    sys.path.insert(0, str(HERE / 'artifact'))
    import build_artifact as ba
    html = ba.render(ba.collect(str(HERE / 'results')), None)
    assert '"census-5m-15m-session-ladder"' in html and '"malkan-operator-5-points"' in html
    assert '"c1109"' in html and 'function c1109Tab' in html
