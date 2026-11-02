"""Fabio Model C stand-in meta-label rerun on 2020-01-02..2022-03-31 (PRE_REG_EXT.md). Usage: python run_ext.py [--placebo N] [--no-export]
Writes numbers.json, output.md next to this file, trades to F:/MTS/runs/meta_label_dev_ext_2026-10-31, and the sim-desk result file."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ext_window as W  # noqa: E402
import analyze as A  # noqa: E402
import features as F  # noqa: E402
import fabio_v3  # noqa: E402

OUT = Path('F:/MTS/runs/meta_label_dev_ext_2026-10-31')
SPLIT = (18628, ('2020', '2021-01..2022-03'))       # 18628 = 2021-01-01 (days since epoch)
NAME = 'fabio_c_dev_ext'
TITLE_NAME = 'Fabio Model C price-only stand-in (ours), pre-DEV window 2020-01-02..2022-03-31'


def export(q, r, trades, aux, results_dir):
    import charts as ch
    res = fabio_v3.run(q, progress=lambda *_: None)
    filled = np.flatnonzero(np.asarray(res['filled'], bool))
    tt = np.asarray(res['touch_t'])[filled]
    bucket = {int(trades['touch_t'][i]): int(aux['tc'][j]) for j, i in enumerate(np.flatnonzero(aux['cc']))}
    items = []
    for lab, want in (('Best third by filter', 2), ('Worst third by filter', 0)):
        m = np.zeros(len(res['net']), bool)
        for k, i in enumerate(filled):
            m[i] = bucket.get(int(tt[k])) == want
        sub = dict(res)
        sub['filled'] = m
        for it in ch.make(fabio_v3, q, sub):
            it['note'] = f"{lab}: {it.get('note', '')}"
            items.append(it)
    ex = ch.export_example(items)
    ex['title'] = 'Example trades: 3 winners and 3 losers closest to typical, first in the best third by filter, then in the worst third'
    table = {'kind': 'table', 'title': f"{TITLE_NAME}: what each layer reading did to its trades (all filled trades; each layer's rows add up to the filled-trade count)",
             'caption': 'win % = share of trades above 0 R after fees; average R after fees per trade; readings are the raw state at entry',
             'cols': ['Layer reading', 'trades', 'win %', 'average R after fees'], 'rows': r['table']}
    line = A.verdict_line(r)
    tone = {'PASSED': 'good', 'FAILED': 'bad'}.get(r['verdict'], 'warn')
    rid = f'desk-meta_label_{NAME}'
    title = 'Meta-label rerun on the pre-DEV window, Fabio Model C price-only stand-in (ours): can other layers\' state at entry pick the winners?'
    doc = {'id': rid, 'kind': 'backtest', 'parity': None, 'family': 'Meta-label (layer filter)', 'title': title,
           'what': [{'name': 'Study', 'value_plain': f"{TITLE_NAME}. {fabio_v3.TITLE}: {fabio_v3.label(q)}", 'label': 'OURS'},
                    {'name': 'Filter', 'value_plain': 'same frozen logistic score from 8 layer readings as the DEV test, scored out of fold (6 week-purged blocks); thirds by score. '
                     'Pre-registered in research/meta_label_dev_ext_2026-10-31/PRE_REG_EXT.md before any trade list of this window existed', 'label': 'OURS'}],
           'how': 'Re-ran the study on the older data before DEV, scored every trade out of fold, compared the best third by score with a random third; shuffled-label placebo and day-block bootstrap in RESULT.md.',
           'window': 'pre-DEV 2020-01-02 to 2022-03-31 only (DEV from 2022-04-01, VALIDATION and HOLDOUT never offered)',
           'verdict': {'label': r['verdict'], 'tone': tone}, 'why': [line],
           'kpis': [{'label': 'filled trades', 'value': str(r['n_filled'])}],
           'examples': [table, ex], 'source_files': ['MyTradingSys/research/meta_label_dev_ext_2026-10-31/run_ext.py'], 'commit': 'local desk run'}
    d = Path(results_dir)
    (d / f'{rid}.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    cp = d / '_catalogue.json'
    cat = json.loads(cp.read_text(encoding='utf-8'))
    cat['rows'] = [x for x in cat['rows'] if x['id'] != rid]
    cat['rows'].append({'id': rid, 'family': doc['family'], 'title': title, 'kind': 'backtest', 'kind_source': 'result file', 'verdict': r['verdict'],
                        'source': f'MyTradingSys/research/sim_desk/results/{rid}.json', 'exported': True, 'result_id': rid, 'date': '2026-11-02',
                        'status': 'FAILED' if r['verdict'] == 'FAILED' else 'SEE_VERDICT',
                        'verdict_class': {'PASSED': 'passed', 'FAILED': 'failed'}.get(r['verdict'], 'unclear')})
    cat['rows'].sort(key=lambda x: (not x['exported'], x['family'].lower(), x['title'].lower()))
    cat['count'], cat['exported'] = len(cat['rows']), sum(1 for x in cat['rows'] if x['exported'])
    cp.write_text(json.dumps(cat, indent=0, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    return rid


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--placebo', type=int, default=300)
    ap.add_argument('--no-export', action='store_true')
    ap.add_argument('--trades-only', action='store_true')
    a = ap.parse_args(argv)
    a6, a5 = W.load_window()
    q = W.install(a6, a5)
    res = fabio_v3.run(q, progress=lambda *_: None)
    m = np.asarray(res['filled'], bool)
    order = np.argsort(np.asarray(res['touch_t'])[m], kind='stable')
    t = {k: np.asarray(res[k])[m][order] for k in ('touch_t', 'side', 'net', 'gross', 'fees', 'exit')}
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez(OUT / 'trades_fabio_c_dev_ext.npz', **t)
    W.guard(t['touch_t'], 'trades')
    print('filled n', len(t['net']), 'first/last', int(t['touch_t'][0]), int(t['touch_t'][-1]), 'sd(unconditional)', round(float(t['net'].std(ddof=1)), 4))
    if a.trades_only:
        return
    ctx = F.build_context(a6, W.load_funding())
    raw = F.raw_features(ctx, t['touch_t'])
    r, aux = A.analyse(NAME, t, raw, a.placebo, split=SPLIT)
    r['fill_check'] = A.fill_check(fabio_v3, q)
    r['holm_p'], r['bh_q'], r['family_m'] = A.holm([r['placebo_p']] * 2)[0], A.bh([r['placebo_p']] * 2)[0], 2
    r['pooled_with_P0_n_top_arithmetic'] = r['n_top'] + 162
    md = [f"# Output of run_ext.py ({TITLE_NAME})\n", f"{A.verdict_line(r)}\n",
          f"Holm placebo p {r['holm_p']:.3f} (m = 2), BH q {r['bh_q']:.3f}\n", '| layer reading | trades | win % | average R after fees |', '|---|---|---|---|']
    md += ['| ' + ' | '.join(row) + ' |' for row in r['table']] + ['']
    (HERE / 'numbers.json').write_text(json.dumps(r, indent=1) + '\n', encoding='utf-8', newline='\n')
    (HERE / 'output.md').write_text('\n'.join(md) + '\n', encoding='utf-8', newline='\n')
    if not a.no_export:
        print('export', export(q, r, t, aux, HERE.parent / 'sim_desk' / 'results'))


if __name__ == '__main__':
    main()
