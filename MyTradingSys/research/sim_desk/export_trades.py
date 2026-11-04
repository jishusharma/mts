"""Per-trade replay exports for the Fabio v3 and Tom studies: results/desk-trades-<name>-<date>.json, every filled trade with its entry, stop, target,
exit (percent from the fill, signed in the trade's favour), exit reason, 1m bars held and net R after fees. DEV window only (the studies refuse
other dates). Runs go through desk.run_setting, so each setting is counted in the trial ledger like a desk click.

  python MyTradingSys/research/sim_desk/export_trades.py            # all of RUNS
  python MyTradingSys/research/sim_desk/export_trades.py fabio_v3-b  # one
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402
from studies import _bars  # noqa: E402
from artifact import build_artifact as ba  # noqa: E402

NL = '\n'
DATE = '2026-11-04'   # export date in the id: result rows added after the 2026-11-03 cards set carry it
LABELS = {'zero': 'Entry (fill)', 'l2': 'Stop', 't1': 'Target (the exit when there is none)', 't2': 'Exit'}
# name -> (study id, settings); defaults otherwise (OURS: the study defaults, one setting each, no search)
RUNS = {'fabio_v3-c': ('fabio_v3', {'model': 'C'}),
        'fabio_v3-b': ('fabio_v3', {'model': 'B'}),
        'tom_vp-fade': ('tom_vp', {'setup': 'FADE'}),
        'tom_spike_level': ('tom_spike_level', {})}
NOT_MEASURED = {'fabio_v3-ad': ('Fabio v3 Models A and D: per-trade replay',
                                'Models A (balance + CVD pressure, LVN pullback) and D (absorbed push, failed auction) need delta and big-trade fields; '
                                'the order-flow bars start 2024-12-02, after the DEV window ends 2024-06-30, so no DEV trade exists to replay '
                                '(studies/fabio_v3.py docstring; SETUP_REVIEW.md 3.1-3.2: CODED-UNSCORED).')}


def build(name, study, q, out, rows, results_dir):
    rid = f'desk-trades-{name}-{DATE}'
    tone = {'FAILED': 'bad', 'PASSED': 'good'}.get(out['verdict'], 'warn')
    cum = [round(float(x), 4) for x in np.cumsum([r['r'] for r in rows])]
    doc = {'id': rid, 'kind': 'backtest', 'parity': None, 'family': 'Desk runs',
           'title': f"{study.TITLE}: every trade ({out['label']})",
           'what': [{'name': 'Study', 'value_plain': f"{study.TITLE}: {out['describe']}", 'label': 'OURS'},
                    {'name': 'Settings', 'value_plain': out['label'], 'label': 'OURS'}],
           'how': 'export_trades.py replays every filled trade of the desk run from its own ref (same bars, same code, same fees) and lists entry, '
                  'stop, target and exit as percent from the fill, signed in the trade\'s favour; net R is after fees.',
           'window': f"DEV only, {q['start']} to {q['end']} (VALIDATION and HOLDOUT never offered)",
           'verdict': {'label': out['verdict'], 'tone': tone}, 'why': [out['reason']],
           'kpis': [{'label': 'filled trades', 'value': str(out['n'])},
                    {'label': 'average per trade, after fees', 'value': f"{out['mean']:+.3f} R" if out.get('mean') is not None else '-'},
                    {'label': '95 % range', 'value': f"{out['lo']:+.3f} to {out['hi']:+.3f} R" if out.get('lo') is not None else '-'},
                    {'label': 'try number', 'value': str(out['try_no'])}],
           'examples': [{'kind': 'replay', 'title': 'Every trade: entry, stop, target, exit (percent from the fill)', 'unit': 'R', 'labels': LABELS,
                         'trades': rows, 'cum': cum}] if rows else [{'kind': 'none', 'title': 'no filled trades'}],
           'source_files': ['MyTradingSys/research/sim_desk/export_trades.py', f'MyTradingSys/research/sim_desk/studies/{study.ID}.py'],
           'commit': 'local desk run', 'trades_exported': len(rows)}
    doc['banner'] = ba.banner_of(doc)
    p = Path(results_dir) / f'{rid}.json'
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + NL, encoding='utf-8', newline=NL)
    return rid


def not_measured(name, title, why, results_dir):
    rid = f'desk-trades-{name}-{DATE}'
    doc = {'id': rid, 'kind': 'backtest', 'parity': None, 'family': 'Desk runs', 'title': title,
           'what': [{'name': 'Study', 'value_plain': why, 'label': 'OURS'}], 'how': 'Not run: no data in the window.',
           'window': 'DEV only, 2022-04-01 to 2024-06-30 (VALIDATION and HOLDOUT never offered)',
           'verdict': {'label': 'NOT MEASURED', 'tone': 'warn'}, 'why': [why], 'kpis': [{'label': 'filled trades', 'value': '0'}],
           'examples': [{'kind': 'none', 'title': 'no trades: the data these models need starts after DEV'}],
           'source_files': ['MyTradingSys/research/sim_desk/export_trades.py'], 'commit': 'local desk run', 'trades_exported': 0}
    doc['banner'] = ba.banner_of(doc)
    (Path(results_dir) / f'{rid}.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + NL, encoding='utf-8', newline=NL)
    return rid


def export(name, results_dir=desk.RESULTS, progress=print, **kw):
    sid, p = RUNS[name]
    study = desk.STUDIES[sid]
    out = desk.run_setting(study, p, progress=progress, **kw)
    q = out['settings']
    res, _ = desk._raw(study, q, kw.get('cache_dir', desk.CACHE), progress)
    a = _bars.load_1m(progress, q.get('symbol', 'BTCUSDT'))
    rows = _bars.trade_rows(a, res, q)
    return build(name, study, q, out, rows, results_dir), len(rows)


def catalogue(rids, results_dir=desk.RESULTS):
    """Add or replace these result files' rows in _catalogue.json (row shape and order of build_catalogue.py). Not a full rebuild:
    that also pulls in other folders' rows that have no result card yet."""
    import build_catalogue as bc
    p = Path(results_dir) / '_catalogue.json'
    cat = json.loads(p.read_text(encoding='utf-8'))
    rows = [r for r in cat['rows'] if r['id'] not in rids]
    for rid in rids:
        d = json.loads((Path(results_dir) / f'{rid}.json').read_text(encoding='utf-8'))
        rows.append(bc.tag({'id': rid, 'family': d['family'], 'title': d['title'], 'kind': d['kind'], 'kind_source': 'result file',
                            'verdict': d['verdict']['label'], 'source': f'MyTradingSys/research/sim_desk/results/{rid}.json',
                            'exported': True, 'result_id': rid, 'date': DATE}))
    rows.sort(key=lambda r: (not r['exported'], r['family'].lower(), r['title'].lower()))
    cat.update(rows=rows, count=len(rows), exported=sum(1 for r in rows if r['exported']))
    p.write_text(json.dumps(cat, indent=0, ensure_ascii=False) + NL, encoding='utf-8', newline=NL)   # build_catalogue.py layout


def main(argv=None):
    names = (argv if argv is not None else sys.argv[1:]) or list(RUNS) + list(NOT_MEASURED)
    rids = []
    for n in names:
        if n in NOT_MEASURED:
            rids.append(not_measured(n, *NOT_MEASURED[n], desk.RESULTS))
            print(rids[-1], 0, flush=True)
        else:
            rid, k = export(n, progress=lambda m: None)
            rids.append(rid)
            print(rid, k, flush=True)
    catalogue(rids)


if __name__ == '__main__':
    main()
