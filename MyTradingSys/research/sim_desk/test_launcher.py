"""Launcher, first-use page and run comparison: no market data needed."""
import json
import sys
import threading
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.read().decode('utf-8')


def test_launcher_starts_answers_and_shuts_down():
    srv, url = desk.start_server(port=0, open_browser=False)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        assert url.startswith('http://127.0.0.1:') and not url.endswith(':0')
        assert 'Simulator' in _get(url + '/')
    finally:
        srv.shutdown()
        srv.server_close()
        t.join(5)
    assert not t.is_alive()


def test_busy_port_falls_forward_to_a_free_one():
    a, ua = desk.start_server(port=0, open_browser=False)
    try:
        b, ub = desk.start_server(port=a.server_address[1], open_browser=False)
        try:
            assert ua != ub
        finally:
            b.server_close()
    finally:
        a.server_close()


def test_first_page_names_the_wired_studies_and_dev_note():
    srv, url = desk.start_server(port=0, open_browser=False)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        html = _get(url + '/')
    finally:
        srv.shutdown(); srv.server_close()
    for s in desk.STUDIES.values():
        assert s.TITLE in html
    for sid in ('levels', 'rsi', 'wavetrend'):
        assert sid in desk.STUDIES
    assert 'DEV window only' in html


def _doc(rid, n, mean, lo, hi, verdict):
    return {'id': rid, 'title': 'T ' + rid, 'verdict': {'label': verdict, 'tone': 'warn'}, 'why': ['because'],
            'what': [{'name': 'Settings', 'value_plain': 'x', 'label': 'OURS'}],
            'kpis': [{'label': 'filled trades', 'value': str(n)}, {'label': 'ideas never filled', 'value': '0'},
                     {'label': 'average per trade, after fees', 'value': f'{mean:+.3f} R'},
                     {'label': '95 % range', 'value': f'{lo:+.3f} to {hi:+.3f} R'}]}


def test_runs_table_reads_results_files(tmp_path):
    import runs_view
    (tmp_path / 'desk-rsi-aaaa1111.json').write_text(json.dumps(_doc('desk-rsi-aaaa1111', 75, -0.02, -0.2, 0.15, 'NOT ENOUGH DATA')))
    (tmp_path / 'desk-levels-bbbb2222.json').write_text(json.dumps(_doc('desk-levels-bbbb2222', 255, -0.119, -0.3, 0.05, 'FAILED')))
    (tmp_path / 'other.json').write_text(json.dumps({'id': 'x', 'kpis': 'not a list'}))   # foreign schema is skipped, not fatal
    (tmp_path / 'bad.json').write_text('{nope')
    rows = runs_view.list_runs(tmp_path)
    assert [r['id'] for r in rows] == ['desk-levels-bbbb2222', 'desk-rsi-aaaa1111']
    r = rows[0]
    assert (r['study'], r['hash'], r['n'], r['mean'], r['lo'], r['hi'], r['verdict']) == ('levels', 'bbbb2222', 255, -0.119, -0.3, 0.05, 'FAILED')


def test_run_detail_refuses_path_tricks(tmp_path):
    import runs_view
    (tmp_path / 'desk-rsi-aaaa1111.json').write_text(json.dumps(_doc('desk-rsi-aaaa1111', 1, 0, 0, 0, 'FAILED')))
    assert runs_view.get_run(tmp_path, 'desk-rsi-aaaa1111')['id'] == 'desk-rsi-aaaa1111'
    for bad in ('../x', 'desk-rsi-aaaa1111/../../x', 'missing', ''):
        assert runs_view.get_run(tmp_path, bad) is None


def test_run_outside_dev_window_is_not_listed(tmp_path):
    import runs_view
    d = _doc('desk-rsi-cccc3333', 5, 0, 0, 0, 'FAILED'); d['window'] = 'DEV only, 2024-07-01 to 2025-01-01'
    (tmp_path / 'desk-rsi-cccc3333.json').write_text(json.dumps(d))
    assert runs_view.list_runs(tmp_path) == [] and runs_view.get_run(tmp_path, 'desk-rsi-cccc3333') is None


def test_every_study_default_sits_inside_dev():
    for s in desk.STUDIES.values():
        q = s.normalize({})
        if 'start' in q:
            desk.check_dates(q['start'], q['end'])
