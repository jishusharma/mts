"""Conditions panel tests. Expected keep-masks are worked out by hand from the stated bars and times (calendar via
datetime, EMA/ATR by the textbook formulas on tiny series), never from conditions.py."""
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conditions as cd  # noqa: E402
import desk  # noqa: E402
from studies import _bars  # noqa: E402

H = 3_600_000
DAY = 86_400_000
MIN = 60_000


def ms(y, mo, d, h=0, mi=0):
    return int(dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone.utc).timestamp() * 1000)


def keep(c, t, side=None, **kw):
    t = np.asarray(t, np.int64)
    return cd.mask(cd.normalize(c), t, np.ones(len(t), int) if side is None else side, resample=_bars.resample, **kw).tolist()


def test_hour_window_and_wrap():
    t = [ms(2023, 5, 1, 3), ms(2023, 5, 1, 9), ms(2023, 5, 1, 16), ms(2023, 5, 1, 23)]
    assert keep({'hour_from': 8, 'hour_to': 16}, t) == [False, True, False, False]       # 16 is excluded
    assert keep({'hour_from': 22, 'hour_to': 4}, t) == [True, False, False, True]        # wraps midnight


def test_weekday_filter():
    # 2023-05-01 Monday, 05-03 Wednesday, 05-06 Saturday
    t = [ms(2023, 5, 1, 12), ms(2023, 5, 3, 12), ms(2023, 5, 6, 12)]
    assert dt.date(2023, 5, 1).weekday() == 0
    assert keep({'days': 'mon,sat'}, t) == [True, False, True]
    assert keep({'days': '2'}, t) == [False, True, False]


def test_side_filter():
    t = [1, 2, 3]
    assert keep({'side': 'long'}, t, side=np.array([1, -1, 1])) == [True, False, True]
    assert keep({'side': 'short'}, t, side=np.array([1, -1, 1])) == [False, True, False]


def _hourly(closes, start=ms(2023, 1, 1)):
    """1m bars whose every minute of hour k has close closes[k] (flat), so 60m bars have close = closes[k]."""
    rows = []
    for k, c in enumerate(closes):
        for m in range(60):
            rows.append([start + k * H + m * MIN, c, c, c, c])
    return np.array(rows, float)


def test_ema_trend_is_causal_and_by_hand():
    # hourly closes 10,10,10,10,20 ; EMA3 (alpha .5, seeded 10): 10,10,10,10,15 -> close 20 > 15 on the last bar
    closes = [10, 10, 10, 10, 20, 20, 20, 5]
    a = _hourly(closes)
    s = ms(2023, 1, 1)
    t_after_5th = s + 5 * H            # bar 4 (close 20) just closed: 20 > EMA 15 -> above
    t_inside_bar7 = s + 7 * H + 30 * MIN   # bar 7 (close 5) still open: last closed is bar 6, close 20
    c = {'ema_rel': 'above', 'ema_tf': 60, 'ema_len': 3}
    assert keep(c, [t_after_5th], minute_bars=a) == [True]
    assert keep({**c, 'ema_rel': 'below'}, [t_after_5th], minute_bars=a) == [False]
    assert keep(c, [t_inside_bar7], minute_bars=a) == [True]        # the open bar's crash is not used
    assert keep(c, [s + 2 * H], minute_bars=a) == [False]            # warm-up: fewer bars than the EMA length


def test_atr_percentile_by_hand():
    # hourly bars: ranges 1,1,1,1,1,1 then 5. ATR2 of last two true ranges (flat close so TR = high-low)
    rows = []
    s = ms(2023, 1, 1)
    for k, rg in enumerate([1, 1, 1, 1, 1, 1, 5, 1]):
        for m in range(60):
            lo, hi = 100.0, 100.0 + (rg if m == 0 else 0)
            rows.append([s + k * H + m * MIN, 100.0, hi, lo, 100.0])
    a = np.array(rows)
    c = {'atr_lo': 90, 'atr_hi': 100, 'atr_tf': 60, 'atr_len': 2, 'atr_win': 20}
    # after bar 6 closes: ATR2 = (1+5)/2 = 3, window ATRs (bars 1..6) = 1,1,1,1,1,3 -> 100th percentile
    assert keep(c, [s + 7 * H], minute_bars=a) == [True]
    # after bar 3 closes: ATR2 = 1; window (bars 1..3) = 1,1,1 -> all <= 1 -> 100th too; so test the LOW band on bar 7 end
    low = {**c, 'atr_lo': 0, 'atr_hi': 50}
    assert keep(low, [s + 7 * H], minute_bars=a) == [False]
    # after bar 7 closes: ATR2 = (5+1)/2 = 3 still; but at bar 8 boundary ATR2 stays high vs history -> top band
    assert keep(c, [s + 8 * H], minute_bars=a) == [True]


