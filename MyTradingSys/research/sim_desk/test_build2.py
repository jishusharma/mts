"""sim_build2: breakdown table, collapsed page sections, catalogue-safe saving. Expected numbers are worked out by hand."""
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402
from test_conditions import SideStudy  # noqa: E402


def ms(y, mo, d, h=0):
    return int(dt.datetime(y, mo, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)


def test_breakdown_by_hand():
    """4 filled trades + 1 never filled. 2022-05-01 03h long +1.0; 2022-06-01 05h short -1.0; 2023-01-01 03h long +0.5;
    2023-02-01 23h long -0.5; the unfilled idea (2023, long, +9) must not count. Buckets are 4 h wide, UTC."""
    res = {'net': [1.0, -1.0, 0.5, -0.5, 9.0], 'filled': [True, True, True, True, False], 'side': [1, -1, 1, 1, 1],
           'touch_t': [ms(2022, 5, 1, 3), ms(2022, 6, 1, 5), ms(2023, 1, 1, 3), ms(2023, 2, 1, 23), ms(2023, 3, 1, 3)]}
    b = desk.breakdown(res)
    assert b['year'] == [{'k': '2022', 'n': 2, 'mean': 0.0, 'few': True}, {'k': '2023', 'n': 2, 'mean': 0.0, 'few': True}]
    assert b['side'] == [{'k': 'long', 'n': 3, 'mean': pytest.approx(0.333, abs=1e-3), 'few': True},
                         {'k': 'short', 'n': 1, 'mean': -1.0, 'few': True}]
    assert b['hour'] == [{'k': '00-04 UTC', 'n': 2, 'mean': 0.75, 'few': True}, {'k': '04-08 UTC', 'n': 1, 'mean': -1.0, 'few': True},
                         {'k': '20-24 UTC', 'n': 1, 'mean': -0.5, 'few': True}]


def test_breakdown_marks_few_only_under_30():
    n = 30
    res = {'net': [0.1] * (n + 1), 'filled': [True] * (n + 1), 'side': [1] * (n + 1), 'touch_t': [ms(2022, 5, 1, 1) + i for i in range(n)] + [ms(2023, 5, 1, 1)]}
    y = {r['k']: r for r in desk.breakdown(res)['year']}
    assert y['2022']['n'] == 30 and y['2022']['few'] is False and y['2023']['few'] is True


def test_breakdown_empty_run():
    assert desk.breakdown({'net': [], 'touch_t': [], 'filled': [], 'side': []}) == {'year': [], 'side': [], 'hour': []}


def test_page_collapses_charts_and_ledger_and_shows_breakdown():
    h = (HERE / 'page.html').read_text(encoding='utf-8')
    assert 'id="bd"' in h and 'too few trades' in h
    assert '<details id="chartbox"' in h and '<details id="ledgerbox"' in h
    assert h.index('id="nums"') < h.index('id="bd"') < h.index('id="chartbox"')   # verdict, numbers, breakdown above the toggles


def test_saved_run_is_in_the_catalogue(tmp_path):
    """Fails if a run the desk saves to results/ has no catalogue row (that file broke CI once)."""
    class Fake(SideStudy):   # own class: SideStudy.calls is shared state in test_conditions
        calls = 0
        TITLE = 'Side fake'
    trials = tmp_path / 'TRIALS.md'
    trials.write_text('', encoding='utf-8')
    out = desk.run_setting(Fake, {}, trials_path=trials, cache_dir=tmp_path / 'c')
    res = tmp_path / 'res'
    rid = desk.export_result(out, Fake, res)
    cat = json.loads((res / '_catalogue.json').read_text(encoding='utf-8'))
    saved = {p.stem for p in res.glob('*.json') if not p.name.startswith('_')}
    assert saved == {rid}
    assert {r['result_id'] for r in cat['rows'] if r['exported']} == saved
    assert len({r['id'] for r in cat['rows']}) == len(cat['rows'])
    row = next(r for r in cat['rows'] if r['id'] == rid)
    assert row['kind'] == 'backtest' and row['exported'] is True and row['verdict'] == out['verdict']
