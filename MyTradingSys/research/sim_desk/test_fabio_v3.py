"""Fabio v3 price-only study on the desk (research/sim_desk/studies/fabio_v3.py) and the exported trade charts of both new studies.

Expected numbers are worked by hand below (stop, target, fees), not taken from the study. Verifies: plug-in labelling and date lock; Model C and
Model B each fire on a hand-built NY window exactly once and the trade is scored with a real stop or target (Model B is NOT 0 R); causality
(bars after the decision bar change nothing); the exported result files carry the 3 winners + 3 losers charts with no raw prices.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import charts  # noqa: E402
import desk  # noqa: E402
from studies import _bars  # noqa: E402

MIN, DAY = _bars.MIN, _bars.DAY
OPEN_MS = int(dt.datetime(2022, 4, 4, 13, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)   # a Monday inside US DST: NY open 13:30 UTC


def study():
    found = desk.load_studies()
    assert 'fabio_v3' in found
    return found['fabio_v3']


def test_plugged_in_labelled_and_date_locked():
    s = study()
    assert s.ID == 'fabio_v3' and 'price-only' in s.TITLE
    for f in s.params():
        if f.get('date'):
            continue
        for t in (list(f['choices'].values()) if f.get('choices') else [f['label']]):
            assert '(trader' in t or '(ours' in t or 'fee' in t.lower() or f['name'] == 'model' or 'Model' in t, t
    for bad in ({'end': '2024-07-01'}, {'start': '2022-03-31'}, {'model': 'A'}, {'model': 'D'}, {'n_bal': 100}, {'m': 10}, {'push': 'DELTA'}, {'f_pct': 'x'}):
        with pytest.raises(ValueError):
            s.normalize(bad)
    q = s.normalize({})
    assert q['model'] == 'C' and q['target_r'] is None and q['n_bal'] == 120
    d = s.describe(q)
    for word in ('price-only', 'development window only', 'Models A and D'):
        assert word in d, word
    assert 'C m15 push OFF' in s.label(q)


def _window(rows, pre=0):
    """1m bars (t, o, h, l, c, volume): `pre` flat-minute rows before the NY open, then the rows given, then flat to fill 390 minutes + 30 spare."""
    out = []
    n = max(len(rows), 420)
    last = rows[-1]
    full = list(rows) + [(last[3], last[3], last[3], last[3])] * (n - len(rows))
    for k in range(-pre, n):
        o, h, l, c = full[k] if k >= 0 else rows[0]
        out.append((OPEN_MS + k * MIN, o, h, l, c, 1.0))
    return np.array(out, float)


def _patch(monkeypatch, s, arr):
    monkeypatch.setattr(s._bars, 'load_1m', lambda *a, **k: arr[:, :5])
    monkeypatch.setattr(s._volume(), 'load_1m_vol', lambda *a, **k: arr)
    s._IDEAS.clear()


def _c_rows():
    rows = [(1005, 1006, 1004, 1005)] * 30
    rows[3] = (1005, 1010, 1004, 1005)             # IB high 1010
    rows[5] = (1005, 1006, 1000, 1005)             # IB low 1000 -> middle 1005
    rows += [(1005, 1012.5, 1005, 1012),           # bar 30: first close above 1010 -> long
             (1012, 1013, 1006, 1010),             # bar 31: entry at its open 1012
             (1010, 1010.5, 1004, 1004.5)]         # bar 32: low 1004 <= stop
    return rows


def test_model_c_hand_checked_stop_trade(monkeypatch):
    """IB 1000..1010, mid 1005. Close 1012 at bar 30 -> long at the next open 1012. Structural stop = 1012 - 1005 + 0.1 = 7.1 (floor 0.5 % = 5.06, smaller),
    stop 1004.9; bar 32 low 1004 hits it, bar open 1010 is above the stop so the fill is the stop. gross = (1004.9 - 1012) / 7.1 = -1 R.
    fees = 0.07 % x (1012 + 1004.9) / 7.1 = 0.198847 R (taker 0.05 % + 0.02 % slippage on both legs). net = -1.198847 R."""
    s = study()
    _patch(monkeypatch, s, _window(_c_rows()))
    q = s.normalize({'start': '2022-04-04', 'end': '2022-04-04'})
    res = s.run(q, lambda m: None)
    assert res['filled'].tolist() == [True] and res['exit'].tolist() == ['STOP'] and res['side'].tolist() == [1]
    assert res['gross'][0] == pytest.approx(-1.0) and res['net'][0] == pytest.approx(-1.198847, abs=1e-5)
    assert res['touch_t'][0] == OPEN_MS + 31 * MIN
    tr = s.chart_trade(res['refs'][0], q)
    assert tr['side'] == 1 and tr['stop'] == pytest.approx(1004.9) and tr['target'] is None and 'Model C' in tr['note']
    assert tr['exits'][0][2] == 'STOP' and tr['entries'][0][1] == 1012


def test_model_c_one_try_per_day_and_floor_drops_wide_stops(monkeypatch):
    s = study()
    _patch(monkeypatch, s, _window(_c_rows()))
    # a 0.1 % floor changes nothing here (structural 7.1 is wider); a Dmax breach (stop wider than 1 % of entry) drops the idea: no trade at all
    rows = _c_rows()
    rows[30] = (1005, 1030.5, 1005, 1030)          # close 1030, next open 1030: structural 25.1 > 1 % x 1030 = 10.3
    rows[31] = (1030, 1031, 1024, 1028)
    _patch(monkeypatch, s, _window(rows))
    q = s.normalize({'start': '2022-04-04', 'end': '2022-04-04'})
    assert len(s.run(q, lambda m: None)['filled']) == 0


def test_model_c_candle_push_stand_in(monkeypatch):
    s = study()
    rows = _c_rows()
    _patch(monkeypatch, s, _window(rows))
    q = s.normalize({'push': 'CANDLES', 'm': 5, 'start': '2022-04-04', 'end': '2022-04-04'})
    assert len(s.run(q, lambda m: None)['filled']) == 1          # bars 26-30: four flat candles and one up candle: net +1 > 0, the push passes
    rows2 = list(rows)
    for k in (27, 28, 29):
        rows2[k] = (1005, 1006, 1004, 1004.5)       # three down candles before the breakout bar
    _patch(monkeypatch, s, _window(rows2))
    assert len(s.run(q, lambda m: None)['filled']) == 0


def _b_window():
    pre = [(1025, 1026, 1024, 1025)] * 62
    day = [(1025, 1026, 1024, 1025)] * 10
    day += [(1025, 1028, 1025, 1027),               # bar 10: close 1027 > H 1026 = probe, extreme 1028
            (1027, 1027, 1025, 1025.5),             # bar 11: close back inside = reclaim -> short
            (1025.5, 1026, 1025, 1025.5),           # bar 12: entry at its open 1025.5
            (1025, 1025.2, 1023.9, 1024.5)]         # bar 13: low 1023.9 <= target 1024 (the box low)
    out = []
    for k, (o, h, l, c) in enumerate(pre + day + [(1024.5, 1025, 1024, 1024.5)] * (420 - len(day))):
        out.append((OPEN_MS + (k - len(pre)) * MIN, o, h, l, c, 1.0))
    return np.array(out, float)


def test_model_b_is_scored_with_a_real_target_not_zero(monkeypatch):
    """Box 1024..1026 (60-candle window). Probe close 1027, reclaim close 1025.5 -> short at the next open 1025.5. Structural = |1028 - 1025.5| + 0.1 = 2.6,
    floor 0.5 % x 1025.5 = 5.1275 is wider -> D 5.1275, stop 1030.6275, target the low edge 1024. Bar 13 low 1023.9 hits it (limit, maker 0.02 %).
    gross = (1025.5 - 1024) / 5.1275 = 0.292540; fees = (0.0007 x 1025.5 + 0.0002 x 1024) / 5.1275 = 0.179942; net = +0.112598 R."""
    s = study()
    _patch(monkeypatch, s, _b_window())
    q = s.normalize({'model': 'B', 'n_bal': 60, 'start': '2022-04-04', 'end': '2022-04-04'})
    res = s.run(q, lambda m: None)
    assert res['filled'].tolist() == [True] and res['exit'].tolist() == ['T1'] and res['side'].tolist() == [-1]
    assert res['net'][0] != 0.0
    assert res['gross'][0] == pytest.approx(0.29254, abs=1e-5) and res['net'][0] == pytest.approx(0.112598, abs=1e-5)
    tr = s.chart_trade(res['refs'][0], q)
    assert tr['target'] == 1024 and tr['stop'] == pytest.approx(1030.6275) and 'Model B' in tr['note']


def test_causality_later_bars_change_nothing(monkeypatch):
    s = study()
    base = _b_window()
    _patch(monkeypatch, s, base)
    q = s.normalize({'model': 'B', 'n_bal': 60, 'start': '2022-04-04', 'end': '2022-04-04'})
    first = s.ideas(base, q)
    junk = base.copy()
    junk[62 + 14:, 1:5] = 5e5                         # everything after the entry bar becomes garbage
    s._IDEAS.clear()
    again = s.ideas(junk, q)
    assert [c['t'] for _, cs in first for c in cs][:1] == [c['t'] for _, cs in again for c in cs][:1]
    assert first[0][1][0]['entry'] == again[0][1][0]['entry'] == 1025.5


def _example(doc):
    ex = [e for e in doc['examples'] if e['kind'] == 'charts']
    assert len(ex) == 1, doc['id']
    return ex[0]


def _check_export(path):
    doc = json.loads(path.read_text(encoding='utf-8'))
    ex = _example(doc)
    kinds = [i['kind'] for i in ex['items']]
    n = int(next(k['value'] for k in doc['kpis'] if k['label'] == 'filled trades'))
    assert kinds == ['winner'] * 3 + ['loser'] * 3 if n >= 30 else set(kinds) <= {'winner', 'loser'}, (doc['id'], kinds)
    for it in ex['items']:
        assert it['svg'].startswith('<svg') and 'data-stop' not in it['svg'] and 'data-target' not in it['svg'] and 'data-exit' not in it['svg']
        assert (it['net_r'] > 0) == (it['kind'] == 'winner')
        m = re.search(r'([+-]\d+\.\d\d) R (long|short), ([a-z ]+) \(', it['svg'])
        assert m and abs(float(m.group(1)) - it['net_r']) < 0.006, (doc['id'], m)
        assert 'UTC' in it['svg'] and it['note']
    return doc


@pytest.mark.parametrize('prefix', ['desk-fabio_v3-', 'desk-tom_vp-'])
def test_exported_runs_carry_trade_charts(prefix):
    files = sorted((HERE / 'results').glob(prefix + '*.json'))
    assert len(files) >= 10, (prefix, len(files))
    for f in files:
        _check_export(f)


def test_export_result_adds_charts_example_and_strips_prices(tmp_path):
    class Fake:
        ID, TITLE = 'fake', 'Fake'
    svg = '<svg xmlns="x" data-stop="1.5" data-exit="2.5" data-target="None" data-fill="3.5" width="1"><text>+1.00 R long, hit target (5m)</text></svg>'
    out = {'settings': {'start': '2022-04-01', 'end': '2022-04-02'}, 'cond': None, 'verdict': 'FAILED', 'describe': 'd', 'label': 'l', 'cond_label': '',
           'curve': {'n': 1, 'r': [1.0], 'usd': [1010.0], 'start_usd': 1000.0, 'risk_pct': 1.0}, 'reason': 'r', 'n': 1, 'nofill': 0, 'mean': 1.0, 'lo': 0.5, 'hi': 1.5,
           'try_no': 1, 'charts': [{'kind': 'winner', 'net_r': 1.0, 'svg': svg, 'note': 'entry reason'}]}
    rid = desk.export_result(out, Fake, results_dir=tmp_path)
    doc = json.loads((tmp_path / (rid + '.json')).read_text(encoding='utf-8'))
    ex = _example(doc)
    assert ex['items'][0]['note'] == 'entry reason' and 'data-' not in ex['items'][0]['svg'] and '+1.00 R long' in ex['items'][0]['svg']
    assert [e['kind'] for e in doc['examples']][0] == 'curve'


def test_page_renders_charts_kind():
    import artifact.build_artifact as ba
    assert 'x.kind==="charts"' in ba.TEMPLATE


@pytest.mark.skipif(not _bars.data_ready(), reason='1m bars not on disk')
def test_dev_run_model_c_filled_only_inside_dev():
    s = study()
    r = s.run(s.normalize({'start': '2023-01-01', 'end': '2023-03-31'}), lambda m: None)
    f = r['filled']
    assert f.sum() > 30 and len(f) == f.sum()                       # no unfilled ideas exist for market entries
    assert (r['touch_t'] >= 1672531200000).all() and (r['touch_t'] < 1680307200000).all()
    assert not set(r['exit'].tolist()) - {'STOP', 'HOLD', 'T1'}