def test_layer_b_within_n_bars():
    b = [ms(2023, 1, 1, 10)]
    t = [ms(2023, 1, 1, 9), ms(2023, 1, 1, 11), ms(2023, 1, 1, 13), ms(2023, 1, 1, 10)]
    c = {'layer_b': 'rsi', 'layer_b_bars': 2, 'layer_b_tf': 60}
    # B fired at 10:00. window = (touch-2h, touch]: 09:00 no (B is later); 11:00 yes; 13:00 no (3 h); 10:00 yes (equal)
    assert keep(c, t, b_times=b) == [False, True, False, True]


def test_normalize_validates_and_labels():
    assert cd.normalize({}) == {} and cd.normalize(None) == {} and cd.normalize({'side': 'both'}) == {}
    n = cd.normalize({'side': 'long', 'hour_from': '8', 'hour_to': 16, 'days': 'Mon, tue'})
    assert n == {'side': 'long', 'hour_from': 8, 'hour_to': 16, 'days': 'mon,tue'}
    assert 'long only' in cd.label(n) and 'UTC 8-16' in cd.label(n)
    for bad in ({'side': 'up'}, {'hour_from': 8}, {'hour_from': 30, 'hour_to': 2}, {'days': 'funday'},
                {'ema_rel': 'above', 'ema_len': 1}, {'atr_lo': 80, 'atr_hi': 20}, {'atr_lo': 'x'}):
        with pytest.raises(ValueError):
            cd.normalize(bad)


class SideStudy:
    ID = 'sidefake'
    calls = 0

    @staticmethod
    def normalize(p):
        return {'x': float(p.get('x', 1)), 'start': '2022-04-01', 'end': '2024-06-30'}

    @staticmethod
    def label(p):
        return f"x {p['x']}"

    @staticmethod
    def describe(p):
        return 'fake'

    @classmethod
    def run(cls, p, progress=None):
        cls.calls += 1
        rng = np.random.default_rng(2)
        n = 400
        days = np.repeat(np.arange(19100, 19100 + 100), 4)
        net = rng.normal(-0.1, 1, n)
        touch = days * DAY + (np.arange(n) % 4) * 6 * H            # hours 0, 6, 12, 18
        return {'day': days, 'touch_t': touch, 'side': np.where(np.arange(n) % 2 == 0, 1, -1), 'net': net, 'gross': net + .1,
                'fees': np.full(n, .1), 'all_days': np.arange(19100, 19200), 'refs': list(range(n)),
                'filled': np.ones(n, bool)}


def test_run_setting_with_conditions_ledger_and_cache(tmp_path):
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    kw = dict(trials_path=trials, cache_dir=tmp_path / 'c')
    base = desk.run_setting(SideStudy, {}, **kw)
    assert base['n'] == 400 and SideStudy.calls == 1
    c = {'side': 'long', 'hour_from': 6, 'hour_to': 19}          # even index = long; hours 6,12,18 -> idx%4 in 1,2,3 and even -> 2 only
    r = desk.run_setting(SideStudy, {}, cond=c, **kw)
    assert r['n'] == 100 and r['n_before_cond'] == 400           # idx%4==2 -> 100 trades
    assert r['cond'] == cd.normalize(c) and 'long only' in r['cond_label']
    assert SideStudy.calls == 1                                  # conditions reuse the cached run
    lines = [ln for ln in trials.read_text(encoding='utf-8').split('\n') if '| sim-desk sidefake ' in ln]
    assert len(lines) == 2 and 'long only' in lines[1] and 'long only' not in lines[0]
    r2 = desk.run_setting(SideStudy, {}, cond=c, **kw)           # same condition again: no new row
    assert r2['already_tried'] and len([ln for ln in trials.read_text(encoding='utf-8').split('\n') if '| sim-desk sidefake ' in ln]) == 2
    desk.run_setting(SideStudy, {}, cond={'side': 'short'}, **kw)
    assert len([ln for ln in trials.read_text(encoding='utf-8').split('\n') if '| sim-desk sidefake ' in ln]) == 3


def test_apply_keeps_arrays_and_refs_aligned():
    res = SideStudy.run({})
    k = cd.mask(cd.normalize({'side': 'short'}), res['touch_t'], res['side'])
    out = cd.apply(res, k)
    assert len(out['net']) == len(out['refs']) == 200 and set(out['side'].tolist()) == {-1}
    assert out['refs'] == [r for r in range(400) if r % 2 == 1]
    assert len(out['all_days']) == 100


