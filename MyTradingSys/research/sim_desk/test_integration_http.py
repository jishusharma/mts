"""End-to-end wiring over real HTTP: page -> /api/* -> study -> verdict, charts, TRIALS.md row, cache, results/<id>.json.

Starts its own desk server on a free port (never 8765). A tiny synthetic study stands in for market data, so these run
anywhere; the date lock and the page/study wiring are also checked for every REAL study in studies/ (the lock refuses
before any data is read). Gaps this file closes: no other test drives POST /api/run or /api/trade through the server.
"""
import json
import re
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402


class Fake:
    """One-file study shape (PLUGIN.md). 40 trades, 20 per side, alternating hours, one hit-or-stop chart each."""
    ID = 'fakewire'
    TITLE = 'Fake wiring study'

    @staticmethod
    def params():
        return [{'name': 'x', 'label': 'X', 'number': True, 'min': 0, 'max': 9, 'step': 1},
                {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
                {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]

    @staticmethod
    def normalize(p):
        p = p or {}
        try:
            x = float(p.get('x', 1))
        except (TypeError, ValueError):
            raise ValueError('X: please type a number')
        s, e = desk.check_dates(p.get('start', '2022-04-01'), p.get('end', '2024-06-30'))
        return {'x': x, 'start': s, 'end': e}

    @staticmethod
    def label(q):
        return f"x {q['x']:g} {q['start']}..{q['end']}"

    @staticmethod
    def describe(q):
        return 'a fake study'

    @staticmethod
    def run(q, progress=None):
        n = 40
        i = np.arange(n)
        net = np.where(i % 2, 1.0, -0.5) * q['x']
        t = (i * 3600_000 * 5 + 1_650_000_000_000).astype(np.int64)    # every 5 h, from 2022-04-15 UTC
        return {'day': t // 86400000, 'touch_t': t, 'side': np.where(i % 4 < 2, 1, -1), 'net': net, 'gross': net, 'fees': np.zeros(n),
                'filled': np.ones(n, bool), 'all_days': np.unique(t // 86400000), 'refs': [int(x) for x in t],
                'exit': np.where(i % 2, 'T1', 'STOP')}

    @staticmethod
    def chart_trade(ref, q):
        bars = [{'t': ref + k * 60000, 'o': 100 + k, 'h': 102 + k, 'l': 99 + k, 'c': 101 + k} for k in range(12)]
        return {'bars': bars, 'side': 1, 'level': 100.0, 'entries': [(ref, 100.0)], 'stop': 98.0, 'target': 104.0,
                'exits': [(ref + 600000, 104.0, 'T1')], 'net_r': 1.0}


@pytest.fixture()
def server(tmp_path, monkeypatch):
    trials, cache, results = tmp_path / 'TRIALS.md', tmp_path / 'cache', tmp_path / 'results'
    trials.write_text('', encoding='utf-8')
    monkeypatch.setattr(desk, 'TRIALS', trials)
    monkeypatch.setattr(desk, 'RESULTS', results)
    monkeypatch.setattr(desk, 'STUDIES', {**desk.STUDIES, Fake.ID: Fake})
    real_run, real_export, real_chart = desk.run_setting, desk.export_result, desk.trade_chart
    monkeypatch.setattr(desk, 'run_setting', lambda *a, **k: real_run(*a, trials_path=trials, cache_dir=cache, **k))
    monkeypatch.setattr(desk, 'export_result', lambda out, study: real_export(out, study, results_dir=results))
    monkeypatch.setattr(desk, 'trade_chart', lambda *a, **k: real_chart(*a, cache_dir=cache, **k))
    monkeypatch.setattr(desk, 'refresh_catalogue', lambda *a, **k: None)
    srv, url = desk.start_server(port=0, open_browser=False)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield url, trials, results
    finally:
        srv.shutdown()
        srv.server_close()
        t.join(5)


def call(url, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url + path, data=data, headers={'Content-Type': 'application/json'} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def rows(trials):
    return [ln for ln in trials.read_text(encoding='utf-8').splitlines() if '| sim-desk fakewire ' in ln]


def test_run_repeat_lock_condition_trade_and_result_file(server):
    url, trials, results = server
    code, studies = call(url, '/api/studies')
    assert code == 200 and Fake.ID in [s['id'] for s in studies]
    assert f'data-study="{Fake.ID}"' in urllib.request.urlopen(url + '/').read().decode()

    code, a = call(url, '/api/run', {'study': Fake.ID, 'params': {'x': 2, 'start': '2023-01-01', 'end': '2023-06-30'}})
    assert code == 200 and a['n'] == 40 and a['cached'] is False and a['already_tried'] is False
    assert a['verdict'] in ('PASSED', 'FAILED', 'NOT ENOUGH DATA') and a['reason'] and len(a['charts']) == 6
    assert a['curve']['n'] == 40 and a['trades']['exit'][:2] and a['breakdown']['exit']
    assert len(rows(trials)) == 1 and a['try_no'] == 1
    rf = results / f"{a['result_id']}.json"
    doc = json.loads(rf.read_text(encoding='utf-8'))
    assert doc['id'] == a['result_id'] and doc['verdict']['label'] == a['verdict'] and doc['window'].startswith('DEV only')

    code, b = call(url, '/api/run', {'study': Fake.ID, 'params': {'x': 2, 'start': '2023-01-01', 'end': '2023-06-30'}})
    assert code == 200 and b['cached'] is True and b['already_tried'] is True and b['result_id'] == a['result_id']
    assert len(rows(trials)) == 1                                     # a repeat adds no ledger row

    for start, end in (('2023-01-01', '2024-07-01'), ('2022-03-31', '2023-01-01'), ('2025-01-01', '2025-02-01')):
        before = sorted(p.name for p in results.iterdir())
        code, e = call(url, '/api/run', {'study': Fake.ID, 'params': {'start': start, 'end': end}})
        assert code == 400 and 'DEV' in e['error']
        assert len(rows(trials)) == 1 and sorted(p.name for p in results.iterdir()) == before   # no row, no file

    code, c = call(url, '/api/run', {'study': Fake.ID, 'params': {'x': 2, 'start': '2023-01-01', 'end': '2023-06-30'}, 'cond': {'side': 'long'}})
    assert code == 200 and c['n_before_cond'] == 40 and 0 < c['n'] < 40 and c['cached'] is True
    assert c['result_id'] != a['result_id'] and (results / f"{c['result_id']}.json").exists()
    assert len(rows(trials)) == 2 and '~ if long only' in rows(trials)[1]   # a new condition is a new trial

    code, t = call(url, '/api/trade', {'study': Fake.ID, 'params': {'x': 2, 'start': '2023-01-01', 'end': '2023-06-30'}, 'i': 3})
    assert code == 200 and t['svg'].startswith('<svg')
    assert call(url, '/api/trade', {'study': 'nope', 'i': 0})[0] == 400
    assert call(url, '/api/run', {'study': 'nope'})[0] == 400
    assert call(url, '/api/run', {'study': Fake.ID, 'params': {'x': 'abc'}}) [0] == 400
    assert call(url, '/api/run', {'study': Fake.ID, 'params': {}, 'cond': {'hour_from': 30}})[0] == 400
    assert len(rows(trials)) == 2


def test_every_real_study_is_wired_to_the_page_and_the_date_lock(server):
    url, trials, results = server
    page = urllib.request.urlopen(url + '/').read().decode()
    code, studies = call(url, '/api/studies')
    real = [s for s in desk.STUDIES if s != Fake.ID]
    assert len(real) >= 4 and {s['id'] for s in studies} >= set(real)
    code, cond = call(url, '/api/conditions')
    assert code == 200 and set(cond['layers']) >= set(real)           # layer-B list includes every study
    for sid in real:
        mod = desk.STUDIES[sid]
        assert f'data-study="{sid}"' in page                          # a chip per study
        listed = next(s for s in studies if s['id'] == sid)
        assert {p['name'] for p in listed['params']} == set(listed['defaults'])      # no orphan control, no unused default
        assert hasattr(mod, 'chart_trade'), f'{sid} has no example-trade chart'
        code, e = call(url, '/api/run', {'study': sid, 'params': {'end': '2024-07-01'}})
        assert code == 400 and 'DEV' in e['error'], sid
        code, e = call(url, '/api/run', {'study': sid, 'params': {'start': '2022-03-31'}})
        assert code == 400 and 'DEV' in e['error'], sid
    assert not [ln for ln in trials.read_text(encoding='utf-8').splitlines() if ln.strip()]   # refused runs write nothing
    assert not results.exists() or not list(results.iterdir())


def test_every_page_endpoint_exists_on_the_server(server):
    url, _, _ = server
    html = (HERE / 'page.html').read_text(encoding='utf-8')
    used = set(re.findall(r"fetch\('(/api/[a-z]+)", html))
    assert {'/api/studies', '/api/conditions', '/api/progress', '/api/run', '/api/trade', '/api/runs'} <= used
    for path in sorted(used):
        if path in ('/api/run', '/api/trade'):
            code, _ = call(url, path, {'study': 'nope'})
            assert code == 400, path                                  # routed (not 404) and refused in plain words
        else:
            assert call(url, path)[0] == 200, path