def test_run_time_is_reported_and_cached_run_is_fast(tmp_path):
    """Step (c): every Run reports run_seconds; a cached Run is far under the 10 s budget."""
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    kw = dict(trials_path=trials, cache_dir=tmp_path / 'c')
    SideStudy.calls = 0
    a = desk.run_setting(SideStudy, {'x': 3}, **kw)
    b = desk.run_setting(SideStudy, {'x': 3}, **kw)
    assert a['run_seconds'] >= 0 and not a['cached']
    assert b['cached'] and b['run_seconds'] < 10 and SideStudy.calls == 1
    assert 'run_seconds' in (HERE / 'page.html').read_text(encoding='utf-8')


def test_equity_curve_filled_only_in_time_order():
    """Step (d): hand-worked: filled nets in time order 1.0, -0.5, 2.0 (the never-filled 0.0 and the early-filed order are handled)."""
    res = {'net': [-0.5, 0.0, 1.0, 2.0], 'touch_t': [20, 15, 10, 30], 'filled': [True, False, True, True]}
    c = desk.curve(res)
    assert c['n'] == 3 and c['idx'] == [1, 2, 3] and c['t'] == [10, 20, 30]
    assert c['r'] == [1.0, 0.5, 2.5]
    assert c['usd'] == [1010.0, 1005.0, 1025.0]          # 1,000 USD, 1 % risk per R, simple sum


def test_equity_curve_downsamples_and_keeps_last_point():
    n = 2000
    res = {'net': [0.1] * n, 'touch_t': list(range(n)), 'filled': [True] * n}
    c = desk.curve(res, points=100)
    assert len(c['idx']) <= 101 and c['idx'][-1] == n and c['r'][-1] == pytest.approx(200.0)


def test_page_has_equity_and_compare():
    h = (HERE / 'page.html').read_text(encoding='utf-8')
    for need in ('id="eqscrub"', 'Keep this run as A', 'id="equnit"', 'worst drawdown', 'drawdown shaded'):
        assert need in h


def test_export_result_standard_schema_and_page_builds(tmp_path):
    """Step (e): a Run's result file is in the standard schema and the static builder turns it into a test."""
    sys.path.insert(0, str(HERE / 'artifact'))
    import build_artifact as ba
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    SideStudy.TITLE = 'Side fake'
    out = desk.run_setting(SideStudy, {}, trials_path=trials, cache_dir=tmp_path / 'c', cond={'side': 'long'})
    rid = desk.export_result(out, SideStudy, tmp_path / 'res')
    assert rid.startswith('desk-sidefake-') and (tmp_path / 'res' / (rid + '.json')).exists()
    assert desk.export_result(out, SideStudy, tmp_path / 'res') == rid            # same run -> same file
    tests = ba.collect(str(tmp_path / 'res'))
    assert [t['id'] for t in tests] == [rid]
    t = tests[0]
    assert t['examples'][0]['kind'] == 'curve' and len(t['examples'][0]['r']) == out['n']
    assert 'long only' in t['title'] and t['verdict']['label'] == out['verdict']
    assert all(w['label'] in ('SOURCED', 'OURS') for w in t['what'])
    ba.main(['--results', str(tmp_path / 'res'), '--out', str(tmp_path / 'i.html')])
    assert 'curveEx' in (tmp_path / 'i.html').read_text(encoding='utf-8')


def test_numbers_strip_by_hand():
    """Filled nets in time order 2.0, -1.0, -1.0, 1.0 (+ one never-filled 0.0): wins 3.0, losses 2.0 -> PF 1.5;
    running 2,1,0,1 -> peak 2, trough 0 -> max drawdown 2.0 R; win rate 2/4; fees 0.1 each; gross = net + 0.1."""
    res = {'net': [-1.0, 0.0, 2.0, 1.0, -1.0], 'touch_t': [3, 9, 1, 4, 2], 'filled': [True, False, True, True, True],
           'gross': [-0.9, 0.0, 2.1, 1.1, -0.9], 'fees': [0.1, 0.0, 0.1, 0.1, 0.1]}
    k = desk.numbers(res)
    assert k['n'] == 4 and k['win_rate'] == 0.5 and k['profit_factor'] == pytest.approx(1.5)
    assert k['max_dd_r'] == pytest.approx(2.0) and k['mean_net'] == pytest.approx(0.25)
    assert k['mean_gross'] == pytest.approx(0.35) and k['mean_fee'] == pytest.approx(0.1)
    assert desk.numbers({'net': [], 'touch_t': [], 'filled': []}) == {'n': 0}
